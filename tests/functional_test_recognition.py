import re
import cv2
from config_log import logger
from recognition import FILEPATH
from typing import List, Tuple, AnyStr


class ImageCoordinates:
    """
    Print points with coordinates in shapes.
    Functional test for checking if every shape is parsed correctly
    The output picture should contain:
        - a shape
        - coordinates (x,y)
        - type of taken shapes.
    """

    def __init__(
        self,
        imagepath=FILEPATH,
        default_quadrilateral_sequence=("rectangles", "diamonds", "inputs"),
    ):
        """Create output centre_coordinates list.
        :param default_quadrilateral_sequence: is responsible for the proper sequence of quadrilateral datasets.
        :param imagepath: path to picture."""
        self.imagepath: AnyStr = imagepath
        self.centre_coordinates: List = []
        self.default_quadrilateral_sequence = default_quadrilateral_sequence

    def check_centre_points(self, list_with_string_coordinates: List) -> None:
        """Start calling private methods for drawing points in picture FILEPATH.
        :param list_with_string_coordinates: a list with parsed coordinates by recognition.py
        """
        if list_with_string_coordinates:
            self.centre_coordinates = self._get_centre_coordinates(
                list_with_string_coordinates
            )
            self._draw_coordinates_on_picture()
        else:
            logger.warning("List with coordinates is required!")

    def _get_centre_coordinates(
        self, list_with_string_coordinates: List
    ) -> List[Tuple]:
        """
        Create a list of int x,y coordinates.
         :param list_with_string_coordinates: a list with parsed coordinates by recognition.py
         The example list is:
            [[[1025, 251], [338, 251], [1975, 359], [1647, 160]],
            [[1416, 879], [426, 730], [1067, 658]], [[2044, 660], [2349, 887]]].
        """
        for shape in list_with_string_coordinates:
            self.centre_coordinates.append(
                list(self._parse_numbers_from_coordinates(shape))
            )
        return self.centre_coordinates

    def _draw_coordinates_on_picture(self):
        """Draw coordinates on the picture from FILEPATH. Type x,y coordinates and type of quadrilateral."""
        logger.debug(f"Parsed quadrilateral: {self.centre_coordinates}")
        image = cv2.imread(self.imagepath)

        # converting image into grayscale image
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # setting threshold of gray image
        _, threshold = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        for quadrilateral in self.centre_coordinates:
            for subelement in quadrilateral:
                logger.error(subelement)
                cv2.circle(
                    image,
                    (subelement[0], subelement[1]),
                    radius=0,
                    color=(0, 0, 255),
                    thickness=-1,
                )
                cv2.putText(
                    image,
                    ".",
                    (subelement[0], subelement[1]),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 0),
                    2,
                )

        cv2.imshow("output", image)
        cv2.waitKey(0)

    @staticmethod
    def _parse_numbers_from_coordinates(string_shape: List[AnyStr]) -> Tuple:
        """Iterate through all 3 lists. Regex match x,y coordinates."""
        for element in string_shape:
            list_of_centre_coordinates = []
            x_cord = int((re.search("c\.x:([0-9]*)", element).group(1)))
            logger.debug(f"x_cord: {x_cord}")
            y_cord = int((re.search("c\.y:([0-9]*)", element).group(1)))
            logger.debug(f"y_cord: {y_cord}")
            list_of_centre_coordinates.append(x_cord)
            list_of_centre_coordinates.append(y_cord)
            yield list_of_centre_coordinates


check_coordinates = ImageCoordinates()
list_a = [
    ["c.x:99, c.y:73", "c.x:580, c.y:105", "c.x:484, c.y:47", "c.x:301, c.y:73"],
    ["c.x:124, c.y:213", "c.x:415, c.y:257", "c.x:313, c.y:193"],
    ["c.x:690, c.y:259", "c.x:483, c.y:46", "c.x:600, c.y:193"],
]  # testing set
# TODO - Send testing set from recognition.py and validate it. https://github.com/Dadoheh/pic2block/issues/12
check_coordinates.check_centre_points(list_with_string_coordinates=list_a)
