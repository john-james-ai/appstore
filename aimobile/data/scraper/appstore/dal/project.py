#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AI-Enabled Opportunity Discovery in Mobile Applications                             #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.10                                                                             #
# Filename   : /aimobile/data/scraper/appstore/dal/project.py                                      #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john.james.ai.studio@gmail.com                                                      #
# URL        : https://github.com/john-james-ai/aimobile                                           #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday March 31st 2023 06:11:59 am                                                  #
# Modified   : Saturday April 8th 2023 12:11:30 am                                                 #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2023 John James                                                                 #
# ================================================================================================ #
import logging
from typing import Union

from itertools import count
import pandas as pd

from aimobile.data.scraper.base import Repo
from aimobile.data.scraper.appstore.database.sqlite import SQLiteDatabase
from aimobile.data.scraper.appstore.entity.project import AppStoreProject
from aimobile import exceptions


# ------------------------------------------------------------------------------------------------ #
class AppStoreProjectRepo(Repo):
    """Repository of scraping projects.

    Args:
        database (SQLiteDatabase): Appstore Database
    """

    __id_gen = count(1)

    def __init__(self, database: SQLiteDatabase) -> None:
        self._database = database
        self._logger = logging.getLogger(f"{self.__module__}.{self.__class__.__name__}")

    def get(self, id: int) -> AppStoreProject:
        """Retrieves a project by id.

        Args:
            id (str): Project id. Optional. If None, all projects are returned.

        Raises: ProjectNotFound if the project was not found.
        """
        query = "SELECT * FROM project WHERE project.id = :id;"
        params = {"id": id}

        df = self._database.query(query=query, params=params)
        if df.shape[0] == 0:
            raise exceptions.ProjectNotFound(id=id)
        else:
            return AppStoreProject.from_df(df.loc[0])

    def getall(self, as_df: bool = True) -> Union[dict, pd.DataFrame]:
        """Returns a dictionary or DataFrame of all projects in the repository

        Args:
            as_df (bool): If True, a pandas DataFrame is returned; otherwise, a dictionary
                where key is the entity id and value is the project, is returned.

        raises ProjectsNotFound if the repository is empty.
        """
        query = "SELECT * FROM project;"
        df = self._database.query(query=query)
        if df.shape[0] == 0:
            raise exceptions.ProjectsNotFound()
        elif as_df is True:
            return df
        else:
            return self._df_to_dict(df=df)

    def add(self, project: AppStoreProject) -> None:
        """Adds a project entity to the repository

        Args:
            data (AppStoreProject): A Project object.
        """
        project.id = next(AppStoreProjectRepo.__id_gen)
        df = project.as_df()
        self._database.insert(data=df, tablename="project")

    def update(self, project: AppStoreProject) -> None:
        """Updates a project in the repo

        Args:
            project (AppStoreProject): Project data

        """
        query = "UPDATE project SET name = :name, description = :description, term = :term, page_limit = :page_limit, max_pages = :max_pages, app_count = :app_count, page_count = :page_count, country = :country, lang = :lang, timeout = :timeout, delay = :delay, sessions = :sessions, started = :started, ended = :ended, duration = :duration, state = :state, source = :source WHERE project.id == :id;"

        params = {
            "name": project.name,
            "description": project.description,
            "term": project.term,
            "page_limit": project.page_limit,
            "max_pages": project.max_pages,
            "app_count": project.app_count,
            "page_count": project.page_count,
            "country": project.country,
            "lang": project.lang,
            "timeout": project.timeout,
            "delay": project.delay,
            "sessions": project.sessions,
            "started": project.started,
            "ended": project.ended,
            "duration": project.duration,
            "state": project.state,
            "source": project.source,
            "id": project.id,
        }
        rowcount = self._database.update(query=query, params=params)
        if rowcount == 0:
            raise exceptions.ProjectNotFound(project.id)

    def remove(self, id: int) -> None:
        """Removes a project from the repo.

        Args:
            id (int): Project identifier.
        """
        query = "DELETE FROM project WHERE project.id = :id;"
        params = {"id": id}
        rowcount = self._database.delete(query=query, params=params)

        if rowcount == 0:
            raise exceptions.ProjectNotFound(id)

    def _df_to_dict(self, df: pd.DataFrame) -> dict:
        """Converts a Dataframe to a dictionary of Projects."""
        d = {}
        for index, row in df.iterrows():
            id = row["id"]
            d[id] = AppStoreProject.from_df(row)
        return d
