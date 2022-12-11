import cv2
from typing import Dict, List, AnyStr, Tuple
import numpy
from config_log import logger

from base import AbstractRecognition
from definitions import RESIZED_SHAPES_PNG


class Recognition(AbstractRecognition):
    """Recognise and represent the shape of block.

    Attributes

    img : cv2
        Image of the shape(s)
    path_to_picture_file : str
        Proper path to file with picture of shape(s).

    Public methods

    read_image():
    find_contours():

    Private methods

    _convert_to_gray():
    _recognise_shape():
    _find_center_point_of_shape():
    _recognise_ellipsoid():
    _recognise_quadrilateral():
    """

    def __init__(self):
        """Construct the beginning attributes for recognising shapes.

        Parameters

        img : cv2
            image with shapes to be read
        x : int
            x-coordinate from center of the shape.
        y : int
            y-coordinate from center of the shape.

        """
        self.img: cv2 = None
        self.x: int = 0
        self.y: int = 0
        self.shapes_dictionary: Dict = {}
        self.rectangles: List = []
        self.diamonds: List = []
        self.inputs: List = []

    def read_image(self, path_to_picture_file: AnyStr = RESIZED_SHAPES_PNG) -> cv2:
        """Read an image from file.
        Ask a user if none path was given.
        """
        if not path_to_picture_file:
            path_to_picture_file = str(
                input("No path to picture was given. Please insert the proper path.")
            )
        self.img = cv2.imread(path_to_picture_file)
        return self.img

    def find_contours(
        self,
    ) -> Tuple:
        """Find contours of shape by given threshold."""
        _, threshold = self._convert_to_gray()
        contours, _ = cv2.findContours(
            threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )

        i = 0
        for contour in contours:  # list for storing names of shapes

            if (
                i == 0
            ):  # miss 0 because findcontour() function detects whole image as shape
                i = 1
                continue

            approx = cv2.approxPolyDP(
                contour,
                0.01 * cv2.arcLength(contour, True),
                True,  # approximate the shape
            )

            logger.debug(f"\n\n# approx variable: {approx}\n\n")
            logger.debug(
                f"\n\n# len of approx variable: {len(approx)}\n\n"
            )  # Logger debug in the future

            cv2.drawContours(self.img, [contour], 0, (255, 0, 0), 5)

            M = cv2.moments(contour)
            logger.debug(f"M center value: {M}")

            x, y = self._find_center_point_of_shape(shape=M)  # TODO - to improve

            if all(v is not None for v in (x, y)):
                self.x = x
                self.y = y

            self.recognise_shape(approx)
        return logger.critical(
            f"\nself.rectangles {self.rectangles}\nself.diamonds: {self.diamonds}\nself.inputs: {self.inputs}"
        )

    def recognise_quadrilateral(self) -> None:
        """
        Recognise between 4 accessible quadrilaterals.
        - input statement
        - exercise block
        - if block

        By a similarity of xs, ys - make a decision what is the shape look like.
        If xs, ys does not have any similarity - then return log.error

        Similarity:
        for (x1,y1), (x2,y2), (x3,y3), (x4,y4)
            for input: y1==y4, y2==y3,
            for exercise: x1==x2, y2==y3, x3==x4, y1==y4
            for if: x1==x3, y2==y4 # TODO Check if better similarities exist

        x and y can be inaccurate between themselves (around 5 pixels)

        Insert centre coordinates into appropriate lists: rectangles, diamonds, inputs.
        """
        logger.info(f"Shapes_dictionary: {self.shapes_dictionary}")
        for key in self.shapes_dictionary.keys():
            if "Quadrilateral" in self.shapes_dictionary[key]:
                coordinates = self.shapes_dictionary[key]["Quadrilateral"]
                coordinates = self.cut_nested_empty_list(coordinates)
                logger.info(
                    f"Checking similarities on coordinates: {coordinates}"
                )  # the order matters
                if (
                    abs(coordinates[0][0] - coordinates[1][0]) < 5
                    and abs(coordinates[1][1] - coordinates[2][1]) < 5
                    and abs(coordinates[2][0] - coordinates[3][0]) < 5
                    and abs(coordinates[0][1] == coordinates[3][1]) < 5
                ):
                    logger.info(f"Found rectangle at: {key}")
                    self.rectangles.append(key)
                elif (
                    abs(coordinates[0][0] - coordinates[2][0]) < 5
                    and abs(coordinates[1][1] - coordinates[3][1]) < 5
                ):  # matrix 4x2
                    logger.info(f"Found diamond at: {key}")
                    self.diamonds.append(key)  # romb
                elif (
                    abs(coordinates[0][1] - coordinates[3][1]) < 5
                    and abs(coordinates[1][1] - coordinates[2][1]) < 5
                ) or (
                    coordinates[0][0]
                    != coordinates[1][0]
                    != coordinates[2][0]
                    != coordinates[3][0]  # TODO Refactor
                ):
                    logger.info(f"Found input at: {key}")
                    self.inputs.append(key)
                else:
                    # raise AttributeError("Inappropriate quadrilateral input!")
                    logger.warning("No type of quadrilateral found.")

        self.rectangles = list(set(self.rectangles))
        self.diamonds = list(set(self.diamonds))
        self.inputs = list(set(self.inputs))
        self._clear_up_similar_inputs_from_rectangles_and_diamonds()

    def recognise_shape(self, approx: numpy.ndarray) -> Dict:
        """
        Make a decision if a shape is quadrilateral or ellipsoid. Create a proper self.shapes_dictionary.

        :param approx: List of approximated centres
        :return: Dictionaries with quadrilateral and ellipsoid shapes.

        Structure of the dictionary:

        {"centre x coordinate, centre y coordinate":{"Type of shape": array(list of points)}}

        e.g.:
        {'c.x:477, c.y:499':
            {'Quadrilateral': array([[[477, 384]], [[349, 499]], [[477, 614]],
                [[605, 499]]])},
        'c.x:332, c.y:215':
            {'Start/Stop': array([[[144, 210]], [[153, 245]], [[187, 276]],
                [[313, 310]], [[451, 289]], [[494, 264]], [[168, 169]]],)}}
        """
        if len(approx) == 4:  # input, exercise, if has 4 points
            self.shapes_dictionary[f"c.x:{self.x}, c.y:{self.y}"] = {
                "Quadrilateral": approx.tolist()
            }  # Quadrilateral

        elif len(approx) > 10:  # or ellipsoid for Start/Stop - plenty of points
            self.shapes_dictionary[f"c.x:{self.x}, c.y:{self.y}"] = {
                "Start/Stop": approx.tolist()
            }

        self.recognise_ellipsoid()
        self.recognise_quadrilateral()
        return self.shapes_dictionary


    def recognise_ellipsoid(self) -> Dict:
        pass
        # TODO https://github.com/Dadoheh/pic2block/issues/17
        logger.debug("To be done")
