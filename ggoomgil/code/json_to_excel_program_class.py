import json
import pandas as pd

def json_to_excel(json_file, excel_file, excel_columns, key_column_mapping):
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            json_data = json.load(file)

        extracted_data = []

        for entry in json_data:
            print(entry.get('class101_categories'))
            class101_categories = entry.get('class101_categories', None)

            category_list: list[str] = []
            for i, category in enumerate(class101_categories):
                first_category = category.get('first_category')
                second_category = category.get('second_category')
                category_list.append(f"{first_category} > {second_category}")
            entry['class101_categories'] = category_list
            row = {}
            for json_key, excel_col in key_column_mapping.items():
                row[excel_col] = entry.get(json_key, None)

            extracted_data.append(row)

        df = pd.DataFrame(extracted_data, columns=excel_columns)

        df.to_excel(excel_file, index=False)
        print(f"Excel file created successfully: {excel_file}")

    except Exception as e:
        print(f"Error while converting JSON to Excel: {e}")

json_file = 'matched.json'
excel_file = 'output.xlsx'

# List of Excel column names
excel_columns = [
    "표준직업분류",
    "class101_카테고리"
]

# Mapping of JSON keys to Excel columns
key_column_mapping = {
    "job_std_class": "표준직업분류",
    "class101_categories": "class101_카테고리"
}

# Convert JSON to Excel
json_to_excel(json_file, excel_file, excel_columns, key_column_mapping)
