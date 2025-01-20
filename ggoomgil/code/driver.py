from selenium import webdriver


class Driver:
    def __init__(self):
        self.driver = None

    def set_chrome(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--lang=ko-KR")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("disable-infobars")
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        chrome_options.add_argument(f"user-agent={user_agent}")

        # 팝업 차단 옵션 추가
        prefs = {
            "profile.default_content_setting_values.notifications": 2,  # 알림 차단
            "profile.default_content_setting_values.popups": 2,       # 팝업 차단
            "profile.default_content_setting_values.automatic_downloads": 1  # 다운로드 자동 허용
        }
        chrome_options.add_experimental_option("prefs", prefs)

        self.driver = webdriver.Chrome(options=chrome_options)

        # Selenium 탐지 방지 설정
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """
        })

        # 모든 브라우저 팝업 제거를 위한 자바스크립트 실행
        self.driver.execute_script("""
            // MutationObserver로 DOM 변경 감지하여 팝업 차단
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === 1) {  // Element 노드
                            node.style.display = 'none';  // 보이지 않게 설정
                        }
                    });
                });
            });
            observer.observe(document.body, { childList: true, subtree: true });

            // alert, confirm, prompt 차단
            window.alert = function() {};
            window.confirm = function() { return false; };
            window.prompt = function() { return null; };
        """)

        self.driver.maximize_window()
        return self.driver
