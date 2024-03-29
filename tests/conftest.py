#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : Appstore Ratings & Reviews Analysis                                                 #
# Version    : 0.1.19                                                                              #
# Python     : 3.10.11                                                                             #
# Filename   : /tests/conftest.py                                                                  #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john.james.ai.studio@gmail.com                                                      #
# URL        : https://github.com/john-james-ai/appstore                                           #
# ------------------------------------------------------------------------------------------------ #
# Created    : Monday March 27th 2023 07:01:48 pm                                                  #
# Modified   : Sunday August 27th 2023 04:21:04 am                                                 #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2023 John James                                                                 #
# ================================================================================================ #
import os
import pytest
import random
import dotenv
import subprocess
from datetime import datetime

import pandas as pd

from appstore.data.acquisition.base import App
from appstore.infrastructure.file.io import IOService
from appstore.infrastructure.cloud.amazon import AWS
from appstore.infrastructure.web.headers import STOREFRONT
from appstore.data.acquisition.appdata.project import AppDataProject
from appstore.data.acquisition.review.request import ReviewRequest
from tests.data.rating.response import batch
from appstore.data.dataset.appdata import AppDataDataset
from appstore.data.dataset.rating import RatingDataset
from appstore.data.dataset.review import ReviewDataset
from appstore.utils.jbook import DocConverter
from appstore.container import AppstoreContainer

# ------------------------------------------------------------------------------------------------ #
collect_ignore = [""]

# ------------------------------------------------------------------------------------------------ #
RATINGS_FILEPATH = "tests/data/appstore_ratings.csv"
APP_IDS = ["297606951", "544007664", "951937596", "310633997", "422689480"]

APPS = [
    {"id": "297606951", "name": "amazon", "category_id": "6024", "category": "SHOPPING"},
    {"id": "544007664", "name": "youtube", "category_id": "6005", "category": "SOCIAL_NETWORKING"},
    {"id": "951937596", "name": "outlook", "category_id": "6000", "category": "BUSINESS"},
    {
        "id": "1288723196",
        "name": "Microsoft Edge: Web Browser",
        "category_id": "6002",
        "category": "UTILITIES",
    },
    {
        "id": "284815942",
        "name": "Google",
        "category_id": "6002",
        "category": "UTILITIES",
    },
]


# ------------------------------------------------------------------------------------------------ #
#                                        CLOUD                                                     #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="module", autouse=False)
def aws():
    """Returns an AWS object configured with default test bucket"""
    return AWS(default_bucket="development-ai")


# ------------------------------------------------------------------------------------------------ #
#                                        APPS                                                      #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="module", autouse=False)
def apps():
    apps = []
    for app in APPS:
        a = App(
            id=app["id"], name=app["name"], category_id=app["category_id"], category=app["category"]
        )
        apps.append(a)
    return apps


# ------------------------------------------------------------------------------------------------ #
#                                        URLS                                                      #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="module", autouse=False)
def urls():
    urls = []
    for id in APP_IDS:  # noqa
        url = f"https://itunes.apple.com/us/customer-reviews/id{id}?displayable-kind=11"
        urls.append(url)

    return urls


# ------------------------------------------------------------------------------------------------ #
#                                   RESET TEST DB                                                  #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="module", autouse=False)
def reset():
    RESET_SCRIPT = "tests/scripts/reset.sh"  # noqa
    subprocess.run(RESET_SCRIPT, shell=True)


# ------------------------------------------------------------------------------------------------ #
#                                  SET MODE TO TEST                                                #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="module", autouse=True)
def mode():
    dotenv_file = dotenv.find_dotenv()
    dotenv.load_dotenv(dotenv_file)
    prior_mode = os.environ["MODE"]
    os.environ["MODE"] = "test"
    dotenv.set_key(dotenv_file, "MODE", os.environ["MODE"])
    yield
    os.environ["MODE"] = prior_mode
    dotenv.set_key(dotenv_file, "MODE", os.environ["MODE"])


# ------------------------------------------------------------------------------------------------ #
#                              DEPENDENCY INJECTION                                                #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="function", autouse=True)
def container():
    container = AppstoreContainer()
    container.init_resources()
    container.wire(
        packages=["appstore.data.acquisition", "appstore.data.dataset", "appstore.data.storage"]
    )

    return container


# ------------------------------------------------------------------------------------------------ #
#                                 DATABASE FIXTURES                                                #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="module", autouse=False)
def dataframe():
    DATAFRAME_FILEPATH = "tests/data/test.csv"  # noqa
    df = IOService.read(DATAFRAME_FILEPATH)
    return df


