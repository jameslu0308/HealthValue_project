
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

from dash import Dash, dcc, html, Input, Output, dash_table, State, callback_context
import dash_daq as daq
import dash_bootstrap_components as dbc


from datetime import datetime, timedelta
from dash import dash_table
import plotly.express as px
import numpy as np

import plotly.graph_objects as go

import pandas as pd
import json
from dash.exceptions import PreventUpdate
import time
from plotly.subplots import make_subplots



theme =  {
    'dark': True,
    'detail': '#007439',
    'primary': '#2D3038',
    'secondary': '#6E6E6E',
    'background':'#23262E',
    'color':'white'
}

def get_key_from_value(dictionary, value):
    keys = [key for key, val in dictionary.items() if val == value]
    return keys

def build_table(errdf):
    return dash_table.DataTable(
        errdf.to_dict('records'),
        [{"name": i, "id": i} for i in errdf.columns],
        page_size = 10,
        fill_width = False, 
        style_data_conditional = [
            {
                'if':{
                    'filter_query':'{tagscore} < 80',
                    'column_id':'tagscore'
                },
                'backgroundColor':'#FF4136',
                'color':'white',
            },
        ],
        style_cell_conditional= [
            {
                'if':{'column_id':'time'},
                'width':'30%'
            },
            {
                'if':{'column_id':'tag'},
                'width':'30%'
            },
            {
                'if':{'column_id':'tagscore'},
                'width':'30%'
            },
        ]
    )

def build_fig(df, ch_tagname):
    fig = make_subplots()
    fig.add_trace(
        go.Scatter(x=df.index, y=df.iloc[:,0], name=ch_tagname), secondary_y=False
        )
    return fig

# 健康度碼表
def build_gauge(ch_name, id_str):
    return daq.Gauge(
        color={'default':'black',"gradient":True,"ranges":{"red":[0,60],"yellow":[60,80],"green":[80,100]}},
        value=80,
        label=ch_name,
        max=100,
        min=0,
        id = id_str,
        showCurrentValue = True,
        style = {'width':'307px', 'display':'inline-block'}
    )


def build_indicator(part_id, ch_name, color):
    return daq.Indicator(
        id = part_id,
        label=ch_name,
        color=color,
        value=True,
        labelPosition = 'right',
        style = {'width':'60px', 'height':'30px'}
    )

# 三個分類標誌
def build_three_indicators(raw_part):
    return html.Div([
        build_indicator(raw_part+'_g_idr', "正常", "#00BB00"),
        build_indicator(raw_part+'_y_idr', "警示", "#FFD306"),
        build_indicator(raw_part+'_r_idr', "異常", "#CE0000"),
    ], style = {'width':'70px','display':'inline-block'})
    
# 碼表 + error table
def build_score_and_table(raw_part):
    if raw_part =='yachu':
        ch_name = '部位A'
    elif raw_part =='roll':
        ch_name = '部位B'
    elif raw_part =='inch':
        ch_name = '部位C'

    return html.Div([
        html.Div([
            build_gauge(ch_name+' 健康度分數',raw_part+'_score'), # 碼表分數 (中文名稱, id)
            build_three_indicators(raw_part), # 三個分類標誌 (id)

        ], style = {'height':'270px', 'display':'flex'}),
        dcc.Loading(
            id = raw_part+'-loading', # loading id 無應用在其他處
            children = [
                html.Div([], id = raw_part+'_err') # error table
            ],
            type = "circle"
        ),
    ], style = {'width':'20%', 'display':'inline-block', 'overflow':'auto', \
    "margin-left": "5px","margin-right": "5px"})







