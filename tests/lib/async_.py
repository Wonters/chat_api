import asyncio
import logging
import time
import websockets
import random
import json
from string import ascii_letters
from typing import Any, Callable, Awaitable

logger = logging.getLogger(__name__)

def time_(func):
    def wrap(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(end - start)
        return result
    return wrap

def run_asyncio(loop, coro: Callable[..., Awaitable], *args: Any, **kwargs: Any) -> Any:
    """ Exécuter une coroutine asyncio dans le thread d'événement existant. """
    future = asyncio.run_coroutine_threadsafe(coro(*args, **kwargs), loop)
    return future.result(timeout=120)  # Attendre la fin de la coroutine avec un timeout

def format_url(sender: int):
    return f"ws://localhost:5000/chat/{sender}"


async def read_message(client: int):
    async with websockets.connect(format_url(receiver)) as ws2:
        logger.info(f"{receiver} connected")
        receiv_messages = await read_message(ws2)
        if receiv_messages:
            logger.info(f"📩👶{receiver} receive messsage {len(receiv_messages)}")
    message_receive = []
    while True:
        try:
            # Attendre un message avec un timeout (évite un blocage infini)
            m = await asyncio.wait_for(ws.recv(), timeout=1)
            message_receive.append(m)
        except asyncio.TimeoutError:
            # Timeout atteint → WebSocket inactif, on ferme
            logger.info("Aucun nouveau message, fermeture du WebSocket.")
            break
    return message_receive

async def send_message(ws)

async def communicate(sender, receiver):
    async with websockets.connect(format_url(sender)) as ws1:
        for _ in range(20):
            message = f"from {sender} : hello {random.choice(ascii_letters)}"
            await ws1.send(json.dumps({'receiver': receiver, 'message': message}))
        logger.info(f"✉️ {sender} send 20")
    async with websockets.connect(format_url(sender)) as ws1:
        receiv_messages = await read_message(ws1)
        if receiv_messages:
            logger.info(f"📩👶 {sender} receive messsage {len(receiv_messages)}")
    async with websockets.connect(format_url(receiver)) as ws2:
        for _ in range(20):
            message = f"from {receiver} : hello {random.choice(ascii_letters)}"
            await ws2.send(json.dumps({'receiver': sender, 'message': message}))
        logger.info(f"✉️ {receiver} send 20")
    async with websockets.connect(format_url(receiver)) as ws2:
        logger.info(f"{receiver} connected")
        receiv_messages = await read_message(ws2)
        if receiv_messages:
            logger.info(f"📩👶{receiver} receive messsage {len(receiv_messages)}")