from .ResultsObject import ResultsObject

from ..utils.scrape_util import *


class Search(ResultsObject):
    attributes = ['vanity_urls']

    @property
    def vanity_urls(self):
        container = first_or_default(self.soup, '.search-results')

        results = all_or_default(
            container, '.blended-srp-results-js ul .search-result__info')

        profiles = list(map(get_user_urls, results))
        # filter out invalid urls
        links = list(
            filter(lambda x: x != '#', profiles))

        return links
