from .ResultsObject import ResultsObject

from ..utils.scrape_util import *


class Pages(ResultsObject):
    attributes = ['pages']

    @property
    def pages(self):
        pagination = {}

        total_results_text = text_or_default(
            self.soup, 'h3.search-results__total', '0')
        total_results = int(total_results_text.replace(
            'About', '').replace('results', '').replace(',', '').strip())
        total_pages = round(total_results / 10)
        pagination['total_pages'] = total_pages
        pagination['total_results'] = total_results
        pagination['max_accessible_pages'] = min(100, total_pages)

        return pagination
