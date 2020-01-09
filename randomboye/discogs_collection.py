from random import randint
import json
import discogs_client
import os

import logging
from logging.config import dictConfig
from logging_config import LOGGING_CONFIG

dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
FUNCTION_CALL_MSG = 'function_call'


class DiscogsCollection():
    def __init__(self, token, collection_file_name="discogs_collection.txt", refresh_collection=False):
        logger.debug(FUNCTION_CALL_MSG)
        self._collection = {}
        self.token = token
        # self.collection_file_name = collection_file_name
        self.absolute_collection_file_path = f"{os.path.dirname(__file__)}/{collection_file_name}"
        self.collection_file_exists = os.path.isfile(self.absolute_collection_file_path)
        if not self.collection_file_exists:
            self._collection = self.get_collection_from_discogs()
            self.write_collection_to_file()
        elif self.collection_file_exists and refresh_collection:
            self._collection = self.get_collection_from_discogs()
            self.write_collection_to_file()
        elif self.collection_file_exists and not refresh_collection:
            self._collection = self.get_collection_from_file()

    @property
    def identity(self):
        logger.debug(FUNCTION_CALL_MSG)
        client = discogs_client.Client(
            'RandomDiscogsRecord/0.1',
            user_token=f"{self.token}"
        )
        return client.identity()

    @property
    def collection(self):
        return self._collection

    def get_collection_from_discogs(self):
        discogs_collection = self.identity.collection_folders[0]
        collection = {}
        collection['record_count'] = discogs_collection.count
        records = []
        for release in discogs_collection.releases:
            record = {}
            record['artist'] = release.release.artists[0].name
            record['title'] = release.release.title
            records.append(record)
        collection['records'] = records
        logger.info(f"Collection with {collection['record_count']} records fetched from discogs.")
        return collection

    def get_collection_from_file(self):
        with open(self.absolute_collection_file_path, "r") as f:
            collection = json.load(f)
        logger.info(f"Collection with {collection['record_count']} records fetched from disk.")
        return collection

    def write_collection_to_file(self):
        try:
            with open(self.absolute_collection_file_path, "w") as f:
                try:
                    # collection = json.load(f)
                    f.seek(0)
                    json.dump(self.collection, f)
                    f.truncate()
                    logger.info(f"Collection with {self.collection['record_count']} records written to disk.")
                except ValueError as e:
                    logger.error(e)

        except Exception as e:
            logger.error(e)

    def get_random_record(self):
        random_record = {}
        records_in_collection = self.collection['record_count']
        record_number = randint(0, records_in_collection - 1)
        random_record['artist'] = self.collection['records'][record_number]['artist']
        random_record['title'] = self.collection['records'][record_number]['title']
        return random_record
