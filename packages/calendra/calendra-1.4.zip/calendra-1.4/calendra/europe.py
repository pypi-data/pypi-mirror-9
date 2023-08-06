# -*- coding: utf-8 -*-

from datetime import date, timedelta

from dateutil import relativedelta as rd

from .core import WesternCalendar, ChristianMixin, OrthodoxMixin
from .core import THU, MON, FRI, SAT
from .core import Holiday


class CzechRepublic(WesternCalendar, ChristianMixin):
    "Czech Republic"
    include_easter_monday = True

    FIXED_HOLIDAYS = WesternCalendar.FIXED_HOLIDAYS + (
        (1, 1, "Restoration Day of the Independent Czech State"),
        (5, 1, "Labour Day"),
        (5, 8, "Liberation Day"),
        (7, 5, "Saints Cyril and Methodius Day"),
        (7, 6, "Jan Hus Day"),
        (9, 28, "St. Wenceslas Day (Czech Statehood Day)"),
        (10, 28, "Independent Czechoslovak State Day"),
        (11, 17, "Struggle for Freedom and Democracy Day"),
        (12, 24, "Christmas Eve"),
        (12, 26, "St. Stephen's Day (The Second Christmas Day)"),
    )


class Sweden(WesternCalendar, ChristianMixin):
    "Sweden"
    include_epiphany = True
    include_good_friday = True
    include_easter_sunday = True
    include_easter_monday = True
    include_ascension = True
    include_whit_sunday = True
    whit_sunday_abel = "Pentecost"
    # Christmas Eve is not a holiday but not a work day either
    include_christmas_eve = True
    include_boxing_day = True
    boxing_day_label = "Second Day of Christmas"

    FIXED_HOLIDAYS = WesternCalendar.FIXED_HOLIDAYS + (
        (5, 1, "Labour Day"),
        (6, 6, "National Day"),
        # New Year's Eve is not a holiday but not a work day either
        (12, 31, "New Year's Eve")
    )

    # Midsummer Eve is not a holiday but not a work day either
    def get_midsummer_eve(self, year):
        date_eve = Sweden.get_nth_weekday_in_month(
            year, 6, FRI, start=date(year, 6, 19))
        return date_eve

    def get_midsummer_day(self, year):
        date_eve = Sweden.get_nth_weekday_in_month(
            year, 6, SAT, start=date(year, 6, 20))
        return date_eve

    def get_variable_all_saints(self, year):
        all_saints = date(year, 10, 31)
        if all_saints.weekday() != SAT:
            all_saints = Sweden.get_nth_weekday_in_month(
                year, 11, SAT)
        return all_saints

    def get_variable_days(self, year):
        days = super(Sweden, self).get_variable_days(year)
        days.append((self.get_midsummer_day(year), "Midsummer's Day"))
        days.append((self.get_midsummer_eve(year), "Midsummer's Eve"))
        days.append((self.get_variable_all_saints(year), "All Saints"))
        return days


class Finland(WesternCalendar, ChristianMixin):
    "Finland"
    include_epiphany = True
    include_good_friday = True
    include_easter_sunday = True
    include_easter_monday = True
    include_ascension = True
    include_whit_sunday = True
    whit_sunday_label = 'Pentecost'
    include_christmas_eve = True
    include_boxing_day = True
    boxing_day_label = "St. Stephen's Day"

    observance_shift = None

    FIXED_HOLIDAYS = WesternCalendar.FIXED_HOLIDAYS + (
        (5, 1, "Labour Day"),
        (12, 6, "Independence Day"),
    )

    def get_midsummer_eve(self, year):
        date_eve = Finland.get_nth_weekday_in_month(
            year, 6, FRI, start=date(year, 6, 19))
        return date_eve

    def get_midsummer_day(self, year):
        date_eve = Finland.get_nth_weekday_in_month(
            year, 6, SAT, start=date(year, 6, 20))
        return date_eve

    def get_variable_all_saints(self, year):
        all_saints = date(year, 10, 31)
        if all_saints.weekday() != SAT:
            all_saints = Finland.get_nth_weekday_in_month(
                year, 11, SAT)
        return all_saints

    def get_variable_days(self, year):
        days = super(Finland, self).get_variable_days(year)
        days.append((self.get_midsummer_eve(year), "Midsummer's Eve"))
        days.append((self.get_midsummer_day(year), "Midsummer's Day"))
        days.append((self.get_variable_all_saints(year), "All Saints"))
        return days


class France(WesternCalendar, ChristianMixin):
    "France"
    include_easter_monday = True
    include_ascension = True
    include_whit_monday = True
    include_all_saints = True
    include_assumption = True

    FIXED_HOLIDAYS = WesternCalendar.FIXED_HOLIDAYS + (
        (5, 1, "Labour Day"),
        (5, 8, "Victory in Europe Day"),
        (7, 14, "Bastille Day"),
        (11, 11, "Armistice Day"),
    )


