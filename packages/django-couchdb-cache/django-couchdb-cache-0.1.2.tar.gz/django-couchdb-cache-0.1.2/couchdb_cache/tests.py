import couchdb
from couchdb_cache.cache import CouchDBCache
from couchdb_cache import exceptions
from django.conf import settings
from django.core.cache import caches
from django.test import TestCase

COUCHDB_URL = getattr(settings, 'COUCHDB_URL', 'http://localhost:5984')
COUCHDB_USER = getattr(settings, 'COUCHDB_USER', 'admin')
COUCHDB_PASSWORD = getattr(settings, 'COUCHDB_PASSWORD', 'admin')

TEST_DB_NAME = 'test'
TEST_CACHE_NAME = 'default'


class GetSetTestCase(TestCase):
    DOC_ID = 'test'

    def setUp(self):
        db_server = couchdb.Server(COUCHDB_URL)
        db_server.resource.credentials = (COUCHDB_USER, COUCHDB_PASSWORD)

        try:
            db_server[TEST_DB_NAME]
        except couchdb.ResourceNotFound:
            db_server.create(TEST_DB_NAME)

        self.cache = CouchDBCache(cache=TEST_CACHE_NAME, db='%s/%s' % (COUCHDB_URL, TEST_DB_NAME))

    def tearDown(self):
        db_server = couchdb.Server(COUCHDB_URL)
        db_server.resource.credentials = (COUCHDB_USER, COUCHDB_PASSWORD)

        try:
            db_server.delete(TEST_DB_NAME)
        except couchdb.ResourceNotFound:
            pass

        caches[TEST_CACHE_NAME].clear()

    def test_get_non_existing_document(self):
        doc = self.cache.get(self.DOC_ID)
        self.assertIsNone(doc)

    def test_get_existing_document(self):
        doc = {'_id': self.DOC_ID, 'something': 'anything'}
        self.cache.set(doc)
        self.assertEquals(doc, self.cache.get(self.DOC_ID))

    def test_get_cached_document(self):
        doc = {'_id': self.DOC_ID, 'something': 'anything'}
        self.cache.set(doc)
        self.cache.get(self.DOC_ID)
        self.assertEquals(doc, self.cache.get(self.DOC_ID))

    def test_set_invalid_string_document(self):
        doc = 'Not a dictionary'
        with self.assertRaises(exceptions.InvalidDocumentError):
            doc = self.cache.set(doc)

    def test_set_dict_child_class_document(self):
        class DictChild(dict):
            pass

        doc = DictChild()
        doc['something'] = 'anything'
        doc = self.cache.set(doc)

    def test_manually_invalidate(self):
        doc = {'_id': self.DOC_ID, 'something': 'anything'}
        self.cache.set(doc)
        self.cache.get(self.DOC_ID)
        doc['new_field'] = 'something'
        self.cache.set(doc)
        self.cache.invalidate(self.DOC_ID)
        self.assertEquals(doc, self.cache.get(self.DOC_ID))

    def test_forced_invalidate(self):
        doc = {'_id': self.DOC_ID, 'something': 'anything'}
        self.cache.set(doc)
        self.cache.get(self.DOC_ID)
        doc['new_field'] = 'something'
        self.cache.set(doc, invalidate=True)
        self.assertEquals(doc, self.cache.get(self.DOC_ID))


class ConfigTestCase(TestCase):

    DOC_ID = 'test'

    def test_missing_couchdb_database(self):
        cache = CouchDBCache(cache=TEST_CACHE_NAME, db='%s/%s' % (COUCHDB_URL, 'bad_database'))
        with self.assertRaises(exceptions.BadConfigurationError):
            cache.set({'_id': self.DOC_ID, 'something': 'anything'})

    def test_missing_cache(self):
        with self.assertRaises(exceptions.BadConfigurationError):
            CouchDBCache(cache='bad_cache', db='%s/%s' % (COUCHDB_URL, TEST_DB_NAME))
