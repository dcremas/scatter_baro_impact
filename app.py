from os.path import dirname, join
from pathlib import Path

import psycopg2
import pandas as pd
import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput, Range1d, Paragraph
from bokeh.plotting import figure

from models import stations, data, headers, time_update

pd_col_dtypes = {
    "rdg_year": int,
    "rdg_month": int,
    "rdg_day": int,
    "rdg_hour": int,
    "slp_3hr_diff": float,
    "slp_6hr_diff": float,
    "slp_24hr_diff": float,
    }

weatherdata = pd.DataFrame(data, columns=headers)
weatherdata = weatherdata.astype(pd_col_dtypes)
weatherdata['date'] = np.array(weatherdata['date'], dtype=np.datetime64)

axis_map = {
    "3 Hour Change": "slp_3hr_diff",
    "6 Hour Change": "slp_6hr_diff",
    "24 Hour Change": "slp_24hr_diff",
}

y_axis_range = {
    "3 Hour Change": (-0.40, 0.40), 
    "6 Hour Change": (-0.70, 0.70),
    "24 Hour Change": (-1.40, 1.40),
}

desc = Div(text=(Path(__file__).parent / "description.html").read_text("utf8"), sizing_mode="stretch_width",
           margin=(2, 2, 5, 15))

years = Slider(title="Year", value=2020, start=2020, end=2024, step=1, margin=(2, 2, 2, 15))
station_name = Select(title="Weather Station Name", value=stations[0], options=stations, margin=(2, 2, 2, 15))
y_axis = Select(title="Main Chart Y Axis", options=['3 Hour Change','6 Hour Change', '24 Hour Change'],
                value="3 Hour Change", margin=(2, 2, 2, 15))

source = ColumnDataSource(data=dict(x=weatherdata[weatherdata['station_name'] == stations[0]]['date'],
                                    y=weatherdata[weatherdata['station_name'] == stations[0]][axis_map[y_axis.value]]))

plot = figure(height=400, title="", toolbar_location=None, sizing_mode="stretch_width",
              x_axis_type="datetime", y_range=y_axis_range[y_axis.value], margin=(10, 10, 10, 15),
              background_fill_color="#f7ffeb")
plot.scatter(x="x", y="y", source=source, alpha=0.40)


def select_weather_records():
    selected = weatherdata[
        (weatherdata.rdg_year == years.value) &
        (weatherdata.station_name == station_name.value)
    ]
    return selected


def update():
    df = select_weather_records()
    y_name = axis_map[y_axis.value]
    plot.yaxis.axis_label = y_axis.value
    y_range_min = y_axis_range[y_axis.value][0]
    y_range_max = y_axis_range[y_axis.value][1]
    plot.y_range.update(start=y_range_min, end=y_range_max)
    source.data = dict(
        x=df['date'],
        y=df[y_name],
    )

controls = [years,  station_name, y_axis]
for control in controls:
    control.on_change('value', lambda attr, old, new: update())

update_text_1 = f'The Postgresql AWS Cloud Database that feeds the visuals was last updated:'
update_text_2 = f'Date: {time_update.strftime("%d %B, %Y")}'
update_text_3 = f'Time: {time_update.strftime("%I:%M:%S %p")}'

p1 = Paragraph(text=update_text_1, width=800, height=10, margin=(25, 25, 5, 15))
p2 = Paragraph(text=update_text_2, width=800, height=10, margin=(5, 25, 5, 15))
p3 = Paragraph(text=update_text_3, width=800, height=10, margin=(5, 25, 25, 15))

hyperlink_github = Div(
    text="""<p><i>To see the full codebase for this interactive web-based visualization: </i><a href="https://github.com/dcremas/scatter_baro_impact">Link to my github account</a></p>""",
    width=800, height=25, margin=(10, 10, 10, 15)
    )

hyperlink_div = Div(
    text="""<a href="https://dataviz.dustincremascoli.com">Go back to Data Visualizations Main Page</a>""",
    width=400, height=100, margin=(10, 10, 10, 15)
    )

layout = column(desc,
                hyperlink_github, 
                years,
                station_name,
                y_axis,
                plot,
                p1,
                p2,
                p3,
                hyperlink_div,
                sizing_mode="stretch_width", height=400)

update()

curdoc().add_root(layout)
curdoc().title = "Barometric Pressure Change Volatility"
