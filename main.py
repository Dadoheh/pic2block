import argparse
import logging
from tests.functional_test_recognition import ImageCoordinates
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
c_handler = logging.StreamHandler()
c_format = logging.Formatter(
    "%(asctime)s - line: %(lineno)d - %(levelname)s - %(message)s"
)

c_handler.setFormatter(c_format)
# logger.addHandler(c_handler)  # TODO - check the proper setting logging with argparse


def functional_recognition(rectangles, diamonds, inputs):
    check_coordinates = ImageCoordinates()
    string_coordinates = {"rectangles": rectangles, "diamonds": diamonds, "inputs": inputs}

    check_coordinates.check_centre_points(string_coordinates=string_coordinates)


def main(run_with_functional_test: bool):
    recognition = Recognition()
    recognition.read_image()
    rectangles, diamonds, inputs = recognition.find_contours()


    functional_recognition(rectangles, diamonds, inputs)



main(run_with_functional_test=True)


"""

    testing_list = [
        ["c.x:99, c.y:73", "c.x:580, c.y:105", "c.x:484, c.y:47", "c.x:301, c.y:73"],
        ["c.x:124, c.y:213", "c.x:415, c.y:257", "c.x:313, c.y:193"],
        ["c.x:690, c.y:259", "c.x:483, c.y:46", "c.x:600, c.y:193"],
    ]  # testing set

"""