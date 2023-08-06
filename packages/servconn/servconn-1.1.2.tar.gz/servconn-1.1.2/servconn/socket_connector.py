import socket, json

class SocketConnector:
    def __init__(self, host, port, bufsize=4096):
        """
        Initializes a SocketConnector with the provided options

        @param host -- the host to connect to
        @param port -- the port to connect to
        @param bufsize -- the size of data allowed to be received (default 4096)
        """
        self.address = (host, port)
        self.bufsize = bufsize

    def send(self, data):
        """
        Sends the data to the server as a JSON string and returns the response.

        @param data -- a Python object to send as JSON

        @return (object|String) the response from the server as a Python object extracted from
            the JSON formatted string. If the response isn't a JSON string, returns the
            response
        """
        socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket.connect(self.address)
        socket.send(json.dumps(data))
        response = socket.recv(self.bufsize)
        socket.close()
        try:
            return json.loads(response)
        except ValueError:
            return response

    @classmethod
    def send_to(cls, host, port, data, bufsize=4096):
        """
        Initializes a SocketConnector and sends the packet. Deletes the SocketConnector
        afterwards. Alias for:

        SocketConnector(host, port).send(data)
        """
        return cls(host, port, bufsize).send(data)