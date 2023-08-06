# -*- coding: utf-8 -*-
'''
Testdata cotaining stylistic (eg. Gothic, Romanesque) and cultural periods 
(eg. La Tène)

.. versionadded:: 0.2.0
'''

from __future__ import unicode_literals

from skosprovider.providers import DictionaryProvider
from skosprovider.uri import UriPatternGenerator
from .stijl_data import STIJLDATA

styles_and_cultures = DictionaryProvider(
    {'id': 'STYLE'},
    STIJLDATA,
    uri_generator = UriPatternGenerator('https://id.erfgoed.net/thesauri/stijlen_en_culturen/%s')
)
