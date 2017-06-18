import unittest
import flappy


class FlappyTest(unittest.TestCase):
    def test_int2bin(self):
        self.assertEqual(flappy.int2bin(0), [0])
        self.assertEqual(flappy.int2bin(1), [1])
        self.assertEqual(flappy.int2bin(2), [1, 0])
        self.assertEqual(flappy.int2bin(3), [1, 1])
        self.assertEqual(flappy.int2bin(100), [1, 1, 0, 0, 1, 0, 0])


if __name__ == "__main__":
    unittest.main()
