#!/usr/bin/env python
# encoding: utf-8
#This file was automatically created using QNET.

"""
kerr_oscillator2_cc.py

Created automatically by $QNET/bin/parse_qhdl.py
Get started by instantiating a circuit instance via:

    >>> KerrOscillator2()

"""

__all__ = ['KerrOscillator2']

from qnet.circuit_components.library import make_namespace_string
from qnet.circuit_components.component import Component
from qnet.algebra.circuit_algebra import cid, P_sigma, FB, SLH
import unittest
from sympy import symbols
from qnet.circuit_components.kerr_oscillator_cc import KerrOscillator
from qnet.circuit_components.beamsplitter_cc import Beamsplitter



class KerrOscillator2(Component):

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
    PORTSIN = ['bias', 'differential']
    
    # list of output port names
    PORTSOUT = ['common', 'osc']

    # sub-components
    
    @property
    def BS1(self):
        return Beamsplitter(make_namespace_string(self.name, 'BS1'))

    @property
    def BS2(self):
        return Beamsplitter(make_namespace_string(self.name, 'BS2'))

    @property
    def KO(self):
        return KerrOscillator(make_namespace_string(self.name, 'KO'), phi_1 = self.phi_1, eta = self.eta, kappa = self.kappa, chi_C = self.chi_C, phi_2 = self.phi_2, Delta = self.Delta, chi = self.chi, delta = self.delta, gamma = self.gamma)

    _sub_components = ['BS1', 'BS2', 'KO']
    

    def _toSLH(self):
        return self.creduce().toSLH()
        
    def _creduce(self):

        BS1, BS2, KO = self.BS1, self.BS2, self.KO

        return ((P_sigma(1, 0) << BS2) + cid(3)) << P_sigma(1, 0, 2, 3, 4) << KO << (BS1 + cid(3))

    @property
    def _space(self):
        return self.creduce().space


# Test the circuit
class TestKerrOscillator2(unittest.TestCase):
    """
    Automatically created unittest test case for KerrOscillator2.
    """

    def testCreation(self):
        a = KerrOscillator2()
        self.assertIsInstance(a, KerrOscillator2)

    def testCReduce(self):
        a = KerrOscillator2().creduce()

    def testParameters(self):
        if len(KerrOscillator2._parameters):
            pname = KerrOscillator2._parameters[0]
            obj = KerrOscillator2(name="TestName", namespace="TestNamespace", **{pname: 5})
            self.assertEqual(getattr(obj, pname), 5)
            self.assertEqual(obj.name, "TestName")
            self.assertEqual(obj.namespace, "TestNamespace")

        else:
            obj = KerrOscillator2(name="TestName", namespace="TestNamespace")
            self.assertEqual(obj.name, "TestName")
            self.assertEqual(obj.namespace, "TestNamespace")

    def testToSLH(self):
        aslh = KerrOscillator2().toSLH()
        self.assertIsInstance(aslh, SLH)

if __name__ == "__main__":
    unittest.main()