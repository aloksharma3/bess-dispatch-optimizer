# BESS Dispatch Optimizer

Reinforcement learning driven Energy Storage System (BESS) dispatch optimizer using three sophisticated components: 
(1) Coulomb counter for real-time SoC estimation, 
(2) physics-based SEI degradation modeling using PyBaMM for battery SoH tracking.
(3) Proximal Policy Optimization (PPO) agent that learns optimal charge/discharge strategies
Learns to balance short-term revenue against long-term battery health

## Overview

### The Problem

Battery energy storage systems need to make real-time charge/discharge decisions that:
- **Maximize revenue**: Charge when prices are low, discharge when prices are high
- **Minimize degradation**: Protect battery from excessive cycling (extends lifespan)
- **Balance both**: Short-term profit vs long-term asset preservation

**Challenge**: These goals conflict. The system must learn when to sacrifice short-term revenue to protect battery health.



### The Solution

A reinforcement learning agent (PPO algorithm) that learns optimal dispatch by observing:
- **State**: [SoC, SoH] - Current charge level and battery health
- **Reward**: Revenue - Degradation penalty
- **Goal**: Maximize long-term profit, not just immediate revenue 

**Phase 1: Coulomb Counter**
- Discharge/charge SoC estimation
- Bounds checking [0, 1]
- unit tests passing

**Phase 2: SoH Degradation**
- PyBaMM SEI degradation simulator
- Efficient SoH tracking
- EOL detection and RUL calculation
- Ready for RL integration

**Phase 3: RL Dispatch Optimization**
- Gym environment setup
- Stable-Baselines3 Proximal Policy Optimization (PPO) training
- Hyperparameter fine-tuning


| Aspect | Why PPO |
|--------|---------|
| **Stability** | Prevents catastrophic policy updates |
| **Sample Efficiency** | Learns from less data than DQN |
| **Continuous Actions** | Perfect for variable charge rates |
| **Industry Standard** | Used by OpenAI, DeepMind, Tesla |
| **Production Ready** | Proven in real-world applications |

## Project Structure
```
bess-dispatch-optimizer/
│
├── battery_model/                    # Battery modeling & state estimation
│   ├── __init__.py
│   ├── coulomb_counter.py           # SoC estimation (real-time)
│   ├── degradation_models.py        # SoH degradation (PyBaMM physics)
│   └── soh_estimator.py             # SoH tracking & utilities
│
├── rl_agent/                         # Reinforcement learning (Phase 3)
│   ├── __init__.py
│   ├── environment.py               # Gym-compatible BESS environment
│   ├── training.py                  # PPO training pipeline
│   └── policy.py                    # Neural network policy
│
├── tests/                            # Unit tests
│   ├── __init__.py
│   └── test_coulomb_counter.py      # Coulomb counter validation
│
├── notebooks/                        # Jupyter notebooks
│   └── Pybamm_run_spm.ipynb         # PyBaMM SPM reference
│
├── results/                          # Generated outputs
│   ├── ppo_model.zip                # Trained PPO agent
│   ├── learning_curve.png           # Training visualization
│   └── dispatch_comparison.png      # Baseline vs RL comparison
│
├── README.md                         # This file
├── requirements.txt                  # Python dependencies
└── .gitignore                        # Git exclusions
```

## System Architecture

