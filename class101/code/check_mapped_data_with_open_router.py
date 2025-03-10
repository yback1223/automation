from openai import OpenAI
from typing import Any

import json


OPEN_ROUTER_DEEPSEEK_API_KEY = "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"

OPEN_ROUTER_API_KEY = OPEN_ROUTER_DEEPSEEK_API_KEY

class OpenRouterClient:
    def __init__(self, open_router_api_key: str, base_url: str = "https://openrouter.ai/api/v1"):
        self.client = OpenAI(
            base_url=base_url,
            api_key=open_router_api_key,
            default_headers={
                "HTTP-Referer": "https://github.com/",  # 필수 헤더
                "X-Title": "Python Script"  # 필수 헤더
            }
        )

    def get_completion(self, message):
        completion = self.client.chat.completions.create(
            extra_body = {
                "transforms": ["middle-out"]
            },
            # model = "deepseek/deepseek-r1:free",
            model = "google/gemini-2.0-flash-exp:free",
            messages = [
                {
                    "role": "user",
                    "content": message
                }
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return completion.choices[0].message.content
    
    def make_message(self, job_hir_code: dict[str, Any]) -> list[dict[str, Any]]:
        return f"""
job_hir_code: {job_hir_code}

prompt:
Analyze the following job_hir_code dictionary and remove only the categories that are not directly related to the job title.
- Delete categories with low relevance, but do not add any new categories.
- The deletion can be skipped if the categories are related to the job title.
- Only return the modified job_hir_code dictionary. 
- No Explanation is needed.
- Don't include like ```python or ```json in the response. I need just the dictionary.
"""

if __name__ == "__main__":
    open_router_client = OpenRouterClient(open_router_api_key = OPEN_ROUTER_API_KEY)

    with open("./job_hir_codes.json", "r", encoding='utf-8') as f:
        job_hir_codes = json.load(f)

    new_job_hir_codes = []
    failed_job_hir_codes = []

    for job_hir_code in job_hir_codes:
        message = open_router_client.make_message(job_hir_code)

        response_content = open_router_client.get_completion(message=message)
    
        result_flag = False
        if not response_content:
            print(f"Empty response content for job_hir_code: {job_hir_code}")
            result_flag = True
            
        try:
            parsed_content = json.loads(response_content)
            new_job_hir_codes.append(parsed_content)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON response for job_hir_code: {parsed_content}")
            print(f"Error: {e}")
            result_flag = True

        if result_flag:
            failed_job_hir_codes.append(job_hir_code)

    with open("./new_job_hir_codes.json", "w", encoding='utf-8') as f:
        json.dump(new_job_hir_codes, f, ensure_ascii=False, indent=4)

    with open("./failed_job_hir_codes.json", "w", encoding='utf-8') as f:
        json.dump(failed_job_hir_codes, f, ensure_ascii=False, indent=4)
