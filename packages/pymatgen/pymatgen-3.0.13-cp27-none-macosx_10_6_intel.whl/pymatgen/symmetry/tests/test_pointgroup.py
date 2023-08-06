# coding: utf-8

from __future__ import division, unicode_literals

"""
TODO: Change the module doc.
"""


__author__ = "shyuepingong"
__version__ = "0.1"
__maintainer__ = "Shyue Ping Ong"
__email__ = "shyuep@gmail.com"
__status__ = "Beta"
__date__ = "5/9/13"


import unittest
import os

from pymatgen.core.structure import Molecule
from pymatgen.symmetry.pointgroup import PointGroupAnalyzer
from pymatgen.io.xyzio import XYZ
from pymatgen.io.smartio import read_mol

try:
    import scipy
except ImportError:
    scipy = None

test_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..",
                        'test_files', "molecules")


H2O2 = Molecule(["O", "O", "H", "H"],
                [[0, 0.727403, -0.050147], [0, -0.727403, -0.050147],
                 [0.83459, 0.897642, 0.401175],
                 [-0.83459, -0.897642, 0.401175]])

C2H2F2Br2 = Molecule(["C", "C", "F", "Br", "H", "F", "H", "Br"],
                     [[-0.752000, 0.001000, -0.141000],
                      [0.752000, -0.001000, 0.141000],
                      [-1.158000, 0.991000, 0.070000],
                      [-1.240000, -0.737000, 0.496000],
                      [-0.924000, -0.249000, -1.188000],
                      [1.158000, -0.991000, -0.070000],
                      [0.924000, 0.249000, 1.188000],
                      [1.240000, 0.737000, -0.496000]])

H2O = Molecule(["H", "O", "H"],
               [[0, 0.780362, -.456316], [0, 0, .114079],
                [0, -.780362, -.456316]])

C2H4 = Molecule(["C", "C", "H", "H", "H", "H"],
                [[0.0000, 0.0000, 0.6695], [0.0000, 0.0000, -0.6695],
                 [0.0000, 0.9289, 1.2321], [0.0000, -0.9289, 1.2321],
                 [0.0000, 0.9289, -1.2321], [0.0000, -0.9289, -1.2321]])

NH3 = Molecule(["N", "H", "H", "H"],
               [[0.0000, 0.0000, 0.0000], [0.0000, -0.9377, -0.3816],
                [0.8121, 0.4689, -0.3816], [-0.8121, 0.4689, -0.3816]])

BF3 = Molecule(["B", "F", "F", "F"],
               [[0.0000, 0.0000, 0.0000], [0.0000, -0.9377, 0.00],
                [0.8121, 0.4689, 0], [-0.8121, 0.4689, 0]])

CH4 = Molecule(["C", "H", "H", "H", "H"], [[0.000000, 0.000000, 0.000000],
               [0.000000, 0.000000, 1.08],
               [1.026719, 0.000000, -0.363000],
               [-0.513360, -0.889165, -0.363000],
               [-0.513360, 0.889165, -0.363000]])

PF6 = Molecule(["P", "F", "F", "F", "F", "F", "F"],
               [[0, 0, 0], [0, 0, 1], [0, 0, -1], [0, 1, 0], [0, -1, 0],
                [1, 0, 0], [-1, 0, 0]])


@unittest.skipIf(scipy is None, "Scipy not present.")
class PointGroupAnalyzerTest(unittest.TestCase):

    def test_spherical(self):
        a = PointGroupAnalyzer(CH4)
        self.assertEqual(a.sch_symbol, "Td")
        self.assertEqual(len(a.get_pointgroup()), 24)
        a = PointGroupAnalyzer(PF6)
        self.assertEqual(a.sch_symbol, "Oh")
        self.assertEqual(len(a.get_pointgroup()), 48)
        xyz = XYZ.from_file(os.path.join(test_dir, "c60.xyz"))
        a = PointGroupAnalyzer(xyz.molecule)
        self.assertEqual(a.sch_symbol, "Ih")

    def test_linear(self):
        coords = [[0.000000, 0.000000, 0.000000],
                  [0.000000, 0.000000, 1.08],
                  [0, 0.000000, -1.08]]
        mol = Molecule(["C", "H", "H"], coords)
        a = PointGroupAnalyzer(mol)
        self.assertEqual(a.sch_symbol, "D*h")
        mol = Molecule(["C", "H", "N"], coords)
        a = PointGroupAnalyzer(mol)
        self.assertEqual(a.sch_symbol, "C*v")

    def test_asym_top(self):
        coords = [[0.000000, 0.000000, 0.000000],
                  [0.000000, 0.000000, 1.08],
                  [1.026719, 0.000000, -0.363000],
                  [-0.513360, -0.889165, -0.363000],
                  [-0.513360, 0.889165, -0.363000]]
        mol = Molecule(["C", "H", "F", "Br", "Cl"], coords)
        a = PointGroupAnalyzer(mol)
        self.assertEqual(a.sch_symbol, "C1")
        self.assertEqual(len(a.get_pointgroup()), 1)
        coords = [[0.000000, 0.000000, 1.08],
                  [1.026719, 0.000000, -0.363000],
                  [-0.513360, -0.889165, -0.363000],
                  [-0.513360, 0.889165, -0.363000]]
        cs_mol = Molecule(["H", "F", "Cl", "Cl"], coords)
        a = PointGroupAnalyzer(cs_mol)
        self.assertEqual(a.sch_symbol, "Cs")
        self.assertEqual(len(a.get_pointgroup()), 2)
        a = PointGroupAnalyzer(C2H2F2Br2)
        self.assertEqual(a.sch_symbol, "Ci")
        self.assertEqual(len(a.get_pointgroup()), 2)

    def test_cyclic(self):
        a = PointGroupAnalyzer(H2O2)
        self.assertEqual(a.sch_symbol, "C2")
        self.assertEqual(len(a.get_pointgroup()), 2)
        a = PointGroupAnalyzer(H2O)
        self.assertEqual(a.sch_symbol, "C2v")
        self.assertEqual(len(a.get_pointgroup()), 4)
        a = PointGroupAnalyzer(NH3)
        self.assertEqual(a.sch_symbol, "C3v")
        self.assertEqual(len(a.get_pointgroup()), 6)
        cs2 = read_mol(os.path.join(test_dir, "Carbon_Disulfide.xyz"))
        a = PointGroupAnalyzer(cs2, eigen_tolerance=0.001)
        self.assertEqual(a.sch_symbol, "C2v")

    def test_dihedral(self):
        a = PointGroupAnalyzer(C2H4)
        self.assertEqual(a.sch_symbol, "D2h")
        self.assertEqual(len(a.get_pointgroup()), 8)
        a = PointGroupAnalyzer(BF3)
        self.assertEqual(a.sch_symbol, "D3h")
        self.assertEqual(len(a.get_pointgroup()), 12)
        xyz = XYZ.from_file(os.path.join(test_dir, "b12h12.xyz"))
        a = PointGroupAnalyzer(xyz.molecule)
        self.assertEqual(a.sch_symbol, "D5d")


if __name__ == "__main__":
    unittest.main()
