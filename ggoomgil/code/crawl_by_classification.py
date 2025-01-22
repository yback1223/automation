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


class MultiDepthCrawler:
    def __init__(self, driver):
        self.driver = driver
        self.result = []
        self.tbody_ids = ["tbody1", "tbody2", "tbody3", "tbody4"]

    def collect_text_and_click(self):
        result = []
        collected = {"depth_1": "", "depth_2": "", "depth_3": "", "depth_4": ""}

        # 클릭하여 첫 번째 리스트 표시
        classification_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[onclick*='popUtil.jobTypeSearchPop']"))
        )
        classification_button.click()

        time.sleep(WORK_TERM_SLEEP)
        depth = 0
        stack = [(depth, -1)]

        while stack:
            depth, last_index = stack.pop()

            if depth == len(self.tbody_ids):
                result.append(collected.copy())
                continue

            tbody_id = self.tbody_ids[depth]
            tbody_element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, tbody_id))
            )
            buttons = tbody_element.find_elements(By.TAG_NAME, "button")

            for i in range(last_index + 1, len(buttons)):
                button = buttons[i]
                button_text = button.text.strip()

                # Update the collected dictionary
                collected[f"depth_{depth + 1}"] = button_text

                # Click the button
                button.click()
                time.sleep(1)  # Wait for the next list to load

                # Push the current state and move deeper
                stack.append((depth, i))
                stack.append((depth + 1, -1))

                break

        return result
    
    
    def choose_classification(self, classification):
        try:
            # 첫 번째 버튼 클릭하여 분류 시작
            classification_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[onclick*='popUtil.jobTypeSearchPop']"))
            )
            classification_button.click()
            time.sleep(WORK_TERM_SLEEP)

            depths = ["depth_1", "depth_2", "depth_3", "depth_4"]

            for depth, depth_value in enumerate(depths):
                value = classification.get(depth_value)
                if not value:
                    break

                tbody_id = self.tbody_ids[depth]

                tbody_element = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.ID, tbody_id))
                )

                buttons = tbody_element.find_elements(By.TAG_NAME, "button")
                found = False
                for button in buttons:
                    button_text = button.text.strip()
                    if button_text == value:
                        button.click()
                        time.sleep(WORK_TERM_SLEEP)  # 다음 리스트가 로드될 시간 대기
                        found = True
                        break

                if not found:
                    raise ValueError(f"Value '{value}' not found in depth {depth + 1}")
            
            time.sleep(WORK_TERM_SLEEP)
            close_select_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.cs-btn.cs-btn-x.cs-btn-blue[id='choiceBtn']"))
            )
            close_select_button.click()
            time.sleep(WORK_TERM_SLEEP)
            search_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.cs-btn.cs-btn-blue.btn-search[onclick*='fn_search()']"))
            )
            search_button.click()

            print("Classification successfully selected.")

        except Exception as e:
            print(f"Error selecting classification: {e}")





