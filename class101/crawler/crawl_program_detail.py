from class101.utils.driver import Driver
from class101 import RESOURCE_DIR
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
from typing import Any, Union

import re, os
import clipboard, time
import pandas as pd
import math, random, json


WORK_TERM_SLEEP = 1
LIST_FILE = os.path.join(RESOURCE_DIR, "class101_program_list.json")
CRAWLED_FILE = os.path.join(RESOURCE_DIR, "class101_program_details.json")

class Class101ProgramDetailCrawler:
    def __init__(self):
        self.driver = Driver().set_chrome()
        self.actions = ActionChains(self.driver)
        self.current_page = 1


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


    def run(self):
        try:

            category_names = [
                "디지털 드로잉", "드로잉", "공예", "요리 · 음료", "베이킹 · 디저트", "음악", "운동", "라이프스타일", "사진 · 영상",
                "금융 · 재테크", "창업 · 부업", "성공 마인드",
                "프로그래밍", "데이터사이언스", "제품 기획", "비즈니스", "생산성", "마케팅", "디자인", "영상/3D", 
                "영어", "외국어 시험", "제2 외국어",
                "아이 교육", "부모 교육"
            ]
            for big_category in category_names:
                not_crawled_contents = self.load_not_crawled_contents(crawled_file=CRAWLED_FILE, program_list_file=LIST_FILE, category=big_category)
                for content in not_crawled_contents:
                    content_link = content.get('link')
                    image_url = content.get('image_url')

                    self.driver.get(content_link)
                    time.sleep(WORK_TERM_SLEEP)

                    try:
                        program_name, program_bookmark_count, program_link = self.find_and_click_share_button()
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

                        extracted_price = self.get_price_or_payment()
                        program_price = extracted_price if extracted_price else "N/A"

                        program_start_date = program_info[0] if len(program_info) > 0 else "N/A"
                        program_info_detail = [info.strip() for info in program_info[1].split("·")] if len(program_info) > 1 else []
                        program_difficulty = program_info_detail[0] if len(program_info_detail) > 0 else "N/A"
                        program_video_count = program_info_detail[1] if len(program_info_detail) > 1 else "N/A"
                        program_total_time = program_info[2] if len(program_info) > 2 else "N/A"
                        program_audio_languages = program_info[3] if len(program_info) > 3 else "N/A"
                        program_subtitles = program_info[4] if len(program_info) > 4 else "N/A"

                        program_first_category, program_second_category = self.extract_text_from_home_section() or ("N/A", "N/A")

                        crawled_program = {
                            "content_link": content_link,
                            "program_name": program_name,
                            "program_image_url": image_url,
                            "program_creator": program_creator,
                            "program_price": program_price,
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
                        }

                        self.save_to_json(crawled_file=CRAWLED_FILE, crawled_data=crawled_program)

                        print(f'Program "{program_name}" successfully added to the list.')
                    except Exception as e:
                        print(f"Error processing content link '{content_link}': {e}")
                        continue

        except Exception as e:
            print(f"Error during crawling: {e}")
        finally:
            self.driver.quit()



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
        collected_links = []
        self.click_close_alert_button()

        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(WORK_TERM_SLEEP)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("Reached the end of the page.")
                break
            last_height = new_height

        try:
            list_elements = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li a[href]"))
            )
            for element in list_elements:
                self.click_close_alert_button()
                href = element.get_attribute("href")
                if href and not self.is_duplicate_link(href, collected_links):
                    image_url = self.extract_image_url(element)
                    if image_url:
                        collected_links.append({
                            "link": href,
                            "image_url": image_url
                        })
                        print(f"Collected: {href} with image: {image_url}")
        except Exception as e:
            self.click_close_alert_button()
            print(f"Error while collecting links: {e}")

        return collected_links

    def extract_image_url(self, element):
        try:
            # First, try to find the source element with srcset
            try:
                image_source = element.find_element(By.XPATH, ".//picture[@data-testid='image']/source")
                srcset = image_source.get_attribute('srcset')
                if srcset:
                    urls = srcset.split(',')
                    if len(urls) >= 2:  # Check if there are at least two URLs
                        second_url = urls[1].strip()
                        return second_url.split(' ')[0]  # Return the second URL without size descriptor
            except Exception as e:
                print(f"Error finding or processing srcset")

            # If the above fails, look for the img tag directly inside the picture
            try:
                image_element = element.find_element(By.XPATH, ".//picture[@data-testid='image']/img")
                src = image_element.get_attribute('src')
                if src:
                    return src  # Return the src of the img tag since srcset is not available
            except Exception as e:
                print(f"Error finding or processing img src")

            print("No image URL found.")
            return None
        except Exception as e:
            print(f"Unexpected error in extract_image_url: {e}")
            return None

    def is_duplicate_link(self, link, collected_links):
        return any(existing_link['link'] == link for existing_link in collected_links)

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


    def get_price_or_payment(self):
        try:
            try:
                price_elements = self.driver.find_elements(By.XPATH, ".//div[@class='css-1ru7dyh']")
                span_elements = price_elements[-1].find_elements(By.TAG_NAME, 'span')

                if span_elements:
                    last_span_text = span_elements[-1].text.strip()
                    return last_span_text
                else:
                    return None
            except:
                pass

            try:
                spans = self.driver.find_elements(By.XPATH, "//div[@class='css-10c2f7i']/div[@class='css-fqykbc']/button[@class='css-1hvtp3b']/div[@class='css-12fz3yr']/span[contains(text(), '무이자 할부')]")

                for i, span in enumerate(spans):
                    button = span.find_element(By.XPATH, "./ancestor::button[@class='css-1hvtp3b']")
                    span_text = span.text.strip()
                    button_text = button.text.strip()

                for span in spans:
                    button = span.find_element(By.XPATH, "./ancestor::button[@class='css-1hvtp3b']")
                    if button.is_displayed() and button.is_enabled():
                        try:
                            button.click()
                            time.sleep(2)
                            break
                        except Exception as e:
                            self.driver.execute_script("arguments[0].click();", button)
                            time.sleep(2)
                            break
                else:
                    print("No clickable button found")

                price_elements = self.driver.find_elements(By.XPATH, "//div[@class='css-fqykbc']/div[@class='css-slclp7']/h3[@class='css-12r95pg' and contains(text(), '원')]")

                final_price = price_elements[-1].text.strip()
                return final_price
            except:
                pass

            try:
                subscribe_button = self.driver.find_element(By.XPATH, "//span[@data-testid='button-text' and text()='구독으로 시작하기']")
                return '구독'
            except:
                pass

            try:
                alert_apply_button = self.driver.find_element(By.XPATH, "//button[@data-testid='button-text' and text()='알림 신청하기']")
                return '알림 신청 중'
            except:
                pass
        except:
            print(f'가격을 찾지 못함!')
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
                        print(f'title_text = {title_text}')


                        self.click_close_alert_button()
                        divs = self.driver.find_elements(By.XPATH, "//div[@class='css-1e43e8r']")

                        for div in divs:
                            if 'bookmark-thin' in div.get_attribute("innerHTML"):
                                try:
                                    bookmark_value = div.find_element(By.XPATH, "./span[@data-testid='body']").get_attribute('textContent').strip()
                                    break
                                except Exception as e:
                                    print(f"Failed to find bookmark element: {e}")

                        else:
                            print("No div with bookmark-thin was found.")

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

                        return title_text, bookmark_value, clipboard.paste()

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
            curriculum_html = paper_element.get_attribute('outerHTML')

            program_curriculum_text = self.parse_html_to_json(curriculum_html)

            return program_info, program_curriculum_text

        except Exception as e:
            print(f"Error extracting program info")
            self.click_close_alert_button()
            return None



    def parse_html_to_json(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')

        result = []
        containers = soup.find_all('div', class_='css-1jenhu5')

        for container in containers:
            big_section = container.find('div', class_='css-slv2ha')
            if big_section:
                big_section_title = big_section.find('h3', {'data-testid': 'title'})
                if big_section_title:
                    big_section_title_text = big_section_title.text.strip()

                    small_sections = container.find_all('button', class_='css-1hvtp3b')
                    small_sections_data = []

                    for section in small_sections:
                        title_elem = section.find('h3', {'data-testid': 'title', 'class': 'css-u3phay'})
                        time_elem = section.find('span', {'data-testid': 'body', 'class': 'css-bgvpp3'})

                        if title_elem and time_elem:
                            title_text = title_elem.text.strip()
                            time_text = time_elem.text.strip()
                            small_sections_data.append({
                                "small_section": title_text,
                                "time": time_text
                            })

                    if small_sections_data:
                        result.append({
                            "big_section": big_section_title_text,
                            "small_sections": small_sections_data
                        })
                    else:
                        print(f"No small sections data for {big_section_title_text}")
            else:
                print("No big section found in this container.")

        return result




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
            print(f"Error: Kit doesn't exist!")
            self.click_close_alert_button()
            return None


    def click_close_alert_button(self):
        try:
            close_button = self.driver.find_element(By.CSS_SELECTOR, "button.ab-close-button[aria-label='Close Message']")
            close_button.click()
        except:
            pass


if __name__ == "__main__":
    crawler = Class101ProgramDetailCrawler()
    crawler.run()
