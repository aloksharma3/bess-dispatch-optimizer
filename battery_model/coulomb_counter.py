
#Math: SoC(t) = SoC(t-1) - ∫ I(τ) dτ / Q_nominal



#create a class CoulombCounter:

class CoulombCounter:
    def __init__(self,nominal_capacity,initial_soc=1.0):
    
        self.nominal_capacity = nominal_capacity
        self.soc = initial_soc
        
    def discharge(self,current_A,time_step_s):
        #update SoC downward
        
        self.soc -= current_A * (time_step_s/3600.0) / self.nominal_capacity
        #clamp SoC to [0, 1]
        self.soc = max(0, min(1, self.soc))
        
        
    def charge(self,current_A,time_step_s):
        #update SoC upward
        
        self.soc += current_A * (time_step_s/3600.0) / self.nominal_capacity
        #clamp SoC to [0, 1]
        self.soc = max(0, min(1, self.soc))
        
    def get_soc(self):        #returns [0, 1] fraction
        return self.soc
    
    def set_soc(self,target_soc):  #direct SoC calibration
        self.soc = max(0, min(1, target_soc))
        
    def get_remaining_capacity(self):  #returns Ah remaining
        return self.soc * self.nominal_capacity