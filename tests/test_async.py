import asyncio
import logging
import os
import threading
import time
import random
from locust import User, task, between, events
from lib.async_ import run_asyncio, communicate
# Configuration du logger
logger = logging.getLogger(__name__)

senders = []
commutications = []

class AsyncioInLocustTest(User):
    wait_time = between(0.1, 1)  # Temps d'attente entre les requêtes

    shared_loop = None
    shared_thread = None
    initialized_pid = None  # Stocke l'ID du processus


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Détecter les processus forkés et initialiser la boucle asyncio
        current_pid = os.getpid()
        if AsyncioInLocustTest.initialized_pid != current_pid:
            self.init_process_resources(current_pid)

        self.loop = AsyncioInLocustTest.shared_loop  # Récupérer la boucle asyncio
        self.user = random.randint(0,1000)
        self.receiver = random.randint(1000,2000)
        senders.append(self.user)


    @classmethod
    def init_process_resources(cls, current_pid):
        """ Initialisation des ressources asyncio dans chaque processus """
        cls.initialized_pid = current_pid
        logger.info(f"Initialisation thread pour le PID {current_pid}")
        cls.shared_loop = asyncio.get_event_loop_policy().new_event_loop()
        cls.shared_thread = threading.Thread(target=cls.shared_loop.run_forever, daemon=True)
        cls.shared_thread.start()

    def async_run(self, func, *args, **kwargs):
        start_time = time.time()

        try:
            # Exécution de la coroutine asynchrone
            result = run_asyncio(self.loop, func, *args, **kwargs)

            # Événement Locust en cas de succès
            events.request.fire(
                request_type="asyncio_task",
                name=func.__name__,
                response_time=int((time.time() - start_time) * 1000),
                response_length=len(str(result)),
                exception=None
            )
            return result
        except Exception as e:
            raise e
            # Événement Locust en cas d'erreur
            events.request.fire(
                request_type="asyncio_task",
                name=func.__name__,
                response_time=int((time.time() - start_time) * 1000),
                response_length=0,
                exception=e
            )
            logging.error(f"Erreur Asyncio: {e}")

    @task
    def communication(self):
        """

        :return:
        """
        active_communication = {self.user, self.receiver}
        commutications.append(active_communication)
        start = time.time()
        try:
            self.async_run(communicate,self.user, self.receiver)
            commutications.remove(active_communication)
        except TimeoutError:
            end = time.time()
            logger.warning(f"Timeout for sender {self.user} receiver {self.receiver} in {end-start}")




