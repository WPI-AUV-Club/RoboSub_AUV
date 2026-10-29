import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import controls
import numpy as np
import pytest
import rclpy


@pytest.fixture(scope="function")
def ros_context():
    rclpy.init()
    yield
    rclpy.shutdown()


def test_sanity():
    assert 1 == 1


def test_plos(ros_context):
    node = controls.ControlsNode()
    path = [np.array([1, 0, 0]).T, np.array([2, 0, 0]).T]
    assert (0, 0, 0) == node.plos(path, node.LFindex)
