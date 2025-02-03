import json
import re

def load_json(file_path):
    """Load JSON data from a file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def save_json(data, file_path):
    """Save JSON data to a file."""
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def match_jobs_with_programs(job_list, crawled_data):
    """Match jobs with programs based on exact text matches."""
    result = []

    for job_entry in job_list:
        job_name = job_entry['job']
        matching_programs = []

        for program in crawled_data:
            # Combine all relevant text fields into a single string
            program_text = " ".join([
                program.get('program_name', ''),
                program.get('program_creator', ''),
                program.get('program_description', ''),
                program.get('program_creator_description', ''),
                program.get('program_curriculum', ''),
                program.get('program_first_category', ''),
                program.get('program_second_category', '')
            ])

            # Check for exact word match using regex with word boundaries
            if re.search(rf'\b{re.escape(job_name)}\b', program_text):
                matching_programs.append(program)

        # Append to the result if there are matching programs
        if matching_programs:
            result.append({
                "job": job_name,
                "programs": matching_programs
            })

    return result

if __name__ == "__main__":
    # Load job list and crawled data
    job_list = load_json('job_list.json')
    crawled_data = load_json('crawled_data.json')

    # Match jobs with programs
    matched_data = match_jobs_with_programs(job_list, crawled_data)

    # Save the result to a new JSON file
    save_json(matched_data, 'matched_jobs_programs.json')

    print("Matching completed. Results saved to 'matched_jobs_programs.json'.")