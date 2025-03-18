from twisted.internet import reactor, protocol
import json
from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol

class ChatProtocol(WebSocketServerProtocol):
    def __init__(self):
        super().__init__()  # Call the parent class constructor

    def onOpen(self):
        self.factory.clients.append(self)  # Add the new client to the list
        print("New client connected")

    def connectionLost(self, reason):
        super().connectionLost(reason)  # Call the parent method
        self.factory.clients.remove(self)  # Remove the client from the list
        print("Client disconnected")

    def onMessage(self, payload, isBinary):
        message = payload.decode('utf8') if not isBinary else payload
        print(f"Message received: {message}")
        # Broadcast the message to all connected clients
        self.broadcast(f"Echo: {message}")

    def broadcast(self, message):
        for client in self.factory.clients:
            client.sendMessage(message.encode('utf8'))


class ChatFactory(WebSocketServerFactory):
    def __init__(self, url):
        super().__init__(url)
        self.clients = []  # Keep track of connected clients

    def buildProtocol(self, addr):
        protocol = ChatProtocol()
        protocol.factory = self  # Pass the factory reference to the protocol
        return protocol


if __name__ == "__main__":
    factory = ChatFactory("ws://localhost:9000")
    reactor.listenTCP(9000, factory)
    print("Chat server started on ws://localhost:9000")
    reactor.run()