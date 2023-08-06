# -*- coding: utf-8 -*-

import re

from bs4 import BeautifulSoup, NavigableString

from ..model import AmendementSummary, Amendement, AmendementSearchResult


def parse_dossier_legislatif_from_amendement_search_page(url, html_response):
    assert url == 'http://www2.assemblee-nationale.fr/recherche/amendements'

    soup = BeautifulSoup(html_response)

    dossiers = [li.text() for li in soup.find('ul', class_='chzn-results').find_all('li')]

    numero_regex = re.compile('\(Texte : (\d+)\)')
    dossiers_with_numero = [{'title': d, 'numero': numero_regex.match(d).group(1)} for d in dossiers]

    return {
        'url': url,
        'dossiers_legislatifs': dossiers_with_numero
    }