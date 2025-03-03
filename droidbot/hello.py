from SocketClient import SocketClient
import asyncio

async def main():
    await SocketClient.connect()
    SocketClient.send_message('message_from_client', {'verdict': 'fail', "response": 'ok'})

asyncio.run(main())
