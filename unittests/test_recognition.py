import pytest
from numpy import array
from unittest.mock import MagicMock
from pic2block.recognition import Recognition

approx_1 = [[[844, 234]], [[754, 287]], [[539, 286]], [[628, 233]]]
approx_2 = [
    [[-1, -1]],
    [[-2, -2]],
    [[-3, -3]],
    [[-4, -4]],
    [[1, 1]],
    [[2, 2]],
    [[3, 3]],
    [[4, 4]],
    [[5, 5]],
    [[6, 6]],
    [[7, 7]],
]
output_1 = {
    "c.x:0, c.y:0": {
        "Quadrilateral": [[[844, 234]], [[754, 287]], [[539, 286]], [[628, 233]]]
    }
}
output_2 = {
    "c.x:0, c.y:0": {
        "Start/Stop": [
            [[-1, -1]],
            [[-2, -2]],
            [[-3, -3]],
            [[-4, -4]],
            [[1, 1]],
            [[2, 2]],
            [[3, 3]],
            [[4, 4]],
            [[5, 5]],
            [[6, 6]],
            [[7, 7]],
        ]
    }
}


@pytest.fixture
def object(monkeypatch):

    monkeypatch.setattr("pic2block.recognition.logger", MagicMock())
    monkeypatch.setattr(
        "pic2block.recognition.Recognition.recognise_quadrilateral", MagicMock()
    )
    recognition = Recognition()
    return recognition


@pytest.mark.parametrize("approx, output", [(approx_1, output_1), (approx_2, output_2)])
def test_recognize_shape(approx, output, object):

    answer = object.recognise_shape(array(approx))
    assert type(answer) is dict
    assert answer == output


def test_recognize_shape_error(object):

    approx = [[[]]]
    with pytest.raises(ValueError) as exc:
        object.recognise_shape(array(approx))
        assert "No approx points!" in str(exc.value)
