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
                content_links = self.scroll_and_collect_links()

                for content_link in content_links:
                    self.driver.get(content_link)
                    time.sleep(WORK_TERM_SLEEP)

                    try:
                        program_name, program_bookmark_count, program_link = self.find_and_click_share_button()
                        
                        if not program_name or not program_link:
                            print("Failed to extract program details. Skipping this program.")
                            continue

                        if any(program.get("program_name") == program_name for program in self.programs):
                            print(f"Program '{program_name}' already exists. Skipping...")
                            continue

                        program_kit = self.extract_kit_content()
                        program_description = self.extract_program_description()

                        if not program_kit and program_description:
                            keyword = "클래스 준비물"
                            if keyword in program_description:
                                split_index = program_description.index(keyword)
                                program_kit = program_description[split_index:].strip()
                                program_description = program_description[:split_index].strip()
                            else:
                                print("Keyword '클래스 준비물' not found in description.")
                                program_kit = "N/A"

                        program_creator_detail = self.extract_creator_section_data()
                        program_creator = program_creator_detail.get('creator_name', "N/A")
                        program_creator_description = ' '.join(program_creator_detail.get('description', []))

                        program_info, program_curriculum = self.extract_program_info_and_curriculum()
                        if not program_info:
                            print("Failed to extract program info. Skipping this program.")
                            continue

                        program_start_date = program_info[0] if len(program_info) > 0 else "N/A"
                        program_info_detail = [info.strip() for info in program_info[1].split("·")] if len(program_info) > 1 else []
                        program_difficulty = program_info_detail[0] if len(program_info_detail) > 0 else "N/A"
                        program_video_count = program_info_detail[1] if len(program_info_detail) > 1 else "N/A"
                        program_total_time = program_info[2] if len(program_info) > 2 else "N/A"
                        program_audio_languages = program_info[3] if len(program_info) > 3 else "N/A"
                        program_subtitles = program_info[4] if len(program_info) > 4 else "N/A"

                        program_first_category, program_second_category = self.extract_text_from_home_section() or ("N/A", "N/A")

                        self.programs.append({
                            "program_name": program_name,
                            "program_creator": program_creator,
                            "program_link": program_link,
                            "program_difficulty": program_difficulty,
                            "program_total_time": program_total_time,
                            "program_subtitles": program_subtitles,
                            "program_audio_languages": program_audio_languages,
                            "program_bookmark_count": program_bookmark_count,
                            "program_description": program_description,
                            "program_kit": program_kit,
                            "program_start_date": program_start_date,
                            "program_video_count": program_video_count,
                            "program_curriculum": program_curriculum,
                            "program_creator_description": program_creator_description,
                            "program_first_category": program_first_category,
                            "program_second_category": program_second_category,
                        })

                        self.save_to_json("crawled_data.json")

                    except Exception as e:
                        print(f"Error processing content link '{content_link}': {e}")
                        continue

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
            self.click_close_alert_button()
            category_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='카테고리']]"))
            )
            self.driver.execute_script("arguments[0].click();", category_button)
            time.sleep(WORK_TERM_SLEEP)
            self.click_close_alert_button()

            print("Successfully clicked the category button.")
        except Exception as e:
            self.click_close_alert_button()

            print(f"Error clicking category button")


    def collect_links(self):
        try:
            self.click_close_alert_button()

            self.click_category_button()
            self.click_close_alert_button()

            link_elements = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[data-testid='pressable']"))
            )
            self.click_close_alert_button()

            links = [element.get_attribute("href") for element in link_elements]
            category_links = [link for link in links if "categories" in link]
            self.click_close_alert_button()
            
            return category_links
        except Exception as e:
            self.click_close_alert_button()
            return []


    def scroll_and_collect_links(self):
        collected_links = set()
        self.click_close_alert_button()
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while True:
            try:
                list_elements = self.driver.find_elements(By.CSS_SELECTOR, "li a[href]")
                for element in list_elements:
                    self.click_close_alert_button()
                    href = element.get_attribute("href")
                    if href and href not in collected_links:
                        collected_links.add(href)
                        print(f"Collected: {href}")
            except Exception as e:
                self.click_close_alert_button()
                print(f"Error while collecting links")
            self.click_close_alert_button()

            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(WORK_TERM_SLEEP)
            self.click_close_alert_button()

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("Reached the end of the page.")
                break
            last_height = new_height
            self.click_close_alert_button()

        return list(collected_links)


    def extract_title(self):
        try:
            self.click_close_alert_button()
            subscription_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[span[text()='구독으로 시작하기']]"))
            )
            self.click_close_alert_button()

            parent_section = subscription_button.find_element(By.XPATH, "./ancestor::div[@data-testid='paper']")
            self.click_close_alert_button()

            title_element = parent_section.find_element(By.XPATH, ".//h2[@data-testid='title']")
            title_text = title_element.text.strip() if title_element else "N/A"
            self.click_close_alert_button()


            return title_text

        except Exception as e:
            print(f"Error while extracting section data")
            self.click_close_alert_button()
            return None

            
    def find_and_click_share_button(self):
        try:
            buttons = self.driver.find_elements(By.TAG_NAME, "button")

            for button in buttons:
                try:
                    if "공유" in button.text:
                        self.click_close_alert_button()
                        parent_section = button.find_element(By.XPATH, "./ancestor::div[@data-testid='paper']")
                        
                        self.click_close_alert_button()
                        title_element = parent_section.find_element(By.XPATH, ".//h2[@data-testid='title']")
                        title_text = title_element.text.strip() if title_element else "N/A"

                        if any(program.get("program_name") == title_text for program in self.programs):
                            print(f"Program '{title_text}' already exists. Skipping...")
                            return None, None, None

                        self.click_close_alert_button()
                        number_elements = parent_section.find_elements(By.XPATH, ".//span[@data-testid='body']")
                        number_text = number_elements[1].text.strip() if number_elements[1] else "N/A"

                        self.click_close_alert_button()
                        button.click()
                        print("공유 버튼을 클릭했습니다.")
                        time.sleep(WORK_TERM_SLEEP * 2)

                        self.click_close_alert_button()
                        buttons = self.driver.find_elements(By.TAG_NAME, "button")
                        for button in buttons:
                            if "공유 링크 복사" in button.text:
                                self.click_close_alert_button()
                                button.click()
                                print("공유 링크 복사 버튼을 클릭했습니다.")
                                time.sleep(WORK_TERM_SLEEP)
                                break

                        return title_text, number_text, clipboard.paste()

                except Exception as inner_e:
                    print(f"버튼 검사 중 오류 발생")
                    return None

            print("공유 버튼을 찾을 수 없습니다.")
        except Exception as e:
            print(f"전체 HTML에서 버튼 검색 중 오류 발생")


    def extract_creator_section_data(self):
        try:
            self.click_close_alert_button()
            creator_section = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "creator"))
            )
            
            self.click_close_alert_button()
            data = {}

            self.click_close_alert_button()
            title_element = creator_section.find_element(By.CSS_SELECTOR, "h2[data-testid='title']")
            data["title"] = title_element.text if title_element else "N/A"

            self.click_close_alert_button()
            profile_image_element = creator_section.find_element(By.CSS_SELECTOR, "picture[data-testid='image'] img")
            data["profile_image"] = profile_image_element.get_attribute("src") if profile_image_element else "N/A"

            self.click_close_alert_button()
            creator_name_elements = creator_section.find_elements(By.CSS_SELECTOR, "h2[data-testid='title']")
            data["creator_name"] = creator_name_elements[1].text if creator_name_elements[1] else "N/A"

            self.click_close_alert_button()
            description_elements = creator_section.find_elements(By.CSS_SELECTOR, "div p")
            data["description"] = [desc.text for desc in description_elements if desc.text]

            return data

        except Exception as e:
            print(f"Error while extracting creator section data")
            self.click_close_alert_button()
            return None


    def extract_program_info_and_curriculum(self):
        try:
            self.click_close_alert_button()
            class_info_element = self.driver.find_element(By.XPATH, "//h3[text()='클래스 정보']")

            self.click_close_alert_button()
            paper_element = class_info_element.find_element(By.XPATH, "./ancestor::*[@data-testid='paper']")

            self.click_close_alert_button()
            all_texts = paper_element.text.split("\n")

            self.click_close_alert_button()
            program_info = all_texts[1:6]

            self.click_close_alert_button()
            curriculum_lines = [
                line for line in all_texts[6:]
                if "미리보기" not in line and not re.match(r"\d{2}:\d{2}", line)
            ]
            sections = []
            current_section = {"title": None, "lectures": []}

            self.click_close_alert_button()
            for line in curriculum_lines:
                if line[0].isdigit() and line[1] == ".":
                    current_section["lectures"].append(line)
                else:
                    if current_section["title"]:
                        sections.append(current_section)
                    current_section = {"title": line, "lectures": []}

            self.click_close_alert_button()
            if current_section["title"]:
                sections.append(current_section)

            program_curriculum_text = ""
            for curriculum in sections:
                program_curriculum_text += f"{curriculum.get('title')}\n"
                for lecture in curriculum.get('lectures'):
                    program_curriculum_text += f"{lecture}\n"
                program_curriculum_text += "\n"
                

            return program_info, program_curriculum_text

        except Exception as e:
            print(f"Error extracting program info")
            self.click_close_alert_button()
            return None


    def extract_text_from_home_section(self):
        try:
            self.click_close_alert_button()
            home_element = self.driver.find_element(By.XPATH, "//p[button[text()='홈']]")
            
            self.click_close_alert_button()
            content_area = home_element.find_element(By.XPATH, "./ancestor::div[@data-testid='content-area']")
            
            self.click_close_alert_button()
            all_texts = content_area.text.strip().split("\n")

            return all_texts[1], all_texts[2]
        except Exception as e:
            print(f"Error extracting text from home section")
            self.click_close_alert_button()
            return None
        

    def extract_program_description(self):
        try:
            self.click_close_alert_button()
            section = self.driver.find_element(By.ID, "class_description")
            
            self.click_close_alert_button()
            elements = section.find_elements(By.XPATH, ".//*")
            time.sleep(WORK_TERM_SLEEP)
            result = []
            self.click_close_alert_button()
            for element in elements:
                if element.tag_name in ['h3', 'p', 'h2']:
                    text = element.text.strip()
                    if text:
                        self.click_close_alert_button()
                        result.append(text)

            return ' '.join(result)

        except Exception as e:
            print(f"Error extracting tags in order")
            self.click_close_alert_button()
            return None


    def extract_kit_content(self):
        try:

            self.click_close_alert_button()
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            count = 0
            for button in buttons:
                if "더보기" in button.text:
                    count += 1
                    if count == 2:
                        button.click()
            
            time.sleep(WORK_TERM_SLEEP)

            self.click_close_alert_button()
            section = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "kit"))
            )
            self.click_close_alert_button()

            elements = section.find_elements(By.XPATH, ".//*[self::h2 or self::h3 or self::p]")

            result = []
            self.click_close_alert_button()

            for element in elements:
                text = element.text.strip()
                if text:
                    result.append(text)

            self.click_close_alert_button()

            return ' '.join(result)

        except Exception as e:
            print(f"Error kit:")
            self.click_close_alert_button()
            return None
        

    def click_close_alert_button(self):
        try:
            close_button = self.driver.find_element(By.CSS_SELECTOR, "button.ab-close-button[aria-label='Close Message']")
            close_button.click()
        except:
            pass
            

if __name__ == "__main__":
    crawler = Class101Crawler()
    crawler.run()
