import os
import json
import time
import google.generativeai as genai
from class101 import RESOURCE_DIR

GEMINI_API_KEY = "AIzaSyBT3p4sqHvx-eHW0HZlbGKle4YxPfoN8E4"

class GeminiProgramDescriptionModifier:
    def __init__(self, api_key: str = GEMINI_API_KEY, file_path: str = None):
        self.api_key = api_key
        self.input_file_path = file_path or os.path.join(RESOURCE_DIR, "class101_program_details_gemini.json")
        self.output_file_path = file_path or os.path.join(RESOURCE_DIR, "class101_program_details_gemini.json")
        self.data = None

    def load_crawled_data(self) -> list[dict]:
        try:
            with open(self.input_file_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
                return self.data
        except FileNotFoundError:
            # 파일이 없으면 빈 리스트로 새로 생성
            self.data = []
            with open(self.input_file_path, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=4)
            return self.data
    
    def save_all_data(self) -> None:
        """모든 데이터를 한 번에 저장합니다."""
        with open(self.output_file_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def update_program_description(self, edited_data: str, index: int) -> None:
        """메모리 상의 데이터를 업데이트합니다."""
        if index >= len(self.data):
            self.data.append({})
        self.data[index]["program_description_by_gemini"] = edited_data

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
        - Fully utilize the program_description without omitting any part of it, and expand it to make the output (in characters) significantly longer than the program_description.
        - Mention program_kit items explicitly in the equipment section.
        - Keep the tone cheerful, creative, and engaging throughout.
        """
        return program_description_prompt_input

    def get_data_length(self) -> int:
        if self.data is None:
            self.load_crawled_data()
        return len(self.data)

    def get_particular_program(self, index: int) -> dict:
        if self.data is None:
            self.load_crawled_data()
        return self.data[index]

    def get_program_description_from_gemini(self, program_description_prompt_input: str) -> str:
        genai.configure(api_key=self.api_key)

        # Create the model
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }

        model = genai.GenerativeModel(
            model_name="gemma-3-27b-it",
            generation_config=generation_config,
        )

        chat_session = model.start_chat(
            history=[]
        )

        try:
            response = chat_session.send_message(program_description_prompt_input)
            return response.text
        except Exception as e:
            if "429" in str(e):
                print(f"API 할당량 초과. 10초 대기 후 재시도...")
                time.sleep(10)
                return self.get_program_description_from_gemini(program_description_prompt_input)
            else:
                print(f"에러 발생: {str(e)}")
                raise e

    def process_programs(self, start_index: int) -> None:
        if self.data is None:
            self.load_crawled_data()
        
        length_of_crawled_data = self.get_data_length()
        requests_in_minute = 0
        minute_start_time = time.time()
        save_interval = 10  # 10개의 프로그램마다 저장

        for i in range(start_index, length_of_crawled_data):
            try:
                start_time = time.time()
                program = self.get_particular_program(index=i)

                if program.get("program_description_by_gemini"):
                    print(f'{i}번째 프로그램은 이미 처리되었습니다.')
                    continue
                print(f'{i}번째 프로그램 처리 중...{program["program_name"]}')
                
                program_description_prompt_input = self.get_program_description(program=program)
                program_description_from_gemini = self.get_program_description_from_gemini(program_description_prompt_input=program_description_prompt_input)
                
                self.update_program_description(edited_data=program_description_from_gemini, index=i)
                
                # 일정 간격으로 저장
                if (i + 1) % save_interval == 0:
                    print(f"중간 저장 중... ({i + 1}/{length_of_crawled_data})")
                    self.save_all_data()

                end_time = time.time()
                processing_time = end_time - start_time
                print(f"Finished {i} - {program['program_name']} (처리 시간: {processing_time:.2f}초)")

                # 1분당 요청 수 제한 처리
                requests_in_minute += 1
                current_time = time.time()
                time_elapsed = current_time - minute_start_time

                if requests_in_minute >= 2:
                    if time_elapsed < 60:
                        wait_time = 60 - time_elapsed
                        print(f"1분당 2개 요청 제한. {wait_time:.2f}초 대기...")
                        time.sleep(wait_time)
                    
                    # 1분 카운터 리셋
                    requests_in_minute = 0
                    minute_start_time = time.time()

            except Exception as e:
                print(f"프로그램 {i} 처리 중 에러 발생: {str(e)}")
                # 에러 발생 시에도 현재까지의 데이터 저장
                self.save_all_data()
                continue

        # 모든 처리가 끝난 후 최종 저장
        self.save_all_data()