class FranceAlsaceMoselle(France):
    "France Alsace/Moselle"
    include_good_friday = True
    include_boxing_day = True


class Greece(OrthodoxMixin, WesternCalendar):
    "Greece"
    FIXED_HOLIDAYS = WesternCalendar.FIXED_HOLIDAYS + (
        (3, 25, "Independence Day"),
        (5, 1, "Labour Day"),
        (10, 28, "Ohi Day"),
    )
    include_epiphany = True
    include_clean_monday = True
    include_annunciation = True
    include_good_friday = True
    include_easter_sunday = True
    include_easter_monday = True
    include_whit_sunday = True
    whit_sunday_label = "Pentecost"
    include_whit_monday = True
    include_assumption = True
    include_boxing_day = True
    boxing_day_label = "Glorifying Mother of God"


class Hungary(WesternCalendar, ChristianMixin):
    "Hungary"
    include_easter_sunday = True
    include_easter_monday = True
    include_whit_sunday = True
    whit_sunday_label = "Pentecost Sunday"
    include_whit_monday = True
    whit_monday_label = "Pentecost Monday"
    include_boxing_day = True
    boxing_day_label = "Second Day of Christmas"
    include_all_saints = True

    FIXED_HOLIDAYS = WesternCalendar.FIXED_HOLIDAYS + (
        (3, 15, "National Day"),
        (5, 1, "Labour Day"),
        (8, 20, "St Stephen's Day"),
        (10, 23, "National Day"),
    )


class Iceland(WesternCalendar, ChristianMixin):
    "Iceland"
    include_holy_thursday = True
    include_good_friday = True
    include_easter_monday = True
    include_ascension = True
    include_whit_monday = True
    include_christmas_eve = True
    include_boxing_day = True
    boxing_day_label = "St Stephen's Day"

    FIXED_HOLIDAYS = WesternCalendar.FIXED_HOLIDAYS + (
        (5, 1, "Labour Day"),
        (6, 17, "Icelandic National Day"),
        (12, 31, "New Year's Eve"),
    )

    def get_first_day_of_summer(self, year):
        """It's the first thursday *after* April, 18th.
        If April the 18th is a thursday, then it jumps to the 24th.
        """
        return WesternCalendar.get_nth_weekday_in_month(
            year, 4, THU,
            start=date(year, 4, 19))

    def get_variable_days(self, year):
        days = super(Iceland, self).get_variable_days(year)
        days += [
            (
                self.get_first_day_of_summer(year),
                "First day of summer"),
            (
                Iceland.get_nth_weekday_in_month(year, 8, MON),
                "Commerce Day"),
        ]
        return days


class Italy(WesternCalendar, ChristianMixin):
    "Italy"
    FIXED_HOLIDAYS = WesternCalendar.FIXED_HOLIDAYS + (
        (4, 25, "Liberation Day"),
        (5, 1, "International Workers' Day"),
        (6, 2, "Republic Day"),
    )
    include_immaculate_conception = True
    include_epiphany = True
    include_easter_monday = True
    include_assumption = True
    include_all_saints = True
    include_assumption = True
    include_boxing_day = True
    boxing_day_label = "St Stephen's Day"


class Norway(WesternCalendar, ChristianMixin):
    "Norway"
    include_holy_thursday = True
    include_good_friday = True
    include_easter_sunday = True
    include_easter_monday = True
    include_ascension = True
    include_whit_monday = True
    include_whit_sunday = True
    include_boxing_day = True
    boxing_day_label = "St Stephen's Day"

    FIXED_HOLIDAYS = WesternCalendar.FIXED_HOLIDAYS + (
        (5, 1, "Labour Day"),
        (5, 17, "Constitution Day"),
    )


class Poland(WesternCalendar, ChristianMixin):
    "Poland"
    FIXED_HOLIDAYS = WesternCalendar.FIXED_HOLIDAYS + (
        (1, 6, 'Trzech Kroli'),
        (5, 1, 'Labour Day'),
        (5, 3, 'Constitution Day'),
        (11, 11, 'Independence Day'),
    )
    include_easter_sunday = True
    include_easter_monday = True
    include_whit_sunday = True
    whit_sunday_label = "Pentecost Sunday"
    include_corpus_christi = True
    include_assumption = True
    include_all_saints = True
    include_boxing_day = True


class UnitedKingdom(WesternCalendar, ChristianMixin):
    "United Kingdom"
    include_good_friday = True
    include_easter_sunday = True
    include_easter_monday = True
    include_boxing_day = True
    shift_new_years_day = True

    def get_variable_days(self, year):
        days = super(UnitedKingdom, self).get_variable_days(year)
        days += [
            Holiday(
                date(year, 5, 1) + rd.relativedelta(weekday=rd.MO(1)),
                "Early May Bank Holiday",
                indication="1st Monday in May",
            ),
            Holiday(
                date(year, 5, 30) + rd.relativedelta(weekday=rd.MO(-1)),
                "Spring Bank Holiday",
                indication="Last Monday in May",
            ),
            Holiday(
                date(year, 8, 31) + rd.relativedelta(weekday=rd.MO(-1)),
                "Late Summer Bank Holiday",
                indication="Last Monday in August",
            ),
        ]
        return days


