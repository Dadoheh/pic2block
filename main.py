import argparse
import logging
from config_log import c_format, c_handler, logger
from recognition import Recognition

parser = argparse.ArgumentParser()
parser.add_argument(
    '-d', '--debug',
    help="Debugging statements and everything else too.",
    action="store_const", dest="loglevel", const=logging.DEBUG,
    default=logging.INFO,
)
parser.add_argument(
    '-i', '--info',
    help="Everything but Debug",
    action="store_const", dest="loglevel", const=logging.INFO,
)
parser.add_argument(
    '-w', '--warning',
    help="Only Warnings, Critical and Errors",
    action="store_const", dest="loglevel", const=logging.WARNING,
)
parser.add_argument(
    '-c', '--critical',
    help="Only Critical and Errors",
    action="store_const", dest="loglevel", const=logging.CRITICAL,
)
args = parser.parse_args()
logging.basicConfig(level=args.loglevel)

c_handler.setFormatter(c_format)
logger.addHandler(c_handler)

def main():
    recognition = Recognition()
    recognition.read_image()
    recognition.find_contours()


main()