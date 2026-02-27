import os
import json
import time
import yaml
import random
import shortuuid
import pandas as pd
import requests
from typing import Optional, TYPE_CHECKING
import boto3
from pathlib import Path
from glob import glob
from threading import Lock
import base64
import uuid
from giga import GigaChat
from tqdm import tqdm
from google.genai.types import Part, Content, GenerateContentConfig, HttpOptions as GoogleHttpOptions
from google import genai
import threading
import time

from utils.bedrock_utils import create_llama3_body, create_nova_messages, extract_answer

# API setting constants
API_MAX_RETRY = 3
API_RETRY_SLEEP = 10
API_ERROR_OUTPUT = None
CLIENT: Optional["GigaChat"] = None
LOCK = Lock()

registered_api_completion = {}
registered_engine_completion = {}


def register_api(api_type):
    def decorator(func):
        registered_api_completion[api_type] = func
        return func

    return decorator


def register_engine(engine_type):
    def decorator(func):
        registered_engine_completion[engine_type] = func
        return func

    return decorator


def load_questions(question_file: str):
    """Load questions from a file."""
    questions = []
    with open(question_file, "r") as ques_file:
        for line in ques_file:
            if line:
                questions.append(json.loads(line))
    return questions


def load_model_answers(answer_dir: str):
    """Load model answers.

    The return value is a python dict of type:
    Dict[model_name: str -> Dict[uid: int -> answer: dict]]
    """
    filenames = glob(os.path.join(answer_dir, "*.jsonl"))
    filenames.sort()
    model_answers = {}

    for filename in filenames:
        model_name = os.path.basename(filename)[:-6]
        answer = {}
        with open(filename) as fin:
            for line in fin:
                line = json.loads(line)
                answer[line["uid"]] = line
        model_answers[model_name] = answer

    return model_answers


def load_id_to_model_answers(answer_dir: str):
    """Load model answers.

    The return value is a python dict of type:
    Dict[model_name: str -> Dict[uid: int -> answer: dict]]
    """
    filenames = glob(os.path.join(answer_dir, "*.jsonl"))
    filenames.sort()
    model_answers = {}

    for filename in filenames:
        model_name = os.path.basename(filename)[:-6]
        
        with open(filename) as fin:
            for line in fin:
                line = json.loads(line)
                
                if line["uid"] in model_answers:
                    model_answers[line["uid"]][model_name] = line
                else:
                    model_answers[line["uid"]] = {model_name: line}
                
    return model_answers


def get_endpoint(endpoint_list):
    if endpoint_list is None:
        return None
    assert endpoint_list is not None
    # randomly pick one
    api_dict = random.choices(
        endpoint_list
    )[0]
    return api_dict


# load config args from config yaml files
def make_config(config_file: str) -> dict:
    config_kwargs = {}
    with open(config_file, "r") as f:
        config_kwargs = yaml.load(f, Loader=yaml.SafeLoader)

    return config_kwargs

class GeminiClientWrapper:
    def __init__(self, api_key, index, BASE_URL_SDK, INITIAL_CONCURRENCY = 8, MIN_CONCURRENCY = 1):
        self.index = index

        HTTP_OPTIONS = GoogleHttpOptions(base_url=BASE_URL_SDK, client_args={"verify": False, "cert": None})

        self.client = genai.Client(api_key=api_key, http_options=HTTP_OPTIONS)
        self.concurrency = INITIAL_CONCURRENCY
        self.min_concurrency = MIN_CONCURRENCY
        self.active_requests = 0
        self.lock = threading.Lock()
        self.is_active = True
        self.cooldown_until = 0
        self.consecutive_rate_limits = 0

    def can_accept_request(self):
        with self.lock:
            if not self.is_active:
                return False
            if time.time() < self.cooldown_until:
                return False
            return self.active_requests < self.concurrency

    def acquire(self):
        with self.lock:
            self.active_requests += 1

    def release(self):
        with self.lock:
            self.active_requests -= 1

    def throttle(self):
        """Called when 429 is encountered"""
        with self.lock:
            self.consecutive_rate_limits += 1
            
            # If we are already at MIN_CONCURRENCY and keep hitting limits
            if self.concurrency == self.min_concurrency and self.consecutive_rate_limits >= 3:
                print(f"[Client {self.index}] Repeated 429s at min concurrency. Likely Quota Exceeded. Marking inactive.")
                self.is_active = False
                return

            old_concurrency = self.concurrency
            self.concurrency = max(self.min_concurrency, self.concurrency // 2)
            self.cooldown_until = time.time() + 5 # 5 seconds cooldown
            print(f"[Client {self.index}] Throttling down: {old_concurrency} -> {self.concurrency} (Consecutive 429s: {self.consecutive_rate_limits})")

    def mark_inactive(self):
        with self.lock:
            self.is_active = False
            print(f"[Client {self.index}] Quota exceeded or fatal error. Marking inactive.")

    def success(self):
        """Called on success"""
        with self.lock:
            self.consecutive_rate_limits = 0 # Reset counter on success


@register_api("openai")
def chat_completion_openai(model, messages, temperature, max_tokens, api_dict=None, **kwargs):
    import openai
    if api_dict:
        client = openai.OpenAI(
            base_url=api_dict["api_base"],
            api_key=api_dict["api_key"],
        )
    else:
        client = openai.OpenAI()

    processed_messages = []
    for msg in messages:
        m = msg.copy()
        image_url = m.pop("image_url", None)
        if image_url:
            content = m.get("content", "")
            parts = content if isinstance(content, list) else (
                [{"type": "text", "text": content}] if content else []
            )
            parts.append({"type": "image_url", "image_url": {"url": image_url}})
            m["content"] = parts
        processed_messages.append(m)
        
    if api_dict and "model_name" in api_dict:
        model = api_dict["model_name"]
    
    output = API_ERROR_OUTPUT
    for _ in range(API_MAX_RETRY):
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=processed_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                )
            output = {
                "answer": completion.choices[0].message.content
            }
            break
        except openai.RateLimitError as e:
            print(type(e), e)
            time.sleep(API_RETRY_SLEEP)
        except openai.BadRequestError as e:
            print(processed_messages)
            print(type(e), e)
        except KeyError:
            print(type(e), e)
            break
    
    return output


