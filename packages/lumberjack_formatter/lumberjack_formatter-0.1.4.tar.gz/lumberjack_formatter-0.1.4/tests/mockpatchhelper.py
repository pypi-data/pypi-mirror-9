import unittest

class MockingTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(MockingTestCase, self).__init__(*args, **kwargs)

        self.patches = []

    def _patch(self, p):
        self.patches.append(p)
        p.start()

    def tearDown(self):
        self._unpatchAll()

    def _unpatchAll(self):
        for p in self.patches:
            p.stop()
