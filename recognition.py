
import cv2


class Recognition:
    """Recognise and represent the shape of block.

    Attributes
    ___________
    img : cv2
        Image of the shape(s)
    path_to_picture_file : str
        Proper path to file with picture of shape(s).

    Public methods
    _________
    read_image():
    find_contours():

    Private methods
    ---------
    _convert_to_gray():
    _recognise_shape():
    _find_center_point_of_shape():
    """
    def __init__(self):
        """Construct the beginning attributes for recognising shapes.

        Parameters
        ___________
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

    def read_image(self, path_to_picture_file: str = "shapes.png") -> cv2:
        """Read an image from file.
        Ask a user if none path was given.
        """
        if not path_to_picture_file:
            path_to_picture_file = str(input("No path to picture was given. Please insert the proper path."))
        self.img = cv2.imread(path_to_picture_file)
        return self.img

    def _convert_to_gray(self) -> cv2:
        """Convert image into grayscale image and set a threshold."""
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        _, threshold = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

        return gray, threshold

    def find_contours(self) -> cv2.findContours:  # TODO - try to resolve state of public/private method - find_contours
        """Find contours of shape by given threshold."""
        _, threshold = self._convert_to_gray()
        contours, _ = cv2.findContours(
            threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )

        #  list for storing names of shapes
        i = 0
        for contour in contours:

            # here we are ignoring first counter because
            # findcontour function detects whole image as shape
            if i == 0:
                i = 1
                continue

            # cv2.approxPolyDP() function to approximate the shape
            approx = cv2.approxPolyDP(
                contour, 0.01 * cv2.arcLength(contour, True), True
            )

            print(f'\n\n# approx variable: {approx}\n\n')  # Logger debug in the future
            print(f'\n\n# len of approx variable: {len(approx)}\n\n')  # Logger debug in the future

            # using drawContours() function
            cv2.drawContours(self.img, [contour], 0, (255, 0, 0), 5)

            M = cv2.moments(contour)
            print(f"M center value: {M}")  # Logger debug in the future

            x, y = self._find_center_point_of_shape(shape=M)  # TODO - to improve

            if all(v is not None for v in (x, y)):
                self.x = x
                self.y = y

            self._recognise_shape(approx)

        self._show_window(self.img)

    @staticmethod
    def _find_center_point_of_shape(shape: cv2) -> (int, int):
        #  finding center point of shape
        if shape['m00'] != 0.0:
            x = int(shape['m10'] / shape['m00'])
            y = int(shape['m01'] / shape['m00'])
            print(f"m00 center value: {shape['m00']}")
            print(f"m00 center value: {shape['m10']}")
            print(f"m00 center value: {shape['m01']}")
            return x, y
        else:
            return None, None

    def _recognise_shape(self, approx):
        """Recognise between 4 accessible statements.
            - input statement
            - exercise block
            - if block
            - start/finish

            By a similarity of xs, ys - make a decision what is the shape look like.
            If xs, ys does not have any similarity - then return log.error
        """
        # naming shapes by number of points
        if len(approx) == 3:
            cv2.putText(self.img, 'Triangle', (self.x, self.y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        elif len(approx) == 4:
            print(f'\n\n ## Quadrilateral value: {approx}'
                  f'\nLets try finding some correlations')
            cv2.putText(self.img, 'Quadrilateral', (self.x, self.y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        elif len(approx) == 5:
            cv2.putText(self.img, 'Pentagon', (self.x, self.y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        elif len(approx) == 6:
            cv2.putText(self.img, 'Hexagon', (self.x, self.y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        else:
            cv2.putText(self.img, 'circle', (self.x, self.y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

    @staticmethod
    def _show_window(img):
        cv2.imshow('shapes', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


recognition = Recognition()
recognition.read_image()
recognition.find_contours()
