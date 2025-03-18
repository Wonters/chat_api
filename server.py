import asyncio
import logging
import redis.asyncio as redis
import uvicorn
import time
from rich.logging import RichHandler
import fastapi
import json
import multiprocessing as mp
from contextlib import asynccontextmanager
import anyio
from fastapi import FastAPI
from fastapi.websockets import WebSocket
from starlette.websockets import WebSocketDisconnect
from tasks import send, read

logging.basicConfig(
    level=logging.WARNING,  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    format="%(asctime)s:%(name)s:%(funcName)s:%(lineno)d %(message)s",
    handlers=[
        RichHandler()  # Permet d'afficher les logs dans la console
    ]
)
logger = logging.getLogger(__name__)
logging.getLogger("uvicorn.access").disabled = True
logging.getLogger("uvicorn.error").disabled = True
logging.getLogger("fastapi").disabled = True  # Désactive FastAPI logs

redis_host = "127.0.0.1"
redis_port = 6379

processus = []
active_connections = {}
message_queues = set()


### HANDLE PROCESSES CLEAN ####
@asynccontextmanager
async def start_processus(app: FastAPI):
    """
    Je vais démarrer le processus de lecture des messages dans la file redis
    :return:
    """
    for proces in processus:
        proces.start()
        logger.info(f"✅ Process {proces.pid} running")
    yield
    for proces in processus:
        if proces and proces.is_alive():
            proces.terminate()
            proces.join()
            logger.info("🔴 Redis process stopped.")
    client = redis.Redis(host=redis_host, port=redis_port)
    pubsub = client.pubsub()
    for name in message_queues:
        await pubsub.unsubscribe(name)
    logger.info("✅ Reset messages")


app = fastapi.FastAPI(lifespan=start_processus)


@app.get("/account")
async def account():
    """"""


@app.websocket("/chat/{sender}")
async def chat(websocket: WebSocket, sender: int):
    """
    Select a receiver
    :param websocket
    :param sender:
    :return:
    """
    await websocket.accept()
    active_connections[sender] = websocket
    logger.info(f"👶✅ Sender {sender} connected")
    logger.warning(f"active connections:{len(active_connections)}")
    redis_client = await redis.Redis(host=redis_host, port=redis_port)
    ## SEND STEP
    tasks = list()
    tasks.append(asyncio.create_task(send(websocket,
                                          sender,
                                          redis_client,
                                          active_connections),
                                     name=f"send-{sender}"))
    ### RECEIVE STEP FOR MESSAGE IN MEMORY
    tasks.append(asyncio.create_task(read(websocket,
                                          sender,
                                          redis_client,
                                          active_connections),
                                     name=f"read-{sender}"))
    done, pending = await asyncio.wait(tasks, return_when="ALL_COMPLETED")
    for task in done:
        try:
            task.result()
            logger.debug(f"✅ Completed: {task.get_name()}")
        except WebSocketDisconnect as e:
            pass
        finally:
            logger.info(f"👶🔴 Sender {sender} is gone")
            del active_connections[sender]
    for task in pending:
        logger.debug(f"⏳ Cancelling: {task.get_name()}")
        task.cancel()




@app.get("/test")
def hello_world():
    return "ok"


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5000,
        log_level="warning",
        reload=True
    )
