ServConn
========

This repository defines classes that wrap connections to certain servers. The current classes defined are:
- DatabaseConnector: a class that wraps a MySQL connection
- SocketConnector: a class that wraps a socket connection

Development
-----------

To develop, use the following to setup your environment

1. (optional) Setup a virtual environment with virtualenv
2. Install pip
3. `pip install -r requirements.txt`

Installing
----------

To install this package, either run `python setup.py install` from this project or call `pip install servconn`.

DatabaseConnector
-----------------

This class lets you query a connection without dealing with connection or cursor objects. Other database connections may be supported in later versions (PostgreSQL, SQLite, etc)

### Usage

The DatabaseConnector can be used as a regular object or as a context manager.

```
from servconn import DatabaseConnector

db = DatabaseConnector(host, username='test')
db.execute('INSERT INTO table VALUES (1,2)')

with DatabaseConnector(host) as db:
    db.query('SELECT * FROM table')
```

### Class Methods
- `DatabaseConnector.__init__([host, username, password, port, database])`: Creates a new DatabaseConnector object. Connects to localhost by default, optionally with the given username, password, port, and database.
- `DatabaseConnector.__del__()`: Closes the connection before this object is deleted.
- `DatabaseConnector.__enter__()`: Allows a DatabaseConnector to be used as a context manager
- `DatabaseConnector.__exit__()`: Closes the connection on exit as a context manager

### Instance Variables
- `DatabaseConnector.connection`: The MySQL Connection object
- `DatabaseConnector.c`: The MySQL Cursor object

### Instance Methods
- `query(query)`: Returns the result of running the given query on the connection
- `execute(query)`: Executes the query but doesn't return anything. Useful for INSERT or DROP operations
- `compute(query)`: Returns the first row of the result of the running the query. Useful for SQL aggregate functions
- `close()`: Closes the connection from any further queries

SocketConnector
---------------

This class lets you send and receive JSON packets to the provided server.

### Usage

The SocketConnector is used as a regular Python object.

```
from servconn import SocketConnector

socket = SocketConnector(host, port)
data = {
    'hello': 'world'
}
response = socket.send(data)
```

### Class Methods
- `SocketConnector.__init__(host, port[, bufsize=4096])`: Creates a new SocketConnector object that will connect to the given host and port. The bufsize may also be specified (see instance variables)

### Instance Variables
- `SocketConnector.host`: The host to connect to
- `SocketConnector.port`: The port to connect to
- `SocketConnector.bufsize`: The maximum amount of data allowed to be received at once through this socket (by default 4096)

### Instance Methods
- `send(data)`: Sends the provided data over the socket as a JSON-formatted string