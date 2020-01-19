from definitions import ROOT_DIR, FUNCTION_CALL_MSG
from random import randint
import json
import discogs_client
import os

from logs.config import get_logger
logger = get_logger(__name__)


class DiscogsCollection():
    def __init__(self, auth_token, collection_file_name="discogs_collection.txt", refresh_collection=False):
        logger.debug(f"{FUNCTION_CALL_MSG}, {__class__}")
        self._collection = {}
        self.auth_token = auth_token
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
        logger.debug(FUNCTION_CALL_MSG)
        client = discogs_client.Client(
            'RandomDiscogsRecord/0.1',
            user_token=f"{self.auth_token}"
        )
        return client.identity()

    @property
    def collection(self):
        logger.debug(FUNCTION_CALL_MSG)
        return self._collection

    def get_collection_from_discogs(self):
        logger.debug(FUNCTION_CALL_MSG)
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
        artist_index = self.create_artist_index(records)
        collection['artist_index'] = artist_index
        collection['artist_count'] = len(artist_index.keys())
        logger.info(f"Collection with {collection['record_count']} records fetched from discogs.")
        return collection

    def create_artist_index(self, records):
        artist_index = {}

        for i, record in enumerate(records):
            if record['artist'] not in artist_index.keys():
                artist_index[record['artist']] = [i]
            else:
                artist_index[record['artist']].append(i)
        return artist_index

    def get_collection_from_file(self):
        logger.debug(FUNCTION_CALL_MSG)
        with open(self.absolute_collection_file_path, "r") as f:
            collection = json.load(f)
        logger.info(f"Collection with {collection['record_count']} records fetched from disk.")
        return collection

    def write_collection_to_file(self):
        logger.debug(FUNCTION_CALL_MSG)
        try:
            with open(self.absolute_collection_file_path, "w") as f:
                try:
                    f.seek(0)
                    json.dump(self.collection, f)
                    f.truncate()
                    logger.info(f"Collection with {self.collection['record_count']} records written to disk.")
                except ValueError as e:
                    logger.error(e)

        except Exception as e:
            logger.error(e)

    def get_random_record(self):
        logger.debug(FUNCTION_CALL_MSG)
        random_record = {}
        records_in_collection = self.collection['record_count']
        record_number = randint(0, records_in_collection - 1)
        random_record = {}
        random_record['record'] = self.collection['records'][record_number]
        random_record['number'] = record_number
        logger.info(f"Random record: {random_record}")
        return random_record

    def get_record_for_random_artist(self):
        logger.debug(FUNCTION_CALL_MSG)
        artist_index = self.collection['artist_index']
        artist_in_collection = self.collection['artist_count']
        artist_number = randint(0, artist_in_collection - 1)
        logger.info(f"Artist number: {artist_number}")
        random_artist = list(artist_index.keys())[artist_number]
        random_artist_index = artist_index[random_artist]
        logger.info(f"Index of random artist: {random_artist_index}")
        record_index_number = randint(0, len(random_artist_index) - 1)
        record_number = random_artist_index[record_index_number]
        random_record = {}
        random_record['record'] = self.collection['records'][record_number]
        random_record['number'] = record_number
        logger.info(f"Random record: {random_record}")
        return random_record
