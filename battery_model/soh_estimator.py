"""
SoH (State of Health) Estimator for Battery Degradation Tracking

Tracks battery health over cycles with efficient updates.
Integrates with CoulombCounter for real-time SoC and SoH estimation.
"""

import numpy as np
import pandas as pd
from typing import List, Dict,Optional


class SoHEstimator:
    """
    Track and estimate State of Health (SoH) over battery cycles.
    
    SoH = Current_Capacity / Nominal_Capacity
    
    Features:
    - Bulk load from pre-computed DataFrame
    - Efficient incremental updates
    - End-of-life detection
    - Degradation penalty for RL agent
    """
    def __init__(self,initial_capacity: float, eol_threshold:float=0.80):
        self.nominal_capacity = initial_capacity
        self.eol_threshold  = eol_threshold
        
        
        self.cycle_history = []  #to store cycle numbers
        self.capacity_history = []  #to store capacity at each cycle
        self.soh_history = []  #to store SoH at each cycle
        
    def load_from_dataframe(self,df:pd.DataFrame):
        """Bulk load cycle data from a DataFrame."""
        self.cycle_history = df['cycle'].tolist()
        self.capacity_history = df['capacity'].tolist()
        self.soh_history = df['soh'].tolist()
        
    def update_from_cycle(self,cycle_num: int,measured_capacity: float):
        """Update SoH based on new cycle data."""
        soh = measured_capacity / self.nominal_capacity
        if cycle_num < len(self.soh_history):
            self.soh_history[cycle_num] = soh
            self.capacity_history[cycle_num] = measured_capacity
        else:
            self.soh_history.append(soh)
            self.capacity_history.append(measured_capacity)
            self.cycle_history.append(cycle_num)
        
        
    def get_current_soh(self) -> float:
        """Get the most recent SoH value."""
        if self.soh_history:
            return self.soh_history[-1]
        else:
            return 1.0  #Assume new battery starts at 100% SoH
        
    def get_soh_history(self) -> List[float]:
        """Return the history of State of Health (SoH) over cycles."""
        return self.soh_history
    
    def get_capacity_history(self) -> List[float]:
        """Return the history of capacity over cycles."""
        return self.capacity_history
    
    def get_cycle_history(self) -> List[int]:
        """Return the history of cycle numbers."""
        return self.cycle_history
    
    def is_eol(self) -> bool:
        """Check if battery has reached End of Life (EOL) based on SoH threshold."""
        current_soh = self.get_current_soh()
        return current_soh < self.eol_threshold
    
    def get_eol_cycle(self) -> Optional[int]:
        """Get the cycle number at which EOL was reached, if applicable."""
        for cycle, soh in zip(self.cycle_history, self.soh_history):
            if soh < self.eol_threshold:
                return cycle
        return None  #EOL not reached yet
    
    def get_remaining_cycles(self) -> Optional[int]:
        """Estimate remaining cycles until EOL based on current degradation trend."""
            # Safety check: Do we have data?
        if not self.soh_history:
            return None  # ← Explicit: No data loaded yet
        
        eol_cycle=self.get_eol_cycle()
        
        # Get latest cycle tracked
        if eol_cycle is None:
            return None  #EOL not reached yet
        
        current_cycle=self.cycle_history[-1] if self.cycle_history else 0
        
        # Calculate remaining: when will we hit EOL?
        remaining= eol_cycle - current_cycle
        
        # Clamp to 0 if already past EOL
        return max(0, remaining)
    
    
    def get_degradation_penalty(self) -> float:
        """Calculate a degradation penalty for RL agent based on SoH."""
        current_soh = self.get_current_soh()
        penalty = 1.0 - current_soh  #Higher penalty as SoH decreases
        return max(0, penalty)
    
    
    def get_summary(self) -> Dict:
        """Return a summary of current SoH status."""
        return {
            'current_soh': self.get_current_soh(),
            'capacity': self.capacity_history[-1] if self.capacity_history else 0,
            'eol_threshold': self.eol_threshold,
            'is_eol': self.is_eol(),
            'cycles_completed': len(self.cycle_history),
            'remaining_cycles': self.get_remaining_cycles(),
            'degradation_penalty': self.get_degradation_penalty()
        }
        
        
        
class DegradationAwareSoc:
    
    """ Combined SoC and SoH estimation for RL dispatch.
        state=[SoC,SoH] for dispatch otpimization
        Example:[0.75,0.90] # 75% charged ,90% health"""
    
    def  __init__(self,coulomb_counter,soh_estimator):
        """ Intialize combined estimator"""
        
        self.cc=coulomb_counter
        self.soh_estimator=soh_estimator
        
        def get_state(self):
            """ Return combined state [SoC, SoH]"""
            soc=self.cc.get_soc()
            soh=self.soh_estimator.get_current_soh()
            return [soc,soh]
        
        def get_state_dict(self):
            """ Return state as a dictionary for clarity"""
            return {
                'soc': self.cc.get_soc(),
                'soh': self.soh_estimator.get_current_soh()
            }
        