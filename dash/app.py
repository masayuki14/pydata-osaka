# -*- coding: utf-8 -*-

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime
from datetime import timedelta

import mysql.connector
import pandas.io.sql as psql
conf = {
    'user': 'root',
    'password': 'root',
    'host': 'db',
    'database': 'pydata'
}

con = mysql.connector.connect(**conf)
df = psql.read_sql('''
select
    *
    , addtime( `date` , `time` ) as `datetime`
    , year(`date`) as year
    , month(`date`) as month
from waiting_time
    join attractions using (attraction_id)
where
    waiting_time is not null
''', con)

attractions = [ df.query('attraction_id == %d' % i) for i in df.attraction_id.unique() ]

graph = dcc.Graph(
    id='time-graph',
    figure={
        'data': [
            go.Scatter(
                x=dfl.datetime,
                y=dfl.waiting_time,
                mode='lines',
                name=dfl.head(1).name.iloc[0],
                x0=0,
                dx=1,
                y0=0,
                dy=60,
            ) for dfl in attractions
        ],
        'layout': go.Layout(
            title='waiting time',
            xaxis={
                'title': 'Date',
            },
            yaxis={
                'title': 'Waiting minutes',
                'gridwidth': 2,
                'dtick': 30,
            },
        )
    }
)

y_slider = dcc.Slider(
    id='year-slider',
    min=df['year'].min(),
    max=df['year'].max(),
    value=df['year'].min(),
    marks={str(year): str(year) for year in df['year'].unique()}
)

m_slider = dcc.Slider(
    id='month-slider',
    min=1,
    max=12,
    value=datetime.today().month,
    marks={ str(m+1): str(m+1) for m in range(12) }
)

external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Hello Theme Park'),

    html.Div(
        style={'width': '80%', 'margin': '0 auto', 'height': '600px'},
        children=[
        graph,
        html.Div([y_slider], style={'margin-bottom': '30px'}),
        html.Div([m_slider], style={'margin-bottom': '30px'})
    ]),
])


@app.callback(
    dash.dependencies.Output('time-graph', 'figure'),
    [dash.dependencies.Input('year-slider', 'value'), dash.dependencies.Input('month-slider', 'value')]
)
def update_figure(selected_year, selected_month):
    return {
        'data': [
            go.Scatter(
                x=dfl.datetime,
                y=dfl.waiting_time,
                mode='markers+lines',
                name=dfl.head(1).name.iloc[0],
                x0=0,
                dx=1,
                y0=0,
                dy=60,
            ) for dfl in attractions
        ],
        'layout': go.Layout(
            xaxis={
                'range': [datetime(selected_year, selected_month, 1), datetime(selected_year, selected_month + 1, 1) - timedelta(days=1)]
            },
            yaxis={
                'title': 'Waiting minutes',
                'gridwidth': 2,
                'dtick': 30,
            },
        )
    }


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
