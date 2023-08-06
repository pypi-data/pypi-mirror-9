class DatabaseConnector:
    def __init__(self, connection, cursor):
        self.connection = connection
        self.cursor = cursor

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

    @classmethod
    def connect_mysql(cls, host='', username='', password='', port=3306, database='', **kwargs):
        """
        Initializes a MySQL connection with the provided credentials.

        @param host -- the host to connect to (default localhost)
        @param username -- the username to login as (optional)
        @param password -- the password to login with (optional)
        @param port -- the port to connect to (default 3306)
        @param database -- the name of the database to connect to (optional)
        """
        try:
            import MySQLdb as mysql
        except ImportError:
            raise ImportError("Please install the mysql-python package")

        connection = mysql.connect(
            host=host,
            user=username,
            passwd=password,
            port=port,
            db=database,
            **kwargs
        )
        c = connection.cursor()
        return cls(connection, c)

    @classmethod
    def connect_sqlite(cls, database=':memory:', **kwargs):
        """
        Initializes a SQLite connection to the given database.

        @param database -- the name of the database file to connect to (default database in RAM)
        """
        import sqlite3

        connection = sqlite3.connect(database=database, **kwargs)
        c = connection.cursor()
        return cls(connection, c)

    @classmethod
    def connect_postgres(cls, host='', username='', password='', port=5432, database='', **kwargs):
        """
        Initializes a PostgreSQL connection with the provided credentials.

        @param host -- the host to connect to (default Unix Socket)
        @param username -- the username to login as (optional)
        @param password -- the password to login with (optional)
        @param port -- the port to connect to (default 5432)
        @param database -- the name of the database to connect to (optional)
        """
        try:
            import psycopg2
        except ImportError:
            raise ImportError("Please install the mysql-python package")

        connection = psycopg2.connect(
            host=host,
            user=username,
            password=password,
            port=port,
            database=database,
            **kwargs
        )
        c = connection.cursor()
        return cls(connection, c)

    @classmethod
    def connect_mssql(cls, host='.', username='', password='', port=1433, database='', **kwargs):
        """
        Initializes a Microsoft SQL connection with the provided credentials.

        @param host -- the host to connect to (default localhost)
        @param username -- the username to login as (optional)
        @param password -- the password to login with (optional)
        @param port -- the port to connect to (default 1433)
        @param database -- the name of the database to connect to (optional)
        """
        try:
            import pymssql
        except ImportError:
            raise ImportError("Please install the pymssql package")

        connection = pymssql.connect(
            server=host,
            user=username,
            password=password,
            port=str(port),
            database=database,
            **kwargs
        )
        c = connection.cursor()
        return cls(connection, c)

    def query(self, query):
        """
        Returns the result of running the query on the database

        @param query -- the query to pass to the connection

        @return (Tuple<String>) the result of the query as a tuple of Strings
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def execute(self, query):
        """
        Runs a query on the database and commits the transaction. Useful for SQL
        executions such as INSERT or DROP.

        @param query -- the query to execute on the connection.
        """
        self.query(query)
        self.connection.commit()

    def compute(self, query):
        """
        Returns the first row of running the query on the database. Useful for SQL aggregate
        queries such as COUNT, MAX, MIN, AVG, FIRST, LAST, or SUM.

        @param query -- the query to pass to the connection

        @return (Tuple<String>) the the first row of the query as a tuple of Strings. Although
        most results will be numerical, cannot predict this ahead of time and the values must
        be cast into numerical data types to use as numbers.
        """
        rows = self.query(query)
        return rows[0]

    def close(self):
        """
        Closes the connection, preventing any further queries
        """
        self.connection.close()