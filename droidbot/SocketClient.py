import socketio

class SocketClient:
    _sio = socketio.Client()
    _connected = False

    @classmethod
    async def connect(cls, server_url='http://localhost:4000'):
        """Connect to the Socket.IO server"""
        if not cls._connected:
            cls._sio.connect(server_url)
            cls._connected = True
            while not cls._connected:
                print("connecting....")
            print("Connected to the server!")

    @classmethod
    def send_message(cls, event_name, message):
        """Send a message to the Socket.IO server"""
        if not cls._connected:
            cls.connect()
        cls._sio.emit(event_name, {"test_case": message})
        print(f"Sent message: {message}")

    @classmethod
    def disconnect(cls):
        """Disconnect from the server"""
        if cls._connected:
            cls._sio.disconnect()
            cls._connected = False
            print("Disconnected from the server!")

    @classmethod
    def register_event(cls, event_name, callback):
        """Register an event listener"""
        cls._sio.on(event_name, callback)

