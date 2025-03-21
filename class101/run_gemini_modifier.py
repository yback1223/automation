import os
import sys

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from class101.ai.modify_program_details_with_gemini import GeminiProgramDescriptionModifier

def main():
    # RESOURCE_DIR을 사용하여 실행
    modifier = GeminiProgramDescriptionModifier()
    modifier.process_programs(start_index=0)

if __name__ == "__main__":
    main() 