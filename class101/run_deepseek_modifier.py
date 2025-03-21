import os
import sys

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.modify_program_details_with_deepseek import DeepSeekProgramDescriptionModifier

def main():
    modifier = DeepSeekProgramDescriptionModifier()
    modifier.process_programs(start_index=192)

if __name__ == "__main__":
    main() 