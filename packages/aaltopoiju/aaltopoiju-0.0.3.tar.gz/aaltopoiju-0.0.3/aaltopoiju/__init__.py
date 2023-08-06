# -*- coding: utf-8 -*-
"""
Parses aaltopoiju.fi weather data
"""

from bs4 import BeautifulSoup
from pprint import pprint
import datetime
import pytz
import requests
import re

class Aaltopoiju(object):
    """
    Parses aaltopoiju.fi marine weather data.
    """
    def __init__(self):
        self.soup = None
        self.data = None

    def fetch(self):
        response = requests.post("http://aaltopoiju.fi/charts.php", {"helsinki": "true", "kalbadagrund": "true", "eestiluoto": "true", "harmaja": "true", "hel_majakka": "true", "makiluoto": "true", "loksa": "true", "naissaare": "true"})
        text = response.text.encode("utf8")
        self.data = text
        return self.parse_string(text)

    def parse_string(self, string):
        parser_opts = {
            u'Aallonkorkeus': {"dest": "wave_height", "callback": self._parse_float},
            u'Aallonperiodi': {"dest": "wave_period", "callback": self._parse_float},
            u'Aallonsuunta': {"dest": "wave_direction", "callback": self._parse_direction},
            u'Tuulensuunta': {"dest": "wind_direction", "callback": self._parse_direction},
            u'Maksimituuli': {"dest": "wind_max", "callback": self._parse_float},
            u'Puuskatuuli': {"dest": "wind_gusts", "callback": self._parse_float},
            u'Suunnanhajonta': {"dest": "wave_dispersion", "callback": self._parse_float},
            u'Tuulennopeus': {"dest": "wind_speed", "callback": self._parse_float},
            u'Ilmanl\xe4mp\xf6tila \xb0C': {"dest": "air_temperature", "callback": self._parse_float},
            u'Vedenl\xe4mp\xf6tila \xb0C': {"dest": "water_temperature", "callback": self._parse_float},
        }

        string = string.replace("<table", "</table><table")

        self.soup = BeautifulSoup(string)

        data = {}
        tables = self.soup.findAll("table", {"class": "chart"})
        for table in tables:
            title = table.find("td", {"class": "title"}).text
            trs = table.findAll("tr")
            line_data = {}
            times = []
            dates = []
            num_observations = 0
            if trs is None:
                continue
            for tr in trs:
                tds = tr.findAll("td")
                row_header = None
                if tds is None:
                    continue
                for td in tds:
                    try:
                        if "header" in td["class"]:
                            row_header = td.text
                            continue
                    except KeyError:
                        continue

                    if row_header is None:
                        continue
                    elif row_header == "EET":
                        if "time" in td["class"]:
                            num_observations += 1
                        times.append(td.text.replace("h", ""))
                    elif row_header == u'P\xe4iv\xe4m\xe4\xe4r\xe4':
                        dates.append(td.text)
                    else:
                        if row_header in parser_opts:
                            options = parser_opts[row_header]
                            dest = options["dest"]
                            if dest not in line_data:
                                line_data[dest] = []
#                            print title, row_header, options, td.text
                            line_data[dest].append(options["callback"](td))

            today = datetime.date.today()
            current_day = today.day
            current_month = today.month
            current_year = today.year
            previous_day = None

            timestamps = []
            for i in range(len(times)):
                hour = times[i]
                date = dates[i]
                date = re.match(".*?([0-9]+).*?", date)
                date = int(date.group(1))
                month = current_month
                year = current_year
                if previous_day is None:
                    # This is first day we process.
                    # It's from a) this month (day or two earlier than current one),
                    #           b) previous month (it's beginning of the month), or
                    #           c) next month (only forecasts available)
                    # c: check whether this is forecast
                    if num_observations == 0 and date < current_day:
                        # Only forecasts available and date is before current day
                        month = (current_month + 1)
                        if month > 12:
                            month = 1
                            year += 1
                    # b
                    elif current_day < 5 and date > current_day:
                        # At the beginning of the month, and date is larger than current one.
                        month = (current_month - 1)
                        if month == 0:
                            month = 12
                            year -= 1

                else:
                    # We already processed data earlier.
                    month = previous_day[1]
                    year = previous_day[0]
                    if date < previous_day[2]:
                        # Date is smaller than previous one -> it must be next month
                        month += 1
                        if month > 12:
                            month = 1
                            year += 1

                previous_day = (year, month, date)
                timestamp_string = "%s-%s-%sT%s" % (year, str(month).zfill(2), str(date).zfill(2), str(hour).zfill(2))
                timestamps.append(datetime.datetime.strptime(timestamp_string, "%Y-%m-%dT%H"))

            table_data = {"observations": [], "forecasts": []}
            observations_until = None
            for i in range(num_observations):
                d = {
                    "timestamp": timestamps[i]
                }
                for field in line_data:
                    d[field] = line_data[field][i]
                table_data["observations"].append(d)
                observations_until = timestamps[i]

            for i in range(num_observations, len(timestamps)):
                if observations_until and observations_until >= timestamps[i]:
                    # Do not add forecasts for times where there's already observations
                    continue
                d = {
                    "timestamp": timestamps[i]
                }
                for field in line_data:
                    try:
                        d[field] = line_data[field][i]
                    except IndexError:
                        pass
                table_data["forecasts"].append(d)

            data[title] = table_data
        return data

    def _TODO(self, *args, **kwargs):
        pass

    @classmethod
    def _parse_direction(cls, elem):
        return float(elem.find("img")["title"].replace(u"\xb0", ""))

    @classmethod
    def _parse_float(cls, value):
        """ Parses float field (may contain unit) to python float. Trailing > is removed. """
        value = value.text
        if value == "-" or len(value) == 0:
            # No data available
            return
        value = value.replace(",", ".").split(u"\xa0")
        value = value[0]
        value = value.split(" ")
        if value[0] == ">":
            value = value[1:]
        return float(value[0])