class GgoomgilCrawler:

    def __init__(self):
        # 기존 JSON 불러오기
        self.programs = self.load_existing_data("crawled_data.json")
        
        self.driver = Driver().set_chrome()
        self.actions = ActionChains(self.driver)
        self.url = "https://www.ggoomgil.go.kr/front/mypage/schlProgramList.do"
        self.current_page = 1
        self.multi_list_crawler = MultiDepthCrawler(self.driver)
        

    def load_existing_data(self, file_name):
        """
        기존에 저장된 JSON 파일을 로드하여 self.programs에 넣어주는 함수.
        파일이 없거나, 파싱 에러가 나면 빈 리스트를 반환.
        """
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
            time.sleep(5)
            self.classifications = self.multi_list_crawler.collect_text_and_click()
            self.save_to_json("classifications.json", self.classifications)

            for one_classification in self.classifications:
                self.driver.get(self.url)
                time.sleep(5)
                self.multi_list_crawler.choose_classification(one_classification)

                self.choose_list_size()

                while True:
                    print(f"Starting page {self.current_page}")
                    
                    program_rows = self.get_rows_from_list()
                    print(f'Found {len(program_rows)} rows on page {self.current_page}.')
                    if not program_rows:
                        print(f"No rows found on page {self.current_page}.")
                        break

                    for program_row in program_rows:
                        try:
                            program_name, corp_type, apply_date, program_rough_location = self.extract_data_from_rows(program_row)
                            
                            existing_program = next((program for program in self.programs if program.get("program_name") == program_name), None)
                            if existing_program:
                                print(f"Updating existing program: {program_name}")
                                existing_program.update({
                                    "depth_1": one_classification.get("depth_1", ""),
                                    "depth_2": one_classification.get("depth_2", ""),
                                    "depth_3": one_classification.get("depth_3", ""),
                                    "depth_4": one_classification.get("depth_4", "")
                                })
                                continue
                            
                            self.driver.execute_script("window.scrollTo(0, 0);")
                            time.sleep(WORK_TERM_SLEEP)


                        except Exception as e:
                            print(f"[경고] 프로그램 하나의 정보를 가져오는 중 오류가 발생했습니다: {e}")

                        finally:
                            time.sleep(WORK_TERM_SLEEP)

                    print(f"Finished page {self.current_page}")

                    if not self.navigate_to_next_page():
                        print("Reached the last page. Exiting loop.")
                        break

                time.sleep(WORK_TERM_SLEEP)
                self.save_to_json("crawled_data_with_classifications.json", self.programs)

        except Exception as e:
            print(f"Error during crawling: {e}")
            self.save_to_json("crawled_data_with_classifications.json", self.programs)
        finally:
            self.driver.quit()
            

    def save_to_json(self, file_name, data):
        try:
            with open(file_name, "w", encoding="utf-8") as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)
            print(f"Data successfully saved to {file_name}")
        except Exception as e:
            print(f"Error saving data to JSON: {e}")

    def navigate_to_next_page(self):
        try:
            next_page = self.current_page + 1

            next_page_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, f"li.paginationjs-page[data-num='{next_page}']"))
            )

            next_page_button.click()
            time.sleep(5)
            print(f"Navigated to page {next_page}")
            self.current_page = next_page
            return True

        except Exception as e:
            print(f"Error navigating to next page: {e}")
            return False

    def choose_list_size(self):
        try:
            select_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "pageSize"))
            )
            select = Select(select_element)
            select.select_by_visible_text("100개씩 보기")
            time.sleep(5)
        except Exception as e:
            print(f"오류 발생: {e}")

    def get_rows_from_list(self):
        try:
            tbody_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'tbody[id="listTbody"]'))
            )
            rows = tbody_element.find_elements(By.TAG_NAME, "tr")
            return rows
        except Exception as e:
            print(f"Error fetching rows: {e}")
            return []

    def extract_data_from_rows(self, program_row):
        try:
            corp_type = ""
            apply_date = ""
            program_rough_location = ""

            try:
                title_element = program_row.find_element(By.CLASS_NAME, "data-list-title")
                program_name = title_element.text.strip()
            except:
                program_name = ""

            try:
                hidden_elements = program_row.find_elements(By.CLASS_NAME, "data-list-m-hidden")
                if len(hidden_elements) >= 3:
                    apply_date = hidden_elements[2].text
                    corp_type = hidden_elements[0].text.strip().split("\n")[1]
            except:
                pass

            try:
                location_element = program_row.find_element(By.CSS_SELECTOR, "td:nth-child(5)")
                program_rough_location = location_element.text.strip()
            except:
                pass

            return program_name, corp_type, apply_date, program_rough_location

        except Exception as e:
            print(f"Error processing row: {e}")
            return "", "", "", ""

if __name__ == "__main__":
    crawler = GgoomgilCrawler()
    crawler.run()