# ------------------------------------------------------------------------------------------------ #
#                                        APPDATA                                                   #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="module", autouse=False)
def appdata():
    APPDATA_HEALTH_FILEPATH = "tests/data/appstore_health.csv"  # noqa
    df = IOService.read(APPDATA_HEALTH_FILEPATH)
    return df


# ================================================================================================ #
#                                    DATASET FIXTURES                                              #
# ================================================================================================ #
# ------------------------------------------------------------------------------------------------ #
#                                    APPDATA DATASET                                               #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="module", autouse=False)
def appdata_dataset():
    APPDATA_DATASET = "tests/data/dataset/appdata.pkl"
    df = IOService.read(APPDATA_DATASET)
    ds = AppDataDataset(df=df)
    return ds


# ------------------------------------------------------------------------------------------------ #
#                                  RATING DATASET                                                  #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="module", autouse=False)
def rating_dataset():
    RATING_DATASET = "tests/data/dataset/rating.pkl"
    df = IOService.read(RATING_DATASET)
    ds = RatingDataset(df=df)
    return ds


# ------------------------------------------------------------------------------------------------ #
#                                  REVIEW DATASET                                                  #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="module", autouse=False)
def review_dataset():
    REVIEW_DATASET = "tests/data/dataset/review.pkl"
    df = IOService.read(REVIEW_DATASET)
    ds = ReviewDataset(df=df)
    return ds


# ================================================================================================ #
#                                  REPOSITORY FIXTURES                                             #
# ================================================================================================ #
# ------------------------------------------------------------------------------------------------ #
#                                    APPDATA REPO                                                  #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="module", autouse=False)
def appdata_repo(container):
    repo = container.data.appdata_repo()
    df = pd.DataFrame()
    try:
        df = repo.getall()
        repo.delete_all()
    except Exception:
        pass  # noqa
    yield repo
    if len(df) > 0:
        repo.load(data=df)


@pytest.fixture(scope="function", autouse=False)
def appdata_repo_loaded(container):
    fp = "tests/data/repo/testdata/appdata.pkl"
    df = IOService.read(filepath=fp)
    repo = container.data.appdata_repo()
    repo.replace(data=df)
    return repo


# ------------------------------------------------------------------------------------------------ #
#                                    RATINGS REPO                                                  #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="module", autouse=False)
def rating_repo(container):
    repo = container.data.rating_repo()
    df = pd.DataFrame()
    try:
        df = repo.getall()
        repo.delete_all()
    except Exception:
        pass  # noqa
    yield repo
    if len(df) > 0:
        repo.load(data=df)


@pytest.fixture(scope="function", autouse=False)
def rating_repo_loaded(container):
    fp = "tests/data/repo/testdata/rating.pkl"
    df = IOService.read(filepath=fp)
    repo = container.data.rating_repo()
    repo.replace(data=df)
    return repo


# ------------------------------------------------------------------------------------------------ #
#                                    REVIEWS REPO                                                  #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="module", autouse=False)
def review_repo(container):
    repo = container.data.review_repo()
    df = pd.DataFrame()
    try:
        df = repo.getall()
        repo.delete_all()
    except Exception:
        pass  # noqa
    yield repo
    if len(df) > 0:
        repo.load(data=df)


@pytest.fixture(scope="function", autouse=False)
def review_repo_loaded(container):
    fp = "tests/data/repo/testdata/review.pkl"
    df = IOService.read(filepath=fp)
    repo = container.data.review_repo()
    repo.replace(data=df)
    return repo


# ------------------------------------------------------------------------------------------------ #
#                                      JOB REPO                                                    #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="module", autouse=False)
def job_repo(container):
    repo = container.data.job_repo()
    df = pd.DataFrame()
    try:
        df = repo.getall()
        repo.delete_all()
    except Exception:
        pass  # noqa
    yield repo
    if len(df) > 0:
        repo.load(data=df)


# ------------------------------------------------------------------------------------------------ #
#                                  REVIEW JOB RUN REPO                                             #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="module", autouse=False)
def review_jobrun_repo(container):
    repo = container.data.review_jobrun_repo()
    df = pd.DataFrame()
    try:
        df = repo.getall()
        repo.delete_all()
    except Exception:
        pass  # noqa
    yield repo
    if len(df) > 0:
        repo.load(data=df)


# ------------------------------------------------------------------------------------------------ #
#                                  RATING JOB RUN REPO                                             #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="module", autouse=False)
def rating_jobrun_repo(container):
    repo = container.data.rating_jobrun_repo()
    df = pd.DataFrame()
    try:
        df = repo.getall()
        repo.delete_all()
    except Exception:
        pass  # noqa
    yield repo
    if len(df) > 0:
        repo.load(data=df)