@register_api("openrouter")
def chat_completion_openrouter(model, messages, temperature, max_tokens, api_dict=None, **kwargs):
    assert api_dict is not None, "api_dict is required for OpenRouter"
    api_base = api_dict.get("api_base", "https://openrouter.ai/api/v1")
    api_key = api_dict.get("api_key")
    assert api_key, "api_key required in api_dict for OpenRouter"
    
    if api_dict and "model_name" in api_dict:
        model = api_dict["model_name"]
    
    def get_file_format(file_path):
        return Path(file_path).suffix.lstrip(".").lower()
    
    def encode_file_to_base64(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')
    
    def is_audio_file(file_path):
        audio_formats = {'wav', 'mp3', 'aiff', 'aac', 'ogg', 'flac', 'm4a'}
        ext = get_file_format(file_path)
        return ext in audio_formats
    
    def is_image_file(file_path):
        image_formats = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
        ext = get_file_format(file_path)
        return ext in image_formats
    
    processed_messages = []
    for msg in messages:
        m = msg.copy()
        
        file_path = m.pop("file_path", None)
        
        text_content = m.get("content", "")

        if not text_content and not file_path:
            print("skip %s because file_path is not provided" % m)
            continue

        if file_path and not os.path.exists(file_path):
            print(f"Warning: File not found: {file_path}")
            continue

        if file_path:
            file_format = get_file_format(file_path)

        assert file_path is not None and file_format, "Unknown format for file"
        
        content_parts = []
        
        if text_content:
            content_parts.append({
                "type": "text",
                "text": text_content
            })

        if file_path:
            base64_file = encode_file_to_base64(file_path)
        
        if file_path and is_audio_file(file_path):
            content_parts.append({
                "type": "input_audio",
                "input_audio": {
                    "data": base64_file,
                    "format": file_format
                }
            })
        elif file_path and is_image_file(file_path):
            data_uri = f"data:image/{file_format};base64,{base64_file}"
            content_parts.append({
                "type": "image_url",
                "image_url": {
                    "url": data_uri
                }
            })
        elif file_path:
            print(f"Warning: Unknown file format for file: {file_path}")
            continue
        
        if not content_parts:
            print(f"Warning: No content parts were created for file: {file_path}")
            continue
        
        if len(content_parts) == 1 and content_parts[0]["type"] == "text":
            m["content"] = content_parts[0]["text"]
        else:
            m["content"] = content_parts
        
        processed_messages.append(m)
    
    url = f"{api_base}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    if api_dict:
        if "http_referer" in api_dict:
            headers["HTTP-Referer"] = api_dict["http_referer"]
        if "x_title" in api_dict:
            headers["X-Title"] = api_dict["x_title"]
    
    payload = {
        "model": model,
        "messages": processed_messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    
    output = API_ERROR_OUTPUT
    for _ in range(API_MAX_RETRY):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            output = {
                "answer": result["choices"][0]["message"]["content"]
            }
            break
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e}")
            if e.response is not None:
                if e.response.status_code == 429:
                    time.sleep(API_RETRY_SLEEP)
                elif e.response.status_code == 400:
                    print(f"Request payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
                    print(f"Response: {e.response.text}")
                    break
                else:
                    time.sleep(API_RETRY_SLEEP)
            else:
                time.sleep(API_RETRY_SLEEP)
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {type(e).__name__}: {e}")
            time.sleep(API_RETRY_SLEEP)
        except KeyError as e:
            print(f"KeyError: {e}")
            if 'response' in locals() and response is not None:
                print(f"Response: {response.text}")
            else:
                print("No response available")
            break
        except Exception as e:
            print(f"Unexpected error: {type(e).__name__}: {e}")
            time.sleep(API_RETRY_SLEEP)
    
    return output


@register_api("openai_thinking")
def chat_completion_openai_thinking(model, messages, api_dict=None, **kwargs):
    import openai
    
    if api_dict:
        client = openai.OpenAI(
            api_key=api_dict["api_key"],
        )
    else:
        client = openai.OpenAI()
    
    output = API_ERROR_OUTPUT
    for i in range(API_MAX_RETRY):
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=messages,
                reasoning_effort=kwargs['reasoning_effort'] if 'reasoning_effort' in kwargs else 'medium',
            )
            output = {
                "answer": completion.choices[0].message.content
            }
            break
        except openai.RateLimitError as e:
            print(type(e), e)
            time.sleep(API_RETRY_SLEEP)
        except openai.BadRequestError as e:
            print(messages)
            print(type(e), e)
        except KeyError:
            print(type(e), e)
            break
    
    return output


@register_api("deepseek_reasoner")
def chat_completion_deepseek_reasoner(messages, api_dict, **kwargs):
    import urllib.request

    chat_endpoint_headers = {
        "User-Agent": "curl/8.7.1",
        "Authorization": "Bearer {}".format(api_dict['api_key']),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    chat_endpoint_url = "https://api.deepseek.com/chat/completions"
    
    req_body = {
        "messages": messages,
        "model": "deepseek-reasoner",
        "stream": False,
    }
    req_data = json.dumps(req_body, ensure_ascii=False).encode("utf-8")
    
    output = API_ERROR_OUTPUT
    for i in range(API_MAX_RETRY):
        try:
            req = urllib.request.Request(
                chat_endpoint_url,
                headers = chat_endpoint_headers.copy(),
                data = req_data,
            )
            
            with urllib.request.urlopen(req) as res:
                res_data = res.read()
            res_body = json.loads(res_data.decode("utf-8"))
            
            output = {
                "thought": res_body["choices"][0]["message"]["reasoning_content"],
                "answer": res_body["choices"][0]["message"]["content"],
            }
            break
        except Exception as e:
            print(type(e), e)
            time.sleep(API_RETRY_SLEEP)
            
    return output


@register_api("deepseek")
def chat_completion_deepseek(messages, max_tokens, api_dict, **kwargs):
    import urllib.request

    chat_endpoint_headers = {
        "User-Agent": "curl/8.7.1",
        "Authorization": "Bearer {}".format(api_dict['api_key']),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    chat_endpoint_url = "https://api.deepseek.com/chat/completions"
    
    req_body = {
        "messages": messages,
        "model": "deepseek-chat",
        "stream": False,
        "max_tokens": max_tokens,
    }
    req_data = json.dumps(req_body, ensure_ascii=False).encode("utf-8")
    
    output = API_ERROR_OUTPUT
    for i in range(API_MAX_RETRY):
        try:
            req = urllib.request.Request(
                chat_endpoint_url,
                headers = chat_endpoint_headers.copy(),
                data = req_data,
            )
            
            with urllib.request.urlopen(req) as res:
                res_data = res.read()
            res_body = json.loads(res_data.decode("utf-8"))
            
            output = {
                "answer": res_body["choices"][0]["message"]["content"],
            }
            break
        except Exception as e:
            print(type(e), e)
            time.sleep(API_RETRY_SLEEP)
            
    return output


@register_api("anthropic")
def chat_completion_anthropic(model, messages, temperature, max_tokens, api_dict=None, **kwargs):
    import anthropic

    if api_dict:
        api_key = api_dict["api_key"]
    else:
        api_key = os.environ["ANTHROPIC_API_KEY"]

    sys_msg = ""
    if messages[0]["role"] == "system":
        sys_msg = messages[0]["content"]
        messages = messages[1:]

    output = API_ERROR_OUTPUT
    for _ in range(API_MAX_RETRY):
        try:
            c = anthropic.Anthropic(api_key=api_key)
            response = c.messages.create(
                model=model,
                messages=messages,
                stop_sequences=[anthropic.HUMAN_PROMPT],
                max_tokens=max_tokens,
                temperature=temperature,
                system=sys_msg
            )
            output = {
                "answer": response.content[0].text
            }
            break
        except anthropic.APIError as e:
            print(type(e), e)
            time.sleep(API_RETRY_SLEEP)
    return output


@register_api("anthropic_thinking")
def chat_completion_anthropic_thinking(model, messages, max_tokens, budget_tokens, **kwargs):
    import anthropic

    client = anthropic.Anthropic(
        timeout=1200,
    )
    
    output = API_ERROR_OUTPUT
    for _ in range(API_MAX_RETRY):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                thinking={
                    "type": "enabled",
                    "budget_tokens": budget_tokens
                },
                messages=messages,
            )
            output = {
                "thought": response.content[0].thinking,
                "answer": response.content[1].text,
            }
            break
        except anthropic.APIError as e:
            print(type(e), e)
            time.sleep(API_RETRY_SLEEP)

    return output


@register_api("mistral")
def chat_completion_mistral(model, messages, temperature, max_tokens, **kwargs):
    from mistralai.client import MistralClient
    from mistralai.models.chat_completion import ChatMessage
    from mistralai.exceptions import MistralException

    api_key = os.environ["MISTRAL_API_KEY"]
    client = MistralClient(api_key=api_key)

    prompts = [ChatMessage(role=message["role"], content=message["content"]) for message in messages]
    
    output = API_ERROR_OUTPUT
    for _ in range(API_MAX_RETRY):
        try:
            chat_response = client.chat(
                model=model,
                messages=prompts,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            output = {
                "answer": chat_response.choices[0].message.content
            }
            break
        except MistralException as e:
            print(type(e), e)
            break

    return output


@register_api("xai")
def chat_completion_xai(model, messages, temperature, max_tokens, api_dict=None, **kwargs):
    import xai_sdk

    client = xai_sdk.Client(api_key=api_dict['api_key'], api_host=api_dict['api_base']).compat
    output = API_ERROR_OUTPUT
    
    for _ in range(API_MAX_RETRY):
        try:
            stream = client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
                max_tokens=max_tokens,
            temperature=temperature,
            top_p=0.95,
            )
            output = ""
            for chunk in stream:
                output += chunk.choices[0].delta.content
                
            break
        except Exception as e:
            print(type(e), e)
    

@register_api("gemini")
def http_completion_gemini(model, messages, **kwargs):
    import requests
    
    api_key = os.environ["GEMINI_API_KEY"]
    
    safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_NONE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_NONE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_NONE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_NONE"
        },
    ]

    sys_prompt = None
    if messages[0]["role"] == "system":
        sys_prompt = {
            "parts":[
                {"text": messages[0]["content"]}
                ]
            }
        messages = messages[1:]
        
    role_map = {"user": "user",
                "assistant": "model"}
    
    conv = [{"parts":[{"text":turn["content"]}], "role":role_map[turn["role"]]} for turn in messages]
    
    json_request = {
            "contents": conv,
            "safetySettings": safety_settings,
            "systemInstruction": sys_prompt,
    }

    if "temperature" in kwargs and "max_tokens" in kwargs:
        gen_config = {
            "temperature": kwargs["temperature"],
            "maxOutputTokens": kwargs["max_tokens"],
        }
        json_request["generationConfig"] = gen_config
    elif "temperature" in kwargs:
        gen_config = {
            "temperature": kwargs["temperature"],
        }
        json_request["generationConfig"] = gen_config
    elif "max_tokens" in kwargs:
        gen_config = {
            "maxOutputTokens": kwargs["max_tokens"],
        }
        json_request["generationConfig"] = gen_config
        
    output = API_ERROR_OUTPUT
    for _ in range(API_MAX_RETRY):
        try:
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}",
                json=json_request,
            )
        except Exception as e:
            print(f"**API REQUEST ERROR** Reason: {e}.")
            time.sleep(API_RETRY_SLEEP)
        if response.status_code != 200:
            print(f"**API REQUEST ERROR** Reason: status code {response.status_code}.")
            time.sleep(API_RETRY_SLEEP)
        try:
            output = {
                "answer": response.json()["candidates"][0]["content"]["parts"][0]["text"],
            }
        except KeyError as e:
            print(type(e), e)
            print(response.json())
    return output
    

