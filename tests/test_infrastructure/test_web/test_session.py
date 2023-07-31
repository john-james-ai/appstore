#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : Appstore Ratings & Reviews Analysis                                                 #
# Version    : 0.1.19                                                                              #
# Python     : 3.10.12                                                                             #
# Filename   : /tests/test_infrastructure/test_web/test_session.py                                 #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john.james.ai.studio@gmail.com                                                      #
# URL        : https://github.com/john-james-ai/appstore                                           #
# ------------------------------------------------------------------------------------------------ #
# Created    : Monday July 31st 2023 05:20:39 pm                                                   #
# Modified   : Monday July 31st 2023 06:10:12 pm                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2023 John James                                                                 #
# ================================================================================================ #
import inspect
from datetime import datetime
import pytest
import logging

import requests

from appstore.infrastructure.web.response import Response

# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)
# ------------------------------------------------------------------------------------------------ #
double_line = f"\n{100 * '='}"
single_line = f"\n{100 * '-'}"

URL = "https://itunes.apple.com/search?"
PARAMS = {
    "media": "software",
    "term": "health",
    "country": "us",
    "lang": "en-us",
    "explicit": "yes",
    "limit": 30,
    "offset": 0,
}


@pytest.mark.session
class TestSession:  # pragma: no cover
    # ============================================================================================ #
    def test_session(self, container, caplog):
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
        session = container.web.session()
        response = session.get(url=URL, params=PARAMS)
        assert isinstance(response, Response)
        assert isinstance(response.response, requests.Response)
        assert isinstance(response.status_code, int)
        assert isinstance(response.size, int)
        assert isinstance(response.latency, float)
        assert isinstance(response.throughput, float)
        assert response.status_code == 200
        logger.debug(response.__str__())

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
