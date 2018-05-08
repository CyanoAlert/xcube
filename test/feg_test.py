import unittest

from xcube.feg import FixedEarthGrid


class MaskSetTest(unittest.TestCase):
    def test_get_res(self):
        feg = FixedEarthGrid()
        self.assertEqual(feg.get_res(0), 1)
        self.assertEqual(feg.get_res(1), 0.5)
        self.assertEqual(feg.get_res(2), 0.25)
        self.assertEqual(feg.get_res(9, units='meters'), 346.03607855902777)
        self.assertEqual(feg.get_res(10, units='meters'), 173.01803927951389)
        feg = FixedEarthGrid(level_zero_res=0.3)
        self.assertEqual(feg.get_res(7, units='meters'), 415.2432942708333)
        self.assertEqual(feg.get_res(8, units='meters'), 207.62164713541665)
        feg = FixedEarthGrid(level_zero_res=0.2)
        self.assertEqual(feg.get_res(7, units='meters'), 276.82886284722224)
        self.assertEqual(feg.get_res(8, units='meters'), 138.41443142361112)
        feg = FixedEarthGrid(level_zero_res=0.18)
        self.assertEqual(feg.get_res(7, units='meters'), 249.1459765625)
        self.assertEqual(feg.get_res(8, units='meters'), 124.57298828125)
        feg = FixedEarthGrid(level_zero_res=0.05)
        self.assertEqual(feg.get_res(5, units='meters'), 276.82886284722224)
        self.assertEqual(feg.get_res(6, units='meters'), 138.41443142361112)

    def test_get_level(self):
        feg = FixedEarthGrid()
        self.assertEqual(feg.get_level(1.0), 0)
        self.assertEqual(feg.get_level(0.5), 1)
        self.assertEqual(feg.get_level(0.25), 2)
        self.assertEqual(feg.get_level(300, units='meters'), 9)
        feg = FixedEarthGrid(level_zero_res=0.3)
        self.assertEqual(feg.get_level(300, units='meters'), 7)
        feg = FixedEarthGrid(level_zero_res=0.2)
        self.assertEqual(feg.get_level(300, units='meters'), 7)
        feg = FixedEarthGrid(level_zero_res=0.18)
        self.assertEqual(feg.get_level(300, units='meters'), 7)
        feg = FixedEarthGrid(level_zero_res=0.05)
        self.assertEqual(feg.get_level(300, units='meters'), 5)

    def test_get_level_and_res(self):
        feg = FixedEarthGrid()
        self.assertEqual(feg.get_level_and_res(2.0), (0, 1))
        self.assertEqual(feg.get_level_and_res(1.0), (0, 1))
        self.assertEqual(feg.get_level_and_res(0.5), (1, 0.5))
        self.assertEqual(feg.get_level_and_res(0.4), (1, 0.5))
        self.assertEqual(feg.get_level_and_res(0.3), (2, 0.25))
        self.assertEqual(feg.get_level_and_res(0.25), (2, 0.25))
        self.assertEqual(feg.get_level_and_res(0.2), (2, 0.25))
        self.assertEqual(feg.get_level_and_res(0.1), (3, 0.125))
        self.assertEqual(feg.get_level_and_res(0.05), (4, 0.0625))
        self.assertEqual(feg.get_level_and_res(0.03), (5, 0.03125))
        self.assertEqual(feg.get_level_and_res(0.02), (6, 0.015625))
        self.assertEqual(feg.get_level_and_res(0.01), (7, 0.0078125))
        self.assertEqual(feg.get_level_and_res(0.005), (8, 0.00390625))

    def test_get_grid_size(self):
        feg = FixedEarthGrid()
        self.assertEqual(feg.get_grid_size(0), (360, 180))
        self.assertEqual(feg.get_grid_size(1), (720, 360))
        self.assertEqual(feg.get_grid_size(5), (11520, 5760))

        feg = FixedEarthGrid(level_zero_res=0.25)
        self.assertEqual(feg.get_grid_size(0), (1440, 720))
        self.assertEqual(feg.get_grid_size(1), (2880, 1440))
        self.assertEqual(feg.get_grid_size(5), (46080, 23040))
