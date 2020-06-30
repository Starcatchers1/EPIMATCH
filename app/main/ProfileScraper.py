from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

from .Scraper import Scraper
from .Profile import Profile

from ..utils.scrape_util import AnyEC


class ProfileScraper(Scraper):
    """
    Scraper for Personal LinkedIn Profiles. See inherited Scraper class for
    details about the constructor.
    """
    MAIN_SELECTOR = '.core-rail'
    PROFILE_SELECTOR = 'profile-content'
    ERROR_SELECTOR = '.profile-unavailable'

    def scrape(self, url='', user=None):
        self.load_profile_page(url, user)

        return self.get_profile()

    def load_profile_page(self, url='', user=None):
        """Load profile page and all async content
        Params:
            - url {str}: url of the profile to be loaded
        Raises:
            ValueError: If link doesn't match a typical profile url
        """
        if not user and url == '':
            me_button = self.driver.find_element_by_css_selector(
                'img.nav-item__profile-member-photo')
            me_button.click()
            try:
                wait = WebDriverWait(self.driver, self.timeout)
                view_profile_element = wait.until(
                    EC.element_to_be_clickable((By.XPATH, '//span[text()="View profile"]')))
                view_profile_element.click()
                # Wait for page to load dynamically via javascript
                try:
                    myElem = WebDriverWait(self.driver, self.timeout).until(EC.presence_of_element_located(
                        (By.ID, self.PROFILE_SELECTOR))
                    )
                except TimeoutException as e:
                    print(
                        """Took too long to load self profile. Common problems/solutions:
                        1. Invalid LI_AT value: ensure that yours is correct (they
                        update frequently)
                        2. Slow Internet: increase the timeout parameter in the Scraper
                        constructor
                        """)
                # Scroll to the bottom of the page incrementally to load any lazy-loaded content
                self.scroll_to_bottom()
            except TimeoutException as e:
                print("""View Profile Button Not Found""")
            return
        if user:
            url = 'https://www.linkedin.com' + user
        if 'com/in/' not in url:
            print(
                "Url must look like... .com/in/NAME")
        self.driver.get(url)
        # Wait for page to load dynamically via javascript
        try:
            myElem = WebDriverWait(self.driver, self.timeout).until(
                AnyEC(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, self.MAIN_SELECTOR)),
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, self.ERROR_SELECTOR))
                )
            )

        except TimeoutException as e:
            print(
                """Took too long to load profile. Common problems/solutions:
                1. Invalid LI_AT value: ensure that yours is correct (they
                update frequently)
                2. Slow Internet: increase the timeout parameter in the Scraper
                constructor
                """)
        # Check if we got the 'profile unavailable' page
        try:
            self.driver.find_element_by_css_selector(self.MAIN_SELECTOR)
        except:
            print(
                'Profile Unavailable: Profile link does not match any current Linkedin Profiles')
        # Scroll to the bottom of the page incrementally to load any lazy-loaded content
        self.scroll_to_bottom()

    def get_profile(self):
        try:
            profile = self.driver.find_element_by_css_selector(
                self.MAIN_SELECTOR).get_attribute("outerHTML")
            contact_info = self.get_contact_info()

            return Profile(profile + contact_info)
        except Exception as e:
            print(e)
            # print("Could not find profile wrapper html. This sometimes happens for exceptionally long profiles.  Try decreasing scroll-increment.")
        return None

    def get_contact_info(self):
        try:
            # Scroll to top to put clickable button in view
            self.driver.execute_script("window.scrollTo(0, 0);")
            button = self.driver.find_element_by_css_selector(
                'a[data-control-name="contact_see_more"]')
            button.click()
            contact_info = self.wait_for_el('.pv-contact-info')

            return contact_info.get_attribute('outerHTML')
        except Exception as e:
            print(e)

            return ""
