#!/usr/bin/env python
# encoding: utf-8
#This file was automatically created using QNET.

"""
phase_lock2_cc.py

Created automatically by $QNET/bin/parse_qhdl.py
Get started by instantiating a circuit instance via:

    >>> PhaseLock2()

"""

__all__ = ['PhaseLock2']

from qnet.circuit_components.library import make_namespace_string
from qnet.circuit_components.component import Component
from qnet.algebra.circuit_algebra import cid, P_sigma, FB, SLH
import unittest
from sympy import symbols
from qnet.circuit_components.kerr_oscillator2_cc import KerrOscillator2
from qnet.circuit_components.three_port_kerr_cavity_cc import ThreePortKerrCavity
from qnet.circuit_components.phase_cc import Phase



class PhaseLock2(Component):

    # total number of field channels
    CDIM = 6
    
    # parameters on which the model depends
    kappa = symbols('kappa', real = True)
    Delta = symbols('Delta', real = True)
    delta = symbols('delta', real = True)
    gamma = symbols('gamma', real = True)
    eta = symbols('eta', real = True)
    chi = symbols('chi', real = True)
    chi_C = symbols('chi_C', real = True)
    kappa_F = symbols('kappa_F', real = True)
    gamma_F = symbols('gamma_F', real = True)
    eta_F = symbols('eta_F', real = True)
    Delta_F = symbols('Delta_F', real = True)
    chi_F = symbols('chi_F', real = True)
    phi = symbols('phi', real = True)
    phi_1 = 3.14159265359
    phi_2 = -3.14159265359
    _parameters = ['Delta', 'Delta_F', 'chi', 'chi_C', 'chi_F', 'delta', 'eta', 'eta_F', 'gamma', 'gamma_F', 'kappa', 'kappa_F', 'phi', 'phi_1', 'phi_2']

    # list of input port names
    PORTSIN = ['bias', 'sig']
    
    # list of output port names
    PORTSOUT = ['common_out', 'sb_ref']

    # sub-components
    
    @property
    def Filter(self):
        return ThreePortKerrCavity(make_namespace_string(self.name, 'Filter'), kappa_2 = self.gamma_F, chi = self.chi_F, kappa_1 = self.kappa_F, kappa_3 = self.eta_F, Delta = self.Delta_F)

    @property
    def OSC(self):
        return KerrOscillator2(make_namespace_string(self.name, 'OSC'), phi_1 = self.phi_1, eta = self.eta, kappa = self.kappa, chi_C = self.chi_C, phi_2 = self.phi_2, Delta = self.Delta, chi = self.chi, delta = self.delta, gamma = self.gamma)

    @property
    def P(self):
        return Phase(make_namespace_string(self.name, 'P'), phi = self.phi)

    _sub_components = ['Filter', 'OSC', 'P']
    

    def _toSLH(self):
        return self.creduce().toSLH()
        
    def _creduce(self):

        Filter, OSC, P = self.Filter, self.OSC, self.P

        return P_sigma(2, 3, 4, 5, 1, 0) << FB(((P_sigma(0, 4, 5, 1, 2, 3) << (((cid(2) + P) << P_sigma(1, 2, 0) << Filter) + cid(3))) + cid(1)) << P_sigma(0, 3, 4, 5, 6, 1, 2) << ((P_sigma(4, 0, 1, 2, 3) << OSC) + cid(2)), 5, 1) << P_sigma(0, 4, 5, 1, 2, 3)

    @property
    def _space(self):
        return self.creduce().space


# Test the circuit
class TestPhaseLock2(unittest.TestCase):
    """
    Automatically created unittest test case for PhaseLock2.
    """

    def testCreation(self):
        a = PhaseLock2()
        self.assertIsInstance(a, PhaseLock2)

    def testCReduce(self):
        a = PhaseLock2().creduce()

    def testParameters(self):
        if len(PhaseLock2._parameters):
            pname = PhaseLock2._parameters[0]
            obj = PhaseLock2(name="TestName", namespace="TestNamespace", **{pname: 5})
            self.assertEqual(getattr(obj, pname), 5)
            self.assertEqual(obj.name, "TestName")
            self.assertEqual(obj.namespace, "TestNamespace")

        else:
            obj = PhaseLock2(name="TestName", namespace="TestNamespace")
            self.assertEqual(obj.name, "TestName")
            self.assertEqual(obj.namespace, "TestNamespace")

    def testToSLH(self):
        aslh = PhaseLock2().toSLH()
        self.assertIsInstance(aslh, SLH)

if __name__ == "__main__":
    unittest.main()