import pybamm
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple



class SEIDegradationSimulator:
    """
    A simulator for modeling SEI (Solid-Electrolyte Interface) degradation in lithium-ion batteries.
    
    """
    def __init__(self,sei_model:str="ex reaction limited",nominal_capacity:float=1.0): #sei/-model,nominal capacity in Ah 
        self.sei_model = sei_model
        self.nominal_capacity = nominal_capacity
        self.cycle_data={
            'cycle':[],
            'capacity':[],
            'soh':[],
            'voltage_min':[],
            'voltage_max':[]    
            } #to store cycle-wise degradation data
        
        #intialize pybamm model with sei submodel
        
        self.model = pybamm.lithium_ion.SPM()  #Single Particle Model
        
        self.model.submodels['sei'] = sei_model  #set SEI degradation model
        
        
    def run_cycle(self,cycle_num:int,duration_s:float=3600)->Dict:
        
        """Run a single charge-discharge cycle with SEI growth and return degradation metrics."""
        
        #Run discharge simulation for duration_s
        sim = pybamm.Simulation(self.model)
        sim.solve([0, duration_s])
        
        #Exctract capacity from pyBaMM
        capacity = sim.solution['Discharge capacity [A.h]'].entries[-1]
        
        #Calculate SoH = capacity / nominal_capacity
        soh = capacity / self.nominal_capacity

        #Extract SEI thickness from model variables
        #sei_thickness = sim.solution['SEI thickness [m]'][-1]
        
        
        #Record voltage min/max
        voltage_data = sim.solution['Terminal voltage [V]'].entries
        voltage_min = min(voltage_data)
        voltage_max = max(voltage_data)

        #Return degradation metrics
        return {
            'cycle': cycle_num,
            'capacity': capacity,
            'soh': soh,
            #'sei_thickness': sei_thickness,
            'voltage_min': voltage_min,
            'voltage_max': voltage_max
        }
        
    def run_multi_cycle(self,num_cycles:int=100) -> pd.DataFrame:
        """Run multiple cycles and store degradation data in a DataFrame."""
        for cycle in range(1, num_cycles + 1):
            metrics = self.run_cycle(cycle)
            if cycle % 10 == 0:
                print(f"Cycle {cycle}: SoH = {metrics['soh']:.2%}")
            for key in self.cycle_data:
                self.cycle_data[key].append(metrics[key])
        
        return pd.DataFrame(self.cycle_data)
    
    
    def get_soh_history(self) -> List[float]:
        """Return the history of State of Health (SoH) over cycles."""
        return self.cycle_data['soh']
    
    
    # def get_sei_thickness_history(self) -> List[float]:
    #     """Get SEI thickness for all cycles"""
    #     return self.cycle_data['sei_thickness']
    
    
    def get_eol_cycle(self,threshold_soh:float=0.8)->int:
        """Determine the End of Life (EOL) cycle based on a SoH threshold."""
        for cycle, soh in zip(self.cycle_data['cycle'], self.cycle_data['soh']):
            if soh < threshold_soh:
                return cycle
        return -1  # Return -1 if EOL not reached within simulated cycles
    
    
    
class SimpleCapacityFadeModel:
    
    """
    Simple square-root capacity fade model for comparison.

    Q(n) = Q₀ × (1 - k√n)
    where Q₀ is the initial capacity, k is the fade rate, and n is the cycle number.
    """
    def __init__(self, initial_capacity: float, fade_rate: float=0.01):
        self.initial_capacity = initial_capacity
        self.fade_rate = fade_rate
        
    def capacity_at_cycle(self, cycle_num: int) -> float:
        """Calculate remaining capacity after a given number of cycles."""
        return self.initial_capacity * (1 - self.fade_rate * np.sqrt(cycle_num))
    
    def soh_at_cycle(self, cycle_num: int) -> float:
        """Calculate State of Health (SoH) after a given number of cycles."""
        return self.capacity_at_cycle(cycle_num) / self.initial_capacity
    

    def get_curve(self,num_cycles:int)->Tuple[List[int], List[float]]:
        """Generate capacity fade curve over a number of cycles."""
        cycles = list(range(1, num_cycles + 1))
        capacities = [self.capacity_at_cycle(cycle) for cycle in cycles]
        return cycles, capacities