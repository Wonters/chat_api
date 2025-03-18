import logging
import time
import json
import redis

logger = logging.getLogger(__name__)

MESSAGE_QUEUE = "message_queue"
redis_host = "127.0.0.1"
redis_port=6379

redis_client = redis.Redis(host=redis_host, port=redis_port, db=0)

async def serve_message(active_connections, client):
    """
    Utilisation de redis pour redistribuer les messages aux destinataires abonnés au canal
    :return:
    """
    logger.info("start listen from redis")
    pubsub = client.pubsub()
    pubsub.subscribe(MESSAGE_QUEUE)
    try:
        for message in pubsub.listen():
            time.sleep(0.5)
            if message['type'] == "message":
                message_data = json.loads(message["data"].decode('utf-8'))
                if message_data['receiver'] in active_connections:
                    logger.info(f"Send message {message_data} to {message_data['receiver']}")
                else:
                    client.publish(MESSAGE_QUEUE, message["data"])
                    # logger.info(f"Waiting receiver {message_data['receiver']}")
    except Exception as e:
        raise e
    finally:
        pubsub.close()