@register_api("gemini-audio")
def http_completion_gemini_audio(api_dict, messages, **kwargs):
    client_wrapper = GeminiClientWrapper(api_dict['api_key'], 0, api_dict['api_base'], kwargs['parallel'])

    user_message_idx = 0
    config = None
    if len(messages) > 1:
        user_message_idx += 1
        config=GenerateContentConfig(
            system_instruction=messages[0]['content'],
        )
    
    user_message = [Part.from_text(text=messages[user_message_idx]['content'])]
    if 'file_path' in messages[user_message_idx]:
        with open(messages[user_message_idx]['file_path'], "rb") as f:
            audio_bytes = f.read()
        
        audio_part = Part.from_bytes(data=audio_bytes, mime_type='audio/wav')
        user_message.append(audio_part)

    resp = client_wrapper.client.models.generate_content(
        model='models/' + kwargs['model'],
        contents=[
            Content(
                role='user',
                parts=user_message
            )
        ],
        config=config,
    )

    return {'answer': resp.candidates[0].content.parts[0].text}
    

@register_api("vertex")
def vertex_completion_gemini(model, messages, project_id, regions, **kwargs):
    import requests
    import subprocess
    
    output = API_ERROR_OUTPUT
    
    # Obtain the access token using gcloud CLI
    access_token = subprocess.check_output(
        ["gcloud", "auth", "application-default", "print-access-token"], 
        text=True
    ).strip()

    if messages[0]["role"] == "system":
        data = {
            "systemInstruction": {
                "role": "system", # ignored by vertexi api (04/18/2025)
                "parts": [{
                    "text": messages[0]["content"]
                }]
            },
        }
        messages = messages[1:]
    else:
        data = {}
        
    role_map = {
        "user": "user",
        "assistant": "model"
    }
    
    messages = [{"parts":[{"text":turn["content"]}], "role":role_map[turn["role"]]} for turn in messages]

    url = (
        f"https://us-central1-aiplatform.googleapis.com/v1/projects/"
        f"{project_id}/locations/{regions}/publishers/google/models/"
        f"{model}:generateContent"
    )
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    data = data | {
        "contents": messages,
    } 
    
    if "temperature" in kwargs or "max_tokens" in kwargs:
        gen_config = {}
        if "temperature" in kwargs:
            gen_config["temperature"] = kwargs["temperature"]
        if "max_tokens" in kwargs:
            gen_config["maxOutputTokens"] = kwargs["max_tokens"]
        data["generationConfig"] = gen_config

    response = requests.post(url, json=data, headers=headers)
    
    try:
        output = {
            "answer": response.json()["candidates"][0]["content"]["parts"][0]["text"],
        }
    except KeyError as e:
        print(type(e), e)
        print(response.json())
        
    return output


