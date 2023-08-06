from datetime import date
from datetime import datetime

import dateutil.relativedelta as rd

from . import GenericCalendarTest
from ..core import MON, TUE, THU, FRI, SAT, SUN
from ..core import Calendar, LunarCalendar, WesternCalendar
from ..core import IslamicMixin, JalaliMixin, ChristianMixin
from ..core import EphemMixin
from ..core import Holiday


class CalendarTest(GenericCalendarTest):

    def test_private_variables(self):
        self.assertTrue(hasattr(self.cal, '_holidays'))
        private_holidays = self.cal._holidays
        self.assertTrue(isinstance(private_holidays, dict))
        self.cal.holidays(2011)
        self.cal.holidays(2012)
        private_holidays = self.cal._holidays
        self.assertTrue(isinstance(private_holidays, dict))
        self.assertIn(2011, self.cal._holidays)
        self.assertIn(2012, self.cal._holidays)

    def test_year(self):
        holidays = self.cal.holidays()
        self.assertTrue(isinstance(holidays, (tuple, list)))
        self.assertEquals(self.cal._holidays[self.year], holidays)

    def test_another_year(self):
        holidays = self.cal.holidays(2011)
        self.assertTrue(isinstance(holidays, (tuple, list)))
        self.assertEquals(self.cal._holidays[2011], holidays)

    def test_is_working_day(self):
        self.assertRaises(
            NotImplementedError,
            self.cal.is_working_day, date(2012, 1, 1))

    def test_nth_weekday(self):
        # first monday in january 2013
        self.assertEquals(
            Calendar.get_nth_weekday_in_month(2013, 1, MON),
            date(2013, 1, 7)
        )
        # second monday in january 2013
        self.assertEquals(
            Calendar.get_nth_weekday_in_month(2013, 1, MON, 2),
            date(2013, 1, 14)
        )
        # let's test the limits
        # Jan 1st is a TUE
        self.assertEquals(
            Calendar.get_nth_weekday_in_month(2013, 1, TUE),
            date(2013, 1, 1)
        )
        # There's no 6th MONday
        self.assertEquals(
            Calendar.get_nth_weekday_in_month(2013, 1, MON, 6),
            None
        )

    def test_nth_weekday_start(self):
        # first thursday after 18th april
        start = date(2013, 4, 18)
        self.assertEquals(
            Calendar.get_nth_weekday_in_month(2013, 4, THU, start=start),
            date(2013, 4, 18)
        )
        # first friday after 18th april
        start = date(2013, 4, 18)
        self.assertEquals(
            Calendar.get_nth_weekday_in_month(2013, 4, FRI, start=start),
            date(2013, 4, 19)
        )

    def test_last_weekday(self):
        # last monday in january 2013
        self.assertEquals(
            Calendar.get_last_weekday_in_month(2013, 1, MON),
            date(2013, 1, 28)
        )
        # last thursday
        self.assertEquals(
            Calendar.get_last_weekday_in_month(2013, 1, THU),
            date(2013, 1, 31)
        )


class LunarCalendarTest(GenericCalendarTest):
    cal_class = LunarCalendar

    def test_new_year(self):
        self.assertEquals(
            self.cal.lunar(2014, 1, 1),
            date(2014, 1, 31)
        )


class MockCalendar(Calendar):

    def holidays(self, year=None):
        return (
            Holiday(date(year, 12, 25), 'Christmas'),
            Holiday(date(year, 1, 1), 'New year'),
        )

    def get_weekend_days(self):
        return []  # no week-end, yes, it's sad


