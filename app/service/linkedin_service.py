from app.main import ProfileScraper, SearchScraper
from app.utils.fs import log_to_file


def scrape_user(url):
    """
    Run scraper to scrape a user
    Returns None / User data
    """
    with ProfileScraper() as scraper:
        profile = scraper.scrape(user=url)
        if not profile:
            return None

        scraped = profile.to_dict()
        if "personal_info" in scraped:
            personal_info = scraped["personal_info"]
            if not "url" in personal_info:
                return None

        # write to local storage
        log_to_file(scraped)

        return scraped

    return None


def scrape_search_results(keywords=[]):
    """
    Run scraper to search with keywords & scrape search results
    Returns None / Search data
    """
    with SearchScraper() as scraper:
        scraped = scraper.search(keywords)

        return scraped

    return None
