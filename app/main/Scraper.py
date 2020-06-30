import time
from selenium import webdriver
from flask import current_app as flask_app
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Scraper(object):
    """
    Wrapper for selenium Chrome driver with methods to scroll through a page and
    to scrape and parse info from a linkedin page
    """

    def __init__(self):
        self.timeout = 30  # adjust accordingly
        self.scroll_pause = 0.381
        self.scroll_increment = 150
        self.max_scroll_times = 85  # scroll limit to break the loop

        driver_options = Options()

        # go headless only in production
        if flask_app.config["ENV"] == 'prod':
            driver_options.add_argument('--headless')
            driver_options.add_argument("--window-size=1920x1080")
            driver_options.add_argument("--no-sandbox")
            driver_options.add_argument("--disable-gpu")

        if flask_app.config["SELENIUM_MODE"] == 'remote':
            URL = '{0}/wd/hub'.format(
                flask_app.config["SELENIUM_REMOTE_URL"])
            self.driver = webdriver.Remote(
                command_executor=URL,
                desired_capabilities=driver_options.to_capabilities()
            )
        else:
            self.driver = webdriver.Chrome(options=driver_options)

        self.driver.get('https://www.linkedin.com/login')
        self.driver.set_window_size(1920, 1080)

        self.login(flask_app.config["LINKEDIN_EMAIL"],
                   flask_app.config["LINKEDIN_PASSWORD"])

    def login(self, email, password):
        email_input = self.driver.find_element_by_name('session_key')
        password_input = self.driver.find_element_by_name('session_password')
        email_input.send_keys(email)
        password_input.send_keys(password)
        password_input.send_keys(Keys.ENTER)

    def scroll_to_bottom(self):
        """Scroll to the bottom of the page
        Params:
            - scroll_pause_time {float}: time to wait (s) between page scroll increments
            - scroll_increment {int}: increment size of page scrolls (pixels)
        """
        expandable_button_selectors = [
            'button[aria-expanded="false"].pv-skills-section__additional-skills',
            'button[aria-expanded="false"].pv-profile-section__see-more-inline',
            'button[aria-expanded="false"].pv-top-card-section__summary-toggle-button',
            'button[data-control-name="contact_see_more"]',
            'button[aria-controls="test-scores-expandable-content"]',
            # fix: For some users, thumbnail model opens somehow
            'button[aria-label="Dismiss"].artdeco-modal__dismiss'
        ]

        current_height = 0
        scrolls_left = self.max_scroll_times
        while True:
            scrolls_left -= 1
            for name in expandable_button_selectors:
                try:
                    self.driver.find_element_by_css_selector(name).click()
                except:
                    pass

            # Use JS to click on invisible expandable 'see more...' elements
            self.driver.execute_script(
                'document.querySelectorAll(".lt-line-clamp__ellipsis:not(.lt-line-clamp__ellipsis--dummy) .lt-line-clamp__more").forEach(el => el.click())')

            # Scroll down to bottom
            new_height = self.driver.execute_script(
                "return Math.min({}, document.body.scrollHeight)".format(current_height + self.scroll_increment))
            """
            this ends in a loop for some profiles
            break on reaching a particular scrolling threshold
            """
            if (new_height == current_height) or (scrolls_left <= 0):
                break
            self.driver.execute_script(
                "window.scrollTo(0, Math.min({}, document.body.scrollHeight));".format(new_height))
            current_height = new_height
            # Wait to load page
            time.sleep(self.scroll_pause)

    def wait(self, condition):
        return WebDriverWait(self.driver, self.timeout).until(condition)

    def wait_for_el(self, selector):
        return self.wait(EC.presence_of_element_located((
            By.CSS_SELECTOR, selector
        )))

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.quit()

    def quit(self):
        if self.driver:
            self.driver.quit()
