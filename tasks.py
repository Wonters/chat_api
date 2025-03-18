import logging
import asyncio
import functools
from starlette.websockets import WebSocketDisconnect

logger = logging.getLogger(__name__)

def catch_ws_exception(func):
    """Decorator to catch WebSocketDisconnect errors."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            await func(*args, **kwargs)  # ✅ Properly execute the wrapped function
        except WebSocketDisconnect as e:
            sender = kwargs.get("sender")  # ✅ Extract sender safely from kwargs
            if sender in kwargs.get('active_connections'):
                del kwargs.get('active_connections')[sender]  # ✅ Safe deletion
                logger.error(f"💥 {e.reason} Client {sender} disconnected")
            else:
                logger.warning(f"⚠️ Client {sender} was already removed.")

    return wrapper  # ✅ Return the wrapped function


async def send(websocket, sender, redis_client, active_connections):
    """"""
    try:
        async for data in websocket.iter_json():
            if data['receiver'] in active_connections:
                await active_connections[data['receiver']].send_json(data['message'])
                logger.info(f"👶✅ Sender {sender} sent {data}")
            else:
                logger.info(f"👶🛑 Receiver {data['receiver']} not connected, save")
                await redis_client.xadd(f"client:{data['receiver']}",
                                        {"sender": sender, "message": data['message']})
            await asyncio.sleep(0.1)
    except WebSocketDisconnect as e:
        try:
            del active_connections[sender]
            logger.error(f"💥{e.reason} Client {sender} disconnected")
        except KeyError:
            pass


async def read(websocket, sender, redis_client, active_connections):
    """"""
    try:
        redis_messages = await redis_client.xread({f"client:{sender}": "0"})
        if redis_messages:
            logger.info(f"👶📩 Sender {sender} receive {len(redis_messages)} message")
        for stream, entries in redis_messages:
            for entry_id, data in entries:
                message = data[b'message'].decode()
                await redis_client.xdel(f"client:{sender}", entry_id)  # Supprimer après lecture
                await websocket.send_json({"message": message})
    except WebSocketDisconnect as e:
        try:
            del active_connections[sender]
            logger.error(f"💥{e.reason} Client {sender} disconnected")
        except KeyError:
            pass