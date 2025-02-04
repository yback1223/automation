from driver import Driver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
import clipboard, time
import pandas as pd
import math, random, json, re

COMCON = Keys.CONTROL
WORK_TERM_SLEEP = 1

class SeoulEduOfficeCrawler:
    def __init__(self):
        self.programs = self.load_existing_data("crawled_data_from_seoul_edu.json")
        self.driver = Driver().set_chrome()
        self.actions = ActionChains(self.driver)
        self.category_url = "https://seoulhsc.sen.go.kr/fus/MI000000000000000066/subjectGuide/seriesInfoContent.do?"

    def load_existing_data(self, file_name):
        try:
            with open(file_name, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"기존 데이터 {len(data)}개 로드 완료.")
            return data
        except (FileNotFoundError, json.JSONDecodeError):
            print("기존 JSON 파일이 없거나 파싱 에러가 발생했습니다. 새로 크롤링합니다.")
            return []
        
    def save_json(self, file_name, data) -> None:
        try:
            with open(file_name, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"데이터가 {file_name}에 성공적으로 저장되었습니다.")
        except Exception as e:
            print(f"JSON 파일 저장 중 오류 발생: {e}")


    def run(self):
        try:
            result = []

            for series_seq_num in range(26, 42):
                url = self.category_url + f"series_seq={series_seq_num}&subject_seq="
                self.driver.get(url)

                line_name, normal_subjects, career_subjects = self.get_line_subjects()
                line_related_majors = self.get_line_related_majors()
                line_mentor_mention = self.get_line_mentor_mention()

                li_elements = self.driver.find_elements(By.CSS_SELECTOR, "ul.category li")

                major_numbers = []

                for li in li_elements:
                    onclick_attr = li.get_attribute("onclick")
                    if onclick_attr:
                        match = re.search(r"fncDetail\('\d+','(\d+)'\)", onclick_attr)
                        if match:
                            major_numbers.append(match.group(1))

                for major_number in major_numbers:
                    full_url = url + major_number
                    self.driver.get(full_url)
                    time.sleep(WORK_TERM_SLEEP)
                    major_info = self.get_major_info()
                    result.append({
                        "line_name": line_name,
                        "line_related_normal_subjects": normal_subjects,
                        "line_related_career_subjects": career_subjects,
                        "line_related_majors": line_related_majors,
                        "line_mentor_mention": line_mentor_mention,
                        **major_info
                    })

                    self.save_json("crawled_data_from_seoul_edu.json", result)

        except Exception as e:
            print(f"Error during crawling: {e}")
        finally:
            self.driver.quit()
            self.save_json("crawled_data_from_seoul_edu.json", result)

    

    def get_line_subjects(self):
        try:
            line_name = self.driver.find_element(By.CSS_SELECTOR, "div.pd-b-60 > h3.sub-title3").text.strip().replace(" 정보", "")
            subject_tables = self.driver.find_elements(By.CSS_SELECTOR, "table.table-style01.mg-b-40 td.textL")
            normal_subjects = subject_tables[0].text.strip().replace(" 등", "").split(", ")
            career_subjects = subject_tables[1].text.strip().replace(" 등", "").split(", ")
            return line_name, normal_subjects, career_subjects
        except Exception as e:
            print(f"Error while extracting line subjects: {e}")

    def get_line_related_majors(self):
        try:
            line_related_majors = self.driver.find_element(By.CSS_SELECTOR, "div.pd-b-60 > div.color-box.pd-b-40 > div.box-2 > div.txt > p").text.strip().split(", ")
            return line_related_majors
        except Exception as e:
            print(f"Error while extracting line related majors: {e}")

    def get_line_mentor_mention(self):
        try:
            mentor_mention = self.driver.find_element(By.CSS_SELECTOR, "div.pd-b-60 > div.color-box > div.box-3 > div.txt > p").text.strip()
            return mentor_mention
        except Exception as e:
            print(f"Error while extracting line mentor mention: {e}")

    def get_major_info(self):
        try:
            major_name_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.pd-b-100 > div.major-info.on > h3.sub-title3"))
            )
            major_name = major_name_element.text.strip().replace(" 학과 정보", "")

            major_table_td_elements = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'major-info')]//table//td[contains(@class, 'textL')]"))
            )


            print(f'len(major_table_td_elements): {len(major_table_td_elements)}')

            major_desc = major_table_td_elements[0].text.strip()
            major_student_type = major_table_td_elements[1].text.strip()
            major_normal_subjects = major_table_td_elements[2].text.strip().replace(" 등", "").split(", ")
            major_career_subjects = major_table_td_elements[3].text.strip().replace(" 등", "").split(", ")
            major_university_in_seoul = major_table_td_elements[4].text.strip().replace(" 등", "").split(", ")
            major_university_near_seoul = major_table_td_elements[5].text.strip().replace(" 등", "").split(", ")
            major_university_in_country = major_table_td_elements[6].text.strip().replace(" 등", "").split(", ")
            major_related_majors = self.driver.find_element(By.XPATH, "//div[contains(@class, 'color-box pd-b-40')]//div[contains(@class, 'box-2')]//div[contains(@class, 'txt')]//p").text.strip().replace(" 등", "").split(", ")
            major_related_career_element = self.driver.find_element(By.XPATH, "//div[contains(@class, 'color-box')]//div[contains(@class, 'box-1')]//div[contains(@class, 'txt')]//p").text.strip()
            
            if "●" in major_related_career_element:
                major_related_career = major_related_career_element
            else:
                major_related_career = major_related_career_element.strip().replace(" 등", "").split(", ")

            return {
                "major_name": major_name,
                "major_desc": major_desc,
                "major_student_type": major_student_type,
                "major_normal_subjects": major_normal_subjects,
                "major_career_subjects": major_career_subjects,
                "major_university_in_seoul": major_university_in_seoul,
                "major_university_near_seoul": major_university_near_seoul,
                "major_university_in_country": major_university_in_country,
                "major_related_majors": major_related_majors,
                "major_related_career": major_related_career
            }
        except Exception as e:
            print(f"Error while extracting major info: {e}")



if __name__ == "__main__":
    crawler = SeoulEduOfficeCrawler()
    crawler.run()
