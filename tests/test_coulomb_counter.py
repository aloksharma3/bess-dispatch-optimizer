"""
Unit Tests for CoulombCounter - Battery SoC Estimation

Comprehensive test coverage for real-time SoC tracking.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from battery_model import CoulombCounter


@pytest.fixture
def battery():
    """Fixture: Battery at 50% SoC with 100 Ah capacity"""
    return CoulombCounter(nominal_capacity=100, initial_soc=0.5)


class TestCoulombCounter:
    """Test suite for CoulombCounter SoC estimation"""
    
    # ============================================================
    # CORE FUNCTIONALITY TESTS
    # ============================================================
    
    def test_discharge(self):
        """Test basic discharge: SoC decreases correctly"""
        cc = CoulombCounter(100, 1.0)
        cc.discharge(10, 3600)  # 10A for 1 hour = 10 Ah
        assert cc.get_soc() == pytest.approx(0.9)
    
    
    def test_charge(self):
        """Test basic charge: SoC increases correctly"""
        cc = CoulombCounter(100, 0.5)
        cc.charge(20, 1800)  # 20A for 30 min = 10 Ah
        assert cc.get_soc() == pytest.approx(0.6)
    
    
    def test_bounds(self, battery):
        """Test bounds checking: SoC stays in [0, 1]"""
        # Over-discharge
        battery.discharge(100, 3600)
        assert 0 <= battery.get_soc() <= 1
        assert battery.get_soc() == pytest.approx(0.0)
        
        # Over-charge
        battery.charge(100, 3600)
        assert 0 <= battery.get_soc() <= 1
        assert battery.get_soc() == pytest.approx(1.0)
    
    
    # ============================================================
    # UTILITY METHODS TESTS
    # ============================================================
    
    def test_get_remaining_capacity(self):
        """Test remaining capacity calculation"""
        cc = CoulombCounter(nominal_capacity=100, initial_soc=0.75)
        remaining = cc.get_remaining_capacity()
        assert remaining == pytest.approx(75.0)
    
    
    def test_set_soc(self):
        """Test direct SoC setting with bounds checking"""
        cc = CoulombCounter(100, 1.0)
        
        # Normal set
        cc.set_soc(0.25)
        assert cc.get_soc() == pytest.approx(0.25)
        
        # Over-set (should clamp to 1.0)
        cc.set_soc(1.5)
        assert cc.get_soc() == pytest.approx(1.0)
        
        # Under-set (should clamp to 0.0)
        cc.set_soc(-0.5)
        assert cc.get_soc() == pytest.approx(0.0)
    
    
    # ============================================================
    # EDGE CASES & BOUNDARY TESTS
    # ============================================================
    
    def test_zero_current(self):
        """Test zero current: SoC should not change"""
        cc = CoulombCounter(100, 0.5)
        initial_soc = cc.get_soc()
        
        cc.discharge(0, 3600)  # 0A discharge
        assert cc.get_soc() == pytest.approx(initial_soc)
        
        cc.charge(0, 3600)     # 0A charge
        assert cc.get_soc() == pytest.approx(initial_soc)
    
    
    def test_very_small_time_step(self):
        """Test very small time step"""
        cc = CoulombCounter(100, 1.0)
        cc.discharge(10, 1)  # 10A for 1 second
        
        # Change: 10A * (1s / 3600s/h) / 100Ah = 0.0002778
        expected_soc = 1.0 - (10 * 1 / 3600) / 100
        assert cc.get_soc() == pytest.approx(expected_soc)
    
    
    def test_very_large_time_step(self):
        """Test very large time step"""
        cc = CoulombCounter(100, 1.0)
        cc.discharge(10, 36000)  # 10A for 10 hours
        
        # Change: 10A * (36000s / 3600s/h) / 100Ah = 1.0
        assert cc.get_soc() == pytest.approx(0.0)
    
    
    # ============================================================
    # SEQUENTIAL OPERATIONS TESTS
    # ============================================================
    
    def test_multiple_discharges(self):
        """Test multiple consecutive discharges"""
        cc = CoulombCounter(100, 1.0)
        
        cc.discharge(10, 3600)  # 10%
        assert cc.get_soc() == pytest.approx(0.9)
        
        cc.discharge(10, 3600)  # 10%
        assert cc.get_soc() == pytest.approx(0.8)
        
        cc.discharge(10, 3600)  # 10%
        assert cc.get_soc() == pytest.approx(0.7)
    
    
    def test_mixed_charge_discharge(self):
        """Test mixed charge and discharge operations"""
        cc = CoulombCounter(100, 1.0)
        
        cc.discharge(25, 3600)  # 25% → 75%
        assert cc.get_soc() == pytest.approx(0.75)
        
        cc.charge(10, 3600)     # 10% → 85%
        assert cc.get_soc() == pytest.approx(0.85)
        
        cc.discharge(5, 3600)   # 5% → 80%
        assert cc.get_soc() == pytest.approx(0.80)
    
    
    # ============================================================
    # DIFFERENT CAPACITY TESTS
    # ============================================================
    
    def test_small_capacity(self):
        """Test with small battery capacity"""
        cc = CoulombCounter(nominal_capacity=10, initial_soc=1.0)
        cc.discharge(1, 3600)  # 1A for 1 hour = 1 Ah
        assert cc.get_soc() == pytest.approx(0.9)
    
    
    def test_large_capacity(self):
        """Test with large battery capacity"""
        cc = CoulombCounter(nominal_capacity=1000, initial_soc=1.0)
        cc.discharge(100, 3600)  # 100A for 1 hour = 100 Ah
        assert cc.get_soc() == pytest.approx(0.9)
    
    
    def test_same_current_different_capacities(self):
        """Test that same current affects different batteries differently"""
        # Small battery
        cc_small = CoulombCounter(50, 1.0)
        cc_small.discharge(10, 3600)
        soc_small = cc_small.get_soc()  # 0.8 (20% loss)
        
        # Large battery
        cc_large = CoulombCounter(200, 1.0)
        cc_large.discharge(10, 3600)
        soc_large = cc_large.get_soc()  # 0.95 (5% loss)
        
        # Same current impacts smaller battery more
        assert soc_small < soc_large
        assert soc_small == pytest.approx(0.8)
        assert soc_large == pytest.approx(0.95)
    
    
    # ============================================================
    # INITIALIZATION TESTS
    # ============================================================
    
    def test_initial_soc_default(self):
        """Test default initial SoC is 1.0 (fully charged)"""
        cc = CoulombCounter(nominal_capacity=100)
        assert cc.get_soc() == pytest.approx(1.0)
    
    
    def test_initial_soc_custom(self):
        """Test custom initial SoC"""
        cc = CoulombCounter(nominal_capacity=100, initial_soc=0.5)
        assert cc.get_soc() == pytest.approx(0.5)
    
    
    def test_initial_soc_zero(self):
        """Test initialization at 0% SoC"""
        cc = CoulombCounter(nominal_capacity=100, initial_soc=0.0)
        assert cc.get_soc() == pytest.approx(0.0)
    
    
    # ============================================================
    # REMAINING CAPACITY TESTS
    # ============================================================
    
    def test_remaining_capacity_at_full(self):
        """Test remaining capacity at 100% SoC"""
        cc = CoulombCounter(nominal_capacity=100, initial_soc=1.0)
        assert cc.get_remaining_capacity() == pytest.approx(100.0)
    
    
    def test_remaining_capacity_at_empty(self):
        """Test remaining capacity at 0% SoC"""
        cc = CoulombCounter(nominal_capacity=100, initial_soc=0.0)
        assert cc.get_remaining_capacity() == pytest.approx(0.0)
    
    
    def test_remaining_capacity_after_operations(self):
        """Test remaining capacity after charge/discharge"""
        cc = CoulombCounter(nominal_capacity=100, initial_soc=0.5)
        cc.discharge(10, 3600)  # Discharge 10 Ah
        
        # SoC: 50% - 10% = 40%, Remaining: 40 Ah
        assert cc.get_remaining_capacity() == pytest.approx(40.0)