@register_api("cohere")
def chat_completion_cohere(model, messages, temperature, max_tokens, **kwargs):
    import cohere

    co = cohere.Client(os.environ["COHERE_API_KEY"])
    assert len(messages) > 0

    template_map = {"system":"SYSTEM",
                    "assistant":"CHATBOT",
                    "user":"USER"}

    assert messages[-1]["role"] == "user"
    prompt = messages[-1]["content"]

    if len(messages) > 1:
        history = []
        for message in messages[:-1]:
            history.append({"role":template_map[message["role"]], "message":message["content"]})
    else:
        history = None

    output = API_ERROR_OUTPUT
    for _ in range(API_MAX_RETRY):
        try:
            response = co.chat(
                message=prompt,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                chat_history=history,
            )
            output = {
                "answer": response.text
            }
            break
        except cohere.core.api_error.ApiError as e:
            print(type(e), e)
            raise
        except Exception as e:
            print(type(e), e)
            break
    
    return output


@register_api("meta")
def chat_completion_meta(model, messages, temperature, max_tokens, api_dict, **kwargs):
    assert api_dict
    texts = [{"role": m["role"],
              "text": m["content"]} for m in messages]
            
    output = ""
    for _ in range(API_MAX_RETRY):
        try:
            res = requests.post(
                f"{api_dict['api_base']}/chat_stream_completions?access_token={api_dict['api_key']}",
                stream=True,
                headers={"Content-Type": "application/json"},
                json={
                    "model": model,
                    "chunks_delimited": True,
                    "messages": texts,
                    "options": {
                        "max_tokens": max_tokens,
                        "generation_algorithm": "top_p",
                        "top_p": 1,
                        "temperature": temperature,
                    },
                },
                timeout=30,
            )
            if res.status_code == 200:
                for line in res.iter_lines():
                    if line:
                        part = json.loads(line.decode("utf-8"))
                        if "text" in part:
                            output += part["text"]
                break
            else:
                print(f"**API REQUEST ERROR** Code: {res.status_code}")
                time.sleep(API_RETRY_SLEEP)
        except Exception as e:
            print("**API REQUEST ERROR** Reason: Unknown.")
            time.sleep(API_RETRY_SLEEP)
            continue
        
    return {
        "answer": output
    }


