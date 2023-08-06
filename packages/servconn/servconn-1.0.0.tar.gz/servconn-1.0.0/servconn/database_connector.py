import MySQLdb as mysql

class DatabaseConnector:
    def __init__(self, host='', username='', password='', port=0, database=''):
        """
        Initializes a MySQL connection with the provided credentials.

        @param host -- the host to connect to (default localhost)
        @param username -- the username to login as (optional)
        @param password -- the password to login with (optional)
        @param port -- the port to connect to (optional)
        @param database -- the name of the database to connect to (optional)
        """
        self.connection = mysql.connect(
            host=host,
            user=username,
            passwd=password,
            port=port,
            db=database
        )
        self.c = self.connection.cursor()

    def __del__(self):
        """
        When this object is being deleted, close the connection
        """
        if self.connection:
            self.close()

    def __enter__(self):
        """
        Allows a DatabaseConnector to be used as a context manager
        """
        return self

    def __exit__(self, type, value, traceback):
        """
        On exit as a context manager, close the connection
        """
        self.close()

    def query(self, query):
        """
        Returns the result of running the query on the database

        @param query -- the query to pass to the connection

        @return (Tuple<String>) the result of the query as a tuple of Strings
        """
        self.c.execute(query)
        return self.c.fetchall()

    def execute(self, query):
        """
        Runs a query on the database, but doesn't return the result of the query. Does the
        same thing as query otherwise. Useful for SQL executions such as INSERT or DROP.

        @param query -- the query to execute on the connection.
        """
        self.query(query)

    def compute(self, query):
        """
        Returns the first row of running the query on the database. Useful for SQL aggregate
        queries such as COUNT, MAX, MIN, AVG, FIRST, LAST, or SUM.

        @param query -- the query to pass to the connection

        @return (Tuple<String>) the the first row of the query as a tuple of Strings. Although
        most results will be numerical, 
        """
        rows = self.query(query)
        return rows[0]

    def close(self):
        """
        Closes the connection, preventing any further queries
        """
        self.connection.close()