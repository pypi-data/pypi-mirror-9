import unittest
import pkg_resources


class Test_availability(unittest.TestCase):
    def get_scaffold(self, name='ziggurat'):
        eps = list(pkg_resources.iter_entry_points('pyramid.scaffold'))
        for entry in eps:
            try:
                scaffold_class = entry.load()
                scaffold = scaffold_class(entry.name)
                if scaffold.name == name:
                    return scaffold
            except Exception as e: # pragma: no cover
                print('Warning: could not load entry point %s (%s: %s)' % (
                    entry.name, e.__class__.__name__, e))

    def test_availability(self):
        found = self.get_scaffold()
        self.assertEqual(found, 'found')
