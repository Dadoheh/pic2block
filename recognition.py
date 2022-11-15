import cv2
from typing import Dict, List, AnyStr

FILEPATH = "shapes/shapes2.png"


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
    ) -> Dict:  # TODO - try to resolve state of public/private method - find_contours
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

            print(f"\n\n# approx variable: {approx}\n\n")  # Logger debug in the future
            print(
                f"\n\n# len of approx variable: {len(approx)}\n\n"
            )  # Logger debug in the future

            cv2.drawContours(self.img, [contour], 0, (255, 0, 0), 5)

            M = cv2.moments(contour)
            print(f"M center value: {M}")  # Logger debug in the future

            x, y = self._find_center_point_of_shape(shape=M)  # TODO - to improve

            if all(v is not None for v in (x, y)):
                self.x = x
                self.y = y

            self._recognise_shape(approx)
        return self.shapes_dictionary

    @staticmethod
    def _find_center_point_of_shape(shape: cv2) -> (int, int):
        if shape["m00"] != 0.0:  # finding center point of shape
            x = int(shape["m10"] / shape["m00"])
            y = int(shape["m01"] / shape["m00"])
            print(f"m00 center value: {shape['m00']}")
            print(f"m00 center value: {shape['m10']}")
            print(f"m00 center value: {shape['m01']}")
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

    def _recognise_quadrilateral(self) -> Dict:
        """
        Recognise between 4 accessible quadrilaterals.
        - input statement
        - exercise block
        - if block

        By a similarity of xs, ys - make a decision what is the shape look like.
        If xs, ys does not have any similarity - then return log.error

        Similarity:
        for (x1,y1), (x2,y2), (x3,y3), (x4,y4)
            for input: y1==y4, y2==y3
            for exercise: x1==x2, y2==y3, x3==x4, y1==y4
            for if: x1==x3, y2==y4

        x and y can be inaccurate between themselves (around 5 pixels)

        Insert centre coordinates into appropriate lists: rectangles, diamonds, inputs.
        """
        print(self.shapes_dictionary)
        for key in self.shapes_dictionary.keys():
            if "Quadrilateral" in self.shapes_dictionary[key]:
                coordinates = self.shapes_dictionary[key]["Quadrilateral"]
                coordinates = self.cut_nested_empty_list(coordinates)
                print(f"Checking similarities on coordinates: {coordinates}")
                if (
                    abs(coordinates[0][0] - coordinates[2][0]) < 5
                    and abs(coordinates[1][1] - coordinates[3][1]) < 5
                ):  # matrix 4x2
                    self.diamonds.append(key)
                elif (
                    abs(coordinates[0][1] - coordinates[3][1]) < 5
                    and abs(coordinates[1][1] - coordinates[2][1]) < 5
                ):
                    self.inputs.append(key)
                elif (
                    abs(coordinates[0][0] - coordinates[1][0]) < 5
                    and abs(coordinates[1][1] - coordinates[2][1]) < 5
                    and abs(coordinates[2][0] - coordinates[3][0]) < 5
                    and abs(coordinates[0][1] == coordinates[3][1]) < 5
                ):
                    self.rectangles.append(key)
                else:
                    # raise AttributeError("Inappropriate quadrilateral input!")
                    print("No type of quadrilateral found.")

        self.rectangles = list(set(self.rectangles))
        self.diamonds = list(set(self.diamonds))
        self.inputs = list(set(self.inputs))

        print(
            f"self.rectangles {self.rectangles}\nself.diamonds: {self.diamonds}\nself.inputs: {self.inputs}"
        )

    def _recognise_ellipsoid(self) -> Dict:
        pass

    @staticmethod
    def cut_nested_empty_list(nested_list: List) -> List:
        """Cut unimportant nesting"""
        improved_list = []
        for element in nested_list:
            improved_list.append(element[0])
        print(f"improved_list: {improved_list}")
        return improved_list


recognition = Recognition()
recognition.read_image()
print(f"\n{recognition.find_contours()}")
