from random import randint
from secrets import token_hex
from sqlalchemy import func
from data_management.db_models import *


def chart_from_column_elements(column, title='', type="bar"):
    hostname_counts = db.session.query(column, func.count().label('count')) \
        .group_by(column) \
        .all()
    # Convert the result into a dictionary for easy printing
    hostname_counts_dict = {hostname: count for hostname, count in hostname_counts}
    # Print the key-value pairs
    data = []
    for hostname, count in hostname_counts_dict.items():
        data.append(ChartDataElement(hostname, count))
    return Chart(name=token_hex(10), title=title, w="250em", h="150em", chart_type=type, chart_data=data)


class ChartDataElement:
    def __init__(self, label, value, color=None):
        self.label = label
        self.value = value
        if color is None:
            r = randint(0, 255)
            g = randint(0, 255)
            b = randint(0, 255)
            self.color = f"rgba({r}, {g}, {b}, 0.7)"
        else:
            self.color = color


class Chart:
    def __init__(self, name, w, h, chart_type, chart_data: list, title="", precision=0):
        if chart_data is None:
            chart_data = []
        self.name = name
        self.w, self.h = w, h
        self.type = chart_type
        self.data = chart_data
        self.title = title
        self.precision = precision
