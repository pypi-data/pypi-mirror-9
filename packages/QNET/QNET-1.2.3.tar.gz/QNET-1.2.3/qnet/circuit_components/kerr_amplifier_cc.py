#!/usr/bin/env python
# encoding: utf-8
#This file was automatically created using QNET.

"""
kerr_amplifier_cc.py

Created automatically by $QNET/bin/parse_qhdl.py
Get started by instantiating a circuit instance via:

    >>> KerrAmplifier()

"""

__all__ = ['KerrAmplifier']

from qnet.circuit_components.library import make_namespace_string
from qnet.circuit_components.component import Component
from qnet.algebra.circuit_algebra import cid, P_sigma, FB, SLH
import unittest
from sympy import symbols
from qnet.circuit_components.two_port_kerr_cavity_cc import TwoPortKerrCavity
from qnet.circuit_components.beamsplitter_cc import Beamsplitter



class KerrAmplifier(Component):

    # total number of field channels
    CDIM = 4
    
    # parameters on which the model depends
    kappa = symbols('kappa', real = True)
    eta = symbols('eta', real = True)
    Delta = symbols('Delta', real = True)
    chi = symbols('chi', real = True)
    _parameters = ['Delta', 'chi', 'eta', 'kappa']

    # list of input port names
    PORTSIN = ['In1', 'bias']
    
    # list of output port names
    PORTSOUT = ['Out1', 'bias_noise']

    # sub-components
    
    @property
    def BS1(self):
        return Beamsplitter(make_namespace_string(self.name, 'BS1'))

    @property
    def BS2(self):
        return Beamsplitter(make_namespace_string(self.name, 'BS2'))

    @property
    def K1(self):
        return TwoPortKerrCavity(make_namespace_string(self.name, 'K1'), kappa_2 = self.eta, chi = self.chi, kappa_1 = self.kappa, Delta = self.Delta)

    @property
    def K2(self):
        return TwoPortKerrCavity(make_namespace_string(self.name, 'K2'), kappa_2 = self.eta, chi = self.chi, kappa_1 = self.kappa, Delta = self.Delta)

    _sub_components = ['BS1', 'BS2', 'K1', 'K2']
    

    def _toSLH(self):
        return self.creduce().toSLH()
        
    def _creduce(self):

        BS1, BS2, K1, K2 = self.BS1, self.BS2, self.K1, self.K2

        return (((BS2 + cid(1)) << P_sigma(0, 2, 1) << (K2 + cid(1))) + cid(1)) << (cid(2) + K1) << ((P_sigma(0, 2, 1) << ((P_sigma(1, 0) << BS1) + cid(1))) + cid(1)) << P_sigma(1, 0, 2, 3)

    @property
    def _space(self):
        return self.creduce().space


# Test the circuit
class TestKerrAmplifier(unittest.TestCase):
    """
    Automatically created unittest test case for KerrAmplifier.
    """

    def testCreation(self):
        a = KerrAmplifier()
        self.assertIsInstance(a, KerrAmplifier)

    def testCReduce(self):
        a = KerrAmplifier().creduce()

    def testParameters(self):
        if len(KerrAmplifier._parameters):
            pname = KerrAmplifier._parameters[0]
            obj = KerrAmplifier(name="TestName", namespace="TestNamespace", **{pname: 5})
            self.assertEqual(getattr(obj, pname), 5)
            self.assertEqual(obj.name, "TestName")
            self.assertEqual(obj.namespace, "TestNamespace")

        else:
            obj = KerrAmplifier(name="TestName", namespace="TestNamespace")
            self.assertEqual(obj.name, "TestName")
            self.assertEqual(obj.namespace, "TestNamespace")

    def testToSLH(self):
        aslh = KerrAmplifier().toSLH()
        self.assertIsInstance(aslh, SLH)

if __name__ == "__main__":
    unittest.main()