import couchdb
from django.conf import settings
from django.core.cache import caches, InvalidCacheBackendError

import exceptions

DEFAULT_CACHE_TTL = getattr(settings, 'COUCHDB_CACHE_TTL', 3600)


class CouchDBCache(object):

    MODULE_PREFIX = 'cdc'

    def __init__(self, cache, db, cache_ttl=-1):
        try:
            self._cache = caches[cache]
        except InvalidCacheBackendError:
            raise exceptions.BadConfigurationError('Invalid cache backend: %s' % cache)
        self._cache_ttl = cache_ttl if cache_ttl != -1 else DEFAULT_CACHE_TTL

        self._db = couchdb.Database(db)
        self._build_cache_prefix(db)

    def get(self, id):
        doc = self._read_from_cache(id)
        if doc is None:
            doc = self._read_from_db(id)
            self._store_in_cache(id, doc)

        return doc

    def set(self, doc, invalidate=False):
        if not isinstance(doc, dict):
            raise exceptions.InvalidDocumentError('Expected dict, received "%s"' % type(doc))

        if invalidate and doc.get('_id'):
            self.invalidate(doc.get('_id'))

        self._store_in_db(doc)

    def invalidate(self, id):
        self._cache.delete(self._build_cache_key(id))

    def _build_cache_prefix(self, db):
        db_name_parts = db.split('/')
        if len(db_name_parts) > 1:
            db_name = db_name_parts[-1]
        else:
            raise exceptions.BadConfigurationError('Wrong CouchDB database url: %s' % db)

        self._cache_prefix = '%s:%s:' % (self.MODULE_PREFIX, db_name)

    def _build_cache_key(self, id):
        return self._cache_prefix + id

    def _read_from_cache(self, id):
        return self._cache.get(self._build_cache_key(id))

    def _store_in_cache(self, id, doc):
        self._cache.set(self._build_cache_key(id), doc, self._cache_ttl)

    def _read_from_db(self, id):
        try:
            return self._db.get(id)
        except couchdb.ResourceNotFound:
            raise exceptions.BadConfigurationError('CouchDB database not found')

    def _store_in_db(self, doc):
        try:
            self._db.save(doc)
        except couchdb.ResourceNotFound:
            raise exceptions.BadConfigurationError('CouchDB database not found')
