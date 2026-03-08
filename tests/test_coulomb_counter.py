import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from battery_model import CoulombCounter


@pytest.fixture
def battery():
    return CoulombCounter(nominal_capacity=100, initial_soc=0.5)


class TestCoulombCounter:

    def test_discharge(self):
        cc = CoulombCounter(100, 1.0)
        cc.discharge(10, 3600)
        assert cc.get_soc() == pytest.approx(0.9)

    def test_charge(self):
        cc = CoulombCounter(100, 0.5)
        cc.charge(20, 1800)
        assert cc.get_soc() == pytest.approx(0.6)

    def test_bounds(self, battery):
        battery.discharge(100, 3600)
        assert 0 <= battery.get_soc() <= 1

        battery.charge(100, 3600)
        assert 0 <= battery.get_soc() <= 1