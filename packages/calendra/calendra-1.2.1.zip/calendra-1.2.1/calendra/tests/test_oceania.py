from datetime import date

from . import GenericCalendarTest
from ..oceania import Australia
from ..oceania import AustraliaCapitalTerritory
from ..oceania import AustraliaNewSouthWales
from ..oceania import AustraliaNorthernTerritory
from ..oceania import AustraliaQueensland
from ..oceania import SouthAustralia
from ..oceania import Tasmania, Hobart
from ..oceania import Victoria
from ..oceania import WesternAustralia
from ..oceania import MarshallIslands


class AustraliaTest(GenericCalendarTest):
    cal_class = Australia

    def test_year_2013(self):
        holidays = self.cal.holidays_set(2013)
        self.assertIn(date(2013, 1, 26), holidays)
        self.assertIn(date(2013, 1, 28), holidays)  # Australia day shift
        self.assertIn(date(2013, 1, 26), holidays)
        self.assertIn(date(2013, 3, 29), holidays)  # Good Friday
        self.assertIn(date(2013, 4, 25), holidays)
        self.assertIn(date(2013, 12, 25), holidays)

    def test_new_year_shift(self):
        holidays = self.cal.holidays_set(2012)
        self.assertIn(date(2012, 1, 2), holidays)  # 1st was a sunday

    def test_anzac_shift(self):
        holidays = self.cal.holidays_set(2010)
        self.assertIn(date(2010, 4, 26), holidays)


class AustraliaCapitalTerritoryTest(AustraliaTest):
    cal_class = AustraliaCapitalTerritory

    def test_regional_specific_2013(self):
        holidays = self.cal.holidays_set(2013)
        self.assertIn(date(2013, 3, 11), holidays)
        self.assertIn(date(2013, 3, 30), holidays)  # Easter Saturday
        self.assertIn(date(2013, 4, 1), holidays)  # Easter Monday
        self.assertIn(date(2013, 6, 10), holidays)  # Queen's Bday
        self.assertIn(date(2013, 9, 30), holidays)
        self.assertIn(date(2013, 10, 7), holidays)  # Labour day october
        self.assertIn(date(2013, 12, 26), holidays)  # Boxing day


class AustraliaNewSouthWalesTest(AustraliaTest):
    cal_class = AustraliaNewSouthWales

    def test_regional_specific_2013(self):
        holidays = self.cal.holidays_set(2013)
        self.assertIn(date(2013, 3, 30), holidays)  # Good friday
        self.assertIn(date(2013, 3, 31), holidays)  # Easter Sunday
        self.assertIn(date(2013, 6, 10), holidays)  # Queen's Bday
        self.assertIn(date(2013, 10, 7), holidays)  # Labour day october
        self.assertIn(date(2013, 12, 26), holidays)  # Boxing day

    def test_anzac_shift(self):
        # We don't shift
        holidays = self.cal.holidays_set(2010)
        self.assertNotIn(date(2010, 4, 26), holidays)


class AustraliaNorthernTerritoryTest(AustraliaTest):
    cal_class = AustraliaNorthernTerritory

    def test_regional_specific_2013(self):
        holidays = self.cal.holidays_set(2013)
        self.assertIn(date(2013, 3, 30), holidays)  # Easter Saturday
        self.assertIn(date(2013, 5, 6), holidays)  # May Day
        self.assertIn(date(2013, 6, 10), holidays)  # Queen's Bday
        self.assertIn(date(2013, 8, 5), holidays)  # Picnic day
        self.assertIn(date(2013, 12, 26), holidays)  # Boxing day


class AustraliaQueenslandTest(AustraliaTest):
    cal_class = AustraliaQueensland

    def test_regional_specific_2013(self):
        holidays = self.cal.holidays_set(2013)
        self.assertIn(date(2013, 3, 30), holidays)  # Easter Saturday
        self.assertIn(date(2013, 5, 6), holidays)  # May's labour day
        self.assertIn(date(2013, 6, 10), holidays)  # Queen's Bday
        self.assertIn(date(2013, 12, 26), holidays)  # Boxing day


