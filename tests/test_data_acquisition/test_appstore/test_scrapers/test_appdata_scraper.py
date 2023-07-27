#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : Enter Project Name in Workspace Settings                                            #
# Version    : 0.1.19                                                                              #
# Python     : 3.10.11                                                                             #
# Filename   : /tests/test_data_acquisition/test_appstore/test_scrapers/test_appdata_scraper.py    #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john.james.ai.studio@gmail.com                                                      #
# URL        : Enter URL in Workspace Settings                                                     #
# ------------------------------------------------------------------------------------------------ #
# Created    : Saturday April 22nd 2023 10:39:34 am                                                #
# Modified   : Tuesday July 25th 2023 01:04:29 pm                                                  #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2023 John James                                                                 #
# ================================================================================================ #
import inspect
from datetime import datetime
import pytest
import logging

import pandas as pd
import numpy as np

from appstore.data.acquisition.appdata.scraper import AppDataScraper


# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)
# ------------------------------------------------------------------------------------------------ #
double_line = f"\n{100 * '='}"
single_line = f"\n{100 * '-'}"
# ------------------------------------------------------------------------------------------------ #


# ------------------------------------------------------------------------------------------------ #
@pytest.mark.scraper
@pytest.mark.appdata_scraper
class TestAppDataScraper:  # pragma: no cover
    # ============================================================================================ #
    def test_scraper(self, container, caplog):
        start = datetime.now()
        logger.info(
            "\n\nStarted {} {} at {} on {}".format(
                self.__class__.__name__,
                inspect.stack()[0][3],
                start.strftime("%I:%M:%S %p"),
                start.strftime("%m/%d/%Y"),
            )
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        TERM = "health"
        MAX_PAGES = 2
        LIMIT = 5
        a1 = pd.DataFrame()
        scraper = AppDataScraper(term=TERM, limit=LIMIT, max_pages=MAX_PAGES)
        for i, scrape in enumerate(scraper, start=1):
            result = scrape.content
            pd.concat([a1, result], axis=0)
            assert isinstance(result, pd.DataFrame)
            assert result.shape[0] == LIMIT
            assert isinstance(result["id"][0], np.int64)
            assert isinstance(result["name"][0], str)
            assert isinstance(result["description"][0], str)
            assert isinstance(result["category_id"][0], np.int64)
            assert isinstance(result["category"][0], str)
            assert isinstance(result["price"][0], float)
            assert isinstance(result["developer_id"][0], np.int64)
            assert isinstance(result["developer"][0], str)
            assert isinstance(result["rating"][0], float)
            assert isinstance(result["ratings"][0], np.int64)
            assert isinstance(result["released"][0], datetime)
            assert isinstance(result["source"][0], str)
            assert scrape.pages == i
            logger.debug(f"\n\nThe {i}th page returned {scrape.results} results.")
            logger.debug(f"\nResult:\n{scrape.content}\n")

        # ---------------------------------------------------------------------------------------- #
        TERM = "health"
        MAX_PAGES = 1
        LIMIT = 10
        a2 = pd.DataFrame()
        scraper = AppDataScraper(term=TERM, limit=LIMIT, max_pages=MAX_PAGES)
        for i, scrape in enumerate(scraper, start=1):
            result = scrape.content
            pd.concat([a2, result], axis=0)
            assert isinstance(result, pd.DataFrame)
            assert result.shape[0] == LIMIT
            assert isinstance(result["id"][0], np.int64)
            assert isinstance(result["name"][0], str)
            assert isinstance(result["description"][0], str)
            assert isinstance(result["category_id"][0], np.int64)
            assert isinstance(result["category"][0], str)
            assert isinstance(result["price"][0], float)
            assert isinstance(result["developer_id"][0], np.int64)
            assert isinstance(result["developer"][0], str)
            assert isinstance(result["rating"][0], float)
            assert isinstance(result["ratings"][0], np.int64)
            assert isinstance(result["released"][0], datetime)
            assert isinstance(result["source"][0], str)
            assert scrape.pages == i
            logger.debug(f"\n\nThe {i}th page returned {scrape.results} results.")
            logger.debug(f"\nResult:\n{scrape.content}\n")

        assert a1.equals(a2)

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            "\nCompleted {} {} in {} seconds at {} on {}".format(
                self.__class__.__name__,
                inspect.stack()[0][3],
                duration,
                end.strftime("%I:%M:%S %p"),
                end.strftime("%m/%d/%Y"),
            )
        )
        logger.info(single_line)
