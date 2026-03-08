# BESS Dispatch Optimizer

Battery Energy Storage System (BESS) dispatch optimizer with Coulomb Counter-based SoC estimation.

## Overview

This project develops a dispatch optimizer for battery energy storage systems with:
- **Coulomb Counter**: Real-time State of Charge (SoC) estimation
- **Unit Tests**: Comprehensive test coverage
- **PyBaMM Integration**: Battery electrochemical modeling (coming soon)

## Project Structure
```
bess-dispatch-optimizer/
├── battery_model/
│   ├── coulomb_counter.py      # SoC estimation
│   ├── spm_simulator.py        # PyBaMM wrapper
│   └── __init__.py
├── tests/
│   ├── test_coulomb_counter.py # Unit tests
│   └── __init__.py
├── notebooks/
│   └── Pybamm_run_spm.ipynb
├── results/
├── README.md                   # This file
├── requirements.txt
└── .gitignore
```

## Installation
```bash
# Clone and setup
git clone 
cd bess-dispatch-optimizer

# Install dependencies
pip install -r requirements.txt
```

## Quick Start
```python
from battery_model import CoulombCounter

# Initialize: 100 Ah battery at 100% SoC
cc = CoulombCounter(nominal_capacity=100, initial_soc=1.0)

# Discharge 10A for 1 hour
cc.discharge(current_A=10, time_step_s=3600)
print(f"SoC: {cc.get_soc():.2%}")  # Output: 90%
```

## Testing
```bash
pytest tests/test_coulomb_counter.py -v
```

### Test Results
- ✅ test_discharge: PASSED
- ✅ test_charge: PASSED
- ✅ test_bounds: PASSED

## API Reference

### CoulombCounter

**Methods:**
- `discharge(current_A, time_step_s)` - Decrease SoC
- `charge(current_A, time_step_s)` - Increase SoC
- `get_soc()` - Get current SoC [0, 1]
- `set_soc(target_soc)` - Calibrate SoC
- `get_remaining_capacity()` - Get remaining Ah

## Dependencies

- numpy >= 1.19.0
- matplotlib >= 3.3.0
- pytest >= 6.0.0
- pybamm >= 0.15.0 (optional)

## Roadmap

- [x] Coulomb Counter implementation
- [x] Unit tests (3 test cases)
- [ ] SoH degradation modeling
- [ ] Dispatch optimization (RL agent)
- [ ] Multi-cycle simulation

## License

MIT License