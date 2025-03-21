import json

class ResourceModifier:
    def __init__(self, resource_json_file_path: str) -> None:
        self.resource_json_file_path = resource_json_file_path

    def delete_md_format_from_resource(self) -> None:
        with open(self.resource_json_file_path, "r", encoding="utf-8") as f:
            resource_json = json.load(f)

        print(len(resource_json))

        for resource in resource_json:
            resource["program_description_by_gemini"] = resource["program_description_by_gemini"].replace("##", "").replace("**", "").strip()
        
        with open(self.resource_json_file_path, "w", encoding="utf-8") as f:
            json.dump(resource_json, f, ensure_ascii=False, indent=4)
        
        print(f"Successfully deleted MD format from {self.resource_json_file_path}")

if __name__ == "__main__":
    resource_modifier = ResourceModifier("class101_program_details_gemini.json")
    resource_modifier.delete_md_format_from_resource()


