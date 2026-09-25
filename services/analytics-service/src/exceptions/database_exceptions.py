class DatabaseError(Exception):
    """Base Database Exception"""

    pass


class DatabaseQueryError(DatabaseError):
    """Raised when a query on the database fails"""

    pass


class DatabaseIntegrityError(DatabaseError):
    """Raised when the database throws an integrity error"""

    pass
