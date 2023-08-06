#!/usr/bin/env python3

# Copyright Louis Paternault 2011-2014
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>. 1

"""Configuration file and its representation."""

import datetime
import logging
import re

from scal import errors

LOGGER = logging.getLogger(__name__)

WEEK_CHOICES = ['both', 'none', 'work', 'iso']

def parse_weeks(text):
    """Convert text into the inner representation of week option."""
    if text not in WEEK_CHOICES:
        raise KeyError(text)
    return {
        'work': text in ['both', 'work'],
        'iso': text in ['both', 'iso'],
        }

def is_between(start, middle, end):
    """Return True if `middle` is between `start` and `end`."""
    return start <= middle and middle <= end

class Period:
    """A (possibly named) period of time"""
    #pylint: disable=too-few-public-methods

    start = None
    end = None
    name = None

    def __init__(self, start, end, name=None):
        if start > end:
            raise errors.ConfigError("Start date is older than end date.")
        self.start = start
        self.end = end
        self.name = name

    def __str__(self):
        txt = "{} --- {}".format(self.start, self.end)
        if self.name:
            return "{}: {}".format(txt, self.name)
        else:
            return txt

    def is_in(self, day):
        """Return True iff ``day`` is in this period."""
        return is_between(self.start, day, self.end)

RE_DATE_STR = r'((?P<year{id}>\d{{4}})-)?(?P<month{id}>\d{{2}})-(?P<day{id}>\d{{2}})' #pylint: disable=line-too-long
RE_DATE = re.compile(RE_DATE_STR.format(id=""))
RE_FROMTO = re.compile(r'^From *{} *to *{}$'.format(
    RE_DATE_STR.format(id='0'),
    RE_DATE_STR.format(id='1'),
    ))
RE_HOLIDAY = re.compile(r'^(?P<start>{})? *(?P<end>{}) *(?P<name>.*)$'.format(
    RE_DATE_STR.format(id='0'),
    RE_DATE_STR.format(id='1'),
    ))
RE_AFFECTATION = re.compile(r'^(?P<name>\w*) *= *(?P<value>.*)$')

DEFAULT_CONFIG = {
    'lang': 'english',
    'papersize': 'a4paper',
    }

WEDNESDAY = 3

def date(year, month, day):
    """Return a `datetime.date` object.

    The arguments may be anything that can be converted to integers.
    """
    return datetime.date(int(year), int(month), int(day))

def last_day_of_month(mydate):
    "Return a date corresponding to the last day of the month of the argument."
    if mydate.month == 12:
        next_month = mydate.replace(mydate.year + 1, 1, 1)
    else:
        next_month = mydate.replace(mydate.year, mydate.month + 1, 1)
    return next_month - datetime.timedelta(days=1)

def weeknumber(day):
    """Return week number."""
    return day.isocalendar()[1]

