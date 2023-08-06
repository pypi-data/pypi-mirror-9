####################################################################################################

from PySpice.Spice.Netlist import SubCircuitFactory
from PySpice.Unit.Units import *

####################################################################################################

class BasicOperationalAmplifier(SubCircuitFactory):

    __name__ = 'BasicOperationalAmplifier'
    __nodes__ = ('non_inverting_input', 'inverting_input', 'output')

    ##############################################

    def __init__(self):

        super(BasicOperationalAmplifier, self).__init__()
                                         
        # Input impedance
        self.R('input', 'non_inverting_input', 'inverting_input', mega(10))
        
        # dc gain=100k and pole1=100hz
        # unity gain = dcgain x pole1 = 10MHZ
        self.VCVS('gain', 'non_inverting_input', 'inverting_input', 1, self.gnd, voltage_gain=kilo(100))
        self.R('P1', 1, 2, kilo(1))
        self.C('P1', 2, self.gnd, micro(1.5915))
        
        # Output buffer and resistance
        self.VCVS('buffer', 2, self.gnd, 3, self.gnd, 1)
        self.R('out', 3, 'output', 10)

####################################################################################################

class BasicComparator(SubCircuitFactory):

    __name__ = 'BasicComparator'
    __nodes__ = ('non_inverting_input', 'inverting_input',
                 'voltage_plus', 'voltage_minus',
                 'output')

    ##############################################

    def __init__(self,):

        super(BasicOperationalAmplifier, self).__init__()

        # Fixme: ngspice is buggy with such subcircuit

        # Fixme: how to pass voltage_plus, voltage_minus ?
        # output_voltage_minus, output_voltage_plus = 0, 15

        # to plug the voltage source
        self.R(1, 'voltage_plus', 'voltage_minus', mega(1))
        self.NonLinearVoltageSource(1, 'output', 'voltage_minus',
                                    expression='V(non_inverting_input, inverting_input)',
                                    # table=((-micro(1), output_voltage_minus),
                                    #       (micro(1), output_voltage_plus))
                                    table=(('-1uV', '0V'), ('1uV', '15V'))
                                )

####################################################################################################
# 
# End
# 
####################################################################################################
