#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AI-Enabled Opportunity Discovery in Mobile Applications                             #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.10                                                                             #
# Filename   : /aimobile/data/scraper/appstore/entity/project.py                                   #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john.james.ai.studio@gmail.com                                                      #
# URL        : https://github.com/john-james-ai/aimobile                                           #
# ------------------------------------------------------------------------------------------------ #
# Created    : Wednesday April 5th 2023 10:46:15 am                                                #
# Modified   : Saturday April 8th 2023 12:01:14 am                                                 #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2023 John James                                                                 #
# ================================================================================================ #
"Project Module: Defines the unit of work for scraping operations."
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
import pprint

import pandas as pd

from aimobile.data.scraper.base import Entity


# ------------------------------------------------------------------------------------------------ #
@dataclass
class AppStoreProject(Entity):
    name: str
    description: str
    term: str
    page_limit: int = 200  # Number of items to return from a requests call
    max_pages: int = 20000  # Number of total pages or request calls to make
    app_count: int = 0  # The number of apps returned
    page_count: int = 0  # The number of pages returned
    country: str = "us"
    lang: str = "en_us"
    timeout: int = 30
    delay: tuple = 3
    sessions: int = 3
    started: datetime = ""
    ended: datetime = ""
    duration: int = 0
    state: str = "not_started"
    source: str = "appstore"
    id: int = None

    def __eq__(self, other: AppStoreProject) -> bool:
        return (
            self.name == other.name
            and self.description == other.description
            and self.term == other.term
            and self.page_limit == other.page_limit
            and self.max_pages == other.max_pages
            and self.app_count == other.app_count
            and self.page_count == other.page_count
            and self.country == other.country
            and self.lang == other.lang
            and self.timeout == other.timeout
            and self.delay == other.delay
            and self.sessions == other.sessions
            and self.state == other.state
            and self.source == other.source
            and self.id == other.id
        )

    def start(self, id: str, name: str, description: str) -> None:
        """Initialization"""
        self.app_count = 0
        self.page_count = 0
        self.started = datetime.now()

    def end(self) -> None:
        """Finalizes the project state"""
        self.ended = datetime.now()
        self.duration = (self.ended - self.started).total_seconds()
        self.state = "success" if self.state == "in-progress" else self.state

    def update(self, num_results: int) -> None:
        """Updates the Project with current app_count and page_count.

        The datetime variables are set and stored in the database on each
        scrape iteration, so that we know how far we have processed
        the data in the event an exception occurs.

        Args:
            num_results (int): The number of apps returned from the appstore.

        """
        self.app_count += num_results
        self.page_count += 1
        # Snapshot
        self.started = datetime.now() if isinstance(self.started, str) else self.started
        self.ended = datetime.now()
        self.duration = (self.ended - self.started).total_seconds()
        self.state = "in-progress" if self.state != "fail" else self.state

    @classmethod
    def from_df(cls, data: pd.DataFrame) -> AppStoreProject:
        return cls(
            id=int(data["id"]),
            name=data["name"],
            description=data["description"],
            term=data["term"],
            page_limit=int(data["page_limit"]),
            max_pages=int(data["max_pages"]),
            app_count=int(data["app_count"]),
            page_count=int(data["page_count"]),
            country=data["country"],
            lang=data["lang"],
            timeout=int(data["timeout"]),
            delay=int(data["delay"]),
            sessions=int(data["sessions"]),
            started=data["started"],
            ended=data["ended"],
            duration=int(data["duration"]),
            state=data["state"],
            source=data["source"],
        )

    def summary(self) -> None:
        """Prints a summary of the project"""
        summary = self.as_dict()
        pprint(summary)
