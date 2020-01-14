from definitions import ROOT_DIR
from random import randint
import json
import discogs_client
import os

from logs.config import logger
logger = logger(__name__)


class DiscogsCollection():
    def __init__(self, token, collection_file_name="discogs_collection.txt", refresh_collection=False):
        logger.debug('function_call')
        self._collection = {}
        self.token = token
        self.absolute_collection_file_path = f"{ROOT_DIR}/data/{collection_file_name}"
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
        logger.debug('function_call')
        client = discogs_client.Client(
            'RandomDiscogsRecord/0.1',
            user_token=f"{self.token}"
        )
        return client.identity()

    @property
    def collection(self):
        logger.debug('function_call')
        return self._collection

    def get_collection_from_discogs(self):
        logger.debug('function_call')
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
        logger.debug('function_call')
        with open(self.absolute_collection_file_path, "r") as f:
            collection = json.load(f)
        logger.info(f"Collection with {collection['record_count']} records fetched from disk.")
        return collection

    def write_collection_to_file(self):
        logger.debug('function_call')
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
        logger.debug('function_call')
        random_record = {}
        records_in_collection = self.collection['record_count']
        record_number = randint(0, records_in_collection - 1)
        random_record['artist'] = self.collection['records'][record_number]['artist']
        random_record['title'] = self.collection['records'][record_number]['title']
        random_record['number'] = record_number
        logger.info(f"Random record: {random_record}")
        return random_record
