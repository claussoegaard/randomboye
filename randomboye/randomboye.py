from randomboye.discogs_collection import DiscogsCollection

from logs.config import logger
logger = logger(__name__)


def start(auth_token, is_test, refresh_collection):
    if not is_test:
        from randomboye.raspi import RaspberryPi
        RaspberryPi()
        logger.debug("After Raspberry Pi Is Init")
    else:
        pass

    dc = DiscogsCollection(auth_token=auth_token, refresh_collection=refresh_collection)
    dc.get_random_record()
