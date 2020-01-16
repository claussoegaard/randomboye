from randomboye.discogs_collection import DiscogsCollection
from multiprocessing import Process
from logs.config import logger
logger = logger(__name__)


def start(auth_token, is_test, refresh_collection):
    if not is_test:
        from randomboye.raspi import RaspberryPi
        pi = Process(target=RaspberryPi)
        pi.start()
        logger.debug("After Raspberry Pi Is Init")
        logger.debug(f"{pi}")
    else:
        pass

    dc = DiscogsCollection(auth_token=auth_token, refresh_collection=refresh_collection)
    dc.get_random_record()