def reorg_answer_file(answer_file):
    """Sort by question id and de-duplication"""
    answers = {}
    with open(answer_file, "r") as fin:
        for l in fin:
            qid = json.loads(l)["uid"]
            answers[qid] = l

    qids = sorted(list(answers.keys()))
    with open(answer_file, "w") as fout:
        for qid in qids:
            fout.write(answers[qid])


def batch_submit_sglang(
    executor, 
    tokenizer, 
    temperature, 
    max_tokens, 
    all_context,
    max_context_length=None,
    end_think_token=None,
):
    print(f"DEBUG: sglang_completion_qwq: max_context_length: {max_context_length}")
    
    sampling_params = {
        "temperature": temperature,
        "skip_special_tokens": False,
        "max_new_tokens": max_tokens - 1,
        "no_stop_trim": True,
    }
        
    batch_prompt_token_ids = []
    batch_uids =[]
    uid_to_prompt = {}
    uid_to_response = {}
    
    for context in all_context:
        prompt_token_ids = tokenizer.apply_chat_template(
            context['turns'],
            add_generation_prompt=True,
            tokenize=True,
        )
        
        if max_context_length and (len(prompt_token_ids) + max_tokens) > max_context_length:
            print(f"DEBUG: sglang_completion_qwq: context length ({len(prompt_token_ids) + max_tokens}) > max_context_length ({max_context_length}), skip this context")
            continue
        
        batch_prompt_token_ids.append(prompt_token_ids)
        batch_uids.append(context['uid'])
        
        uid_to_prompt[context['uid']] = context['turns']
        
    err_msg = f"ERROR: len(batch_prompt_token_ids): {len(batch_prompt_token_ids)} != len(batch_uids): {len(batch_uids)}"
    assert len(batch_prompt_token_ids) == len(batch_uids), err_msg
    
    _ = executor.submit(
        prompt_token_ids=batch_prompt_token_ids,
        sampling_params=[sampling_params] * len(batch_uids),
        keys=batch_uids,
    )
    
    for request in tqdm(executor.as_completed(), total=len(batch_uids)):
        uid = request.key()
        result = request.result()
        raw_response = tokenizer.decode(
            result['output_ids'],
            skip_special_tokens=True,
        )
        
        if end_think_token:
            thought, _, ans = raw_response.partition(end_think_token)
            if ans == "":
                uid_to_response[uid] = {"thought": thought, "answer": raw_response}
            else:
                uid_to_response[uid] = {"thought": thought, "answer": ans}
        else:
            uid_to_response[uid] = {"answer": raw_response}
    
    # assert len(uid_to_response) == len(all_context), f"ERROR: len output ({len(uid_to_response)}) != len input ({len(all_context)})"
    return uid_to_response


def _infer_cuda_tp_world_size():
    cuda_devices = os.environ.get("CUDA_VISIBLE_DEVICES", None)
    if cuda_devices is None:
        tp_world_size = 8
    else:
        tp_world_size = len(cuda_devices.split(","))
    return tp_world_size


