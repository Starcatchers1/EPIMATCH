import time
from urllib.parse import urlencode
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

from .Pages import Pages
from .Search import Search
from .Scraper import Scraper

from ..utils.scrape_util import AnyEC, BothEC


class SearchScraper(Scraper):

    # Percentage of pages to visit(Update with 100 to visit all pages)
    PAGES_LIMIT_PERCENT = 99
    # Limit of users(max is 1000)
    MAX_PROFILES_COUNT = 999
    # css selectors
    MAIN_SELECTOR = '.core-rail'
    ERROR_SELECTOR = '.search-no-results'
    SEARCH_LOADER = 'div.search-is-loading'
    SEARCH_LIMIT_REACHED_SELECTOR = 'div.search-paywall'
    PAGINATION_NEXT_SELECTOR = 'button[aria-label="Next"]'
    DEFAULT_SEARCH_PREFIX_URL = 'https://www.linkedin.com/search/results/people/?facetGeoRegion=["fr%3A0"%2C"fr%3A5227"]&facetNetwork=["S"%2C"O"]&origin=FACETED_SEARCH&'

    def go_to_search_page(self, url):
        return self.driver.get(url)

    def load_search_page(self):
        # Wait for page to load dynamically via javascript
        try:
            # Wait until the loader `div.search-is-loading` is gone as `MAIN_SELECTOR` never unmounts
            myElem = WebDriverWait(self.driver, self.timeout).until(
                # This checks for both conditions to be true
                # Checks if loader screen is hidden & any of the core elements is located
                BothEC(EC.invisibility_of_element_located(
                    (By.CSS_SELECTOR, self.SEARCH_LOADER)),
                    AnyEC(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, self.MAIN_SELECTOR)),
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, self.ERROR_SELECTOR))
                )
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
        # Check if we got the 'No results found' page
        try:
            self.driver.find_element_by_css_selector(self.MAIN_SELECTOR)
        except:
            print('No results found.')
        # Scroll to the bottom of the page incrementally to load any lazy-loaded content
        self.scroll_to_bottom()

    def search(self, skills=[]):
        max_accessible_pages = 1
        keywords = " ".join(skills)
        params = {'keywords': keywords}
        encoded = urlencode(params)

        # pass encoded url
        self.go_to_search_page(self.DEFAULT_SEARCH_PREFIX_URL + encoded)
        self.load_search_page()
        print('Currently at Page 1')

        stats = self.get_result_stats().to_dict()
        if stats and "pages" in stats and "max_accessible_pages" in stats["pages"]:
            max_accessible_pages = stats["pages"]["max_accessible_pages"]
        user_urls = self.get_urls(max_accessible_pages)

        return {
            'urls': {
                'vanity_urls': user_urls,
                'total': len(user_urls)
            },
            'stats': stats["pages"]
        }

    def get_urls(self, total_pages):
        urls = []
        """
        PAGES_LIMIT_PERCENT controls percent of pages to be visited
        if set to 25% and total_pages = 21,
           visits upto ((21 * 25 / 100) - 1) ~= 5(rounded)

        MAX_PROFILES_COUNT limits pagination and breaks on reaching this many users
        """
        pagination_limit = round(
            (total_pages * self.PAGES_LIMIT_PERCENT / 100) - 1)

        # get first page results
        results = self.get_results().to_dict()
        if results and "vanity_urls" in results:
            urls.extend(results["vanity_urls"])

        for page in range(pagination_limit):
            try:
                # click next page button
                wait = WebDriverWait(self.driver, self.timeout)

                next_button = wait.until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, self.PAGINATION_NEXT_SELECTOR)))
                next_button.click()
                self.load_search_page()
            except Exception as e:
                # Check if we got the 'you are a power searcher.' page
                try:
                    self.driver.find_element_by_css_selector(
                        self.SEARCH_LIMIT_REACHED_SELECTOR)
                    print('Search limit on LinkedIn reached')
                    # stop search loop
                    break
                except:
                    pass

                print(e)
                continue

            print('Currently at Page {}'.format(page + 2))

            results = self.get_results().to_dict()
            # append to list
            if results and "vanity_urls" in results:
                urls.extend(results["vanity_urls"])

            # break on reaching max profile count
            if len(urls) >= self.MAX_PROFILES_COUNT:
                break

        # filter out duplicates(if any)
        return list(set(urls))

    def get_result_stats(self):
        try:
            search = self.driver.find_element_by_css_selector(
                self.MAIN_SELECTOR).get_attribute("outerHTML")
            return Pages(search)
        except:
            print("Could not find search wrapper html.")
        return None

    def get_results(self):
        try:
            search = self.driver.find_element_by_css_selector(
                self.MAIN_SELECTOR).get_attribute("outerHTML")
            return Search(search)
        except:
            print("Could not find search wrapper html.")
        return None

    def scroll_to_bottom(self):
        """
        Scroll to the bottom of the page
        """
        current_height = 0
        while True:
            # Scroll down to bottom
            new_height = self.driver.execute_script(
                "return Math.min({}, document.body.scrollHeight)".format(current_height + self.scroll_increment))
            if (new_height == current_height):
                break
            self.driver.execute_script(
                "window.scrollTo(0, Math.min({}, document.body.scrollHeight));".format(new_height))
            current_height = new_height
            # Wait to load page
            time.sleep(self.scroll_pause)
