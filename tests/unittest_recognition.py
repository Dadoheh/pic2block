import unittest
from unittest.mock import Mock, MagicMock
import pic2block
from pic2block.recognition import Recognition


class TestRecognition(unittest.TestCase):
    def setUp(self) -> None:
        self.object = Recognition

    def test_find_contours(self):
        self.object._recognise_shape = MagicMock

    def test_read_image(self):
        pass

    def cut_nested_empty_list(self):
        pass
