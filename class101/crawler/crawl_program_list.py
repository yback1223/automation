from class101 import RESOURCE_DIR
from class101.utils.driver import Driver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from typing import Union, Any

import time
import json
import os

WORK_TERM_SLEEP = 1
OUTPUT_FILE = os.path.join(RESOURCE_DIR, "class101_program_list.json")

class Class101ProgramListCrawler:
    def __init__(self):
        self.driver = Driver().set_chrome()
        self.actions = ActionChains(self.driver)
        self.url = "https://class101.net/ko"
        self.current_page = 1

    def run(self) -> None:
        try:
            self.driver.get(self.url)
            time.sleep(WORK_TERM_SLEEP)
            
            category_and_content_links: list[dict[str, Union[str, list[dict[str, str]]]]] = []

            category_links: list[dict[str, str]] = self.collect_links()
            for category_link in category_links:
                category_name: str = category_link.get('category_name')
                category_link: str = category_link.get('category_link')
                self.driver.get(category_link)
                time.sleep(WORK_TERM_SLEEP)
                content_links: list[dict[str, str]] = self.scroll_and_collect_links()

                category_and_content_links.append({
                    "category_name": category_name,
                    "content_links": content_links
                })

                self.save_to_json(crawled_data=category_and_content_links, file_name=OUTPUT_FILE)

        except Exception as e:
            print(f"Error during crawling: {e}")
            self.save_to_json(crawled_data=category_and_content_links, file_name=OUTPUT_FILE)
        finally:
            self.driver.quit()



    def save_to_json(self, crawled_data: Any, file_name: str) -> None:
        try:
            with open(file_name, "w", encoding="utf-8") as json_file:
                json.dump(crawled_data, json_file, ensure_ascii=False, indent=4)
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
            category_names = [
                "디지털 드로잉", "드로잉", "공예", "요리 · 음료", "베이킹 · 디저트", "음악", "운동", "라이프스타일", "사진 · 영상",
                "금융 · 재테크", "창업 · 부업", "성공 마인드",
                "프로그래밍", "데이터사이언스", "제품 기획", "비즈니스", "생산성", "마케팅", "디자인", "영상/3D", 
                "영어", "외국어 시험", "제2 외국어",
                "아이 교육", "부모 교육"
            ]
            links = []

            for element in link_elements:
                if "categories" in element.get_attribute("href") and element.find_element(By.XPATH, ".//h3[@data-testid='title']").text.strip() in category_names:
                    links.append({
                        "category_name": element.find_element(By.XPATH, ".//h3[@data-testid='title']").text.strip(),
                        "category_link": element.get_attribute("href")
                    })
            print(f'links = {links}')

            self.click_close_alert_button()
            
            return links
        except Exception as e:
            self.click_close_alert_button()
            return []


    def scroll_and_collect_links(self) -> list[dict[str, str]]:
        collected_links: list[dict[str, str]] = []
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

    def click_close_alert_button(self):
        try:
            close_button = self.driver.find_element(By.CSS_SELECTOR, "button.ab-close-button[aria-label='Close Message']")
            close_button.click()
        except:
            pass

    def is_duplicate_link(self, href: str, collected_links: list[dict[str, str]]) -> bool:
        return any(link["link"] == href for link in collected_links)

    def extract_image_url(self, element) -> str:
        try:
            img_element = element.find_element(By.TAG_NAME, "img")
            return img_element.get_attribute("src")
        except:
            return ""
            

if __name__ == "__main__":
    crawler = Class101ProgramListCrawler()
    crawler.run()