class MockCalendarTest(GenericCalendarTest):
    cal_class = MockCalendar

    def test_holidays_set(self):
        self.assertIn(
            date(self.year, 12, 25), self.cal.holidays_set(self.year))

        self.assertIn(
            date(self.year, 1, 1), self.cal.holidays_set(self.year))

    def test_sorted_dates(self):
        holidays = list(self.cal.holidays(self.year))
        day, label = holidays.pop()
        for next_day, label in holidays:
            self.assertTrue(day <= next_day)
            day = next_day

    def test_add_workingdays_simple(self):
        # day is out of non-working-day
        self.assertEquals(
            self.cal.add_working_days(date(self.year, 12, 20), 0),
            date(self.year, 12, 20)
        )
        self.assertEquals(
            self.cal.add_working_days(date(self.year, 12, 20), 1),
            date(self.year, 12, 21)
        )

    def test_add_workingdays_on_holiday(self):
        # day is in holidays
        self.assertEquals(
            self.cal.add_working_days(date(self.year, 12, 25), 0),
            date(self.year, 12, 25)
        )
        self.assertEquals(
            self.cal.add_working_days(date(self.year, 12, 24), 1),
            date(self.year, 12, 26)
        )
        self.assertEquals(
            self.cal.add_working_days(date(self.year, 12, 24), 2),
            date(self.year, 12, 27)
        )

    def test_add_workingdays_span(self):
        day = date(self.year, 12, 20)
        # since this calendar has no weekends, we'll just have a 2-day-shift
        self.assertEquals(
            self.cal.add_working_days(day, 20),
            date(self.year + 1, 1, 11)
        )

    def test_add_working_days_exceptions(self):
        day = date(self.year, 12, 20)
        christmas = date(self.year, 12, 25)
        boxing = date(self.year, 12, 26)
        # exceptional workday
        self.assertEquals(
            self.cal.add_working_days(day, 20, extra_working_days=[christmas]),
            date(self.year + 1, 1, 10)
        )
        # exceptional holiday + exceptional workday
        self.assertEquals(
            self.cal.add_working_days(day, 20,
                                      extra_working_days=[christmas],
                                      extra_holidays=[boxing]),
            date(self.year + 1, 1, 11)
        )

    def test_add_exceptions(self):
        december_20th = date(self.year, 12, 20)
        christmas = date(self.year, 12, 25)
        # target_working_day *is* a working day
        target_working_day = self.cal.add_working_days(december_20th, 1)
        # Add extra working days
        extra_working_days = [christmas]
        # add extra holidays
        extra_holidays = [target_working_day]
        self.assertFalse(self.cal.is_working_day(christmas))
        self.assertTrue(
            self.cal.is_working_day(christmas,
                                    extra_working_days=extra_working_days))

        self.assertTrue(self.cal.is_working_day(target_working_day))
        self.assertFalse(
            self.cal.is_working_day(target_working_day,
                                    extra_holidays=extra_holidays))
        # test is_holiday
        self.assertTrue(self.cal.is_holiday(christmas))

    def test_datetime(self):
        self.assertFalse(
            self.cal.is_working_day(datetime(2014, 1, 1)))

    def test_add_working_days_backwards(self):
        day = date(self.year, 1, 3)
        # since this calendar has no weekends, we'll just have a 1-day-shift
        self.assertEquals(
            self.cal.add_working_days(day, -7),
            date(self.year - 1, 12, 26)
        )
        self.assertEquals(
            self.cal.sub_working_days(day, 7),
            date(self.year - 1, 12, 26)
        )
        # Negative argument to sub_working_days -> converted to positive.
        self.assertEquals(
            self.cal.sub_working_days(day, -7),
            date(self.year - 1, 12, 26)
        )


class SimpleObservanceCalendar(Calendar):
    """
    A simple calendar with a couple of holidays with typical observance rules:
    If a holiday falls on a weekend, then its observance is shifted to a
    nearby weekday.
    """
    FIXED_HOLIDAYS = (
        Holiday(
            date(2000, 12, 24), 'Christmas Eve', indication='December 24th',
            observance_shift=dict(weekday=rd.FR(-1)),
        ),
        Holiday(date(2000, 12, 25), 'Christmas', indication='December 25th'),
    )

    def get_weekend_days(self):
        return SAT, SUN


class ObservanceCalendarTest(GenericCalendarTest):
    """
    A simple calendar with days shifted for observance.
    """
    cal_class = SimpleObservanceCalendar

    def test_observance(self):
        """
        Each Holiday returned by the calendar should be aware of its indicated
        date and observance date.
        """
        holidays = list(self.cal.holidays(2011))
        assert len(holidays) == 2
        xmas_eve, xmas_day = holidays
        assert xmas_eve == date(2011, 12, 24)
        assert self.cal.get_observed_date(xmas_eve) == date(2011, 12, 23)
        assert xmas_day == date(2011, 12, 25)
        assert self.cal.get_observed_date(xmas_day) == date(2011, 12, 26)


