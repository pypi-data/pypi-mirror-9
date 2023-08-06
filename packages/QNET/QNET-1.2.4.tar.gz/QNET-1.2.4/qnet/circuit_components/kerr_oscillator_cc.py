#!/usr/bin/env python
# encoding: utf-8
#This file was automatically created using QNET.

"""
kerr_oscillator_cc.py

Created automatically by $QNET/bin/parse_qhdl.py
Get started by instantiating a circuit instance via:

    >>> KerrOscillator()

"""

__all__ = ['KerrOscillator']

from qnet.circuit_components.library import make_namespace_string
from qnet.circuit_components.component import Component
from qnet.algebra.circuit_algebra import cid, P_sigma, FB, SLH
import unittest
from sympy import symbols
from qnet.circuit_components.phase_cc import Phase
from qnet.circuit_components.three_port_kerr_cavity_cc import ThreePortKerrCavity



class KerrOscillator(Component):

    # total number of field channels
    CDIM = 5
    
    # parameters on which the model depends
    Delta = symbols('Delta', real = True)
    chi = symbols('chi', real = True)
    kappa = symbols('kappa', real = True)
    gamma = symbols('gamma', real = True)
    eta = symbols('eta', real = True)
    delta = symbols('delta', real = True)
    chi_C = 0
    phi_1 = 3.14159265359
    phi_2 = -3.14159265359
    _parameters = ['Delta', 'chi', 'chi_C', 'delta', 'eta', 'gamma', 'kappa', 'phi_1', 'phi_2']

    # list of input port names
    PORTSIN = ['In1', 'In2']
    
    # list of output port names
    PORTSOUT = ['Out1', 'Out2']

    # sub-components
    
    @property
    def K1(self):
        return ThreePortKerrCavity(make_namespace_string(self.name, 'K1'), kappa_2 = self.kappa, chi = self.chi, kappa_1 = self.kappa, kappa_3 = self.eta, Delta = self.Delta)

    @property
    def K2(self):
        return ThreePortKerrCavity(make_namespace_string(self.name, 'K2'), kappa_2 = self.kappa, chi = self.chi, kappa_1 = self.kappa, kappa_3 = self.eta, Delta = self.Delta)

    @property
    def KC(self):
        return ThreePortKerrCavity(make_namespace_string(self.name, 'KC'), kappa_2 = self.gamma, chi = self.chi_C, kappa_1 = self.gamma, kappa_3 = self.eta, Delta = self.delta)

    @property
    def P1(self):
        return Phase(make_namespace_string(self.name, 'P1'), phi = self.phi_1)

    @property
    def P2(self):
        return Phase(make_namespace_string(self.name, 'P2'), phi = self.phi_2)

    _sub_components = ['K1', 'K2', 'KC', 'P1', 'P2']
    

    def _toSLH(self):
        return self.creduce().toSLH()
        
    def _creduce(self):

        K1, K2, KC, P1, P2 = self.K1, self.K2, self.KC, self.P1, self.P2

        return P_sigma(2, 3, 0, 1, 4) << FB(((P_sigma(2, 0, 3, 1) << FB((K2 + cid(2)) << P_sigma(0, 3, 4, 1, 2) << ((KC << (cid(1) + P1 + cid(1))) + cid(2)), 1, 1)) + cid(2)) << P_sigma(0, 4, 5, 1, 2, 3) << ((K1 << (cid(1) + P2 + cid(1))) + cid(3)), 3, 1) << P_sigma(0, 3, 4, 2, 1)

    @property
    def _space(self):
        return self.creduce().space


# Test the circuit
class TestKerrOscillator(unittest.TestCase):
    """
    Automatically created unittest test case for KerrOscillator.
    """

    def testCreation(self):
        a = KerrOscillator()
        self.assertIsInstance(a, KerrOscillator)

    def testCReduce(self):
        a = KerrOscillator().creduce()

    def testParameters(self):
        if len(KerrOscillator._parameters):
            pname = KerrOscillator._parameters[0]
            obj = KerrOscillator(name="TestName", namespace="TestNamespace", **{pname: 5})
            self.assertEqual(getattr(obj, pname), 5)
            self.assertEqual(obj.name, "TestName")
            self.assertEqual(obj.namespace, "TestNamespace")

        else:
            obj = KerrOscillator(name="TestName", namespace="TestNamespace")
            self.assertEqual(obj.name, "TestName")
            self.assertEqual(obj.namespace, "TestNamespace")

    def testToSLH(self):
        aslh = KerrOscillator().toSLH()
        self.assertIsInstance(aslh, SLH)

if __name__ == "__main__":
    unittest.main()