import unittest


import datetime_helpers

class TestDaySpanGenerator(unittest.TestCase):
	def test_dayspan(self) :
		#Setup
		datestring = '2013-05-07T05:00:00'
		expected_start = '2013-05-07T00:00:00'
		expected_end = '2013-05-07T23:59:59'
		result = datetime_helpers.get_hansard_range(datestring)

		self.assertEqual(expected_start, result[0])
		self.assertEqual(expected_end, result[1])

if __name__ == '__main__':
	unittest.main()