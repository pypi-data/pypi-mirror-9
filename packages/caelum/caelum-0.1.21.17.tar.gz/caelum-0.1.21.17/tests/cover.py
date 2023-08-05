import unittest
import unit

class CoverageTest(unittest.TestCase):
    def test_module(self):
        from coverage import coverage
        cov = coverage()
        cov.start()
        suite = unittest.TestLoader().loadTestsFromTestCase(unit.BaseEERETest)
        unittest.TextTestRunner(verbosity=2).run(suite)
        cov.stop()
        r = cov.report()
        self.assertAlmostEquals(r, 985289)

if __name__ == '__main__':
    unittest.main()
