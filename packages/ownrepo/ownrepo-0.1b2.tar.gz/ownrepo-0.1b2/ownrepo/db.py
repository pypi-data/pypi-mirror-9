import functools
import sqlite3


class ConnectionClosedError(Exception):
    pass


class Connection:
    """
    Represents a database connection
    """

    def __init__(self, path):
        self._path = path
        self._closed = False

        self._conn = sqlite3.connect(path)
        self._conn.row_factory = sqlite3.Row

    def _prevent_when_closed(func):
        """ Prevent method execution when the connection is closed """
        @functools.wraps(func)
        def _wrapper(self, *args, **kwargs):
            if self._closed:
                raise ConnectionClosedError
            return func(self, *args, **kwargs)
        return _wrapper

    @_prevent_when_closed
    def load_file(self, path):
        """ Load a SQL file from the file system """
        with open(path, 'r') as f:
            content = f.read()

        # Execute the SQL file
        self._conn.cursor().executescript(content)
        self._conn.commit()

    @_prevent_when_closed
    def query(self, query, *args, one=False, edit=False):
        """ Query the database """
        # Execute the query
        cursor = self._conn.execute(query, args)

        # If the query was an edit query, commit it
        if edit:
            cursor.close()
            self._conn.commit()
            return

        # Else return the result
        else:
            result = cursor.fetchall()
            cursor.close()
            if one:
                try:
                    return result[0]
                except IndexError:
                    return
            else:
                return result

    def close(self):
        """ Close the connection """
        self._closed = True
        self._conn.close()
