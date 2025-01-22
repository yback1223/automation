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

class Class101Crawler:
    def __init__(self):
        self.programs = self.load_existing_data("crawled_data.json")
        self.driver = Driver().set_chrome()
        self.actions = ActionChains(self.driver)
        self.url = "https://class101.net/ko"
        self.current_page = 1


    def load_existing_data(self, file_name):
        try:
            with open(file_name, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"기존 데이터 {len(data)}개 로드 완료.")
            return data
        except (FileNotFoundError, json.JSONDecodeError):
            print("기존 JSON 파일이 없거나 파싱 에러가 발생했습니다. 새로 크롤링합니다.")
            return []


    def run(self):
        try:
            self.driver.get(self.url)
            time.sleep(WORK_TERM_SLEEP)

            category_links = self.collect_links()
            for link in category_links:
                self.driver.get(link)
                time.sleep(WORK_TERM_SLEEP)
                # content_links = self.scroll_and_collect_links()

                for content_link in ['https://class101.net/ko/products/615d1035be1e59000dd23aa3']:
                    self.driver.get(content_link)
                    time.sleep(WORK_TERM_SLEEP)

                    program_name: str = None
                    program_creator: str = None
                    program_link: str = None
                    program_difficulty: str = None
                    program_chapter_count: int = None
                    program_total_time: str = None
                    program_subtitles: str = None
                    program_audio_languages: str = None
                    program_bookmark_count: int = None
                    program_description: str = None
                    program_kit: str = None
                    program_start_date: str = None
                    program_video_count: str = None
                    program_curriculum: dict[str, list[str]] = None
                    program_creator_description: str = None
                    program_first_category: str = None
                    program_second_category: str = None

                    program_name, program_bookmark_count, program_link = self.find_and_click_share_button()
                    program_creator_detail = self.extract_creator_section_data()
                    program_creator = program_creator_detail['creator_name']
                    program_creator_description = ' '.join(program_creator_detail['description'])
                    print(f'program_name: {program_name}')
                    print(f'program_bookmark_count: {program_bookmark_count}')
                    print(f'program_link: {program_link}')
                    print(f'program_creator: {program_creator}')
                    print(f'program_creator_description: {program_creator_description}')

                    program_info, program_curriculum = self.extract_program_info_and_curriculum()
                    program_start_date = program_info[0]
                    program_info_detail = [info.strip() for info in program_info[1].split("·")]
                    program_difficulty = program_info_detail[0]
                    program_video_count = program_info_detail[1]
                    program_total_time = program_info[2]
                    program_audio_languages = program_info[3]
                    program_subtitles = program_info[4]
                    print(f'program_start_date: {program_start_date}')
                    print(f'program_difficulty: {program_difficulty}')
                    print(f'program_video_count: {program_video_count}')
                    print(f'program_total_time: {program_total_time}')
                    print(f'program_audio_languages: {program_audio_languages}')
                    print(f'program_subtitles: {program_subtitles}')
                    print(f'program_curriculum: {program_curriculum}')

                    program_first_category, program_second_category = self.extract_text_from_home_section()
                    print(f'program_first_category: {program_first_category}')
                    print(f'program_second_category: {program_second_category}')

                    program_description = self.extract_program_description()
                    print(f'program_description: {program_description}')

                    program_kit = self.extract_program_kit()
                    print(f'program_kit: {program_kit}')

                    


                    # self.programs.append({
                    #     "program_name": program_name,
                    #     "program_creator": program_creator,
                    #     "program_link": program_link,
                    #     "program_difficulty": program_difficulty,
                    #     "program_chapter_count": program_chapter_count,
                    #     "program_total_time": program_total_time,
                    #     "program_subtitles": program_subtitles,
                    #     "program_audio_languages": program_audio_languages,
                    #     "program_bookmark_count": program_bookmark_count,
                    #     "program_description": program_description,
                    #     "program_preparation": program_preparation,
                    #     "program_start_date": program_start_date,
                    #     "program_video_count": program_video_count,
                    #     "program_curriculum": program_curriculum,
                    #     "program_creator_description": program_creator_description,
                    #     "program_creator_sns_links": program_creator_sns_links,
                    #     "program_first_category": program_first_category,
                    #     "program_second_category": program_second_category,
                    # })

                    self.save_to_json("crawled_data.json")

        except Exception as e:
            print(f"Error during crawling: {e}")
            self.save_to_json("crawled_data.json")
        finally:
            self.driver.quit()

    def save_to_json(self, file_name):
        try:
            with open(file_name, "w", encoding="utf-8") as json_file:
                json.dump(self.programs, json_file, ensure_ascii=False, indent=4)
            print(f"Data successfully saved to {file_name}")
        except Exception as e:
            print(f"Error saving data to JSON: {e}")


    def click_category_button(self):
        try:
            category_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='카테고리']]"))
            )
            self.driver.execute_script("arguments[0].click();", category_button)
            time.sleep(WORK_TERM_SLEEP)
            print("Successfully clicked the category button.")
        except Exception as e:
            print(f"Error clicking category button: {e}")


    def collect_links(self):
        try:
            self.click_category_button()

            link_elements = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[data-testid='pressable']"))
            )

            links = [element.get_attribute("href") for element in link_elements]
            category_links = [link for link in links if "categories" in link]
            
            return category_links
        except Exception as e:
            print(f"Error collecting links: {e}")
            return []


    def scroll_and_collect_links(self):
        collected_links = set()
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while True:
            try:
                list_elements = self.driver.find_elements(By.CSS_SELECTOR, "li a[href]")
                for element in list_elements:
                    href = element.get_attribute("href")
                    if href and href not in collected_links:
                        collected_links.add(href)
                        print(f"Collected: {href}")
            except Exception as e:
                print(f"Error while collecting links: {e}")

            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(WORK_TERM_SLEEP)

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("Reached the end of the page.")
                break
            last_height = new_height

        return list(collected_links)

    def extract_title(self):
        try:
            subscription_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[span[text()='구독으로 시작하기']]"))
            )
            print(1)
            parent_section = subscription_button.find_element(By.XPATH, "./ancestor::div[@data-testid='paper']")
            print(2)
            title_element = parent_section.find_element(By.XPATH, ".//h2[@data-testid='title']")
            title_text = title_element.text.strip() if title_element else "N/A"
            print(3)

            return title_text

        except Exception as e:
            print(f"Error while extracting section data")
            return None

            
    def find_and_click_share_button(self):
        try:
            buttons = self.driver.find_elements(By.TAG_NAME, "button")

            for button in buttons:
                try:
                    if "공유" in button.text:
                        # 공유 버튼의 부모 섹션 찾기
                        parent_section = button.find_element(By.XPATH, "./ancestor::div[@data-testid='paper']")
                        
                        # 제목 텍스트 추출
                        title_element = parent_section.find_element(By.XPATH, ".//h2[@data-testid='title']")
                        title_text = title_element.text.strip() if title_element else "N/A"

                        # 숫자 텍스트 추출
                        number_elements = parent_section.find_elements(By.XPATH, ".//span[@data-testid='body']")
                        number_text = number_elements[1].text.strip() if number_elements[1] else "N/A"

                        # 공유 버튼 클릭
                        button.click()
                        print("공유 버튼을 클릭했습니다.")
                        time.sleep(WORK_TERM_SLEEP)

                        # 공유 링크 복사 버튼 찾기
                        buttons = self.driver.find_elements(By.TAG_NAME, "button")
                        for button in buttons:
                            if "공유 링크 복사" in button.text:
                                button.click()
                                print("공유 링크 복사 버튼을 클릭했습니다.")
                                time.sleep(WORK_TERM_SLEEP)
                                break

                        return title_text, number_text, clipboard.paste()

                except Exception as inner_e:
                    print(f"버튼 검사 중 오류 발생: {inner_e}")

            print("공유 버튼을 찾을 수 없습니다.")
        except Exception as e:
            print(f"전체 HTML에서 버튼 검색 중 오류 발생: {e}")



    def extract_creator_section_data(self):
        try:
            # Creator 섹션 찾기
            creator_section = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "creator"))
            )
            
            data = {}

            title_element = creator_section.find_element(By.CSS_SELECTOR, "h2[data-testid='title']")
            data["title"] = title_element.text if title_element else "N/A"

            profile_image_element = creator_section.find_element(By.CSS_SELECTOR, "picture[data-testid='image'] img")
            data["profile_image"] = profile_image_element.get_attribute("src") if profile_image_element else "N/A"

            creator_name_element = creator_section.find_element(By.CSS_SELECTOR, "h2[data-testid='title']")
            data["creator_name"] = creator_name_element.text if creator_name_element else "N/A"

            description_elements = creator_section.find_elements(By.CSS_SELECTOR, "div p")
            data["description"] = [desc.text for desc in description_elements if desc.text]

            return data

        except Exception as e:
            print(f"Error while extracting creator section data: {e}")
            return None


    def extract_program_info_and_curriculum(self):
        try:
            class_info_element = self.driver.find_element(By.XPATH, "//h3[text()='클래스 정보']")

            paper_element = class_info_element.find_element(By.XPATH, "./ancestor::*[@data-testid='paper']")

            all_texts = paper_element.text.split("\n")

            program_info = all_texts[1:6]

            curriculum_lines = [
                line for line in all_texts[6:]
                if "미리보기" not in line and not re.match(r"\d{2}:\d{2}", line)
            ]
            sections = []
            current_section = {"title": None, "lectures": []}

            for line in curriculum_lines:
                if line[0].isdigit() and line[1] == ".":
                    current_section["lectures"].append(line)
                else:
                    if current_section["title"]:
                        sections.append(current_section)
                    current_section = {"title": line, "lectures": []}

            if current_section["title"]:
                sections.append(current_section)

            return program_info, sections

        except Exception as e:
            print(f"Error extracting program info: {e}")
            return None


    def extract_text_from_home_section(self):
        try:
            home_element = self.driver.find_element(By.XPATH, "//p[button[text()='홈']]")
            
            content_area = home_element.find_element(By.XPATH, "./ancestor::div[@data-testid='content-area']")
            
            all_texts = content_area.text.strip().split("\n")

            return all_texts[1], all_texts[2]
        except Exception as e:
            print(f"Error extracting text from home section: {e}")
            return None

    def extract_program_description(self):
        try:
            section = self.driver.find_element(By.ID, "class_description")
            
            elements = section.find_elements(By.XPATH, ".//*")

            result = []
            for element in elements:
                if element.tag_name in ['h3', 'p']:
                    text = element.text.strip()
                    if text:
                        result.append(text)


            return ' '.join(result)

        except Exception as e:
            print(f"Error extracting tags in order: {e}")
            return None

    def extract_program_kit(self):
        try:
            buttons = self.driver.find_elements(By.TAG_NAME, "button")

            for button in buttons:
                if "더보기" in button.text:
                    button.click()
                    print("더보기 버튼을 클릭했습니다.")
                    time.sleep(WORK_TERM_SLEEP)
                    break

            section = self.driver.find_element(By.ID, "kit")
            
            elements = section.find_elements(By.XPATH, ".//*")

            result = []
            for element in elements:
                if element.tag_name in ['h2', 'h3', 'p']:
                    text = element.text.strip()
                    if text:
                        result.append(text)


            return ' '.join(result)

        except Exception as e:
            print(f"Error extracting tags in order: {e}")
            return None


if __name__ == "__main__":
    crawler = Class101Crawler()
    crawler.run()
