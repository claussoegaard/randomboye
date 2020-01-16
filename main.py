from logs.config import logger
from randomboye import randomboye
import os

# from randomboye.raspi import RaspberryPi
from definitions import FUNCTION_CALL_MSG
import argparse
logger = logger(__name__)


def main():
    logger.debug(FUNCTION_CALL_MSG)
    parser = argparse.ArgumentParser(description="Random Record Boye")

    parser.add_argument("-a", "--auth-token", type=str, metavar="", help="Discogs auth token")
    parser.add_argument("-t", "--test", action='store_true', dest="is_test", help="Test mode")
    parser.add_argument("-r", "--refresh-collection", action='store_true', help="Update Collection on start")

    args = parser.parse_args()
    logger.debug(f"Args: (-a: {args.auth_token}, -t: {args.is_test}, -r: {args.refresh_collection})")
    # If auth-token is missing from args,
    # see if its stored as DISCOGS_TOKEN
    # os environment variable. If neither,
    # Throw exception and exit
    if not args.auth_token:
        logger.debug("Auth-token not in args, trying to find in os.environ")
        try:
            args.auth_token = os.environ["DISCOGS_TOKEN"]
            logger.debug("Auth-token found in os.environ!")
        except KeyError:
            logger.exception("No auth-token arg and environment var DISCOGS_TOKEN not set.")
            logger.debug("Exiting script")
            raise SystemExit

    randomboye.start(args.auth_token, args.is_test, args.refresh_collection)


if __name__ == '__main__':
    main()
