import os
import json
import google.generativeai as genai

gemini_api_key = "AIzaSyBT3p4sqHvx-eHW0HZlbGKle4YxPfoN8E4"


def load_crawled_data(file_path: str) -> list[dict]:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
    

def save_crawled_data_to_particular_program(file_path: str, edited_data: str, index: int) -> None:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        data[index]["program_description_by_gemini"] = edited_data
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_program_description(program: dict) -> str:    
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

def get_data_length(file_path: str) -> int:
    crawled_data = load_crawled_data(file_path=file_path)
    return len(crawled_data)

def get_particular_program(file_path: str, index: int) -> dict:
    crawled_data = load_crawled_data(file_path=file_path)
    return crawled_data[index]

def get_program_description_from_gemini(program_description_prompt_input: str) -> str:
    genai.configure(api_key=gemini_api_key)

    # Create the model
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )

    chat_session = model.start_chat(
        history=[
        ]
    )

    response = chat_session.send_message(program_description_prompt_input)
    return response.text

file_path = "crawled_program_details_tmp.json"

length_of_crawled_data = get_data_length(file_path=file_path)

for i in range(1544, length_of_crawled_data):
    program = get_particular_program(file_path=file_path, index=i)
    program_description_prompt_input = get_program_description(program=program)
    program_description_from_gemini = get_program_description_from_gemini(program_description_prompt_input=program_description_prompt_input)

    save_crawled_data_to_particular_program(file_path=file_path, edited_data=program_description_from_gemini, index=i)
    print(f"Finished {i} - {program['program_name']}")
