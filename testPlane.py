import unittest
import mock
import calendar


class TestPlaneRisia(unittest.TestCase):
    def setUp(self):
        self.coterminousMonth = self.generateMockMonth()
        self.risia = calendar.Plane("risia", self.coterminousMonth, 1, 28, 28,
                                    812, 812, -9000)

    def test_initialCoter(self):
        self.periodTest(0, -9000, "Coterminous", 28)
        self.periodTest(5, -9000, "Coterminous", 23)
        self.periodTest(27, -9000, "Coterminous", 1)

    def test_nextCoter(self):
        self.periodTest(0, -8995, "Coterminous", 28)
        self.periodTest(5, -8995, "Coterminous", 23)
        self.periodTest(27, -8995, "Coterminous", 1)

    def test_initialRemote(self):
        self.periodTest(168, -8998, "Remote", 28)
        self.periodTest(172, -8998, "Remote", 24)
        self.periodTest(195, -8998, "Remote", 1)

    def test_nextRemote(self):
        self.periodTest(168, -8993, "Remote", 28)
        self.periodTest(172, -8993, "Remote", 24)
        self.periodTest(195, -8993, "Remote", 1)

    def test_initialWane(self):
        self.periodTest(28, -9000, "Waning", 812)
        self.periodTest(28, -8999, "Waning", 476)
        self.periodTest(28, -8998, "Waning", 140)
        self.periodTest(167, -8998, "Waning", 1)

    def test_initialWax(self):
        self.periodTest(196, -8998, "Waxing", 812)
        self.periodTest(196, -8997, "Waxing", 476)
        self.periodTest(196, -8996, "Waxing", 140)
        self.periodTest(335, -8996, "Waxing", 1)

    def periodTest(self, dayOfYear, year, state, daysLeft):
        mockCalendar = mock.Mock()
        fillerMonths = [self.generateMockMonth() for _ in range(11)]
        mockCalendar.months = [self.coterminousMonth] + fillerMonths
        mockCalendar.yearLength = 336
        retState, retDaysLeft = self.risia.getPlaneAtDate(dayOfYear, year,
                                                          mockCalendar)
        self.assertEqual(retState, state)
        self.assertEqual(retDaysLeft, daysLeft)

    def generateMockMonth(self):
        mockMonth = mock.Mock()
        mockMonth.length = 28
        return mockMonth
