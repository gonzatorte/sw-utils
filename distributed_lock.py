import os
from time import sleep

from redis_lock import Lock
from django.conf import settings
from redis.client import StrictRedis

from redlock.lock import RedLock
from sw_utils.logs.log_handler import log_info


REDIS_HOST = getattr(settings, 'REDIS_HOST', None)


class DistributedLock:
    def __init__(self, id_key):
        self.id_key = id_key

    def acquire(self):
        pass

    def release(self):
        pass

    def __enter__(self):
        self.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


class DistributedLock_1(DistributedLock):
    redis_cli = StrictRedis(host=REDIS_HOST, port=6379, db=6)
    def __init__(self, id_key):
        DistributedLock.__init__(self, id_key)
        self.sem = Lock(self.redis_cli, 'sem_event_alarm_%s' % self.id_key)
        self.ini_times = None
        # idtimed = "%s-%s" % (Random().randint(a=1,b=8192), datetime.now().strftime("%d:%H:%M:%S"))
        # sem = Lock(redis_client=redis_cli, name='sem_event_alarm_%s' % position.vehiculo_id, expire=2,
        #            id=idtimed)

    def acquire(self):
        id_blocked = self.sem._client.get(self.sem._name)
        if id_blocked is None:
            id_blocked = "Nada"
        else:
            id_blocked = id_blocked.__hash__()
        log_info("SEMLOCK<%s>: request lock. Bussy by <%s>", self.sem._id.__hash__(), id_blocked)
        self.ini_times = os.times()

        self.sem.acquire(blocking=True)


    def release(self):
        #Hacer que el release no tenga problemas si se hace release 2 veces
        self.sem.release()
        fin_times = os.times()
        e_times = map(lambda x,y: x-y, fin_times, self.ini_times)
        log_info("SEMLOCK<%s>: release lock. e_times:<%s>", self.sem._id.__hash__(), e_times)


class DistributedLock_2(DistributedLock_1):
    def acquireLock(self):
        while not self.sem.acquire(blocking=False):
            sleep(0.5)


class DistributedLock_3(DistributedLock):
    dlm = RedLock([{"host": REDIS_HOST, "port": 6379, "db": 6}, ])
    def __init__(self, id_key):
        DistributedLock.__init__(self, id_key)

    def acquire(self):
        tries = 0
        while tries < 3:
            my_lock = self.dlm.lock("%s" % self.id_key, 1000)
            if not my_lock:
                tries += 1
        if tries == 3:
            raise Exception("No puedo adquirir el lock")

    def release(self):
        pass
