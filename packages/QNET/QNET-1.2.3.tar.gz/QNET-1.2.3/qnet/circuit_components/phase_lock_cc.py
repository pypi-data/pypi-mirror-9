#!/usr/bin/env python
# encoding: utf-8
#This file was automatically created using QNET.

"""
phase_lock_cc.py

Created automatically by $QNET/bin/parse_qhdl.py
Get started by instantiating a circuit instance via:

    >>> PhaseLock()

"""

__all__ = ['PhaseLock']

from qnet.circuit_components.library import make_namespace_string
from qnet.circuit_components.component import Component
from qnet.algebra.circuit_algebra import cid, P_sigma, FB, SLH
import unittest
from sympy import symbols
from qnet.circuit_components.kerr_oscillator2_cc import KerrOscillator2
from qnet.circuit_components.three_port_kerr_cavity_cc import ThreePortKerrCavity
from qnet.circuit_components.kerr_amplifier_cc import KerrAmplifier
from qnet.circuit_components.phase_cc import Phase



class PhaseLock(Component):

    # total number of field channels
    CDIM = 9
    
    # parameters on which the model depends
    kappa = symbols('kappa', real = True)
    Delta = symbols('Delta', real = True)
    delta = symbols('delta', real = True)
    gamma = symbols('gamma', real = True)
    eta = symbols('eta', real = True)
    chi = symbols('chi', real = True)
    chi_C = symbols('chi_C', real = True)
    phi_1 = 3.14159265359
    phi_2 = -3.14159265359
    kappa_F = symbols('kappa_F', real = True)
    gamma_F = symbols('gamma_F', real = True)
    eta_F = symbols('eta_F', real = True)
    Delta_F = symbols('Delta_F', real = True)
    Delta_A = symbols('Delta_A', real = True)
    kappa_A = symbols('kappa_A', real = True)
    chi_A = symbols('chi_A', real = True)
    phi = symbols('phi', real = True)
    eta_A = symbols('eta_A', real = True)
    _parameters = ['Delta', 'Delta_A', 'Delta_F', 'chi', 'chi_A', 'chi_C', 'delta', 'eta', 'eta_A', 'eta_F', 'gamma', 'gamma_F', 'kappa', 'kappa_A', 'kappa_F', 'phi', 'phi_1', 'phi_2']

    # list of input port names
    PORTSIN = ['bias', 'sig']
    
    # list of output port names
    PORTSOUT = ['sb_ref']

    # sub-components
    
    @property
    def A(self):
        return KerrAmplifier(make_namespace_string(self.name, 'A'), chi = self.chi_A, eta = self.eta_A, kappa = self.kappa_A, Delta = self.Delta_A)

    @property
    def Filter(self):
        return ThreePortKerrCavity(make_namespace_string(self.name, 'Filter'), kappa_2 = self.gamma_F, chi = 0, kappa_1 = self.kappa_F, kappa_3 = self.eta_F, Delta = self.Delta_F)

    @property
    def OSC(self):
        return KerrOscillator2(make_namespace_string(self.name, 'OSC'), phi_1 = self.phi_1, eta = self.eta, kappa = self.kappa, chi_C = self.chi_C, phi_2 = self.phi_2, Delta = self.Delta, chi = self.chi, delta = self.delta, gamma = self.gamma)

    @property
    def P(self):
        return Phase(make_namespace_string(self.name, 'P'), phi = self.phi)

    _sub_components = ['A', 'Filter', 'OSC', 'P']
    

    def _toSLH(self):
        return self.creduce().toSLH()
        
    def _creduce(self):

        A, Filter, OSC, P = self.A, self.Filter, self.OSC, self.P

        return P_sigma(1, 2, 3, 4, 0, 5, 6, 7, 8) << FB(((P_sigma(0, 1, 2, 5, 3, 4) << (((cid(3) + P) << P_sigma(3, 0, 1, 2) << A) + cid(2)) << (cid(1) + (P_sigma(0, 3, 4, 1, 2) << ((P_sigma(2, 0, 1) << Filter) + cid(2))))) + cid(4)) << (cid(1) + (P_sigma(0, 5, 6, 7, 8, 1, 2, 3, 4) << ((P_sigma(1, 0, 2, 3, 4) << OSC) + cid(4)))), 5, 2) << P_sigma(1, 0, 7, 8, 5, 6, 2, 3, 4)

    @property
    def _space(self):
        return self.creduce().space


# Test the circuit
class TestPhaseLock(unittest.TestCase):
    """
    Automatically created unittest test case for PhaseLock.
    """

    def testCreation(self):
        a = PhaseLock()
        self.assertIsInstance(a, PhaseLock)

    def testCReduce(self):
        a = PhaseLock().creduce()

    def testParameters(self):
        if len(PhaseLock._parameters):
            pname = PhaseLock._parameters[0]
            obj = PhaseLock(name="TestName", namespace="TestNamespace", **{pname: 5})
            self.assertEqual(getattr(obj, pname), 5)
            self.assertEqual(obj.name, "TestName")
            self.assertEqual(obj.namespace, "TestNamespace")

        else:
            obj = PhaseLock(name="TestName", namespace="TestNamespace")
            self.assertEqual(obj.name, "TestName")
            self.assertEqual(obj.namespace, "TestNamespace")

    def testToSLH(self):
        aslh = PhaseLock().toSLH()
        self.assertIsInstance(aslh, SLH)

if __name__ == "__main__":
    unittest.main()