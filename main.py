from logs.config import logger
from randomboye.discogs_collection import DiscogsCollection
from randomboye.raspi import RaspberryPi
from definitions import FUNCTION_CALL_MSG
import argparse

logger = logger(__name__)

parser = argparse.ArgumentParser(description="Random Record Boye")

parser.add_argument("-a", "--auth-token", type=str, metavar="", help="Discogs auth token")
parser.add_argument("-t", "--test", action='store_true', dest="is_test", help="Test mode")
parser.add_argument("-u", "--update", action='store_true', help="Update Collection on start")

args = parser.parse_args()


def main():
    logger.debug(FUNCTION_CALL_MSG)

    pi = RaspberryPi()

    # dc = DiscogsCollection(token=args.auth_token, refresh_collection=args.update)

    # dc.get_random_record()


if __name__ == '__main__':
    main()
