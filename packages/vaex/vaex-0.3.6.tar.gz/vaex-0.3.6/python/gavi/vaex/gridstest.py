__author__ = 'maartenbreddels'

import unittest


class MyTestCase(unittest.TestCase):
	def test_something(self):
		self.assertEqual(True, False)

		grids = Grids()
		grids.add_grid(512, )


if __name__ == '__main__':
	unittest.main()
