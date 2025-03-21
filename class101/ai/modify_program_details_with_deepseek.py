import os
import json
import time
from openai import OpenAI
from class101 import RESOURCE_DIR

# OPENROUTER_API_KEY = "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"  # OpenRouter API 키를 여기에 입력하세요
OPENROUTER_API_KEY = "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"

class DeepSeekProgramDescriptionModifier:
    def __init__(self, api_key: str = OPENROUTER_API_KEY, file_path: str = None):
        self.api_key = api_key
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.input_file_path = file_path or os.path.join(RESOURCE_DIR, "class101_program_details_deepseek.json")
        self.output_file_path = file_path or os.path.join(RESOURCE_DIR, "class101_program_details_deepseek.json")

    def load_crawled_data(self) -> list[dict]:
        try:
            with open(self.input_file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            # 파일이 없으면 빈 리스트로 새로 생성
            with open(self.input_file_path, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=4)
            return []
    
    def save_crawled_data_to_particular_program(self, edited_data: str, index: int) -> None:
        try:
            with open(self.output_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            # 출력 파일이 없으면 입력 파일의 데이터로 초기화
            data = self.load_crawled_data()
        
        # 리스트가 비어있거나 인덱스가 범위를 벗어났을 경우 새 항목 추가
        if index >= len(data):
            data.append({})
        
        data[index]["program_description_by_deepseek"] = edited_data
        
        with open(self.output_file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def get_program_description(self, program: dict) -> str:    
        program_description = program["program_description"]
        program_kit = program["program_kit"]

        program_description_prompt_input = f"""
        program_description: {program_description}
        program_kit: {program_kit}

        Generate a text output based on the provided program_description and program_kit. The output must be plain text with no Markdown formatting (e.g., no #, *, or ```) and written entirely in Korean. Use a variety of fun and expressive emojis (e.g., 🌟, 🎉, 🖌️, 🍎, 🚚) as list markers to keep it lively, but do not include emojis within the list items themselves.

        The output should include these sections:

        1. Title: A catchy and relevant title inspired by program_description.
        2. Summary: A detailed and friendly overview that fully incorporates the program_description, expanding on it with additional context or appeal.
        3. Software Requirements: A list of required software (state they are not included), adding brief explanations if relevant.
        4. Equipment Options: A detailed list of items from program_kit, including any specs or extras, elaborated for clarity.
        5. Delivery Info: Details on shipping or availability, with practical and upbeat phrasing.
        6. Final Note: A positive and motivating closing statement that ties back to program_description.

        Additional requirements:
        - The output must be in Korean with no links or URLs.
        - The output length must be at least 3 times longer than the input program_description.
        - Each section (Title, Summary, etc.) should be expanded with rich details and examples.
        - For the Summary section, add relevant background information and benefits.
        - For the Equipment Options section, provide detailed descriptions and usage tips for each item.
        - For the Software Requirements section, explain why each software is needed and how it will be used.
        - For the Delivery Info section, include estimated delivery times and handling instructions.
        - Keep the tone cheerful, creative, and engaging throughout.
        - Make sure to maintain a natural flow between sections.
        """
        return program_description_prompt_input

    def get_data_length(self) -> int:
        crawled_data = self.load_crawled_data()
        return len(crawled_data)

    def get_particular_program(self, index: int) -> dict:
        crawled_data = self.load_crawled_data()
        return crawled_data[index]

    def get_program_description_from_deepseek(self, program_description_prompt_input: str) -> str:
        max_retries = 3
        retry_delay = 60  # 60초 대기

        for attempt in range(max_retries):
            try:
                completion = self.client.chat.completions.create(
                    model="deepseek/deepseek-r1:free",
                    messages=[
                        {
                            "role": "user",
                            "content": program_description_prompt_input
                        }
                    ]
                )
                return completion.choices[0].message.content

            except Exception as e:
                raise e

    def process_programs(self, start_index):
        length_of_crawled_data = self.get_data_length()

        for i in range(start_index, length_of_crawled_data):
            try:
                program = self.get_particular_program(index=i)
                program_description_prompt_input = self.get_program_description(program=program)

                program_description_from_deepseek = self.get_program_description_from_deepseek(program_description_prompt_input=program_description_prompt_input)
                self.save_crawled_data_to_particular_program(edited_data=program_description_from_deepseek, index=i)
                print(f"Finished {i} - {program['program_name']}")
                
                # API 호출 간 딜레이 추가
                time.sleep(2)  # 2초 대기
                
            except Exception as e:
                print(f"Error processing index {i}: {str(e)}")
                continue

if __name__ == "__main__":
    modifier = DeepSeekProgramDescriptionModifier()
    modifier.process_programs(start_index=0) 