### Overall System Flow
```
┌─────────────────────────────────────────────────────────────────┐
│                    BESS DISPATCH OPTIMIZER                      │
│                                                                 │
│  Real-time battery dispatch with RL Driven optimization         │
└─────────────────────────────────────────────────────────────────┘

                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ↓             ↓             ↓
        ┌──────────────┐ ┌────────────┐ ┌──────────────┐
        │  Input Data  │ │ Market     │ │ Battery      │
        │              │ │ Prices     │ │ Parameters   │
        │ - Time       │ │ $/MWh      │ │ - Capacity   │
        │ - Weather    │ │            │ │ - Max Power  │
        └──────────────┘ └────────────┘ └──────────────┘
                │             │             │
                └─────────────┼─────────────┘
                              │
                              ↓
        ┌─────────────────────────────────────────┐
        │      State Estimation Module            │
        │                                         │
        │  ┌──────────────┐  ┌──────────────┐    │
        │  │ CoulombCtr   │  │ SoHEstimator │    │
        │  │              │  │              │    │
        │  │ Tracks: SoC  │  │ Tracks: SoH  │    │
        │  │ [0, 1]       │  │ [0, 1]       │    │
        │  └──────────────┘  └──────────────┘    │
        └─────────────────────────────────────────┘
                              │
                         State = [SoC, SoH]
                              │
                              ↓
        ┌─────────────────────────────────────────┐
        │      RL Policy Network (PPO)            │
        │                                         │
        │  Input: [SoC, SoH]                      │
        │    ↓                                    │
        │  Neural Network (128×128)               │
        │    ↓                                    │
        │  Output: Charge/Discharge Action       │
        └─────────────────────────────────────────┘
                              │
                         Action = [-1, 1]
                              │
                              ↓
        ┌─────────────────────────────────────────┐
        │      Battery Control Module             │
        │                                         │
        │  Apply charge/discharge action          │
        │  Update battery state                   │
        │  Simulate next timestep                 │
        └─────────────────────────────────────────┘
                              │
                              ↓
        ┌─────────────────────────────────────────┐
        │      Reward Calculation                 │
        │                                         │
        │  R = Revenue - Degradation_Penalty      │
        │                                         │
        │  Revenue = Price × Discharge            │
        │  Penalty = 1 - SoH                      │
        └─────────────────────────────────────────┘
                              │
                        Next State + Reward
                              │
                              ↓
        ┌─────────────────────────────────────────┐
        │      RL Training Loop                   │
        │      (repeat 1M+ timesteps)             │
        │                                         │
        │  Agent learns optimal policy            │
        │  Converges to best dispatch strategy    │
        └─────────────────────────────────────────┘
                              │
                              ↓
        ┌─────────────────────────────────────────┐
        │      Trained Policy Model               │
        │                                         │
        │  ppo_final.zip (20k parameters)         │
        │  Ready for deployment                   │
        └─────────────────────────────────────────┘
```



## Installation
```bash
# Clone repository
git clone <repo-url>
cd bess-dispatch-optimizer

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### 1. Coulomb Counter - SoC Estimation
```python
from battery_model import CoulombCounter

# Initialize: 100 Ah battery at 100% SoC
cc = CoulombCounter(nominal_capacity=100, initial_soc=1.0)

# Discharge at 10A for 1 hour
cc.discharge(current_A=10, time_step_s=3600)
print(f"SoC: {cc.get_soc():.2%}")  # 90%

# Charge at 5A for 2 hours
cc.charge(current_A=5, time_step_s=2*3600)
print(f"SoC: {cc.get_soc():.2%}")  # 100%
```

### 2. PyBaMM SEI Degradation Simulator
```python
from battery_model.degradation_models import SEIDegradationSimulator

# Initialize simulator
simulator = SEIDegradationSimulator(
    sei_model="ec reaction limited",
    nominal_capacity=100
)

# Run 100 cycles
df = simulator.run_multi_cycle(num_cycles=100)

# Get results
print(f"Cycle 1: SoH = {df.loc[1, 'soh']:.2%}")
print(f"Cycle 100: SoH = {df.loc[100, 'soh']:.2%}")
```

### 3. SoH Estimator - State of Health Tracking
```python
from battery_model import CoulombCounter
from battery_model.soh_estimator import SoHEstimator, DegradationAwareSoC

# Initialize
cc = CoulombCounter(nominal_capacity=100, initial_soc=0.5)
soh_est = SoHEstimator(initial_capacity=100)

# Load pre-computed degradation data
soh_est.load_from_dataframe(df)

# Get current health
print(f"Current SoH: {soh_est.get_current_soh():.2%}")
print(f"Is EOL: {soh_est.is_eol()}")
print(f"Remaining cycles: {soh_est.get_remaining_cycles()}")

