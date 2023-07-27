#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : Enter Project Name in Workspace Settings                                            #
# Version    : 0.1.19                                                                              #
# Python     : 3.10.11                                                                             #
# Filename   : /tests/test_infrastructure/test_persistence/test_mysql.py                           #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john.james.ai.studio@gmail.com                                                      #
# URL        : Enter URL in Workspace Settings                                                     #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday March 31st 2023 09:09:07 am                                                  #
# Modified   : Wednesday July 26th 2023 09:59:29 am                                                #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2023 John James                                                                 #
# ================================================================================================ #
import inspect
from datetime import datetime
import pytest
import logging

import pandas as pd
from sqlalchemy.exc import SQLAlchemyError

from appstore.infrastructure.database.mysql import MySQLDatabase


# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)
# ------------------------------------------------------------------------------------------------ #
double_line = f"\n{100 * '='}"
single_line = f"\n{100 * '-'}"
# ------------------------------------------------------------------------------------------------ #


@pytest.mark.db
class TestMySQLDatabase:  # pragma: no cover
    # ============================================================================================ #
    def test_setup(self, caplog):
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
        query = "DROP TABLE IF EXISTS iris;"
        db = MySQLDatabase(name="test")
        with db as connection:
            connection.execute(query=query)
        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            "\n\tCompleted {} {} in {} seconds at {} on {}".format(
                self.__class__.__name__,
                inspect.stack()[0][3],
                duration,
                end.strftime("%I:%M:%S %p"),
                end.strftime("%m/%d/%Y"),
            )
        )
        logger.info(single_line)

    # ============================================================================================ #
    def test_insert_without_commit(self, dataframe, caplog):
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
        db = MySQLDatabase(name="test")
        db.connect()
        _ = db.insert(data=dataframe, tablename="iris")
        db.rollback()  # Rollback has no effect when not in transaction.

        query = "SELECT * FROM iris;"
        df = db.query(query=query)
        db.close()
        assert df.shape[0] != 0
        self.test_setup(caplog=caplog)
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

    # ============================================================================================ #
    def test_insert_in_context(self, dataframe, caplog):
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
        db = MySQLDatabase(name="test")
        with db as connection:
            rows_inserted = connection.insert(data=dataframe, tablename="iris")
        assert isinstance(rows_inserted, int)
        assert rows_inserted == dataframe.shape[0]
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

    # ============================================================================================ #
    def test_properties(self, caplog):
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
        db = MySQLDatabase(name="test")
        db.name == "test"
        assert db.is_connected is True
        db.close()
        assert db.is_connected is False
        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            "\n\tCompleted {} {} in {} seconds at {} on {}".format(
                self.__class__.__name__,
                inspect.stack()[0][3],
                duration,
                end.strftime("%I:%M:%S %p"),
                end.strftime("%m/%d/%Y"),
            )
        )
        logger.info(single_line)

    # ============================================================================================ #
    def test_query(self, caplog):
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
        QUERY = "SELECT * FROM iris WHERE iris.Name = :name;"
        PARAMS = {"name": "Iris-virginica"}

        db = MySQLDatabase(name="test")
        with db as connection:
            df = connection.query(query=QUERY, params=PARAMS)
        assert isinstance(df, pd.DataFrame)
        logger.debug(df)

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            "\n\tCompleted {} {} in {} seconds at {} on {}".format(
                self.__class__.__name__,
                inspect.stack()[0][3],
                duration,
                end.strftime("%I:%M:%S %p"),
                end.strftime("%m/%d/%Y"),
            )
        )
        logger.info(single_line)

    # ============================================================================================ #
    def test_update(self, dataframe, caplog):
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
        query = "UPDATE iris SET PetalWidth = :pw WHERE iris.Name = :name;"
        params = {"pw": 99, "name": "Iris-setosa"}

        db = MySQLDatabase(name="test")
        with db as database:
            rows_updated = database.update(query=query, params=params)
        logger.debug(f"\n\nRows Updated{rows_updated}")
        assert isinstance(rows_updated, int)
        assert rows_updated == len(dataframe[dataframe["Name"] == "Iris-setosa"])
        query = "SELECT * FROM iris WHERE iris.Name = :name;"
        params = {"name": "Iris-setosa"}
        db.connect()
        df = db.query(query=query, params=params)
        db.close()
        logger.debug(f"\n\n{df}")
        self.test_query(caplog=caplog)
        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            "\n\tCompleted {} {} in {} seconds at {} on {}".format(
                self.__class__.__name__,
                inspect.stack()[0][3],
                duration,
                end.strftime("%I:%M:%S %p"),
                end.strftime("%m/%d/%Y"),
            )
        )
        logger.info(single_line)

    # ============================================================================================ #
    def test_delete(self, dataframe, caplog):
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
        query = "DELETE FROM iris WHERE Name = :name;"
        params = {"name": "Iris-virginica"}

        db = MySQLDatabase(name="test")
        with db as database:
            rows_deleted = database.delete(query=query, params=params)
        logger.debug(f"\n\nRows Deleted{rows_deleted}")
        assert isinstance(rows_deleted, int)
        assert rows_deleted == len(dataframe[dataframe["Name"] == "Iris-virginica"])

        query = "SELECT EXISTS(SELECT 1 FROM iris WHERE Name = :name LIMIT 1);"
        db.connect()
        exists = db.exists(query=query, params=params)
        assert exists is True
        db.close()
        logger.debug(f"\n\n{exists}\n{type(exists)}")
        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            "\n\tCompleted {} {} in {} seconds at {} on {}".format(
                self.__class__.__name__,
                inspect.stack()[0][3],
                duration,
                end.strftime("%I:%M:%S %p"),
                end.strftime("%m/%d/%Y"),
            )
        )
        logger.info(single_line)

    # ============================================================================================ #
    def test_transaction_insert(self, dataframe, caplog):
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
        query = "SELECT * FROM iris;"
        # Confirm beginning state, not in transaction
        db = MySQLDatabase(name="test")
        db.connect()
        result = db.in_transaction()
        assert result is False

        # Get current number of rows
        df = db.query(query=query)
        starting_rows = df.shape[0]

        # Start transaction and confirm state
        # db.begin() Apparently execute causes a transaction to begin automatically.
        result = db.in_transaction()
        assert result is True

        # Insert rows and rollback
        db.insert(data=dataframe, tablename="iris")
        db.rollback()

        # Confirm rollback
        df = db.query(query=query)
        assert df.shape[0] == starting_rows

        # Try again without rollback
        db.insert(data=dataframe, tablename="iris")

        # Get current number of rows
        df = db.query(query=query)

        # Confirm new rows added.
        assert df.shape[0] > starting_rows
        db.close()

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            "\n\tCompleted {} {} in {} seconds at {} on {}".format(
                self.__class__.__name__,
                inspect.stack()[0][3],
                duration,
                end.strftime("%I:%M:%S %p"),
                end.strftime("%m/%d/%Y"),
            )
        )
        logger.info(single_line)

    # ============================================================================================ #
    def test_transaction_update(self, dataframe, caplog):
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
        # Query to get petalwidth
        select_query = "SELECT iris.PetalWidth FROM iris WHERE iris.Name = :name AND iris.PetalLength = :pl AND iris.SepalWidth = :sw AND iris.SepalLength = :sl;"
        select_params = {"name": "Iris-setosa", "pl": 1.4, "sw": 3.5, "sl": 5.1}

        # Confirm beginning state, not in transaction
        db = MySQLDatabase(name="test")
        db.connect()
        result = db.in_transaction()
        assert result is False

        # Get current PetalWidth for the row. Should be 99.0
        pw = db.query(query=select_query, params=select_params)
        logger.debug(f"\n\nPetalWidth = {pw}")
        assert pw["PetalWidth"].values[0] == 99.0

        # Confirm in transaction as consequency of prior query
        result = db.in_transaction()
        assert result is True

        # Update rows
        # Query to update
        query = "UPDATE iris SET PetalWidth = :pw WHERE iris.Name = :name;"
        params = {"pw": 55.0, "name": "Iris-setosa"}
        db.update(query=query, params=params)
        db.rollback()

        # Confirm rollback
        pw = db.query(query=select_query, params=select_params)
        logger.debug(f"\n\nPetalWidth = {pw}")
        assert pw["PetalWidth"].values[0] == 99.0

        # Try again without rollback
        db.update(query=query, params=params)

        # Confirm rows updated
        pw = db.query(query=select_query, params=select_params)
        logger.debug(f"\n\nPetalWidth = {pw}")
        assert pw["PetalWidth"].values[0] == 55.0
        db.close()

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            "\n\tCompleted {} {} in {} seconds at {} on {}".format(
                self.__class__.__name__,
                inspect.stack()[0][3],
                duration,
                end.strftime("%I:%M:%S %p"),
                end.strftime("%m/%d/%Y"),
            )
        )
        logger.info(single_line)

    # ============================================================================================ #
    def test_transaction_insert_AUTOCOMMIT(self, dataframe, caplog):
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
        query = "SELECT * FROM iris;"
        # Confirm beginning state, not in transaction
        db = MySQLDatabase(name="test")
        db.connect(autocommit=True)
        result = db.in_transaction()
        assert result is False

        # Get current number of rows
        df = db.query(query=query)
        starting_rows = df.shape[0]

        # Start transaction and confirm state
        # db.begin() Apparently execute causes a transaction to begin automatically.
        result = db.in_transaction()
        assert result is True

        # Insert rows and rollback
        db.insert(data=dataframe, tablename="iris")
        db.rollback()

        # Confirm rollback had no effect
        df = db.query(query=query)
        assert df.shape[0] > starting_rows

        # close
        db.close()

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            "\n\tCompleted {} {} in {} seconds at {} on {}".format(
                self.__class__.__name__,
                inspect.stack()[0][3],
                duration,
                end.strftime("%I:%M:%S %p"),
                end.strftime("%m/%d/%Y"),
            )
        )
        logger.info(single_line)

    # ============================================================================================ #
    def test_transaction_update_AUTOCOMMIT(self, dataframe, caplog):
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
        # Query to get petalwidth
        select_query = "SELECT iris.PetalWidth FROM iris WHERE iris.Name = :name AND iris.PetalLength = :pl AND iris.SepalWidth = :sw AND iris.SepalLength = :sl;"

        select_params = {"name": "Iris-setosa", "pl": 1.4, "sw": 3.5, "sl": 5.1}

        # Confirm beginning state, not in transaction
        db = MySQLDatabase(name="test")
        db.connect(autocommit=True)
        result = db.in_transaction()
        assert result is False

        # Get current PetalWidth for the row. Should be 99.0
        pw = db.query(query=select_query, params=select_params)
        logger.debug(f"\n\nPetalWidth = {pw}")
        assert pw["PetalWidth"].values[0] == 99.0

        # Confirm in transaction as consequency of prior query
        result = db.in_transaction()
        assert result is True

        # Update rows
        # Query to update
        query = "UPDATE iris SET PetalWidth = :pw WHERE iris.Name = :name;"
        params = {"pw": 55.0, "name": "Iris-setosa"}
        db.update(query=query, params=params)
        db.rollback()

        # Confirm rollback had no effect
        pw = db.query(query=select_query, params=select_params)
        logger.debug(f"\n\nPetalWidth = {pw}")
        assert pw["PetalWidth"].values[0] == 55.0

        db.close()
        db.dispose()

        with pytest.raises(SQLAlchemyError):
            db.query(query=select_query, params=select_params)

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            "\n\tCompleted {} {} in {} seconds at {} on {}".format(
                self.__class__.__name__,
                inspect.stack()[0][3],
                duration,
                end.strftime("%I:%M:%S %p"),
                end.strftime("%m/%d/%Y"),
            )
        )
        logger.info(single_line)
