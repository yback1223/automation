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

class UdemyCrawler:
    def load_existing_data(self, file_name):
        try:
            with open(file_name, "r", encoding="utf-8") as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            return []

    def __init__(self):
        self.programs = self.load_existing_data("udemy_crawled_data.json")
        self.driver = Driver().set_chrome()
        self.actions = ActionChains(self.driver)
        self.url = "https://www.udemy.com/"
        self.category_urls = [
            # development
            "https://www.udemy.com/courses/development/web-development/",
            "https://www.udemy.com/courses/development/data-science/",
            "https://www.udemy.com/courses/development/mobile-apps/",
            "https://www.udemy.com/courses/development/programming-languages/",
            "https://www.udemy.com/courses/development/game-development/",
            "https://www.udemy.com/courses/development/databases/",
            "https://www.udemy.com/courses/development/software-testing/",
            "https://www.udemy.com/courses/development/software-engineering/",
            "https://www.udemy.com/courses/development/development-tools/",
            "https://www.udemy.com/courses/development/no-code-development/",

            # business
            "https://www.udemy.com/courses/business/entrepreneurship/",
            "https://www.udemy.com/courses/business/communications/",
            "https://www.udemy.com/courses/business/management/",
            "https://www.udemy.com/courses/business/sales/",
            "https://www.udemy.com/courses/business/strategy/",
            "https://www.udemy.com/courses/business/operations/",
            "https://www.udemy.com/courses/business/project-management/",
            "https://www.udemy.com/courses/business/business-law/",
            "https://www.udemy.com/courses/business/analytics-and-intelligence/",
            "https://www.udemy.com/courses/business/human-resources/",
            "https://www.udemy.com/courses/business/industry/",
            "https://www.udemy.com/courses/business/e-commerce/",
            "https://www.udemy.com/courses/business/media/",
            "https://www.udemy.com/courses/business/real-estate/",
            "https://www.udemy.com/courses/business/other-business/",

            # finana-and-accounting
            "https://www.udemy.com/courses/finance-and-accounting/accounting-bookkeeping/",
            "https://www.udemy.com/courses/finance-and-accounting/cryptocurrency-and-blockchain/",
            "https://www.udemy.com/courses/finance-and-accounting/finance-management/",
            "https://www.udemy.com/courses/finance-and-accounting/finance-certification-and-exam-prep/",
            "https://www.udemy.com/courses/finance-and-accounting/financial-modeling-and-analysis/",
            "https://www.udemy.com/courses/finance-and-accounting/investing-and-trading/",
            "https://www.udemy.com/courses/finance-and-accounting/compliance/",
            "https://www.udemy.com/courses/finance-and-accounting/economics/",
            "https://www.udemy.com/courses/finance-and-accounting/money-management-tools/",
            "https://www.udemy.com/courses/finance-and-accounting/taxes/",
            "https://www.udemy.com/courses/finance-and-accounting/other-finance-and-accounting/",

            # it-and-software
            "https://www.udemy.com/courses/it-and-software/it-certification/",
            "https://www.udemy.com/courses/it-and-software/network-and-security/",
            "https://www.udemy.com/courses/it-and-software/hardware/",
            "https://www.udemy.com/courses/it-and-software/operating-systems/",
            "https://www.udemy.com/courses/it-and-software/other-it-and-software/",

            # office-productivity
            "https://www.udemy.com/courses/office-productivity/microsoft/",
            "https://www.udemy.com/courses/office-productivity/apple/",
            "https://www.udemy.com/courses/office-productivity/google/",
            "https://www.udemy.com/courses/office-productivity/sap/",
            "https://www.udemy.com/courses/office-productivity/oracle/",
            "https://www.udemy.com/courses/office-productivity/other-productivity/",

            # personal development
            "https://www.udemy.com/courses/personal-development/personal-transformation/",
            "https://www.udemy.com/courses/personal-development/productivity/",
            "https://www.udemy.com/courses/personal-development/leadership/",
            "https://www.udemy.com/courses/personal-development/career-development/",
            "https://www.udemy.com/courses/personal-development/parenting-and-relationships/",
            "https://www.udemy.com/courses/personal-development/happiness/",
            "https://www.udemy.com/courses/personal-development/religion-and-spirituality/",
            "https://www.udemy.com/courses/personal-development/personal-brand-building/",
            "https://www.udemy.com/courses/personal-development/creativity/",
            "https://www.udemy.com/courses/personal-development/influence/",
            "https://www.udemy.com/courses/personal-development/self-esteem-and-confidence/",
            "https://www.udemy.com/courses/personal-development/stress-management/",
            "https://www.udemy.com/courses/personal-development/memory/",
            "https://www.udemy.com/courses/personal-development/motivation/",
            "https://www.udemy.com/courses/personal-development/other-personal-development/",

            # design
            "https://www.udemy.com/courses/design/web-design/",
            "https://www.udemy.com/courses/design/graphic-design-and-illustration/",
            "https://www.udemy.com/courses/design/design-tools/",
            "https://www.udemy.com/courses/design/user-experience/",
            "https://www.udemy.com/courses/design/game-design/",
            "https://www.udemy.com/courses/design/3d-and-animation/",
            "https://www.udemy.com/courses/design/fashion/",
            "https://www.udemy.com/courses/design/architectural-design/",
            "https://www.udemy.com/courses/design/interior-design/",
            "https://www.udemy.com/courses/design/other-design/",

            # marketing
            "https://www.udemy.com/courses/marketing/digital-marketing/",
            "https://www.udemy.com/courses/marketing/search-engine-optimization/",
            "https://www.udemy.com/courses/marketing/social-media-marketing/",
            "https://www.udemy.com/courses/marketing/branding/",
            "https://www.udemy.com/courses/marketing/marketing-fundamentals/",
            "https://www.udemy.com/courses/marketing/analytics-and-automation/",
            "https://www.udemy.com/courses/marketing/public-relations/",
            "https://www.udemy.com/courses/marketing/advertising/",
            "https://www.udemy.com/courses/marketing/video-and-mobile-marketing/",
            "https://www.udemy.com/courses/marketing/content-marketing/",
            "https://www.udemy.com/courses/marketing/growth-hacking/",
            "https://www.udemy.com/courses/marketing/affiliate-marketing/",
            "https://www.udemy.com/courses/marketing/product-marketing/",
            "https://www.udemy.com/courses/marketing/other-marketing/",

            # lifestyle
            "https://www.udemy.com/courses/lifestyle/arts-and-crafts/",
            "https://www.udemy.com/courses/lifestyle/beauty-and-makeup/",
            "https://www.udemy.com/courses/lifestyle/esoteric-practices/",
            "https://www.udemy.com/courses/lifestyle/food-and-beverage/",
            "https://www.udemy.com/courses/lifestyle/gaming/",
            "https://www.udemy.com/courses/lifestyle/home-improvement/",
            "https://www.udemy.com/courses/lifestyle/pet-care-and-training/",
            "https://www.udemy.com/courses/lifestyle/travel/",
            "https://www.udemy.com/courses/lifestyle/other-lifestyle/",

            # photography-and-video
            "https://www.udemy.com/courses/photography-and-video/digital-photography/",
            "https://www.udemy.com/courses/photography-and-video/photography-fundamentals/",
            "https://www.udemy.com/courses/photography-and-video/portraits/",
            "https://www.udemy.com/courses/photography-and-video/photography-tools/",
            "https://www.udemy.com/courses/photography-and-video/commercial-photography/",
            "https://www.udemy.com/courses/photography-and-video/video-design/",
            "https://www.udemy.com/courses/photography-and-video/other-photography-and-video/",

            # health-and-fitness
            "https://www.udemy.com/courses/health-and-fitness/fitness/",
            "https://www.udemy.com/courses/health-and-fitness/general-health/",
            "https://www.udemy.com/courses/health-and-fitness/sports/",
            "https://www.udemy.com/courses/health-and-fitness/nutrition/",
            "https://www.udemy.com/courses/health-and-fitness/yoga/",
            "https://www.udemy.com/courses/health-and-fitness/mental-health/",
            "https://www.udemy.com/courses/health-and-fitness/self-defense/",
            "https://www.udemy.com/courses/health-and-fitness/safety-and-first-aid/",
            "https://www.udemy.com/courses/health-and-fitness/dance/",
            "https://www.udemy.com/courses/health-and-fitness/meditation/",
            "https://www.udemy.com/courses/health-and-fitness/other-health-and-fitness/",

            # music
            "https://www.udemy.com/courses/music/instruments/",
            "https://www.udemy.com/courses/music/production/",
            "https://www.udemy.com/courses/music/music-fundamentals/",
            "https://www.udemy.com/courses/music/vocal/",
            "https://www.udemy.com/courses/music/music-techniques/",
            "https://www.udemy.com/courses/music/music-software/",
            "https://www.udemy.com/courses/music/other-music/",

            # teaching-and-academics
            "https://www.udemy.com/courses/teaching-and-academics/engineering/",
            "https://www.udemy.com/courses/teaching-and-academics/humanities/",
            "https://www.udemy.com/courses/teaching-and-academics/math/",
            "https://www.udemy.com/courses/teaching-and-academics/online-education/",
            "https://www.udemy.com/courses/teaching-and-academics/science/",
            "https://www.udemy.com/courses/teaching-and-academics/social-science/",
            "https://www.udemy.com/courses/teaching-and-academics/language/",
            "https://www.udemy.com/courses/teaching-and-academics/teacher-training/",
            "https://www.udemy.com/courses/teaching-and-academics/test-prep/",
            "https://www.udemy.com/courses/teaching-and-academics/other-teaching-academics/"
        ]
        self.current_page = 1

    def run(self):
        try:
            self.driver.get(self.url)
            time.sleep(WORK_TERM_SLEEP)

            self.choose_list_size()

            existing_titles = {program.get("program_name") for program in self.programs}
            print(f"Existing titles: {len(existing_titles)} found.")

            while True:
                print(f"Starting page {self.current_page}")

                # 모든 program_rows 가져오기
                program_rows = self.get_rows_from_list()
                print(f"Found {len(program_rows)} rows on page {self.current_page}.")
                if not program_rows:
                    print(f"No rows found on page {self.current_page}.")
                    break

                # 현재 페이지에서 program_name만 추출
                current_titles = self.extract_titles_from_rows(program_rows)
                print(f"Titles on this page: {len(current_titles)}")

                # 기존 데이터와 비교하여 새로운 제목 필터링
                new_titles = [title for title in current_titles if title not in existing_titles]
                print(f"New titles to process: {len(new_titles)}")

                if not new_titles:
                    if not self.navigate_to_next_page():
                        print("Reached the last page. Exiting loop.")
                        break
                    continue

                # 새로운 제목만 포함하는 program_rows 필터링
                filtered_program_rows = [
                    row for row in program_rows 
                    if row.find_element(By.CLASS_NAME, "data-list-title").text.strip() in new_titles
                ]

                # 필터링된 program_rows 처리
                for program_row in filtered_program_rows:
                    try:
                        program_name, corp_type, apply_date, program_rough_location = self.extract_data_from_rows(program_row)

                        program_row.click()
                        time.sleep(3)

                        link = self.get_link()
                        corp_name = self.extract_place()
                        program_term = self.extract_program_term()
                        program_info = self.translate_keys(dl_data=self.extract_dl_elements())
                        elementary_details = self.parse_program_details(self.extract_program_info('초등학교'))
                        middle_details = self.parse_program_details(self.extract_program_info('중학교'))
                        high_details = self.parse_program_details(self.extract_program_info('고등학교'))
                        notice = self.extract_notice()
                        how_to_go = self.extract_location_info()
                        appliable_location = self.extract_available_regions()
                        print(f'링크: {link}\n, 체험처: {corp_name}')


                        self.programs.append({
                            "program_name": program_name,
                            "corp_name": corp_name,
                            "corp_type": corp_type,
                            "link": link,
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

                    except Exception as e:
                        print(f"[경고] 프로그램 하나의 정보를 가져오는 중 오류가 발생했습니다: {e}")

                    finally:
                        self.click_close_button()
                        time.sleep(WORK_TERM_SLEEP)

                print(f"Finished page {self.current_page}")
                if not self.navigate_to_next_page():
                    print("Reached the last page. Exiting loop.")
                    break

            self.save_to_json("crawled_data.json")

        except Exception as e:
            print(f"Error during crawling: {e}")
            self.save_to_json("crawled_data.json")
        finally:
            self.save_to_json("crawled_data.json")
            self.driver.quit()


    def get_link(self):
        try:
            share_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, f"button.btn_share[title='팝업열림']"))
            )
            share_button.click()
            time.sleep(WORK_TERM_SLEEP)
        except:
            print(f"Error opening popup")

        try:
            copy_link_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, f"button.btn_copy[title='url 복사']"))
            )
            copy_link_button.click()
            time.sleep(3)
            corp_name = clipboard.paste()
        except:
            print(f"Error copying url")

        try:
            close_link_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, f"button.btn_share_close[title='팝업닫힘']"))
            )
            close_link_button.click()
            time.sleep(WORK_TERM_SLEEP)
        except:
            print(f"Error closing popup")      

        return corp_name


    def extract_titles_from_rows(self, rows):
        """
        주어진 행 리스트에서 프로그램 제목만 추출.
        """
        titles = []
        for row in rows:
            try:
                title_element = row.find_element(By.CLASS_NAME, "data-list-title")
                titles.append(title_element.text.strip())
            except:
                continue
        return titles

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
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(WORK_TERM_SLEEP)
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
            print(f"Error processing row")
            return "", "", "", ""

    def extract_program_info(self, school_level):
        try:
            section = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.XPATH, f"//div[@class='bylv_tit' and contains(text(), '{school_level}')]/following-sibling::table[1]"))
            )

            rows = section.find_elements(By.CSS_SELECTOR, "tbody tr")
            info = {}
            current_category = None

            for row in rows:
                try:
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
                except Exception as e:
                    continue

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
            print(f"[경고] 체험 장소 추출 중 오류가 발생했습니다")
            return ""

    def extract_program_term(self):
        try:
            program_term_element = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "select.cs-input[id='programTerm'] > option"))
            )
            program_term = program_term_element.text.strip()
            return program_term
        except Exception as e:
            print(f"[경고] 체험 기간(프로그램 신청 기간) 추출 중 오류가 발생했습니다")
            return ""

    def extract_dl_elements(self):
        try:
            dl_wrap_element = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.dl_wrap"))
            )
            dl_elements = dl_wrap_element.find_elements(By.CSS_SELECTOR, "dl")
            data = {}

            for dl in dl_elements:
                try:
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

                except Exception as e:
                    print(f"[경고] DL 요소( {dl.text} ) 정보 추출 중 오류")
                    continue

            return data
        except Exception as e:
            print(f"[경고] dl_wrap 요소를 찾는 중 오류가 발생했습니다")
            return {}

    def translate_keys(self, dl_data):

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

        translated_data = {}
        for k, v in dl_data.items():
            # 매핑된 키가 없으면 기존 키 사용
            new_key = key_translation.get(k, k)
            translated_data[new_key] = v

        return translated_data

    def parse_program_details(self, details):
        try:
            structured_details = {
                "goal": details.get("목표", "").strip(),
                "preparation": (
                    details.get("사전 준비", {}).get("도입", "").strip() 
                    if isinstance(details.get("사전 준비"), dict) 
                    else details.get("사전 준비", "").strip()
                ),
                "beginning": details.get("본활동", "").strip(),
                "activity": details.get("본활동", "").strip(),
                "finale": details.get("마무리", "").strip(),
                "after": details.get("사후활동", "").strip()
            }
            return structured_details
        except Exception as e:
            print(f"[경고] 프로그램 상세 내용을 파싱하는 중 오류가 발생했습니다: {e}")
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
            print(f"[경고] 유의사항 추출 중 오류가 발생했습니다")
            return ""

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
            print(f"[경고] 찾아가는 방법 추출 중 오류가 발생했습니다")
            return ""

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
            print(f"[경고] 체험 가능 지역 정보 추출 중 오류가 발생했습니다")
            return []

    def click_close_button(self):
        try:
            close_button = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.cs-btn.cs-btn-x.cs-btn-white2[onclick='expViewClose()']"))
            )
            close_button.click()
        except Exception as e:
            print(f"[경고] 닫기 버튼 클릭 중 오류가 발생했습니다")


if __name__ == "__main__":
    crawler = GgoomgilCrawler()
    crawler.run()
