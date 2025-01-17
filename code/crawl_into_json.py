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

class GgoomgilCrawler:

    def __init__(self):
        self.driver = Driver().set_chrome()
        self.actions = ActionChains(self.driver)
        self.url = "https://www.ggoomgil.go.kr/front/mypage/schlProgramList.do"
        self.programs = []
        self.current_page = 1

    def run(self):
        try:
            self.driver.get(self.url)
            time.sleep(WORK_TERM_SLEEP)

            self.choose_list_size()

            while True:
                print(f"Starting page {self.current_page}")
                
                program_rows = self.get_rows_from_list()
                print(f'Found {len(program_rows)} rows on page {self.current_page}.')
                if not program_rows:
                    print(f"No rows found on page {self.current_page}.")
                    break

                for program_row in program_rows:

                    program_name, corp_type, apply_date, program_rough_location = self.extract_data_from_rows(program_row)
                    if any(program.get("program_name") == program_name for program in self.programs):
                        print(f"Duplicate program found: {program_name}. Skipping...")
                        continue
                    
                    self.driver.execute_script("window.scrollTo(0, 0);")
                    time.sleep(3)

                    program_row.click()

                    time.sleep(3)

                    corp_name = self.extract_place()
                    program_term = self.extract_program_term()

                    program_info = self.translate_keys(dl_data=self.extract_dl_elements())

                    elementary_details = self.parse_program_details(self.extract_program_info('초등학교'))
                    middle_details = self.parse_program_details(self.extract_program_info('중학교'))
                    high_details = self.parse_program_details(self.extract_program_info('고등학교'))

                    notice = self.extract_notice()

                    how_to_go = self.extract_location_info()

                    appliable_location = self.extract_available_regions()

                    self.programs.append({
                        "program_name": program_name,
                        "corp_name": corp_name,
                        "corp_type": corp_type,
                        "program_rough_location": program_rough_location,
                        "program_term": program_term,
                        "apply_date": apply_date,
                        "program_days": program_info.get("program_days", ""),
                        "program_times": program_info.get("program_times", ""),
                        "available_time": program_info.get("available_time", ""),
                        "headcount": program_info.get("headcount", ""),
                        "program_type": program_info.get("program_type", ""),
                        "program_fee": program_info.get("program_fee", ""),
                        "school_types": program_info.get("school_types", ""),
                        "student_types": program_info.get("student_types", ""),
                        "quals_majors": program_info.get("quals_majors", ""),
                        "elementary_goal": elementary_details.get('goal', ''),
                        "elementary_preparation": elementary_details.get('preparation', ''),
                        "elementary_beginning": elementary_details.get('beginning', ''),
                        "elementary_activity": elementary_details.get('activity', ''),
                        "elementary_finale": elementary_details.get('finale', ''),
                        "elementary_after": elementary_details.get('after', ''),
                        "middle_goal": middle_details.get('goal', ''),
                        "middle_preparation": middle_details.get('preparation', ''),
                        "middle_beginning": middle_details.get('beginning', ''),
                        "middle_activity": middle_details.get('activity', ''),
                        "middle_finale": middle_details.get('finale', ''),
                        "middle_after": middle_details.get('after', ''),
                        "high_goal": high_details.get('goal', ''),
                        "high_preparation": high_details.get('preparation', ''),
                        "high_beginning": high_details.get('beginning', ''),
                        "high_activity": high_details.get('activity', ''),
                        "high_finale": high_details.get('finale', ''),
                        "high_after": high_details.get('after', ''),
                        "notice": notice,
                        "how_to_go": how_to_go,
                        "appliable_location": appliable_location
                    })

                    time.sleep(WORK_TERM_SLEEP)
                    self.click_close_button()
                    time.sleep(3)

                print(f"Finished page {self.current_page}")

                if not self.navigate_to_next_page():
                    print("Reached the last page. Exiting loop.")
                    break
            time.sleep(3)
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
            location = ""  # 새로운 변수 추가

            try:
                title_element = program_row.find_element(By.CLASS_NAME, "data-list-title")
                program_name = title_element.text
            except:
                program_name = ""

            try:
                hidden_elements = program_row.find_elements(By.CLASS_NAME, "data-list-m-hidden")
                if len(hidden_elements) >= 3:
                    apply_date = hidden_elements[2].text
                    corp_type = hidden_elements[0].text.strip().split("\n")[1]
            except:
                corp_type = ""

            try:
                location_element = program_row.find_element(By.CSS_SELECTOR, "td:nth-child(5)")
                program_rough_location = location_element.text.strip()
            except:
                program_rough_location = ""


        except Exception as e:
            print(f"Error processing row: {e}")
        
        return program_name, corp_type, apply_date, program_rough_location

    def extract_program_info(self, school_level):
        try:
            section = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.XPATH, f"//div[@class='bylv_tit' and contains(text(), '{school_level}')]/following-sibling::table[1]"))
            )

            rows = section.find_elements(By.CSS_SELECTOR, "tbody tr")
            info = {}
            current_category = None

            for row in rows:
                th_elements = row.find_elements(By.CSS_SELECTOR, "th")
                td_element = row.find_element(By.CSS_SELECTOR, "td")

                if len(th_elements) == 1:
                    current_category = th_elements[0].text.strip()
                    info[current_category] = td_element.text.strip()
                elif len(th_elements) == 2:
                    sub_category = th_elements[1].text.strip()
                    if current_category not in info or not isinstance(info[current_category], dict):
                        info[current_category] = {}
                    info[current_category][sub_category] = td_element.text.strip()

            return info

        except Exception as e:
            return {}

    def extract_place(self):
        try:
            place_element = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.program_info_conb > span.place"))
            )
            place = place_element.text.strip()
            return place
        except Exception as e:
            print(f"Error extracting place: {e}")
            return None

    def extract_program_term(self):
        try:
            program_term_element = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "select.cs-input[id='programTerm'] > option"))
            )
            program_term = program_term_element.text.strip()
            return program_term
        except Exception as e:
            print(f"Error extracting program term: {e}")
            return None

    def extract_dl_elements(self):
        try:
            dl_wrap_element = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.dl_wrap"))
            )
            dl_elements = dl_wrap_element.find_elements(By.CSS_SELECTOR, "dl")
            data = {}

            for dl in dl_elements:
                dt_text = dl.find_element(By.CSS_SELECTOR, "dt").text.strip()
                dd_element = dl.find_element(By.CSS_SELECTOR, "dd")
                dd_text = dd_element.text.strip()

                if dt_text == "체험주기":
                    active_days = [span.text.strip() for span in dd_element.find_elements(By.CSS_SELECTOR, "span.active")]
                    dd_text = [day.strip() for day in active_days]

                elif dt_text == "체험가능시간":
                    dd_text = [span.text.strip() for span in dd_element.find_elements(By.CSS_SELECTOR, "span") if len(span.text.strip()) > 0]

                elif dt_text == "체험 대상":
                    dd_text = [span.text.strip() for span in dd_element.find_elements(By.CSS_SELECTOR, "span")]

                elif dt_text == "참가비":
                    dd_text = dd_text.replace(",", "").replace("원", "")

                elif dt_text == "체험 직무/학과":
                    dd_text = dd_text.split()

                elif dt_text == "대상학교유형":
                    if dd_text.endswith(" 외 기관"):
                        dd_text = dd_text.replace(" 외 기관", "")
                    dd_text = dd_text.split(",")

                data[dt_text] = dd_text
            return data
        except Exception as e:
            print(f"Error extracting dl elements: {e}")
            return {}
        
    def translate_keys(self, dl_data):
        # Key mapping from Korean to English
        key_translation = {
            '체험주기': 'program_days',
            '체험이수시간': 'program_times',
            '체험가능시간': 'available_time',
            '모집인원': 'headcount',
            '체험유형': 'program_type',
            '대상학교유형': 'school_types',
            '체험 대상': 'student_types',
            '체험 직무/학과': 'quals_majors',
            '참가비': 'program_fee',
            '체험진행장소': 'location'
        }

        translated_data = {key_translation.get(k, k): v for k, v in dl_data.items()}

        return translated_data

    def parse_program_details(self, details):
        try:
            structured_details = {
                "goal": details.get("목표", "").strip(),
                "preparation": details.get("사전 준비", {}).get("도입", "").strip() if isinstance(details.get("사전 준비"), dict) else details.get("사전 준비", "").strip(),
                "beginning": details.get("본활동", "").strip(),
                "activity": details.get("본활동", "").strip(),
                "finale": details.get("마무리", "").strip(),
                "after": details.get("사후활동", "").strip()
            }
            return structured_details
        except Exception as e:
            return {}

    def extract_notice(self):
        try:
            notes_section = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(@class, 'program_info')]//h3[text()='유의사항']/following-sibling::div[contains(@class, 'program_conbox')]")
                )
            )
            notice = notes_section.find_element(By.TAG_NAME, "p").text.strip()
            return notice
        except Exception as e:
            print(f"Error extracting notice: {e}")
            return None
        
    def extract_location_info(self):
        try:
            location_info = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//h4[text()='체험장소 및 찾아가는 방법']/following-sibling::span")
                )
            )
            location_text = location_info.text.strip()
            return location_text
        except Exception as e:
            print(f"Error extracting location info: {e}")
            return None

    def extract_available_regions(self):
        try:
            region_elements = WebDriverWait(self.driver, 3).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "div.program_info[data-trakid='tab4'] .btn_location")
                )
            )
            regions = [element.text.strip() for element in region_elements]
            return regions
        except Exception as e:
            print(f"Error extracting available regions: {e}")
        return []

    def click_close_button(self):
        try:
            close_button = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.cs-btn.cs-btn-x.cs-btn-white2[onclick='expViewClose()']"))
            )
            close_button.click()
        except Exception as e:
            print(f"Error clicking close button: {e}")

if __name__ == "__main__":
    crawler = GgoomgilCrawler()
    crawler.run()

