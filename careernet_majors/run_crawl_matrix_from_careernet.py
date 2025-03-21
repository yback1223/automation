import os
import sys

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from careernet_majors.major_job_matrix_crawler.crawl_matrix_from_careernet import CareernetMajorJobMatrixCrawler

def main():
    crawler = CareernetMajorJobMatrixCrawler()
    crawler.run()

if __name__ == "__main__":
    main() 