class IslamicMixinTest(GenericCalendarTest):
    cal_class = IslamicMixin

    def test_year_conversion(self):
        days = self.cal.converted(2013)
        self.assertEquals(len(days), 365)


class JalaliMixinTest(GenericCalendarTest):
    cal_class = JalaliMixin

    def test_year_conversion(self):
        days = self.cal.converted(2013)
        self.assertEquals(len(days), 365)


class EphemMixinTest(GenericCalendarTest):
    cal_class = EphemMixin

    def test_calculate_some_equinoxes(self):
        self.assertEquals(
            self.cal.calculate_equinoxes(2010),
            (date(2010, 3, 20), date(2010, 9, 23))
        )
        self.assertEquals(
            self.cal.calculate_equinoxes(2010, 'Asia/Taipei'),
            (date(2010, 3, 21), date(2010, 9, 23))
        )
        self.assertEquals(
            self.cal.calculate_equinoxes(2013),
            (date(2013, 3, 20), date(2013, 9, 22))
        )
        self.assertEquals(
            self.cal.calculate_equinoxes(2014),
            (date(2014, 3, 20), date(2014, 9, 23))
        )
        self.assertEquals(
            self.cal.calculate_equinoxes(2020),
            (date(2020, 3, 20), date(2020, 9, 22))
        )

    def test_qingming_festivals(self):
        self.assertEquals(
            self.cal.solar_term(2001, 15),
            date(2001, 4, 4)
        )
        self.assertEquals(
            self.cal.solar_term(2001, 15, 'Asia/Taipei'),
            date(2001, 4, 5)
        )
        self.assertEquals(
            self.cal.solar_term(2011, 15),
            date(2011, 4, 5)
        )
        self.assertEquals(
            self.cal.solar_term(2014, 15),
            date(2014, 4, 4)
        )


class MockChristianCalendar(WesternCalendar, ChristianMixin):
    pass


class MockChristianCalendarTest(GenericCalendarTest):
    cal_class = MockChristianCalendar

    def test_year_2014(self):
        holidays = self.cal.holidays_set(2014)
        self.assertNotIn(date(2014, 1, 6), holidays)  # Epiphany
        self.assertNotIn(date(2014, 3, 3), holidays)  # Clean Monday
        self.assertNotIn(date(2014, 3, 5), holidays)  # Ash Wednesday
        self.assertNotIn(date(2014, 3, 25), holidays)  # Annunciation
        self.assertNotIn(date(2014, 4, 17), holidays)  # Holy Thursday
        self.assertNotIn(date(2014, 4, 18), holidays)  # 'Good Friday
        self.assertNotIn(date(2014, 4, 19), holidays)  # Easter sat
        self.assertNotIn(date(2014, 4, 20), holidays)  # Easter Sun
        self.assertNotIn(date(2014, 4, 21), holidays)  # Easter Mon
        self.assertNotIn(date(2014, 5, 29), holidays)  # Ascension
        self.assertNotIn(date(2014, 6, 8), holidays)   # Whit Sunday
        self.assertNotIn(date(2014, 6, 9), holidays)   # Whit Monday
        self.assertNotIn(date(2014, 6, 19), holidays)  # Corp. Christi
        self.assertNotIn(date(2014, 8, 15), holidays)  # Assumption
        self.assertNotIn(date(2014, 11, 1), holidays)  # All Saints
        self.assertNotIn(date(2014, 12, 8), holidays)  # Imm. Conc.
        self.assertNotIn(date(2014, 12, 24), holidays)  # Xmas Eve
        self.assertNotIn(date(2014, 12, 26), holidays)  # Boxing Day

        # The only Christian day that is a holiday for every calendar
        self.assertIn(date(2014, 12, 25), holidays)  # XMas

        # Only 2 days: Jan 1st and Christmas
        self.assertEquals(len(holidays), 2)
