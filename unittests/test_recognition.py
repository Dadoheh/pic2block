import unittest
from numpy import array
from unittest.mock import Mock, MagicMock, patch
from pic2block.recognition import Recognition


class TestRecognition(unittest.TestCase):
    def setUp(self) -> None:
        self.object = Recognition()

    def test_find_contours(self):
        pass

    def test_recognize_shape(self):

        self.object.recognise_ellipsoid = Mock()
        self.object.recognise_quadrilateral = Mock()
        approx_1 = [[[844, 234]], [[754, 287]], [[539, 286]], [[628, 233]]]
        output_1 = self.object.recognise_shape(array(approx_1))

        self.assertEqual(output_1,
                         {'c.x:0, c.y:0': {'Quadrilateral': [[[844, 234]], [[754, 287]], [[539, 286]], [[628, 233]]]}})
        

    def test_read_image(self):
        pass

    def cut_nested_empty_list(self):
        pass
