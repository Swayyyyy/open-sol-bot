import time
from DrissionPage import ChromiumPage

class CloudflareBypasser:
    def __init__(self, addr_or_opts, max_retries=-1, log=True, retry=5):
        self.set_driver(addr_or_opts)
        self.max_retries = max_retries
        self.log = log
        self.retry = retry

    def search_recursively_shadow_root_with_iframe(self, ele):
        if ele.shadow_root:
            if ele.shadow_root.child().tag == "iframe":
                return ele.shadow_root.child()
        else:
            for child in ele.children():
                result = self.search_recursively_shadow_root_with_iframe(child)
                if result:
                    return result
        return None

    def search_recursively_shadow_root_with_cf_input(self, ele):
        if ele.shadow_root:
            if ele.shadow_root.ele("tag:input"):
                return ele.shadow_root.ele("tag:input")
        else:
            for child in ele.children():
                result = self.search_recursively_shadow_root_with_cf_input(child)
                if result:
                    return result
        return None
    
    def locate_cf_button(self):
        button = None
        eles = self.driver.eles("tag:input")
        for ele in eles:
            if "name" in ele.attrs.keys() and "type" in ele.attrs.keys():
                if "turnstile" in ele.attrs["name"] and ele.attrs["type"] == "hidden":
                    button = ele.parent().shadow_root.child()("tag:body").shadow_root("tag:input")
                    break
            
        if button:
            return button
        else:
            # If the button is not found, search it recursively
            self.log_message("Basic search failed. Searching for button recursively.")
            ele = self.driver.ele("tag:body")
            iframe = self.search_recursively_shadow_root_with_iframe(ele)
            if iframe:
                button = self.search_recursively_shadow_root_with_cf_input(iframe("tag:body"))
            else:
                self.log_message("Iframe not found. Button search failed.")
            return button

    def log_message(self, message):
        if self.log:
            print(message)

    def click_verification_button(self):
        try:
            button = self.locate_cf_button()
            if button:
                self.log_message("Verification button found. Attempting to click.")
                button.click()
            else:
                self.log_message("Verification button not found.")

        except Exception as e:
            self.log_message(f"Error clicking verification button: {e}")

    def is_bypassed(self):
        try:
            title = self.driver.title.lower()
            return "just a moment" not in title
        except Exception as e:
            self.log_message(f"Error checking page title: {e}")
            return False
        
    def set_driver(self, options):
        self.driver = ChromiumPage(addr_or_opts=options)
        
    def bypass(self):
        
        try_count = 0

        while not self.is_bypassed():
            if try_count > self.retry:
                self.log_message("Exceeded maximum retries. Bypass failed.")
                self.set_driver(self.driver.options)
                try_count = 0
            # self.driver.get_driver().delete_all_cookies()
            if 0 < self.max_retries + 1 <= try_count:
                self.log_message("Exceeded maximum retries. Bypass failed.")
                break

            self.log_message(f"Attempt {try_count + 1}: Verification page detected. Trying to bypass...")
            self.click_verification_button()

            try_count += 1
            time.sleep(5)

        if self.is_bypassed():
            self.log_message("Bypass successful.")
        else:
            self.log_message("Bypass failed.")

    def request(self, url):
        self.driver.get(url)
        time.sleep(3)
        self.bypass()
        return self.driver.html