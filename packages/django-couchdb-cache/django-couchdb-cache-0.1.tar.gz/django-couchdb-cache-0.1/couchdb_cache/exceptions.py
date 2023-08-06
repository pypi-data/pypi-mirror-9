class CouchDBCacheError(Exception):
    pass


class InvalidDocumentError(CouchDBCacheError):
    pass


class BadConfigurationError(CouchDBCacheError):
    pass
