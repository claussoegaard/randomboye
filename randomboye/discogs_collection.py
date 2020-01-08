from random import randint
import json
import discogs_client
import os


class DiscogsCollection():
    def __init__(self, token, collection_file_name="discogs_collection.txt", update=False):
        self.token = token
        self.collection_file_name = collection_file_name
        self.update = update
        if not os.path.isfile(self.absolute_collection_file_path):
            self.update = True
            self.write_collection_to_file()
            self.update = update

    @property
    def absolute_collection_file_path(self):
        return f"{os.path.dirname(__file__)}/{self.collection_file_name}"

    @property
    def identity(self):
        client = discogs_client.Client(
            'RandomDiscogsRecord/0.1',
            user_token=f"{self.token}"
        )
        return client.identity()

    @property
    def collection(self):
        if self.update:
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
        else:
            with open(self.absolute_collection_file_path, "r") as f:
                collection = json.load(f)
        return collection

    def write_collection_to_file(self):
        try:
            with open(self.absolute_collection_file_path, "w+") as f:
                try:
                    data = json.load(f)
                except ValueError:
                    data = {}
                # Only overwrite contents of file if record count has changed
                if 'record_count' not in data or \
                        data.get('record_count') != \
                        self.collection.get('record_count'):
                    f.seek(0)
                    json.dump(self.collection, f)
                    f.truncate()
        except Exception as e:
            print("Something went wrong:")
            print(e)

    # def get_random_record(self):

    def get_random_record(self):
        record = {}
        records_in_collection = self.collection['record_count']
        record_number = randint(0, records_in_collection - 1)
        record['artist'] = self.collection['records'][record_number]['artist']
        record['title'] = self.collection['records'][record_number]['title']
        return record
        # with open(self.absolute_collection_file_path, "r") as f:
        #     data = json.load(f)
        #     records_in_collection = data['record_count']
        #     record_number = randint(0, records_in_collection - 1)
        #     record['artist'] = data['records'][record_number]['artist']
        #     record['title'] = data['records'][record_number]['title']
        # return record


my_collection = DiscogsCollection("CWhLmAdMsIhLXCeIfCXDZszstBbeWxbsTlmvntFf")

# my_collection.write_collection_to_file()
# print(my_collection.collection_file_exists)
print(my_collection.get_random_record())
