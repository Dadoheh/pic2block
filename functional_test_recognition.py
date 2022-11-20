import re
from config_log import logger
from recognition import FILEPATH
from typing import List, Union, Tuple, AnyStr


class ImageCoordinates:
    def __init__(self, imagepath=FILEPATH):
        self.imagepath: AnyStr = imagepath
        self.centre_coordinates: List = []

    def _get_centre_coordinates(self, list_of_shapes: List[List[AnyStr]]) -> List[Tuple]:
        if list_of_shapes:
            for shape in list_of_shapes:
                self.centre_coordinates.append(self._parse_numbers_from_coordinates(shape))
        return self.centre_coordinates

    def _parse_numbers_from_coordinates(self, string_shape: List[AnyStr]) -> Tuple:
        for element in string_shape:
            x_cord = int((re.search("c\.x:([0-9]*)", element).group(1)))
            logger.debug(f"x_cord: {x_cord}")
        pass

    def _draw_coordinates_on_picture(self):
        pass

    def check_centre_points(self):
        self._get_centre_coordinates()
        self._parse_numbers_from_coordinates()
