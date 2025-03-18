import asyncio
import string
import websocket
import random
import anyio
from anyio import to_thread
ws = websocket.WebSocket()
ws.connect("ws://localhost:9000")

async def message(m: str):

        # Sending a message to the server
        await to_thread.run_sync(ws.send, m)
        print(f"Message sent to the server {m}")
        # Receiving a message from the server
        response = await to_thread.run_sync(ws.recv)
        print(f"Message received from the server: {response}")

async def main():
    messages = [''.join(random.choices(string.ascii_letters, k=10)) for _ in range(10000)]
    tasks = [asyncio.create_task(message(m)) for m in messages]
    done, pending = await asyncio.wait(tasks)
    for t in done:
        print(f"Task completed with results {t.result()}")

if __name__ == "__main__":

    asyncio.run(main())