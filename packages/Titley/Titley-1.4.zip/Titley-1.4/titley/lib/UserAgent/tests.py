import unittest
from useragent import RoundRobinRotator

class TestRoundRobinRotator(unittest.TestCase):
    def setUp(self):
        rotator = RoundRobinRotator()
        rotator.add('http', '1.2.3.1')
        rotator.add('http', '1.2.3.2')
        rotator.add('http', '1.2.3.3')
        rotator.add('http', '1.2.3.4')
        rotator.add('http', '1.2.3.5')
        rotator.add('https', '1.2.4.1')
        rotator.add('https', '1.2.4.2')
        rotator.add('https', '1.2.4.3')
        rotator.add('https', '1.2.4.4')
        rotator.add('https', '1.2.4.5')
        self.test_rotator = rotator

    def test_get(self):
        for _ in range(1, 2):
            for i in range(1, 6):
                self.assertEqual(self.test_rotator.get('http'), '1.2.3.{}'.format(i))

        for _ in range(1, 2):
            for i in range(1, 6):
                self.assertEqual(self.test_rotator.get('https'), '1.2.4.{}'.format(i))

unittest.main()
