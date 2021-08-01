import datetime

import pandas as pd


class DateGenerator(object):

    def __new__(cls, date_attr):
        cls.date_generator = {
            "Today": cls.generate_date(0, 1),
            "Yesterday": cls.generate_date(1, 2),
            "Tomorrow": cls.generate_date(-1, 0),
            "This week": cls.generate_date_this_week(),
            "Last week": cls.generate_date_last_week(),
            "Last 7 days": cls.generate_date(1, 8),
            "This month": cls.generate_date_this_month(),
            "Last month": cls.generate_date_last_month(),
            "Last 30 days": cls.generate_date(1, 31),
            "This year": cls.generate_date_this_year(),
            "Last year": cls.generate_date_last_year()
        }
        return cls.date_generator[date_attr]


    @staticmethod
    def generate_date(range1, range2):
        return [(datetime.date.today() - datetime.timedelta(days=x)).strftime('%Y-%m-%d') for x in
                range(range1, range2)]


    @staticmethod
    def generate_date_this_week():
        today = datetime.date.today()
        start = today - datetime.timedelta(days=today.weekday()) - datetime.timedelta(days=1)
        return [(start + datetime.timedelta(days=x)).strftime('%Y-%m-%d') for x in range(0, 7)]


    @staticmethod
    def generate_date_last_week():
        today = datetime.date.today()
        start = today - datetime.timedelta(days=today.weekday()) - datetime.timedelta(days=1) - datetime.timedelta(
            days=7)
        return [(start + datetime.timedelta(days=x)).strftime('%Y-%m-%d') for x in range(0, 7)]


    @staticmethod
    def generate_date_this_month():
        given_date = datetime.datetime.today()
        first_day_of_month = given_date.replace(day=1)
        next_month = first_day_of_month.replace(day=28) + datetime.timedelta(days=4)
        last_day_of_month = next_month - datetime.timedelta(days=next_month.day)
        return [(first_day_of_month + datetime.timedelta(days=x)).strftime('%Y-%m-%d') for x in
                range(abs((last_day_of_month - first_day_of_month).days) + 1)]


    @staticmethod
    def generate_date_last_month():
        given_date = datetime.datetime.today()
        first_day_of_this_month = given_date.replace(day=1)
        any_day_of_last_month = first_day_of_this_month - datetime.timedelta(days=4)
        first_day_of_month = any_day_of_last_month.replace(day=1)
        next_month = first_day_of_month.replace(day=28) + datetime.timedelta(days=4)
        last_day_of_month = next_month - datetime.timedelta(days=next_month.day)
        return [(first_day_of_month + datetime.timedelta(days=x)).strftime('%Y-%m-%d') for x in
                range(abs((last_day_of_month - first_day_of_month).days) + 1)]

    @staticmethod
    def generate_date_this_year():
        given_date = datetime.datetime.today()
        first_day_of_year = given_date.replace(month=1).replace(day=1).strftime('%Y-%m-%d')
        last_day_of_year = given_date.replace(month=12).replace(day=31).strftime('%Y-%m-%d')
        return pd.to_datetime(list(pd.date_range(start=first_day_of_year, end=last_day_of_year))).strftime('%Y-%m-%d').tolist()

    @staticmethod
    def generate_date_last_year():
        given_date = datetime.datetime.today()
        #print(given_date.year)
        first_day_of_year = given_date.replace(year=given_date.year-1).replace(month=1).replace(day=1).strftime('%Y-%m-%d')
        last_day_of_year = given_date.replace(year=given_date.year-1).replace(month=12).replace(day=31).strftime('%Y-%m-%d')
        return pd.to_datetime(list(pd.date_range(start=first_day_of_year, end=last_day_of_year))).strftime('%Y-%m-%d').tolist()




# if __name__ == '__main__':
#     print(DateGenerator("Last 30 days"))
#     print(DateGenerator("Last year"))