# Combined state for RL agent
state_tracker = DegradationAwareSoC(cc, soh_est)
state = state_tracker.get_state()  # [SoC, SoH]
print(f"State for RL: {state}")
```

## API Reference

### CoulombCounter

**Methods:**
- `discharge(current_A, time_step_s)` - Decrease SoC
- `charge(current_A, time_step_s)` - Increase SoC
- `get_soc()` - Get current SoC [0, 1]
- `set_soc(target_soc)` - Calibrate SoC
- `get_remaining_capacity()` - Get remaining Ah

### SEIDegradationSimulator

**Methods:**
- `run_cycle(cycle_num, duration_s)` - Simulate one cycle with PyBaMM
- `run_multi_cycle(num_cycles)` - Simulate multiple cycles
- `get_soh_history()` - Get SoH values
- `get_eol_cycle(threshold)` - Find EOL cycle

### SoHEstimator

**Methods:**
- `load_from_dataframe(df)` - Bulk load pre-computed data
- `update_from_cycle(cycle_num, measured_capacity)` - Incremental update
- `get_current_soh()` - Get latest SoH
- `is_eol()` - Check if battery dead
- `get_eol_cycle()` - Find EOL cycle
- `get_remaining_cycles()` - Cycles until EOL
- `get_degradation_penalty()` - Penalty for RL (1 - SoH)
- `get_summary()` - Full health report

### DegradationAwareSoC

**Methods:**
- `get_state()` - Return [SoC, SoH] array
- `get_state_dict()` - Return {'soc': float, 'soh': float}
- `get_health_status()` - Human-readable status

## Testing

Run unit tests:
```bash
# Using pytest
pytest tests/test_coulomb_counter.py -v

# Using Python directly
python tests/test_coulomb_counter.py
```

### Test Results
```
✅ test_discharge: PASSED (100% → 90%)
✅ test_charge: PASSED (50% → 60%)
✅ test_bounds: PASSED (stays in [0, 1])
....
19 passed in 0.23s
```

## Key Concepts

### State of Charge (SoC)
- Current usable energy / Nominal capacity
- Range: [0, 1] or [0%, 100%]
- Tracks: Real-time energy level

### State of Health (SoH)
- Current capacity / Original capacity
- Range: [0, 1] or [0%, 100%]
- Tracks: Battery degradation over cycles
- EOL threshold: 80% (standard industry)

### Coulomb Counting Formula
```
SoC(t) = SoC(t-1) - I × Δt / Q_nominal

Where:
- I = Current (A)
- Δt = Time step (seconds)
- Q_nominal = Nominal capacity (Ah)
```

### SEI Degradation Model

PyBaMM simulates Solid Electrolyte Interface (SEI) growth:
- **Physics**: Electrochemical kinetics and diffusion
- **Mechanism**: SEI layer thickness increases with cycling
- **Effect**: Resistance increases → Available capacity decreases
- **Model**: "ec reaction limited" (electrochemical kinetics)

## Data & Training

### Training Data (Phase 3)

This project uses **offline, reproducible synthetic data**:

**Why Synthetic?**
- No external API dependencies
- 100% reproducible across environments
- Fast training (minutes, not hours)
- Perfect for development and testing

**Data Characteristics:**
- Realistic electricity market patterns (CAISO/NYISO-inspired)
- Daily pricing: 60% premium during peak hours (9am-6pm)
- Weekly patterns: 15% discount on weekends
- Stochastic noise: ±$5 market volatility
- 30-day simulation = 720 hourly timesteps

**Example Price Profile:**
```
00:00 - 06:00: $50/MWh (night, low demand)
06:00 - 09:00: $70/MWh (morning ramp)
09:00 - 18:00: $120/MWh (peak, high demand)
18:00 - 21:00: $80/MWh (evening decline)
21:00 - 00:00: $60/MWh (late evening)

Weekend: -15% across all hours
```

### Production Integration (Future)

The architecture supports easy integration with real data:
```python
# Development (offline)
env = BESSEnvironment(prices=synthetic_prices)

# Production (real-time)
env = BESSEnvironment(prices=caiso_api.get_prices())
# No code changes needed!
```

## Dependencies

- **numpy** >= 1.19.0 - Numerical computing
- **pandas** >= 1.0.0 - Data manipulation
- **matplotlib** >= 3.3.0 - Plotting
- **pytest** >= 6.0.0 - Unit testing
- **pybamm** >= 0.15.0 - Battery electrochemical modeling
- **stable-baselines3** >= 1.6.0 - RL algorithms

## Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -m "feat: description"`
3. Push to branch: `git push origin feature/your-feature`
4. Open pull request

## License

MIT License

## Contact

For questions or issues, please open a GitHub issue.
