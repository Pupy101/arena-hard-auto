import argparse
import json
import os
import re
import time
import concurrent.futures

import tiktoken
import shortuuid
import tqdm

from utils.add_markdown_info import count_markdown_elements, remove_pattern
from utils.completion import (
    load_questions,
    load_model_answers,
    make_config,
    get_endpoint,
    registered_api_completion,
    registered_engine_completion,
    reorg_answer_file,
    API_ERROR_OUTPUT,
)


def get_answer(
    question: dict, answer_file: str, settings: dict
):
    # build messages
    messages = []
    if "sys_prompt" in settings:
        messages.append({"role": "system", "content": settings["sys_prompt"]})
    
    user_message = {"role": "user"}
    prompt = question.get("prompt", "").strip()
    if prompt:
        user_message["content"] = prompt
    
    if "file_url" in question and question["file_url"]:
        user_message["file_url"] = question["file_url"]
    
    if "file_path" in question and question["file_path"]:
        user_message["file_path"] = os.path.join("data", config["main_bench_name"], config["bench_name"], "cache", question["file_path"][9:])
    
    if "file_url" in user_message and "content" not in user_message:
        user_message["content"] = "Solve the problem based on the provided file."
    
    assert "content" in user_message or "file_url" in user_message, \
        f"Question {question.get('uid', 'unknown')} must have either non-empty prompt or image_url"
    
    messages.append(user_message)

    # retrieve the api completion function from register
    api_completion_func = registered_api_completion[settings["api_type"]]
    
    # build arguments for api completions
    kwargs = settings | {
        "api_dict": get_endpoint(settings["endpoints"]),
        "messages": messages,
    }
    
    output = api_completion_func(**kwargs)
        
    if output is API_ERROR_OUTPUT:
        return
    
    messages.append({"role": "assistant", "content": output})

    # Dump answers
    # Extract model name from answer_file path (answer_file format: "data/{bench_name}/model_answer/{model}.jsonl")
    model = os.path.basename(answer_file).replace(".jsonl", "")
    ans = {
        "uid": question["uid"],
        "ans_id": shortuuid.uuid(),
        "model": model,
        "messages": messages,
        "tstamp": time.time(),
    }
    
    encoding = tiktoken.encoding_for_model("gpt-4o")
    metadata = {
        "token_len": len(encoding.encode(output['answer'], disallowed_special=()))
    }
    ans["metadata"] = metadata | count_markdown_elements(
        remove_pattern(
            output['answer'], 
            re.compile("```([^`]*)```")
        ),
        suffix="",
    )

    os.makedirs(os.path.dirname(answer_file), exist_ok=True)
    with open(answer_file, "a", encoding="utf-8") as fout:
        fout.write(json.dumps(ans, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "--config-file", type=str, default="config/gen_answer_config.yaml"
    )
    parser.add_argument(
        "--endpoint-file", type=str, default="config/endpoint.yaml"
    )
    parser.add_argument(
        "--max-samples", type=int, default=None, help="Maximum number of samples to process (limits to first N samples)"
    )
    parser.add_argument("--question-file", type=str, default='question.jsonl', help="Question file to process")
    args = parser.parse_args()

    config = make_config(args.config_file)
    endpoints = make_config(args.endpoint_file)

    existing_answer = load_model_answers(os.path.join("data", config["main_bench_name"], config["bench_name"], "model_answer"))
    
    print(config)

    for model in config["model_list"]:
        assert model in endpoints
        endpoint_settings = endpoints[model]

        question_file = os.path.join("data", config["main_bench_name"], config["bench_name"], args.question_file)
        questions = load_questions(question_file)
        
        # Limit to first N samples if --max-samples is specified
        if args.max_samples is not None:
            questions = questions[:args.max_samples]
            print(f"Limited to first {args.max_samples} samples")

        answer_file = os.path.join("data", config["main_bench_name"], config["bench_name"], "model_answer", f"{model}.jsonl")
        print(f"Output to {answer_file}")

        if "parallel" in endpoint_settings:
            parallel = endpoint_settings["parallel"]
        else:
            parallel = 1

        if 'local_engine' in endpoint_settings and endpoint_settings['local_engine']:
            local_completion_func = registered_engine_completion[endpoint_settings['api_type']]
            
            # Apply max_samples limit for local_engine too
            batch_context = questions
            if args.max_samples is not None:
                batch_context = questions[:args.max_samples]
            
            kwargs = endpoint_settings | {
                "answer_file": answer_file,
                "batch_context": batch_context,
            }
            local_completion_func(**kwargs)
            
            reorg_answer_file(answer_file)
            
        else:
            with concurrent.futures.ThreadPoolExecutor(max_workers=parallel) as executor:
                futures = []
                count = 0
                for index, question in enumerate(questions):
                    if model in existing_answer and question["uid"] in existing_answer[model]:
                        count += 1
                        continue
                    future = executor.submit(
                        get_answer,
                        question,
                        answer_file,
                        endpoint_settings,
                    )
                    futures.append(future)
                if count > 0:
                    print(f"{count} number of existing answers")
                for future in tqdm.tqdm(
                    concurrent.futures.as_completed(futures), total=len(futures)
                ):
                    future.result()

            reorg_answer_file(answer_file)
            
