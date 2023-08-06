"""
This is where the exceptions live
"""


class MultipleObjectsExist(Exception):
    pass


class DoesNotExist(Exception):
    pass


class SerializationError(Exception):
    pass


class ValidationError(Exception):
    pass


class QueryError(Exception):
    "A generic error for signaling issues with querying the database"
    pass


class IntegrityError(Exception):
    "A generic error for signaling issues with updating the database"
    pass
