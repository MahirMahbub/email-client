from enum import Enum


class DateFilters(str, Enum):
    ALL_TIME = "All time"
    TODAY = "Today"
    YESTERDAY = "Yesterday"
    THIS_WEEK = "This week"
    LAST_WEEK = "Last week"
    THIS_MONTH = "This month"
    LAST_MONTH = "Last month"
    THIS_YEAR = "This year"
    LAST_YEAR = "Last year"