def download_model(model: str, max_workers: int = 64):
    import subprocess
    
    env = os.environ.copy()
    env["HF_HUB_ENABLE_HF_TRANSFER"] = "0"
    
    cmd = [
        "huggingface-cli", 
        "download", 
        f"--max-workers={max_workers}", 
        model
    ]
    
    try:
        subprocess.run(cmd, env=env, check=True)
        print(f"Successfully downloaded model '{model}' with {max_workers} max workers.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while downloading the model: {e}")


@register_engine("sglang")
def sglang_completion(
    model, 
    batch_context,
    answer_file,
    temperature,
    max_tokens=32768,
    end_think_token=None,
    **kwargs,
):
    from transformers import AutoTokenizer
    from utils.sglang_server import SGLangServerExecutor
    from utils.add_markdown_info import count_markdown_elements, remove_pattern
    import tiktoken
    import re

    tokenizer = AutoTokenizer.from_pretrained(model)
    
    uids = [context['uid'] for context in batch_context]
    prompts = [context['prompt'] for context in batch_context]
    processed_context = [
        {
            "uid": uids[i], 
            "turns": [{
                "content": prompts[i],
                "role": "user",
            }]
        } 
        for i in tqdm(range(len(uids)))
    ]
    download_model(model=model)
    
    server_args = {
        "model_path": model,
        "dtype": "auto",
        "tp_size": _infer_cuda_tp_world_size(),
        "mem_fraction_static": 0.7,
        "max_prefill_tokens": max_tokens,
        "max_workers": 256,
        "server_port": 30000,
    }
    
    executor = SGLangServerExecutor(
        **server_args,
    )
    
    print(f"DEBUG: sglang_completion_qwq: model: {model}")
    
    uid_to_response = batch_submit_sglang(
        executor=executor, 
        tokenizer=tokenizer,
        temperature=temperature,
        max_tokens=max_tokens,
        all_context=processed_context,
        end_think_token=end_think_token,
    )
    
    executor.join()
    print("DEBUG: sglang_completion_qwq: done, sleep 10 seconds...")
    time.sleep(10)
        
    num_null = sum(
        [uid_to_response[uid]['answer'] is None for uid in uids if uid in uid_to_response]
    )
    print(f"Number of null responses: {num_null}")
    
    df = pd.DataFrame()
    df['uid'] = [context['uid'] for context in processed_context if context['uid'] in uid_to_response]
    df['ans_id'] = [shortuuid.uuid() for _ in range(len(df))]
    df['model'] = model
    df['messages'] = [
        context['turns'] + [
            {"content": uid_to_response[context['uid']], "role": "assistant"}
        ]
        for context in processed_context if context['uid'] in uid_to_response
    ]
    df['tstamp'] = [time.time() for _ in range(len(df))]
    
    encoding = tiktoken.encoding_for_model("gpt-4o")
    metadata = [
        {
            "token_len": len(encoding.encode(uid_to_response[context['uid']]['answer'], disallowed_special=()))
        } | count_markdown_elements(
            remove_pattern(
                uid_to_response[context['uid']]['answer'], 
                re.compile("```([^`]*)```")),
                suffix="",
        )
        for context in processed_context if context['uid'] in uid_to_response
    ]
    df["metadata"] = metadata 
    
    df.to_json(answer_file, lines=True, orient="records", force_ascii=False)
    
    pass


@register_api("aws_claude")
def chat_completion_aws_bedrock_claude(messages, api_dict=None, aws_region="us-west-2", **kwargs):
    """
    Call AWS Bedrock API for chat completion
    
    Args:
        model (str): Model ID
        conv (object): Conversation object containing messages
        temperature (float): Temperature parameter for response generation
        max_tokens (int): Maximum tokens in response
        api_dict (dict, optional): API configuration dictionary
        aws_region (str, optional): AWS region, defaults to "us-west-2"
        
    Returns:
        str: Generated response text or error message
    """
        
    # Configure AWS client if api_dict provided
    if api_dict is not None:
        bedrock_rt_client = boto3.client(
            service_name='bedrock-runtime',
            region_name=aws_region,
            aws_access_key_id=api_dict.get('aws_access_key_id'),
            aws_secret_access_key=api_dict.get('aws_secret_access_key')
        )
    else:
        bedrock_rt_client = boto3.client(
            service_name='bedrock-runtime',
            region_name=aws_region,)
    
    output = API_ERROR_OUTPUT
    
    #get kwargs from settings
    temperature= kwargs["temperature"]
    max_tokens= kwargs["max_tokens"]
    model = kwargs["model_id"]
    
    sys_msg = ""
    if messages[0]["role"] == "system":
        sys_msg = messages[0]["content"]
        messages = messages[1:]
    else:
        prompt = messages[0]['content']

    
    # Retry logic for API calls
    for _ in range(API_MAX_RETRY):
        try:
            # Prepare request body
            prompt_json = {
                "system": sys_msg,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "anthropic_version": "bedrock-2023-05-31",
                "stop_sequences": ["Human"]
            }

            # Call Bedrock API
            response = bedrock_rt_client.invoke_model(
                body=json.dumps(prompt_json, ensure_ascii=False),
                modelId=model,
                accept='application/json',
                contentType='application/json'
            )
            
            # Parse response
            response_body = json.loads(response.get('body').read())
            output = {"answer":response_body.get("content")[0].get("text")}
            break
            
        except Exception as e:
            print(type(e), e)
            time.sleep(API_RETRY_SLEEP)
            
    return output

