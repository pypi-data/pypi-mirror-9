import socket, json, ssl

class SocketConnector:
    def __init__(self, host, port, bufsize=4096, ca_certs=None, delimiter='$'):
        """
        Initializes a SocketConnector with the provided options

        @param host -- the host to connect to
        @param port -- the port to connect to
        @param bufsize -- the size of data allowed to be received (default 4096)
        @param ca_certs -- the certificate file to optionally encrypt the connection
        @param delimiter -- the delimiter to specify the end of a message
        """
        self.address = (host, port)
        self.bufsize = bufsize
        self.ca_certs = ca_certs
        self.delimiter = delimiter

    def _send_data(self, data):
        """
        Connects a socket, sends data, and returns the socket

        @return (Socket) the socket created
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.ca_certs:
            sock = ssl.wrap_socket(sock, cert_reqs=ssl.CERT_REQUIRED, ca_certs=self.ca_certs)

        sock.connect(self.address)
        sock.sendall(json.dumps(data))
        return sock

    def _return_response(self, response):
        """
        Attempts to return the response as JSON, otherwise, just return the response

        @param response -- the response

        @return (String|object) either a JSON object or a string of the response
        """
        try:
            return json.loads(response)
        except ValueError:
            return response

    def send(self, data):
        """
        Sends the data to the server as a JSON string and returns the response.

        @param data -- a Python object to send as JSON

        @return (object|String) the response from the server as a Python object extracted from
            the JSON formatted string. If the response isn't a JSON string, returns the
            response
        """
        sock = self._send_data(data)
        response = sock.recv(self.bufsize)
        sock.close()
        return self._return_response(response)

    def sendall(self, data):
        """
        Sends the data to the server and returns the response. When receiving data, will
        look for delimiter marking the end of the data.

        @param data -- a Python object to send as JSON

        @return (object|String) the response from the server as a Python object extracted from
            the JSON formatted string. If the response isn't a JSON string, returns the
            response
        """
        sock = self._send_data(data)
        response = ''

        while self.delimiter not in response:
            response += sock.recv(self.bufsize)

        sock.close()
        return self._return_response(response[:-1])

    @classmethod
    def send_to(cls, host, port, data, **kwargs):
        """
        Initializes a SocketConnector and sends the packet. Deletes the SocketConnector
        afterwards. Alias for:

        SocketConnector(host, port, **kwargs).send(data)
        """
        return cls(host, port, **kwargs).send(data)