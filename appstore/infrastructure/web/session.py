#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : Enter Project Name in Workspace Settings                                            #
# Version    : 0.1.19                                                                              #
# Python     : 3.10.11                                                                             #
# Filename   : /appstore/infrastructure/web/session.py                                             #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john.james.ai.studio@gmail.com                                                      #
# URL        : Enter URL in Workspace Settings                                                     #
# ------------------------------------------------------------------------------------------------ #
# Created    : Saturday April 8th 2023 03:15:52 am                                                 #
# Modified   : Tuesday July 25th 2023 01:04:44 pm                                                  #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2023 John James                                                                 #
# ================================================================================================ #
import os
from datetime import datetime
import logging
from dotenv import load_dotenv

import requests

from appstore.infrastructure.web.throttle import LatencyThrottle
from appstore.infrastructure.web.adapter import TimeoutHTTPAdapter
from appstore.infrastructure.web.headers import BrowserHeader

load_dotenv()


# ------------------------------------------------------------------------------------------------ #
class SessionHandler:
    """Encapsulates an HTTP Session with retry capability.

    Args:
        timeout (TimeoutHTTPAdapter): An HTTP Adapter for managing timeouts and retries at request level.
        session_retries (int): Number of sessions to retry if timeout retry maximum has been reached.
        delay (tuple): The lower and upper bound on time between requests.
    """

    def __init__(
        self,
        timeout: TimeoutHTTPAdapter,
        throttle: LatencyThrottle,
        headers: BrowserHeader,
        session_retries: int = 3,
    ) -> None:
        self._timeout = timeout
        self._throttle = throttle
        self._headers = iter(headers)

        self._session_retries = session_retries

        self._proxy = None  # The proxy used for the current request
        self._header = None  # The header used for the current request.

        self._sessions = 0
        self._session = None
        self._response = None
        self._status_code = None

        self._logger = logging.getLogger(f"{self.__class__.__name__}")

    @property
    def status_code(self) -> dict:
        """Returns status_code from the last request."""
        return self._status_code

    @property
    def header(self) -> dict:
        """Returns header from the last request."""
        return self._header

    @property
    def proxy(self) -> dict:
        """Returns proxy from the last request."""
        return self._proxy

    @property
    def sessions(self) -> dict:
        """Returns the number of sessions used during the last request."""
        return self._sessions + 1

    @property
    def response(self) -> requests.Response:
        """Returns the response"""
        return self._response

    def get(self, url: str, header: dict = None, params: dict = None):  # noqa: C901
        """Executes the http request and returns a Response object.

        Args:
            url (str): The base url for the http request
            header (dict): A dictionary containing header parameters.If None provided, standard rotating headers will be used.
            params (dict): The parameters to be added to the url

        """
        self._sessions = 0

        while self._sessions < self._session_retries:
            self._setup(header=header)

            try:
                self._response = self._session.get(
                    url=url,
                    headers=self._header,
                    params=params,
                    proxies=self._proxy,
                )
                self._teardown()
                self._throttle.delay(latency=self._latency, wait=True)
                return self

            except Exception as e:  # pragma: no cover
                self._sessions += 1
                msg = f"A {type(e)} exception occurred. \n{e}\nRetrying with session #{self._sessions}."
                self._logger.error(msg)
                self._status_code = 999

        self._logger.error("All retry and session limits have been reached. Exiting.")
        return self

    def _setup(self, header: dict = None) -> None:
        """Conducts pre-request initializations"""

        self._proxy = self._get_proxy()  # From rotating proxies
        self._header = header or next(self._headers)  # From rotating headers

        # Construct session object
        self._session = requests.Session()
        self._session.mount("https://", self._timeout)
        self._session.mount("http://", self._timeout)

        # Set / reset the response
        self._response = None

        # Capture the time to measure latency
        self._start = datetime.now()

    def _teardown(self) -> None:
        """Conducts post-request housekeeping"""
        self._end = datetime.now()
        self._latency = (self._end - self._start).total_seconds()
        self._status_code = int(self._response.status_code)
        self._logger.debug(
            f"\nRequest status code: {self._response.status_code}. Session: {self._sessions}"
        )

    def _get_proxy(self) -> dict:
        """Returns proxy servers"""
        username = os.getenv("WEBSHARE_USER")
        password = os.getenv("WEBSHARE_PWD")
        dns = os.getenv("WEBSHARE_DNS")
        port = os.getenv("WEBSHARE_PORT")

        return {
            "http": f"http://{username}:{password}@{dns}:{port}/",
            "https": f"http://{username}:{password}@{dns}:{port}/",
        }
