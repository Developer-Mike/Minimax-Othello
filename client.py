import socket
import json

class Client:
    def __init__(self, ip_address: str, port: int):
        self.ip_address = ip_address
        self.port = port

        self.s = socket.socket()
        self.s.settimeout(500)
        self.s.connect(socket.getaddrinfo(ip_address, port)[0][-1])

    def execute(self, function: str, parameters: dict = {}):
        payload = {"function": function, "parameters": parameters}

        print("Sending:", payload)
        self.s.send(bytes(json.dumps(payload), "utf-8"))

        response = json.loads(self.s.recv(8192).decode("utf-8"))
        print("Response:", response)
        if not response["success"]:
            raise Exception("Server returned error: " + response["error"])

        return response

    