class UnitedKingdomNorthernIreland(UnitedKingdom):
    "Northern Ireland (UK)"
    def get_variable_days(self, year):
        days = super(UnitedKingdomNorthernIreland, self) \
            .get_variable_days(year)
        # St Patrick's day
        st_patrick = date(year, 3, 17)
        days.append((st_patrick, "Saint Patrick's Day"))
        if st_patrick.weekday() in self.get_weekend_days():
            days.append((
                self.find_following_working_day(st_patrick),
                "Saint Patrick substitute"))

        # Battle of boyne
        battle_of_boyne = date(year, 7, 12)
        days.append((battle_of_boyne, "Battle of the Boyne"))
        if battle_of_boyne.weekday() in self.get_weekend_days():
            days.append((
                self.find_following_working_day(battle_of_boyne),
                "Battle of the Boyne substitute"))
        return days


class EuropeanCentralBank(WesternCalendar, ChristianMixin):
    "European Central Bank"
    FIXED_HOLIDAYS = WesternCalendar.FIXED_HOLIDAYS + (
        (5, 1, "Labour Day"),
        (12, 26, "St. Stephen's Day"),
    )

    include_good_friday = True
    include_easter_monday = True


class Belgium(WesternCalendar, ChristianMixin):
    "Belgium"

    FIXED_HOLIDAYS = WesternCalendar.FIXED_HOLIDAYS + (
        (5, 1, "Labour Day"),
        (7, 21, "National Day"),
        (11, 11, "Armistice of 1918"),
    )

    include_easter_monday = True
    include_ascension = True
    include_whit_monday = True
    include_assumption = True
    include_all_saints = True


class Germany(WesternCalendar, ChristianMixin):
    "Germany"

    FIXED_HOLIDAYS = WesternCalendar.FIXED_HOLIDAYS + (
        (5, 1, "Labour Day"),
        (10, 3, "Day of German Unity"),
    )

    include_easter_monday = True
    include_ascension = True
    include_whit_monday = True
    include_good_friday = True
    include_boxing_day = True
    boxing_day_label = "Second Christmas Day"


class BadenWurttemberg(Germany):
    "Baden-Württemberg"

    include_epiphany = True
    include_corpus_christi = True
    include_all_saints = True


class Bavaria(Germany):
    "Bavaria"

    include_epiphany = True
    include_corpus_christi = True
    include_all_saints = True
    include_assumption = True


class Berlin(Germany):
    "Berlin"


class Brandenburg(Germany):
    "Brandenburg"

    FIXED_HOLIDAYS = Germany.FIXED_HOLIDAYS + (
        (10, 31, "Reformation Day"),
    )


class Bremen(Germany):
    "Bremen"


class Hamburg(Germany):
    "Hamburg"


class Hesse(Germany):
    "Hesse"

    include_corpus_christi = True


class MecklenburgVorpommern(Germany):
    "Mecklenburg-Vorpommern"

    FIXED_HOLIDAYS = Germany.FIXED_HOLIDAYS + (
        (10, 31, "Reformation Day"),
    )


class LowerSaxony(Germany):
    "Lower Saxony"


class NorthRhineWestphalia(Germany):
    "North Rhine-Westphalia"

    include_corpus_christi = True
    include_all_saints = True


class RhinelandPalatinate(Germany):
    "Rhineland-Palatinate"

    include_corpus_christi = True
    include_all_saints = True


class Saarland(Germany):
    "Saarland"

    include_corpus_christi = True
    include_assumption = True
    include_all_saints = True


class Saxony(Germany):
    "Saxony"

    FIXED_HOLIDAYS = Germany.FIXED_HOLIDAYS + (
        (10, 31, "Reformation Day"),
    )

    def get_repentance_day(self, year):
        "Wednesday before November 23"
        day = date(year, 11, 23)
        while day.weekday() != 2:  # 2=Wednesday
            day -= timedelta(days=1)
        return (day, "Repentance Day")

    def get_variable_days(self, year):
        days = super(Germany, self).get_variable_days(year)
        days.append(self.get_repentance_day(year))
        return days


class SaxonyAnhalt(Germany):
    "Saxony-Anhalt"

    FIXED_HOLIDAYS = Germany.FIXED_HOLIDAYS + (
        (10, 31, "Reformation Day"),
    )

    include_epiphany = True


class SchleswigHolstein(Germany):
    "Schleswig-Holstein"


class Thuringia(Germany):
    "Thuringia"

    FIXED_HOLIDAYS = Germany.FIXED_HOLIDAYS + (
        (10, 31, "Reformation Day"),
    )