@register_api("aws_mistral")
def chat_completion_aws_bedrock_mistral(messages, api_dict=None, aws_region="us-west-2", **kwargs):
    """
    Call AWS Bedrock API for chat completion
    
    Args:
        model (str): Model ID
        conv (object): Conversation object containing messages
        temperature (float): Temperature parameter for response generation
        max_tokens (int): Maximum tokens in response
        api_dict (dict, optional): API configuration dictionary
        aws_region (str, optional): AWS region, defaults to "us-west-2"
        
    Returns:
        str: Generated response text or error message
    """
        
    # Configure AWS client if api_dict provided
    if api_dict is not None:
        bedrock_rt_client = boto3.client(
            service_name='bedrock-runtime',
            region_name=aws_region,
            aws_access_key_id=api_dict.get('aws_access_key_id'),
            aws_secret_access_key=api_dict.get('aws_secret_access_key')
        )
    else:
        bedrock_rt_client = boto3.client(
            service_name='bedrock-runtime',
            region_name=aws_region,)
    
    output = API_ERROR_OUTPUT

    #get kwargs from settings
    temperature= kwargs["temperature"]
    max_tokens= kwargs["max_tokens"]
    model = kwargs["model_id"]
    
    # Retry logic for API calls
    for _ in range(API_MAX_RETRY):
        try:
            ## =============== Format prompt ================
            prompt = "\n".join([content for message in messages for content in message["content"]])
            formatted_prompt = f"<s>[INST] {prompt.strip()} [/INST]"            
            body = {
                "prompt": formatted_prompt,
                "max_tokens": max_tokens,
                "stop": ["Human:"],
                "temperature": temperature,
            }

            # Call Bedrock API
            response = bedrock_rt_client.invoke_model(
                body=json.dumps(body, ensure_ascii=False),
                modelId=model,
                accept='application/json',
                contentType='application/json'
            )
            
            # Parse response
            response_body = json.loads(response.get('body').read())
            
            if "pixtral-large" in model: #us.mistral.pixtral-large-2502-v1:0
                output = {"answer": response_body.get("choices")[0].get("message").get("content")}
            else:
                output = {"answer": response_body.get("outputs")[0].get("text")}
      
            break
            
        except Exception as e:
            print(type(e), e)
            time.sleep(API_RETRY_SLEEP)
            
    return output


@register_api("aws_llama")
def chat_completion_aws_bedrock_llama(messages, api_dict=None, aws_region="us-west-2", **kwargs):
    """
    Call AWS Bedrock API for chat completion using Llama models

    Args:
    model (str): Model ID
    conv (object): Conversation object containing messages
    temperature (float): Temperature parameter for response generation
    max_tokens (int): Maximum tokens in response
    api_dict (dict, optional): API configuration dictionary
    aws_region (str, optional): AWS region, defaults to "us-west-2"

    Returns:
    str: Generated response text or error message
    """

    # Configure AWS client if api_dict provided
    if api_dict is not None:
        bedrock_rt_client = boto3.client(
            service_name='bedrock-runtime',
            region_name=aws_region,
            aws_access_key_id=api_dict.get('aws_access_key_id'),
            aws_secret_access_key=api_dict.get('aws_secret_access_key')
        )
    else:
        bedrock_rt_client = boto3.client(
            service_name='bedrock-runtime',
            region_name=aws_region,
        )

    output = API_ERROR_OUTPUT
    
    #get kwargs from settings
    temperature= kwargs["temperature"]
    max_tokens= kwargs["max_tokens"]
    model = kwargs["model_id"]
    
    # Retry logic for API calls
    for _ in range(API_MAX_RETRY):
        try:
            # Prepare request body using the create_llama3_body function
            prompt_json = create_llama3_body(
                messages,
                max_gen_len=max_tokens,
                temperature=temperature                
            )

            # Call Bedrock API
            response = bedrock_rt_client.invoke_model(
                body=prompt_json,
                modelId=model,
                accept='application/json',
                contentType='application/json'
            )

            # Parse response
            response_body = json.loads(response.get('body').read())
            output = {"answer" : response_body.get("generation", "")}
            break

        except Exception as e:
            print(type(e), e)
            time.sleep(API_RETRY_SLEEP)

    return output

