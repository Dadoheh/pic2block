import cv2
import re
from typing import Dict, List, AnyStr, Tuple
from config_log import logger

FILEPATH = "C:\derma-tester\shapes\shapes_resized.png"


class Recognition:
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

    def read_image(self, path_to_picture_file: AnyStr = FILEPATH) -> cv2:
        """Read an image from file.
        Ask a user if none path was given.
        """
        if not path_to_picture_file:
            path_to_picture_file = str(
                input("No path to picture was given. Please insert the proper path.")
            )
        self.img = cv2.imread(path_to_picture_file)
        return self.img

    def _convert_to_gray(self) -> cv2:
        """Convert image into grayscale image and set a threshold."""
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        _, threshold = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

        return gray, threshold

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

            self._recognise_shape(approx)
        return logger.critical(
            f"\nself.rectangles {self.rectangles}\nself.diamonds: {self.diamonds}\nself.inputs: {self.inputs}"
        )

    @staticmethod
    def _find_center_point_of_shape(shape: cv2) -> (int, int):
        if shape["m00"] != 0.0:  # finding center point of shape
            x = int(shape["m10"] / shape["m00"])
            y = int(shape["m01"] / shape["m00"])
            logger.debug(f"m00 center value: {shape['m00']}")
            logger.debug(f"m00 center value: {shape['m10']}")
            logger.debug(f"m00 center value: {shape['m01']}")
            return x, y
        else:
            return None, None

    def _recognise_shape(self, approx: List) -> None:
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
        """
        if len(approx) == 4:  # input, exercise, if has 4 points
            self.shapes_dictionary[f"c.x:{self.x}, c.y:{self.y}"] = {
                "Quadrilateral": approx.tolist()
            }  # Quadrilateral

        elif len(approx) > 10:  # or ellipsoid for Start/Stop - plenty of points
            self.shapes_dictionary[f"c.x:{self.x}, c.y:{self.y}"] = {
                "Start/Stop": approx.tolist()
            }

        quadrilateral_types_dictionary = self._recognise_quadrilateral()
        ellipsoid_dictionary = self._recognise_ellipsoid()

    def _recognise_quadrilateral(self) -> None:
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
            for if: x1==x3, y2==y4 # TODO

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

    def _recognise_ellipsoid(self) -> Dict:
        pass

    @staticmethod
    def cut_nested_empty_list(nested_list: List) -> List:
        """Cut unimportant nesting"""
        improved_list = []
        for element in nested_list:
            improved_list.append(element[0])
        logger.error(f"improved_list: {improved_list}")
        return improved_list