# ================================================================================================ #
#                                     DATA MANAGEMENT                                              #
# ================================================================================================ #
# ------------------------------------------------------------------------------------------------ #
#                                     STORAGE MANAGER                                              #
# ------------------------------------------------------------------------------------------------ #


# ------------------------------------------------------------------------------------------------ #
#                                      RATING BATCH                                                #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="module", autouse=False)
def rating_batch():
    return batch


# ------------------------------------------------------------------------------------------------ #
#                                         JOB DF                                                   #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="module", autouse=False)
def job_df():
    JOBS_FILEPATH = "tests/data/job/jobs.csv"  # noqa
    return IOService.read(JOBS_FILEPATH)


# ------------------------------------------------------------------------------------------------ #
#                                      REVIEW REQUEST                                              #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="module", autouse=False)
def review_request():
    app = APPS[4]
    return ReviewRequest(id=app["id"], category_id=app["category_id"])


# ------------------------------------------------------------------------------------------------ #
#                                     RATING RESPONSES                                             #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="module", autouse=False)
def rating_responses():
    return [
        None,
        [],
        {},
        {
            "ratingAverage": 4,
            "totalNumberOfReviews": 2,
            "ratingCount": 3,
            "ratingListCount": [
                1,
                2,
                3,
            ],
        },
        {
            "ratingAverage": 4,
            "totalNumberOfReviews": 2,
            "ratingCount": 3,
            "ratingCountList": [1, 2, 3, 4, 5],
        },
    ]


# ------------------------------------------------------------------------------------------------ #
#                                     REVIEW RESPONSES                                             #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="module", autouse=False)
def review_responses():
    return [
        None,
        [],
        {"status_code": 300},
        {"status_code": 500},
        {"status_code": 200},
    ]


# ------------------------------------------------------------------------------------------------ #
#                               APPDATA REPO RATINGS UOW                                           #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="module", autouse=False)
def uow(container):
    APPDATA_RATINGS_FILEPATH = "tests/data/appdata/rating/appdata.pkl"  # noqa
    df = IOService.read(APPDATA_RATINGS_FILEPATH)
    uow = container.data.uow()
    uow.rollback()
    uow.appdata_repo.replace(data=df)
    uow.save()
    return uow


# ------------------------------------------------------------------------------------------------ #
#                                        APPDATA PROJECT                                           #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="module", autouse=False)
def appdata_project():
    return AppDataProject(
        controller="AppDataController",
        term="weather",
        status="in_progress",
        page_size=200,
        pages=5,
        vpages=5,
        apps=1000,
        started=datetime.now(),
        updated=datetime.now(),
    )


# ------------------------------------------------------------------------------------------------ #
#                                      APPDATA PROJECT REPO                                        #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="module", autouse=False)
def appdata_project_repo(container, appdata_project):
    uow = container.data.uow()
    return uow.appdata_project_repo


# ------------------------------------------------------------------------------------------------ #
#                                        REVIEWS                                                   #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="module", autouse=False)
def review():
    REVIEWS_FILEPATH = "tests/data/reviews.csv"  # noqa
    df = IOService.read(REVIEWS_FILEPATH)
    return df


# ------------------------------------------------------------------------------------------------ #
#                                        RATINGS                                                   #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="module", autouse=False)
def rating():
    df = IOService.read(RATINGS_FILEPATH)
    return df


# ------------------------------------------------------------------------------------------------ #
#                                      WEB FIXTURES                                                #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="module", autouse=False)
def request_appdata():
    d = {
        "url": "https://itunes.apple.com/search",
        "params": {
            "media": "software",
            "term": "health",
            "country": "us",
            "lang": "en-us",
            "explicit": "yes",
            "limit": 5,
            "offset": 0,
        },
    }
    return d


@pytest.fixture(scope="function", autouse=False)
def request_ratings():
    # Note: Taking '/json' of the end of the url. Want actual response object returned.
    d = {
        "url": f"https://itunes.apple.com/{STOREFRONT['country']}/customer-reviews/id{random.choice(APP_IDS)}?displayable-kind=11",
        "headers": STOREFRONT["headers"],
    }
    return d


# ------------------------------------------------------------------------------------------------ #
#                                    DOC CONVERTER                                                 #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="module", autouse=False)
def converter(container):
    jbook_module = "tests/data/utils/jbooks/jbook"
    jbook_search_path = "tests/data/utils/jbooks/jbook/content/**/*.md"
    notebook_module = "tests/data/utils/jbooks/notebooks"
    notebook_search_path = "tests/data/utils/jbooks/notebooks/content/**/*.ipynb"
    return DocConverter(
        jbook_module=jbook_module,
        jbook_search_path=jbook_search_path,
        notebook_module=notebook_module,
        notebook_search_path=notebook_search_path,
    )
