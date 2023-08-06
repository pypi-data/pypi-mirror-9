#!/usr/bin/env python
# encoding: utf-8
#This file was automatically created using QNET.

"""
double_beamsplitter_cc.py

Created automatically by $QNET/bin/parse_qhdl.py
Get started by instantiating a circuit instance via:

    >>> DoubleBeamsplitter()

"""

__all__ = ['DoubleBeamsplitter']

from qnet.circuit_components.library import make_namespace_string
from qnet.circuit_components.component import Component
from qnet.algebra.circuit_algebra import cid, P_sigma, FB, SLH
import unittest
from sympy import symbols
from qnet.circuit_components.beamsplitter_cc import Beamsplitter



class DoubleBeamsplitter(Component):

    # total number of field channels
    CDIM = 4
    
    # parameters on which the model depends
    theta = 0.785398163397
    _parameters = ['theta']

    # list of input port names
    PORTSIN = ['In1', 'In2', 'In3', 'In4']
    
    # list of output port names
    PORTSOUT = ['Out1', 'Out2', 'Out3', 'Out4']

    # sub-components
    
    @property
    def B1(self):
        return Beamsplitter(make_namespace_string(self.name, 'B1'), theta = self.theta)

    @property
    def B2(self):
        return Beamsplitter(make_namespace_string(self.name, 'B2'), theta = self.theta)

    _sub_components = ['B1', 'B2']
    

    def _toSLH(self):
        return self.creduce().toSLH()
        
    def _creduce(self):

        B1, B2 = self.B1, self.B2

        return (B2 + (P_sigma(1, 0) << B1)) << P_sigma(3, 2, 0, 1)

    @property
    def _space(self):
        return self.creduce().space


# Test the circuit
class TestDoubleBeamsplitter(unittest.TestCase):
    """
    Automatically created unittest test case for DoubleBeamsplitter.
    """

    def testCreation(self):
        a = DoubleBeamsplitter()
        self.assertIsInstance(a, DoubleBeamsplitter)

    def testCReduce(self):
        a = DoubleBeamsplitter().creduce()

    def testParameters(self):
        if len(DoubleBeamsplitter._parameters):
            pname = DoubleBeamsplitter._parameters[0]
            obj = DoubleBeamsplitter(name="TestName", namespace="TestNamespace", **{pname: 5})
            self.assertEqual(getattr(obj, pname), 5)
            self.assertEqual(obj.name, "TestName")
            self.assertEqual(obj.namespace, "TestNamespace")

        else:
            obj = DoubleBeamsplitter(name="TestName", namespace="TestNamespace")
            self.assertEqual(obj.name, "TestName")
            self.assertEqual(obj.namespace, "TestNamespace")

    def testToSLH(self):
        aslh = DoubleBeamsplitter().toSLH()
        self.assertIsInstance(aslh, SLH)

if __name__ == "__main__":
    unittest.main()