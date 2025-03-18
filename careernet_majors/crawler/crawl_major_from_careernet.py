from driver import Driver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.remote.webelement import WebElement
from bs4 import BeautifulSoup
from typing import Any, Union

import re, os
import clipboard, time
import pandas as pd
import math, random, json


WORK_TERM_SLEEP = 1
LIST_FILE = "crawled_program_list.json"
CRAWLED_FILE = "crawled_program_details_tmp.json"

class CareernetMajorCrawler:
    def __init__(self):
        self.driver = Driver().set_chrome()
        self.actions = ActionChains(self.driver)
        self.current_page = 1
        self.driver.get("https://www.career.go.kr/cnet/front/base/major/FunivMajorList.do")

    def load_not_crawled_contents(self, crawled_file: str, program_list_file: str, category: str) -> list[dict[str, str]]:
        try:
            not_crawled_contents: list[dict[str, str]] = []

            with open(program_list_file, "r", encoding="utf-8") as list_file:
                program_list: list[dict[str, Union[str, list[dict[str, str]]]]] = json.load(list_file)
                contents: list[dict[str, str]] = [program.get('content_links') for program in program_list if program.get('category_name') == category][0]
                only_content_links = [content.get('link') for content in contents]

                with open(crawled_file, "r", encoding="utf-8") as crawled_file:
                    crawled_data = json.load(crawled_file)
                    crawled_links = [one_crawled_data.get('content_link') for one_crawled_data in crawled_data if one_crawled_data.get('content_link') in only_content_links]
                    not_crawled_links = [link for link in only_content_links if link not in crawled_links]

                    not_crawled_contents = [content for content in contents if content.get('link') in not_crawled_links]
            return not_crawled_contents
        except (FileNotFoundError, json.JSONDecodeError):
            print("기존 JSON 파일이 없거나 파싱 에러가 발생했습니다. 새로 크롤링합니다.")
            return contents


    def set_list_options(self):
        try:
            select_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "tagUl1"))
            )
            select = Select(select_element)
            select.select_by_value("30")

            list_view = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.icon_list"))
            )
            list_view.click()

            apply_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.list_apply"))
            )
            apply_button.click()

            time.sleep(WORK_TERM_SLEEP)

        except Exception as e:
            print(f"Error setting list options: {e}")


    def get_links_in_one_page(self):
        try:
            tbody = self.driver.find_element(By.TAG_NAME, "tbody")
            trs = tbody.find_elements(By.TAG_NAME, "tr")

            links: list[str] = []
            for tr in trs:
                a_tag = tr.find_element(By.TAG_NAME, "a")
                link = a_tag.get_attribute("href")
                links.append(link)

            return links
        except Exception as e:
            print(f"Error getting links in one page: {e}")
            return []

    def can_move_to_next_page(self) -> bool:
        try:
            current_page_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@id='view2']//strong"))
            )
            print(f'current_page_element: {current_page_element.text}')
            current_page_number: int = int(current_page_element.text)
            next_page_number: int = current_page_number + 1

            next_page_exists: bool = len(self.driver.find_elements(By.XPATH, f"//a[contains(@href, '?pageIndex={next_page_number}')]")) > 0
            next_button_exists: bool = len(self.driver.find_elements(By.XPATH, "//img[@alt='다음']")) > 0

            print(f'next_page_exists: {next_page_exists}, next_button_exists: {next_button_exists}')
            return next_page_exists or next_button_exists

        except Exception as e:
            print(f"Error checking next page availability: {e}")
            return False

    def move_to_next_page(self) -> None:
        try:
            current_page_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@id='view2']//strong"))
            )
            current_page_number: int = int(current_page_element.text)
            next_page_number: int = current_page_number + 1

            try:
                next_page_link = self.driver.find_element(By.XPATH, f"//div[@id='view2']//a[contains(@href, '?pageIndex={next_page_number}')]")
                next_page_link.click()
                time.sleep(WORK_TERM_SLEEP)
            except:
                next_button_link = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//img[@alt='다음']"))
                )
                next_button_link.click()
                time.sleep(WORK_TERM_SLEEP)
        except Exception as e:
            print(f"Error moving to next page: {e}")

    def extract_curriculum(self, major_detail_element: WebElement, major_name_for_error: str):
        try:
            # Use relative XPath to search within major_detail_element
            curriculum_elements = major_detail_element.find_elements(By.XPATH, ".//ul[@class='word_ul detail']")
            curriculum_data: list[dict[str, str]] = []

            for curriculum_element in curriculum_elements:
                li_elements: list[WebElement] = []

                try:
                    li_elements = curriculum_element.find_elements(By.TAG_NAME, 'li')
                except:
                    pass

                one_curriculum_data: dict[str, str] = {}

                for li_element in li_elements:
                    try:
                        # Skip source citation
                        if 'source' in li_element.get_attribute('class'):
                            continue
                            
                        strong_element = li_element.find_element(By.TAG_NAME, 'strong')
                        category = strong_element.text
                        # Get text content after removing the category
                        content = li_element.text[len(category):].strip()
                        one_curriculum_data[category] = content
                    except Exception as inner_e:
                        print(f"Error processing curriculum item: {inner_e}")
                        continue

                curriculum_data.append(one_curriculum_data)

            return curriculum_data if curriculum_data else None

        except Exception as e:
            print(f"Major: {major_name_for_error}, Error extracting curriculum: {e}")
            return None


    def crawl_major_line_page(self, link: str):
        try:
            self.driver.get(link)
            time.sleep(WORK_TERM_SLEEP)

            major_name_element = self.driver.find_element(By.XPATH, "//div[@class='word_tit']/h2")
            major_name = major_name_element.text

            major_info_element = self.driver.find_element(By.XPATH, "//div[@class='job_dic_info']")
            
            major_location_element = major_info_element.find_element(By.XPATH, "//p[@class='job_location']")
            major_location = major_location_element.text

            major_employment_rate_element = major_info_element.find_element(By.XPATH, ".//li[@class='class1']/span/strong")
            major_employment_rate = major_employment_rate_element.text

            major_pay_element = major_info_element.find_element(By.XPATH, ".//li[@class='class2']/span")
            major_pay = major_pay_element.text

            major_detail_element = major_info_element.find_element(By.XPATH, "//div[@class='ui-tabs-panel ui-widget-content ui-corner-bottom']")

            major_detail_elements = major_detail_element.find_elements(By.XPATH, "//ul[@class='word_ul']/li")
            major_details = [element.text for element in major_detail_elements]

            major_outline = major_details[0] if len(major_details) > 0 else "N/A"
            major_characteristics = major_details[1] if len(major_details) > 1 else "N/A"
            major_interest = major_details[2] if len(major_details) > 2 else "N/A"
            major_seek = major_details[3] if len(major_details) > 3 else "N/A"
            major_qualification = major_details[4] if len(major_details) > 4 else "N/A"
            major_related_jobs = major_details[5] if len(major_details) > 5 else "N/A"
            major_related_majors = major_details[6] if len(major_details) > 6 else "N/A"

            major_detail_lists = self.extract_curriculum(major_detail_element, major_name)
            major_related_subjects = major_detail_lists[0] if len(major_detail_lists) > 0 else "N/A"
            major_main_subjects = major_detail_lists[1] if len(major_detail_lists) > 1 else "N/A"
            major_related_works = major_detail_lists[2] if len(major_detail_lists) > 2 else "N/A"

            major_videos: list[dict[str, str]] = []
            try:
                major_related_video_elements = major_info_element.find_elements(By.XPATH, "//ul[@class='video_ul']/li")
                
                for major_related_video_element in major_related_video_elements:
                    video_element = major_related_video_element.find_element(By.XPATH, ".//a")
                    video_link = video_element.get_attribute("href")

                    video_thumbnail_element = major_related_video_element.find_element(By.XPATH, ".//img") 
                    video_thumbnail = video_thumbnail_element.get_attribute("src")

                    video_title_element = major_related_video_element.find_element(By.XPATH, ".//p")
                    video_title = video_title_element.text

                    major_videos.append({
                        "video_link": video_link,
                        "video_thumbnail": video_thumbnail,
                        "video_title": video_title
                    })
            except:
                pass
            
            major_consultings: list[dict[str, str]] = []
            try:
                major_consulting_element = major_info_element.find_element(By.XPATH, "//table[@class='table_job_st1 tab1-tbl']")
                major_consulting_rows = major_consulting_element.find_elements(By.XPATH, ".//tbody/tr")
                
                for row in major_consulting_rows:
                    title_element = row.find_element(By.XPATH, ".//td[1]/a")
                    title = title_element.text
                    link = title_element.get_attribute("href")
                    
                    writer_type = row.find_element(By.XPATH, ".//td[2]").text
                    date = row.find_element(By.XPATH, ".//td[3]").text
                    
                    major_consultings.append({
                        "title": title,
                        "link": link, 
                        "writer_type": writer_type,
                        "date": date
                    })
            except:
                pass

            return {
                "major_name": major_name,
                "major_location": major_location.split(">")[1].strip(),
                "major_employment_rate": major_employment_rate,
                "major_pay": major_pay.split(">")[1].strip(),
                "major_outline": major_outline,
                "major_characteristics": major_characteristics,
                "major_interest": major_interest,
                "major_seek": major_seek,
                "major_qualification": major_qualification,
                "major_related_jobs": major_related_jobs,
                "major_related_majors": major_related_majors,
                "major_related_subjects": major_related_subjects,
                "major_main_subjects": major_main_subjects,
                "major_related_works": major_related_works,
                "major_videos": major_videos,
                "major_consultings": major_consultings
            }

        except Exception as e:
            print(f"Error crawling one major page {major_name}: {e}")

    def crawl_major_university_page(self, major_name_for_error: str):
        try:
            self.move_to_another_tab("#tab2", major_name_for_error)
            
            time.sleep(WORK_TERM_SLEEP)
            university_elements = self.driver.find_elements(By.XPATH, "//table[@class='table_job_st1']//tbody/tr")
            universities = []
            
            for university_element in university_elements:
                max_retries = 3
                retry_count = 0
                
                while retry_count < max_retries:
                    try:
                        region = university_element.find_element(By.XPATH, "./td[1]").text
                        
                        university_link_element = university_element.find_element(By.XPATH, "./td[2]/a")
                        university_name = university_link_element.text
                        university_link = university_link_element.get_attribute("href")
                        
                        major_name = university_element.find_element(By.XPATH, "./td[3]").text
                        
                        universities.append({
                            "region": region,
                            "university_name": university_name,
                            "university_link": university_link,
                            "major_name": major_name
                        })
                        break
                        
                    except Exception as e:
                        retry_count += 1
                        if retry_count == max_retries:
                            print(f"Failed to process university element after {max_retries} attempts: {e}")
                
            return universities
        except Exception as e:
            print(f"Major: {major_name_for_error}, Error crawling university page: {e}")
            return []
        
    def extract_interview_data(self, element, major_name_for_error: str):
        try:
            interview_section_element = element.find_element(By.XPATH, ".//div[@class='intvw_talk aqua']")
            questions = interview_section_element.find_elements(By.XPATH, ".//div[@class='question']")
            answers = interview_section_element.find_elements(By.XPATH, ".//div[@class='answer']")

            interview_data = []

            for i in range(min(len(questions), len(answers))):  # 질문과 답변의 개수가 다를 수 있음
                question_element = questions[i]
                answer_element = answers[i]

                # 질문 내용 추출
                question_text_element = question_element.find_element(By.XPATH, ".//div[@class='bubble']")
                question_text = question_text_element.text

                # 답변 내용 추출
                answer_text_element = answer_element.find_element(By.XPATH, ".//div[@class='bubble']")
                answer_text = answer_text_element.text

                interview_data.append({
                    "question": question_text,
                    "answer": answer_text
                })

            return interview_data

        except Exception as e:
            print(f"Major: {major_name_for_error}, Error extracting interview data: {e}")
            return None

    def crawl_one_major_interview_page(self, major_name_for_error: str):
        try:
            self.move_to_another_tab("#tab4", major_name_for_error)
            time.sleep(WORK_TERM_SLEEP)

            interview_headbx = self.driver.find_element(By.XPATH, "//div[@class='intvw class interview-headbx']")

            interview_section_element = interview_headbx.find_element(By.XPATH, ".//div[@class='intvw_head']")
            
            img_url = interview_section_element.find_element(By.XPATH, ".//div[@class='intvw_img']/img").get_attribute("src")
            major_name = interview_section_element.find_element(By.XPATH, ".//h2").text
            interviewer_university = interview_section_element.find_element(By.XPATH, ".//h3").text
            name = interview_section_element.find_element(By.XPATH, ".//p").text.split('&nbsp;')[0]

            interview_data = self.extract_interview_data(interview_headbx, major_name_for_error=major_name_for_error)

            major_data = {
                "img_url": img_url,
                "major_name": major_name,
                "name": name,
                "interviewer_university": interviewer_university,
                "interview_data": interview_data
            }

            return major_data

        except Exception as e:
            print(f"Major: {major_name_for_error}, Error crawling one major page: {e}")
            return None

    def move_to_another_tab(self, tab_element: str, major_name_for_error: str):
        try:
            tab_element = self.driver.find_element(By.XPATH, f"//li[@class='ui-state-default ui-corner-top']/a[@href='{tab_element}']")
            tab_element.click()
            time.sleep(WORK_TERM_SLEEP)
        except Exception as e:
            print(f"Major: {major_name_for_error}, Error moving to another tab: {e}")

    def run(self):
        try:
            self.set_list_options()
            major_page_links: list[str] = []

            while True:
                current_page_links: list[str] = self.get_links_in_one_page()
                major_page_links.extend(current_page_links)
                
                if not self.can_move_to_next_page():
                    break
                
                self.move_to_next_page()
            
            for link in major_page_links:
                major_data = self.crawl_major_line_page(link)
                university_data = self.crawl_major_university_page(major_name_for_error=major_data["major_name"])
                major_data["university_data"] = university_data

                interview_data = self.crawl_one_major_interview_page(major_name_for_error=major_data["major_name"])
                major_data["interview_data"] = interview_data

                self.save_to_json(CRAWLED_FILE, major_data)

                

        except Exception as e:
            print(f"Error running: {e}")
            return []



    def save_to_json(self, crawled_file: str, crawled_data: dict[str, str]) -> None:
        try:
            existing_data = []

            if os.path.exists(crawled_file) and os.path.getsize(crawled_file) > 0:
                with open(crawled_file, "r", encoding="utf-8") as json_file:
                    existing_data = json.load(json_file)

            existing_data.append(crawled_data)

            with open(crawled_file, "w", encoding="utf-8") as json_file:
                json.dump(existing_data, json_file, ensure_ascii=False, indent=4)

            print(f"Data successfully saved to {crawled_file}")
        except Exception as e:
            print(f"Error saving data to JSON: {e}")


if __name__ == "__main__":
    crawler = CareernetMajorCrawler()
    crawler.run()