class SouthAustraliaTest(AustraliaTest):
    cal_class = SouthAustralia

    def test_regional_specific_2013(self):
        holidays = self.cal.holidays_set(2013)
        self.assertIn(date(2013, 3, 11), holidays)  # Adelaide's cup
        self.assertIn(date(2013, 3, 30), holidays)  # Easter Saturday
        self.assertIn(date(2013, 6, 10), holidays)  # Queen's Bday
        self.assertIn(date(2013, 10, 7), holidays)  # Labour day october
        self.assertIn(date(2013, 12, 26), holidays)  # Proclamation day


class TasmaniaTest(AustraliaTest):
    cal_class = Tasmania

    def test_regional_specific_2013(self):
        holidays = self.cal.holidays_set(2013)
        self.assertIn(date(2013, 3, 11), holidays)  # Eight hours day
        self.assertIn(date(2013, 6, 10), holidays)  # Queen's Bday
        self.assertIn(date(2013, 12, 26), holidays)  # Boxing day

    def test_anzac_shift(self):
        # We don't shift
        holidays = self.cal.holidays_set(2010)
        self.assertNotIn(date(2010, 4, 26), holidays)


class NonHobartTest(TasmaniaTest):
    def test_tasmania_2013(self):
        holidays = self.cal.holidays_set(2013)
        self.assertIn(date(2013, 11, 4), holidays)  # Recreation Day


class HobartTest(TasmaniaTest):
    cal_class = Hobart

    def test_hobart_specific_2013(self):
        holidays = self.cal.holidays_set(2013)
        self.assertIn(date(2013, 2, 11), holidays)  # Royal Hobart Regatta
        # Recreation day not in Hobart
        self.assertNotIn(date(2013, 11, 4), holidays)  # Recreation Day


class VictoriaTest(AustraliaTest):
    cal_class = Victoria

    def test_regional_specific_2013(self):
        holidays = self.cal.holidays_set(2013)
        self.assertIn(date(2013, 3, 11), holidays)  # Labours day in march
        self.assertIn(date(2013, 3, 30), holidays)  # Easter Saturday
        self.assertIn(date(2013, 6, 10), holidays)  # Queen's Bday
        self.assertIn(date(2013, 11, 5), holidays)  # Melbourne's cup
        self.assertIn(date(2013, 12, 26), holidays)  # Boxing day


class WesternAustraliaTest(AustraliaTest):
    cal_class = WesternAustralia

    def test_regional_specific_2013(self):
        holidays = self.cal.holidays_set(2013)
        self.assertIn(date(2013, 3, 4), holidays)  # Labours day in march
        self.assertIn(date(2013, 6, 3), holidays)  # Western Australia Day
        self.assertIn(date(2013, 12, 26), holidays)  # Boxing day
        # It is not possible to surely compute Queen's Birthday holiday in
        # The western Australia territory, since it's based on the Governor
        # Decision (it is typically the last Monday of September or the first
        # Monday of October)


class MarshallIslandsTest(GenericCalendarTest):
    cal_class = MarshallIslands

    def test_year_2013(self):
        holidays = self.cal.holidays_set(2013)
        self.assertIn(date(2013, 1, 1), holidays)  # new year
        self.assertIn(date(2013, 3, 3), holidays)  # Remembrance day
        self.assertIn(date(2013, 3, 29), holidays)  # (good friday)
        self.assertIn(date(2013, 5, 1), holidays)  # constitution day
        self.assertIn(date(2013, 7, 5), holidays)  # Fishermens
        self.assertIn(date(2013, 9, 6), holidays)  # labour day
        self.assertIn(date(2013, 9, 27), holidays)  # Manit Day
        self.assertIn(date(2013, 11, 17), holidays)  # presidents day
        self.assertIn(date(2013, 12, 6), holidays)  # gospel day
        self.assertIn(date(2013, 12, 25), holidays)  # Xmas
        self.assertIn(date(2013, 12, 31), holidays)  # new year's eve
