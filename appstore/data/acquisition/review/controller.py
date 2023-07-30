#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Controller    : AI-Enabled Voice of the Mobile Technology Customer                                  #
# Version    : 0.1.19                                                                              #
# Python     : 3.10.11                                                                             #
# Filename   : /appstore/data/acquisition/review/controller.py                                     #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john.james.ai.studio@gmail.com                                                      #
# URL        : https://github.com/john-james-ai/appstore                                           #
# ------------------------------------------------------------------------------------------------ #
# Created    : Thursday April 20th 2023 05:33:57 am                                                #
# Modified   : Sunday July 30th 2023 03:42:06 am                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2023 John James                                                                 #
# ================================================================================================ #
"""AppStore Scraper Controller Module"""
import sys
import logging
import datetime

import numpy as np
import pandas as pd
from dependency_injector.wiring import inject, Provide


from appstore.data.acquisition import AppStoreCategories
from appstore.data.acquisition.review.scraper import ReviewScraper
from appstore.data.storage.uow import UoW
from appstore.data.acquisition.base import Controller
from appstore.container import AppstoreContainer


# ------------------------------------------------------------------------------------------------ #
#                            APPSTORE REVIEW CONTROLLER                                            #
# ------------------------------------------------------------------------------------------------ #
class ReviewController(Controller):
    """Controls the App Store Review scraping process

    Args:
        scraper (ReviewScraper): A scraper object that returns data from the target urls.
        uow (UoW): Unit of Work containing the repositories.
        min_ratings (int): Since we want apps with a minimum number of reviews, and we don't
            have the number of reviews per app, we are using the number of ratings as
            a proxy for the number of reviews. The default is 20
        max_pages (int): Puts a maximum on the total number of pages to request.
        max_results_per_page (int): This is the limit of results to return on each request.
        verbose (int): An indicator of the level of progress reporting verbosity. Progress
            will be printed to stdout for each 'verbose' number of apps processed.

    """

    @inject
    def __init__(
        self,
        scraper: type[ReviewScraper] = ReviewScraper,
        uow: UoW = Provide[AppstoreContainer.data.uow],
        min_ratings: int = 20,
        max_pages: int = sys.maxsize,
        max_results_per_page: int = 400,
        verbose: int = 10,
    ) -> None:
        super().__init__()
        self._scraper = scraper
        self._uow = uow
        self._min_ratings = min_ratings
        self._max_pages = max_pages
        self._max_results_per_page = max_results_per_page
        self._verbose = verbose

        # State managers
        self._current_category_id = None
        self._current_category = None
        self._current_app_id = None
        self._current_app_name = None

        # Stats
        self._project_stats = {
            "categories": 0,
            "apps": 0,
            "reviews": 0,
            "pages": 0,
            "started": None,
            "ended": None,
            "duration": None,
        }
        self._category_stats = {
            "category_id": None,
            "category": None,
            "apps": 0,
            "apps_with_min_ratings": 0,
            "apps_with_reviews": 0,
            "apps_to_process": 0,
            "app_count": 0,
            "reviews": 0,
            "reviews_per_app": [],
            "min_reviews_per_app": 0,
            "max_reviews_per_app": 0,
            "ave_reviews_per_app": 0,
            "pages": 0,
            "started": None,
            "ended": None,
            "duration": None,
        }
        self._app_stats = {"id": None, "name": None, "reviews": 0}

        self._logger = logging.getLogger(f"{self.__class__.__name__}")

    def summarize(self) -> pd.DataFrame:
        """Returns a DataFrame summarizing the data extracted"""
        return self._uow.review_repo.summarize()

    def scrape(self) -> None:
        """Entry point for scraping operation"""
        if not super().is_locked():
            self._scrape()
        else:
            msg = f"Running {self.__class__.__name__} is not authorized at this time."
            self._logger.info(msg)

    def _scrape(self) -> None:
        """Entry point for scraping operation"""

        self._start_project(category_ids=category_ids)

        for category_id in category_ids:
            apps = self._start_category(category_id=category_id)

            for _, row in apps.iterrows():
                self._start_app(row=row)

                for scraper in self._scraper(
                    app_id=row["id"],
                    app_name=row["name"],
                    category_id=row["category_id"],
                    category=row["category"],
                    max_pages=self._max_pages,
                    max_results_per_page=self._max_results_per_page,
                ):
                    self._start_page()
                    self._save_page(scraper.result)
                    self._end_page(scraper.result)

                self._end_app()

            self._end_category()

        self._end_project()
        self._teardown()

    def start(self) -> None:
        jobs = self._uow.job_repo.get_by_controller(
            controller=self.__class__.__name__, completed=False
        )
        msg = f"\n{self.__class__.__name__} started with {len(jobs)} jobs to complete"
        self._logger.info(msg)

    def end(self) -> None:
        msg = f"\n{self.__class__.__name__} has completed."
        self._logger.info(msg)
        self._logger.info(f"\nJob Status:\n{self._uow.job_repo.getall()}")
        self._logger.info(f"\nRepo Summary:\n{self._uow.review_repo.summary}")

    def _end_project(self) -> None:
        self._project_stats["ended"] = datetime.datetime.now()
        self._project_stats["duration"] = str(
            datetime.timedelta(
                seconds=(
                    self._project_stats["ended"] - self._project_stats["started"]
                ).total_seconds()
            )
        )
        self._announce_project_end()

    def _announce_project_end(self) -> None:
        width = 24
        msg = f"\n\n{'Controller Summary'}\n"
        msg += f"\t{'Categories:'.rjust(width, ' ')} | {self._project_stats['categories']}\n"
        msg += f"\t{'Apps:'.rjust(width, ' ')} | {self._project_stats['apps']}\n"
        msg += f"\t{'Reviews:'.rjust(width, ' ')} | {self._project_stats['reviews']}\n"
        msg += f"\t{'Scrapers:'.rjust(width, ' ')} | {self._project_stats['pages']}\n"
        msg += f"\t{'Started:'.rjust(width, ' ')} | {self._project_stats['started']}\n"
        msg += f"\t{'Ended:'.rjust(width, ' ')} | {self._project_stats['ended']}\n"
        msg += f"\t{'Duration:'.rjust(width, ' ')} | {self._project_stats['duration']}\n"
        self._logger.info(msg)

    def _teardown(self) -> None:
        self._uow.review_repo.export()

    def _start_category(self, category_id: int) -> pd.DataFrame:
        """Obtains apps for the category, removing any apps for which reviews exist."""

        self._current_category_id = category_id
        self._current_category = AppStoreCategories.NAMES[category_id]

        self._category_stats["category_id"] = self._current_category_id
        self._category_stats["category"] = self._current_category
        self._category_stats["reviews_per_app"] = []
        self._category_stats["app_count"] = 0
        self._category_stats["reviews"] = 0
        self._category_stats["min_reviews_per_app"] = 0
        self._category_stats["max_reviews_per_app"] = 0
        self._category_stats["ave_reviews_per_app"] = 0
        self._category_stats["pages"] = 0
        self._category_stats["started"] = datetime.datetime.now()

        # Obtain all apps for the category from the repository.
        apps = self._uow.appdata_repo.get_by_category(category_id=category_id)
        self._category_stats["apps"] = len(apps)

        # Filter the apps that have greater than 'min_ratings'
        apps = apps.loc[apps["ratings"] > self._min_ratings]
        self._category_stats["apps_with_min_ratings"] = len(apps)

        # Obtain apps for which we've already processed the reviews.
        try:
            reviews = self._uow.review_repo.get_by_category(category_id=category_id)
            apps_with_reviews = reviews["app_id"].unique()
            self._category_stats["apps_with_reviews"] = len(apps_with_reviews)
        except Exception:
            self._category_stats["apps_with_reviews"] = 0

        # Remove apps for which reviews exist from the list of apps to process.
        if self._category_stats["apps_with_reviews"] > 0:
            apps = apps.loc[~apps["id"].isin(apps_with_reviews)]
        self._category_stats["apps_to_process"] = len(apps)

        # Announce Category
        self._announce_category_start()
        return apps

    def _announce_category_start(self) -> None:
        width = 32
        msg = f"\n\nCategory: {self._current_category_id}-{self._current_category} Started at {self._category_stats['started'].strftime('%m/%d/%Y, %H:%M:%S')}\n"
        msg += f"\t{'Apps in Category:'.rjust(width, ' ')} | {self._category_stats['apps']}\n"
        msg += f"\t{'Apps with Min Ratings:'.rjust(width, ' ')} | {self._category_stats['apps_with_min_ratings']}\n"
        msg += f"\t{'Apps with Reviews:'.rjust(width, ' ')} | {self._category_stats['apps_with_reviews']}\n"
        msg += f"\t{'Apps to Process:'.rjust(width, ' ')} | {self._category_stats['apps_to_process']}\n"
        self._logger.info(msg)

    def _end_category(self) -> None:
        self._category_stats["min_reviews_per_app"] = np.min(
            self._category_stats["reviews_per_app"]
        )
        self._category_stats["max_reviews_per_app"] = np.max(
            self._category_stats["reviews_per_app"]
        )
        self._category_stats["ave_reviews_per_app"] = np.mean(
            self._category_stats["reviews_per_app"]
        )
        self._category_stats["ended"] = datetime.datetime.now()
        self._category_stats["duration"] = str(
            datetime.timedelta(
                seconds=(
                    self._category_stats["ended"] - self._category_stats["started"]
                ).total_seconds()
            )
        )
        self._announce_category_end()

    def _announce_category_end(self) -> None:
        width = 24
        msg = f"\n\nCategory: {self._current_category_id}-{self._current_category}\n"
        msg += f"\t{'App Count:'.rjust(width, ' ')} | {self._category_stats['app_count']}\n"
        msg += f"\t{'Reviews:'.rjust(width, ' ')} | {self._category_stats['reviews']}\n"
        msg += f"\t{'Min Reviews per App:'.rjust(width, ' ')} | {self._category_stats['min_reviews_per_app']}\n"
        msg += f"\t{'Max Reviews per App:'.rjust(width, ' ')} | {self._category_stats['max_reviews_per_app']}\n"
        msg += f"\t{'Ave Reviews per App:'.rjust(width, ' ')} | {self._category_stats['ave_reviews_per_app']}\n"
        self._logger.info(msg)

    def _start_app(self, row: pd.Series) -> None:
        self._current_app_id = row["id"]
        self._current_app_name = row["name"]

        self._category_stats["app_count"] += 1
        self._project_stats["apps"] += 1
        self._app_stats["id"] = self._current_app_id
        self._app_stats["name"] = self._current_app_name
        self._app_stats["reviews"] = 0

    def _end_app(self) -> None:
        self._category_stats["reviews_per_app"].append(self._app_stats["reviews"])
        if self._category_stats["app_count"] % self._verbose == 0:
            self._announce_batch()

    def _start_page(self) -> None:
        self._project_stats["pages"] += 1
        self._category_stats["pages"] += 1

    def _save_page(self, result: pd.DataFrame) -> None:
        self._uow.review_repo.add(data=result)
        self._uow.save()

    def _end_page(self, result: pd.DataFrame) -> None:
        """Updates stats and announces progress."""
        self._project_stats["reviews"] += result.shape[0]
        self._project_stats["ended"] = datetime.datetime.now()
        duration = (self._project_stats["ended"] - self._project_stats["started"]).total_seconds()
        self._project_stats["reviews_per_second"] = round(
            self._project_stats["reviews"] / duration, 2
        )
        self._project_stats["duration"] = str(datetime.timedelta(seconds=(duration)))

        self._category_stats["reviews"] += result.shape[0]
        self._category_stats["ended"] = datetime.datetime.now()
        self._category_stats["duration"] = str(
            datetime.timedelta(
                seconds=(
                    self._category_stats["ended"] - self._category_stats["started"]
                ).total_seconds()
            )
        )

        self._app_stats["reviews"] += result.shape[0]

    def _announce_batch(self) -> None:
        msg = f"Category: {self._category_stats['category_id']}-{self._category_stats['category']}\
            \tApps: {self._category_stats['app_count']}\tReviews: {self._category_stats['reviews']}\
            \tElapsed Time: {self._category_stats['duration']}"
        self._logger.info(msg)
