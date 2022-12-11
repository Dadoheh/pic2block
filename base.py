import re
import cv2
from abc import ABC, abstractmethod
from typing import Dict, List, AnyStr, Tuple
from config_log import logger
from definitions import RESIZED_SHAPES_PNG


class AbstractRecognition(ABC):
    """Recognition Class - complete process."""

    def __init__(self):
        """Construct the beginning attributes for recognising shapes.

        Parameters

        :param img : cv2 image with shapes to be read
        :param x : int x-coordinate from center of the shape.
        :param y : int y-coordinate from center of the shape.

        """
        self.img: cv2 = None
        self.x: int = 0
        self.y: int = 0
        self.shapes_dictionary: Dict = {}
        self.rectangles: List = []
        self.diamonds: List = []
        self.inputs: List = []

    @abstractmethod
    def read_image(self, path_to_picture_file: AnyStr = RESIZED_SHAPES_PNG) -> cv2:
        """
        Read an image from file.
        Ask a user if none path was given.

        :param path_to_picture_file: Filepath to the picture
        :return: cv2
        """
        pass

    def _convert_to_gray(self) -> cv2:
        """
        Convert image into grayscale image and set a threshold.
        :return: gray picture, threshold
        """
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        _, threshold = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

        return gray, threshold

    @abstractmethod
    def find_contours(self) -> Tuple:
        """
        Find contours of shape by given threshold.
        :return: Tuple with contours
        """
        pass

    @staticmethod
    def _find_center_point_of_shape(shape: cv2) -> (int, int):
        """
        Find the central shape point. Method is used for functional testing.
        :return: int x_central, int y_central
        """
        if shape["m00"] != 0.0:  # finding center point of shape
            x = int(shape["m10"] / shape["m00"])
            y = int(shape["m01"] / shape["m00"])
            logger.debug(f"m00 center value: {shape['m00']}")
            logger.debug(f"m00 center value: {shape['m10']}")
            logger.debug(f"m00 center value: {shape['m01']}")
            return x, y
        else:
            return None, None

    @abstractmethod
    def recognise_shape(self, approx: List) -> Dict:
        """
        Make a decision if a shape is quadrilateral or ellipsoid. Create a proper self.shapes_dictionary.

        Structure of the dictionary:

        {"centre x coordinate, centre y coordinate":{"Type of shape": array(list of points)}}

        e.g.:
        {'c.x:477, c.y:499':
            {'Quadrilateral': array([[[477, 384]], [[349, 499]], [[477, 614]],
                [[605, 499]]])},
        'c.x:332, c.y:215':
            {'Start/Stop': array([[[144, 210]], [[153, 245]], [[187, 276]],
                [[313, 310]], [[451, 289]], [[494, 264]], [[168, 169]]],)}}

        :param approx: List of approximated centres
        :return: Dictionaries with quadrilateral and ellipsoid shapes.
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def recognise_ellipsoid(self) -> Dict:
        """Recognise start/end blocks."""
        pass

    def _clear_up_similar_inputs_from_rectangles_and_diamonds(self) -> None:
        """
        Delete similar centre records from list self.inputs - to avoid repetitive points.
        every record which stayed will be recognised correctly as self.input
            example data structures:
                    self.rectangles['c.x:338, c.y:251', 'c.x:1647, c.y:160', 'c.x:1025, c.y:251', 'c.x:1975, c.y:359']
                    self.diamonds: ['c.x:1416, c.y:879', 'c.x:426, c.y:730', 'c.x:1067, c.y:658']
                    self.inputs: ['c.x:2349, c.y:887', 'c.x:2044, c.y:660', 'c.x:1647, c.y:160', 'c.x:1025, c.y:251',
                                  'c.x:1975, c.y:359', 'c.x:2350, c.y:887', 'c.x:2044, c.y:659', 'c.x:338, c.y:251']
        """
        for element in list(self.inputs):
            if element in self.rectangles or element in self.diamonds:
                self.inputs.remove(element)
        self._clear_up_similar_inputs_from_inputs()
        logger.info(f"Cleared list of inputs: {self.inputs}")
        self._clear_up_similar_inputs_from_inputs()

    def _clear_up_similar_inputs_from_inputs(self) -> None:
        """
        Delete repetitive inputs from self.inputs.
        """
        list_of_repetitive_items = []
        for element in self.inputs:
            x_cord = int((re.search("c\.x:([0-9]*)", element).group(1)))
            logger.debug(f"x_cord: {x_cord}")

            # TODO - TO REFACTOR - check if element in self.inputs[self.inputs.index(element)+1::]
            if not abs((self.inputs.index(element)) - len(self.inputs)) < 0:
                for sub_element in range(
                    self.inputs.index(element) + 1, len(self.inputs)
                ):
                    x_sub_cord = int(
                        (re.search("c\.x:([0-9]*)", self.inputs[sub_element])).group(1)
                    )
                    if abs(x_cord - x_sub_cord) < 5:
                        logger.debug(f"x_sub_cord: {x_sub_cord}")
                        list_of_repetitive_items.append(
                            self.inputs[sub_element]
                        )  # pes. x^2 complexity - to refactor

        logger.critical(list_of_repetitive_items)

        for element in list_of_repetitive_items:
            self.inputs.remove(element)

    @staticmethod
    def cut_nested_empty_list(nested_list: List) -> List:
        """
        Cut unimportant nesting from list.

        :param nested_list: List with redundant nesting.
        :return: List with cut parenthesis
        """
        improved_list = []
        for element in nested_list:
            improved_list.append(element[0])
        logger.error(f"improved_list: {improved_list}")
        return improved_list
