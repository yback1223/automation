import json

input_file = "programs_with_classifications.json"
job_hire_class_file = "final_merged_data.json"
output_file = "updated_programs_with_classifications.json"

def load_json(file_path: str):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: File not found")
        return []
    except json.JSONDecodeError:
        print("Error: Invalid JSON format")
        return []

def save_json(data, file_path: str):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f'Updated JSON saved to {file_path}')

def edit_classes(programs, hire_codes):
    for program in programs:
        if 'classes' in program:
            for one_class in program['classes']:
                for hire_code in hire_codes:
                    if one_class['depth_2'] in hire_code['hire_code_1'] and \
                        one_class['depth_3'] in hire_code['hire_code_2'] and \
                        one_class['depth_4'] in hire_code['hire_code_3']:
                        one_class['depth_2'] = hire_code['hire_code_1'][:4] + one_class['depth_2']
                        one_class['depth_3'] = hire_code['hire_code_2'][:5] + one_class['depth_3']
                        one_class['depth_4'] = hire_code['hire_code_3'][:6] + one_class['depth_4']
                        break
    return programs


if __name__ == "__main__":
    job_data = load_json(job_hire_class_file)

    hire_codes = []

    for job in job_data:
        hire_codes.append({
            'hire_code_1': job['고용직업분류_1'],
            'hire_code_2': job['고용직업분류_2'],
            'hire_code_3': job['고용직업분류_3']
        })

    programs = load_json(input_file)
    print(f'Loaded {len(programs)} programs')
    print(f'Loaded {len(hire_codes)} hire codes')
    updated_programs = edit_classes(programs, hire_codes)

    save_json(updated_programs, output_file)