@register_api("aws_nova")
def chat_completion_aws_bedrock_nova( messages, api_dict=None, aws_region="us-west-2", **kwargs):
    """
    Call AWS Bedrock API for chat completion using Nova models

    Args:
    model (str): Model ID
    conv (object): Conversation object containing messages
    temperature (float): Temperature parameter for response generation
    max_tokens (int): Maximum tokens in response
    api_dict (dict, optional): API configuration dictionary
    aws_region (str, optional): AWS region, defaults to "us-west-2"

    Returns:
    str: Generated response text or error message
    """

    # Configure AWS client if api_dict provided
    
    if api_dict is not None:
        bedrock_rt_client = boto3.client(
            service_name='bedrock-runtime',
            region_name=aws_region,
            aws_access_key_id=api_dict.get('aws_access_key_id'),
            aws_secret_access_key=api_dict.get('aws_secret_access_key')
        )
    else:
        bedrock_rt_client = boto3.client(
            service_name='bedrock-runtime',
            region_name=aws_region,
        )

    output = API_ERROR_OUTPUT

    #get kwargs from settings
    temperature= kwargs["temperature"]
    max_tokens= kwargs["max_tokens"]
    model = kwargs["model_id"]

    # Retry logic for API calls
    for _ in range(API_MAX_RETRY):
        try:
            # Create messages from conversation
            messages = create_nova_messages(messages)
            inferenceConfig = {
                "max_new_tokens": max_tokens,
                "temperature": temperature                 
            }

            # Prepare request body
            model_kwargs = {"messages": messages,
                            "inferenceConfig": inferenceConfig,}
            body = json.dumps(model_kwargs, ensure_ascii=False)

            # Call Bedrock API
            response = bedrock_rt_client.invoke_model(
                body=body,
                modelId=model,
                accept='application/json',
                contentType='application/json'
            )

            # Parse response
            response_body = json.loads(response.get('body').read())
            output = {"answer": response_body['output']['message']['content'][0]['text']}
            break

        except Exception as e:
            print(type(e), e)
            time.sleep(API_RETRY_SLEEP)

    return output

@register_api("aws_deepseek")
def chat_completion_aws_bedrock_deepseek(messages, api_dict=None, aws_region="us-west-2", **kwargs):
    """
    Call AWS Bedrock API for chat completion using DeepSeek models

    Args:
    model (str): Model ID
    conv (object): Conversation object containing messages
    temperature (float): Temperature parameter for response generation
    max_tokens (int): Maximum tokens in response
    api_dict (dict, optional): API configuration dictionary
    aws_region (str, optional): AWS region, defaults to "us-west-2"

    Returns:
    str: Generated response text or error message
    """

    # Configure AWS client if api_dict provided
    if api_dict is not None:
        bedrock_rt_client = boto3.client(
            service_name='bedrock-runtime',
            region_name=aws_region,
            aws_access_key_id=api_dict.get('aws_access_key_id'),
            aws_secret_access_key=api_dict.get('aws_secret_access_key')
        )
    else:
        bedrock_rt_client = boto3.client(
            service_name='bedrock-runtime',
            region_name=aws_region,
        )

    output = API_ERROR_OUTPUT

    #get kwargs from settings
    temperature= kwargs["temperature"]
    max_tokens= kwargs["max_tokens"]
    model = kwargs["model_id"]
    

    # Retry logic for API calls
    for _ in range(API_MAX_RETRY):
        try:
            # Create messages from conversation            
            # Embed the prompt in DeepSeek-R1's instruction format.            
            prompt = "\n".join([content for message in messages for content in message["content"]])
            formatted_prompt = f"""
            <｜begin▁of▁sentence｜><｜User｜>{prompt.strip()}<｜Assistant｜><think>\n
            """
           
            # Prepare request body          
            body = json.dumps({
                                "prompt": formatted_prompt,
                                "max_tokens": max_tokens,
                                "temperature": temperature,
                                "top_p": 0.9,
                            }, ensure_ascii=False)


            # Call Bedrock API
            response = bedrock_rt_client.invoke_model(
                body=body,
                modelId=model,
                accept='application/json',
                contentType='application/json'
            )
            
            # Parse response
            response_body = json.loads(response.get('body').read()) 
            
            # Extract choices
            choices = response_body["choices"]                
            output = {
                "answer": extract_answer(choices[0]['text'])
            }
            
            break

        except Exception as e:
            
            time.sleep(API_RETRY_SLEEP)

    return output


def prepare_audio_file(file_path):
    file_path = Path(file_path)
    with open(file_path, mode="rb") as fp:
        encode_data = base64.b64encode(fp.read())
    return {
        "content": encode_data.decode("utf-8"),
        "mime": "audio/wav",
        "type": "audio",
        "id": str(uuid.uuid4()),
        "name": file_path.name}


@register_api("giga")
def chat_completion_giga(model, messages, temperature, max_tokens, api_dict=None, **kwargs):
    global CLIENT
    
    with LOCK:
        if CLIENT is None:
            CLIENT = GigaChat()
    
    processed_messages = []

    multimodal_mode = os.environ.get("GIGA_MULTIMODAL_MODE", "")
    
    for message in messages:
        processed_message = message.copy()

        if multimodal_mode == "upload":
            processed_message.pop("file_url", None)

        if "file_path" in processed_message:     
            file_path = processed_message.pop("file_path", None)

            if "files" not in processed_message:
                processed_message["files"] = []
            processed_message["files"].append(prepare_audio_file(file_path))

        processed_messages.append(processed_message)

    output = API_ERROR_OUTPUT
    for _ in range(API_MAX_RETRY):
        try:
            completion = CLIENT.chat(
                model=model,
                messages=processed_messages,
                temperature=temperature,
                max_tokens=max_tokens
                )
            output = {"answer": completion['choices'][0]['message']['content']}
            break
        except KeyError as e:
            print(type(e), e)
            break
        except Exception as e:
            print(type(e), e)
            time.sleep(API_RETRY_SLEEP)
    
    return output
