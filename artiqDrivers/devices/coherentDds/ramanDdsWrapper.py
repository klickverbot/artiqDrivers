from artiq.language.core import *
from artiqRoutines.hfQubitTransitionFreq import HfQubitTransitionFreq


class RamanDdsWrapper:
    """Wraps a CoherentDDS class to allow profiles to be set in logical frequencies (detunings from zero field) rather than the physical frequencies that are the input to the Raman AOMs.
    This class is very ugly at the moment as it hardcodes the arrangement of our AOM (inc. the diffraction orders)."""
    def __init__(self, dmgr, device):
        """LO_freq : blue beat note frequency between master and slave laser"""
        self.core = dmgr.get("core")

        self.dds = dmgr.get(device)
        
        self.hfq = HfQubitTransitionFreq()
        
        self.msDiff = 3.2e9 # master-slave Raman laser frequency difference
        self.trans = ['t4030'] # hyperfine transition without Zeeman shift
        self.hfs = self.hfq.dfTrans(0,int(self.trans[2]),self.int(trans[4])) # hyperfinesplitting, independent of B
        self.Rh_freq = -109e6 # frequency of Rh, is -1st order
        
        # range of sensible frequencies for Rpara and Rv        
        self.RparaRange = [170,220]*1e6
        self.RvRange = [105,113]*1e6
    

    def setProfile(self, channel, profile, freq, phase=0.0, amp=1.0, addQubitFreq = True):
    ''' channnel: Rpara or Rv, profile: 0...7, if addQubitFreq=True: the lasers used to create the frequency difference are split by 3.2GHz '''
        if addQubitFreq:
            freqDDS = fself.msDiff-self.Rh_freq-freq
        else:
            freqDDS = freq - self.Rh_freq
        
        if channel == Rpara:
            # Rpara is double passed +1,+1
            freqDDS /= 2
            phase /= 2
            if (freqDDS<self.RparaRange[0]) or (freqDDS>self.RparaRange[1]):
                raise ValueError("Rpara frequency out of range, {:.0f}MHz not in [{:.0f},{:.0f}]MHz".format(freqDDS/1e6,self.RparaRange[0]/1e6,self.RparaRange[1]/1e6))
            else:
                self.dds.setProfile(channel, profile, freqDDS, phase=phase, amp=amp)
            
        elif channel == Rv:
            # Rv is -1st order  
            freqDDS *= -1     
            if (freqDDS<self.RparaRange[0]) or (freqDDS>self.RparaRange[1]):
                raise ValueError("Rpara frequency out of range, {:.0f}MHz not in [{:.0f},{:.0f}]MHz".format(freqDDS/1e6,self.RparaRange[0]/1e6,self.RparaRange[1]/1e6))
            else:
                self.dds.setProfile(channel, profile, freqDDS, phase=phase, amp=amp)
            
        else:
            raise ValueError("Channel can only be Rpara or Rv")