class Calendar:
    """A calendar, that is, a start date, an end date, and holidays."""

    def __init__(self, file):
        self.start = None
        self.end = None
        self.holidays = []
        self.config = DEFAULT_CONFIG.copy()

        linenumber = 0
        for line in file:
            linenumber += 1
            stripped = line.split("#")[0].strip(' \n')
            if not stripped:
                continue
            if RE_FROMTO.match(stripped):
                match = RE_FROMTO.match(stripped)
                self.set_start(
                    match.group('year0'),
                    match.group('month0'),
                    match.group('day0'),
                    )
                self.set_end(
                    match.group('year1'),
                    match.group('month1'),
                    match.group('day1')
                    )
            elif RE_HOLIDAY.match(stripped):
                match = RE_HOLIDAY.match(stripped)
                self.add_holiday(
                    (
                        match.group('year0'),
                        match.group('month0'),
                        match.group('day0'),
                    ),
                    (
                        match.group('year1'),
                        match.group('month1'),
                        match.group('day1'),
                    ),
                    match.group('name'),
                    line
                    )
            elif RE_AFFECTATION.match(stripped):
                match = RE_AFFECTATION.match(stripped)
                self.config[match.group('name')] = match.group('value')
            else:
                raise errors.ConfigError(
                    "Could not parse line {}: '{}'.".format(
                        linenumber,
                        line[:-1],
                    )
                )

        if self.start is None or self.end is None:
            raise errors.ConfigError("Missing start or end date.")

        # Filling first and last month
        if self.start.day != 1:
            self.holidays.append(Period(
                datetime.date(self.start.year, self.start.month, 1),
                self.start - datetime.timedelta(days=1),
                ))
            self.start = datetime.date(self.start.year, self.start.month, 1)
        if self.end != last_day_of_month(self.end):
            self.holidays.append(Period(
                self.end + datetime.timedelta(days=1),
                last_day_of_month(self.end),
                ))
        self.end = last_day_of_month(self.end)

    def set_start(self, year, month, day):
        """Defin the start date of the calendar."""
        if self.start is not None:
            raise errors.ConfigError(
                "Calendar boundaries configured twice."
                )
        if year is None:
            raise errors.ConfigError(
                "Missing year in 'From <DATE> to <DATE>' line."
                )
        self.start = date(year, month, day)

    def set_end(self, year, month, day):
        """Defin the end date of the calendar."""
        if self.end is not None:
            raise errors.ConfigError(
                "Calendar boundaries configured twice."
                )
        if year is None:
            raise errors.ConfigError(
                "Missing year in 'From <DATE> to <DATE>' line."
                )
        self.end = date(year, month, day)

    def add_holiday(self, date0, date1, name="", line=None):
        """Add a holiday, starting on `date0` and ending on `date1`.

        This holiday may be named. If it is read from the
        configuration file, the content of the corresponding line may
        be provided.
        """
        year0, month0, day0 = date0
        year1, month1, day1 = date1
        if (year0 is None) and (month0 is None) and (day0 is None):
            year0, month0, day0 = year1, month1, day1
        if (
                (year0 is None) and (year1 is not None)
            ) or (
                (year0 is not None) and (year1 is None)
            ):
            raise errors.ConfigError(
                "Either one or both years may be omitted (line '{}').".format(
                    str(line)
                )
            )
        if year0 is None:
            for year in range(self.start.year, self.end.year + 1):
                try:
                    if (
                            is_between(
                                self.start,
                                date(year, month0, day0),
                                self.end,
                            )
                            and is_between(
                                self.start,
                                date(year, month1, day1),
                                self.end,
                            )
                        ):
                        self.holidays.append(Period(
                            date(year, month0, day0),
                            date(year, month1, day1),
                            name,
                            ))
                except errors.ConfigError:
                    LOGGER.warning(
                        (
                            "Ignored period {}--{} (invalid or outside "
                            "calendar boundaries)."
                        ).format(
                            date(year, month0, day0),
                            date(year, month1, day1)
                        )
                    )
        else:
            try:
                self.holidays.append(Period(
                    date(year0, month0, day0),
                    date(year1, month1, day1),
                    name,
                    ))
            except errors.ConfigError:
                LOGGER.warning(
                    (
                        "Ignored period {}--{} (invalid or outside calendar "
                        "boundaries)."
                    ).format(
                        date(year0, month0, day0),
                        date(year1, month1, day1),
                    )
                )

    def is_holiday(self, day):
        """Return True iff ``day`` is in a holiday."""
        return len([
            None
            for holiday
            in self.holidays
            if holiday.is_in(day)
            ]) > 0

    def months_count(self):
        """Return the number of months of the calendar."""
        return (
            12 * (self.end.year - self.start.year)
            + self.end.month
            - self.start.month
            + 1
            )

    def year_boundaries(self):
        """Return the first and last month of each year, as a dictionary.

        This is important for the first and last years, which can
        start or end by something else than January or December.
        """
        years = {}
        for year in range(self.start.year, self.end.year + 1):
            if self.start.year == self.end.year:
                boundaries = [self.start.month, self.end.month]
            elif year == self.start.year:
                boundaries = [self.start.month, 12]
            elif year == self.end.year:
                boundaries = [1, self.end.month]
            else:
                boundaries = [1, 12]
            years[year] = [format(i, '02d') for i in boundaries]
        return years

    def is_workingweek(self, wednesday):
        """Return True iff week of argument is a working week."""
        all_holiday = True
        for day in range(wednesday.toordinal() - 2, wednesday.toordinal() + 3):
            all_holiday = (
                all_holiday
                and self.is_holiday(datetime.date.fromordinal(day))
                )
        return not all_holiday


    def week_iterator(self):
        """Iterate over weeks of self."""
        # Looking for first wednesday
        for day in range(self.start.toordinal(), self.start.toordinal()+7):
            if datetime.date.fromordinal(day).isoweekday() == WEDNESDAY:
                wednesday = datetime.date.fromordinal(day)

        workweek = 0
        while wednesday <= self.end:
            if self.is_workingweek(wednesday):
                workweek += 1
                maybe_workweek = workweek
            else:
                maybe_workweek = None
            yield wednesday, maybe_workweek, weeknumber(wednesday)
            wednesday += datetime.timedelta(days=7)

    def weeks(self, work, iso):
        """Return the list of weeks, processed by template."""
        weeks = []
        for (day, work_number, iso_number) in self.week_iterator():
            week = {
                'date': day,
                'work': None,
                'iso': None,
                }
            if work:
                week['work'] = work_number
            if iso:
                week['iso'] = iso_number
            weeks.append(week)
        return weeks

    def __str__(self):
        return (
            "From {} to {}\n".format(self.start, self.end)
            +
            "\n".join([str(holiday) for holiday in self.holidays])
            )
