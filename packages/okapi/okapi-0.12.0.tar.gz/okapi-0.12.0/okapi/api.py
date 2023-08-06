# Copyright 2014 Red Beacon, Inc.  All Rights Reserved
#
# This code, and all derivative work, is the exclusive property of
# Red Beacon, Inc. and may not be used without Red Beacon, Inc.'s
# authorization.
#
# Author: Gobind Ball

"""
okapi.api
~~~~~~~~~
This module implements the Requests API while storing valuable information into mongodb.
"""

import datetime
import logging
import time
import urlparse

from pymongo import errors
from pymongo import MongoClient

logger = logging.getLogger(__name__)


class Api(object):
    DEFAULT_TIMEOUT = 5000
    DEFAULT_MONGO_URI = 'mongodb://localhost'

    def __init__(self, db, project_name, requests_lib):
        """Initialization of class api.

        __init__ requires the following parameters:
        db --  Mongo database object. Use the get_mongodb_client method to get a
        mongo client object. Then set the database name on it to create a
        database object.
        project_name -- name of the mongodb collection
        requests_lib -- library which should be used to make requests
        """
        self.db = db
        self.project_name = project_name
        self.requests_lib = requests_lib
        self.exceptions = requests_lib.exceptions

    def _save_request(self, method, url, status_code, content, start):
        if self.db is not None:

            date = datetime.datetime.utcnow()
            host = urlparse.urlparse(url)

            time_bucket = [
                date.strftime('%Y-%m-%dT%H:%M-minute'),
                date.strftime('%Y-%m-%dT%H-hour'),
                date.strftime('%Y-%m-%d-day'),
            ]

            data = {
                'content': content,
                'date': date,
                'host': host.hostname,
                'method': method,
                'response_time': time.time() - start,
                'status_code': status_code,
                'url': url,
                'time_bucket': time_bucket,
            }

            try:
                # Optimization in order to improve speed: losing resolution in time
                collection = self.db["{}_raw".format(self.project_name)]
                # the w parameter is making the insertion to db asynchronous
                collection.insert(data, w=0)
            except:
                logger.exception('Error writing to MongoDB')

    def request(self, method, url, **kwargs):
        """calls a method of request library while storing info about api call into mongo db"""
        content = ''
        status_code = None
        start = time.time()
        try:
            res = self.requests_lib.request(method, url, **kwargs)
            status_code = res.status_code
            if not res.ok:
                content = res.content
            self._save_request(method, url, status_code, content, start)
        except self.exceptions.ConnectionError:
            content = 'Connection error'
            self._save_request(method, url, status_code, content, start)
            raise
        except self.exceptions.HTTPError:
            content = 'HTTP error'
            self._save_request(method, url, status_code, content, start)
            raise
        except self.exceptions.Timeout:
            content = 'Timeout'
            self._save_request(method, url, status_code, content, start)
            raise

        return res

    def get(self, url, **kwargs):
        return self.request('GET', url, **kwargs)

    def delete(self, url, **kwargs):
        return self.request('DELETE', url, **kwargs)

    def post(self, url, **kwargs):
        return self.request('POST', url, **kwargs)

    def put(self, url, **kwargs):
        return self.request('PUT', url, **kwargs)


def get_mongodb_client(mongodb_uri=Api.DEFAULT_MONGO_URI,
                       connect_timeout_ms=Api.DEFAULT_TIMEOUT):
    """Returns a mongodb client

    This method should ideally be called only once. The value returned should
    then be passed to whichever method needs a db connection.

    See http://docs.mongodb.org/manual/reference/connection-string/ for
    more information about the mongodb_uri parameter.
    """
    client = None
    try:
        client = MongoClient(mongodb_uri, connectTimeoutMS=connect_timeout_ms)
    except (errors.ConnectionFailure, errors.InvalidURI) as e:
        logger.exception('Unable to connect to MongoDB at %s, error_code: %s',
                         mongodb_uri, e)
    except errors.ConfigurationError as e:
        logger.exception(
            'Auth failed when connnecting to MongoDB at %s, error_code: %s',
            mongodb_uri, e
        )
    return client
