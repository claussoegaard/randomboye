import os
import unittest
from randomboye.discogs_collection import DiscogsCollection

token = os.environ["DISCOGS_TOKEN"]


class TestDiscogsCollection(unittest.TestCase):

    def setUp(self):
        self.dc = DiscogsCollection(token)

    def test_get_random_record(self):
        record = self.dc.get_random_record()
        # Got a record without blank artist or title
        self.assertEqual(record['record']['artist'] != '' and record['record']['title'] != '', True)
        # Record exists in collection
        self.assertEqual(record['record'] in self.dc.collection['records'], True)
        # Record number between 0 and total collection count
        self.assertEqual(record['number'] in range(self.dc.collection['record_count']), True)
