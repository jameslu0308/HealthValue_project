# -*- coding: utf-8 -*-
"""
Created on Tue Dec 27 08:26:58 2022

@author: James
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
import random
import calendar
from datetime import datetime
from datetime import timedelta
import pickle
import time
import dash
from dash import Dash, dcc, html, Input, Output, dash_table, State, callback_context
import dash_daq as daq
import dash_bootstrap_components as dbc
import os 
import dashcomp
from dashcomp import build_table, get_key_from_value, build_fig, build_gauge, \
    build_three_indicators, build_score_and_table, theme
from dash.exceptions import PreventUpdate

from plotly.subplots import make_subplots


app = Dash(__name__, suppress_callback_exceptions=True,)
time_format = "%Y-%m-%d %H:%M:%S"

# 假資料

current_path = os.path.abspath(__file__)
parent_directory = os.path.dirname(current_path)
a_path = parent_directory + r'\fake_df\a_df.xlsx'
b_path = parent_directory + r'\fake_df\b_df.xlsx'
c_path = parent_directory + r'\fake_df\c_df.xlsx'

chdf_path = parent_directory + r'\fake_df\f_df.xlsx'
safetag_path = parent_directory + r'\fake_df\safetag_df.xlsx'


a_df = pd.read_excel(a_path, index_col=None)
b_df = pd.read_excel(b_path, index_col=None)
c_df = pd.read_excel(c_path, index_col=None)
chdf = pd.read_excel(chdf_path, index_col=0)
safetag_df = pd.read_excel(safetag_path, index_col=None)

app.layout = html.Div(children=[
    html.Header([
        html.H1(
            className='title1',
            children=['設備']),
        html.Nav(
            html.Ul(children=[
                html.Li(html.A(href='', children=['一'])),
                html.Li(html.A(href='', children=['二'])),
                html.Li(html.A(href='', children=['三'])),
                html.Li(html.A(href='', children=['四']))
            ], className='menu')
        ),
    ]),
    # 設備健康度 更新頻率
    html.Div([
        html.H1(['範例說明']),
        html.Div(
            id="banner-tabs",
            className="tabs",
            children=[
                dcc.Tabs(
                    id="app-banner-tabs",
                    value="health-page",
                    className="custom-tabs",
                    children=[
                        dcc.Tab(
                            id="health-tab",
                            label="分頁一",
                            value="health-page",
                            className="custom-tab",
                            selected_className="custom-tab--selected",
                        ),
                        dcc.Tab(
                            id="safe-tab",
                            label="分頁二",
                            value="safe-page",
                            className="custom-tab",
                            selected_className="custom-tab--selected",
                        ),
                    ],
                )
            ],
        )
    ], style={'padding': '0.5vw'}),
    html.Div(id='layout'),
], style={'margin': '0 auto'})

# tab 頁面 cllback
@app.callback([Output('layout', 'children')],
              [Input('app-banner-tabs', 'value')])
def banner_tab_swith(tab):
    # 設備健康度 tab頁面呈現
    if tab == 'health-page':
        return [html.Div(
            children=[
                html.Div([
                    html.Div(children=[
                        # 機台 1 2 4 5
                        dcc.Dropdown(['機台1', '機台2', '機台3', '機台4', '機台5',
                                     '機台6', '機台C', '機台8'], '機台6', id='machine'),
                        html.Button(children=['確認'],
                                    id='machine_sure', n_clicks=0)
                    ], style={'width': '48%', 'display': 'inline-block'}),

                    html.H2(['機台正常生產中']),
                    html.H2(['模具顯示範例']),
                ], style={'padding': '0.5vw'}),
                html.Br(),
                # 健康度分數
                html.Div(children=[
                    build_score_and_table('yachu'),
                    build_score_and_table('roll'),
                    build_score_and_table('inch')
                ], style={'display': 'flex', 'padding': '0.5vw'}),
                # 點位選取列
                dbc.Row(
                    [
                        html.Div("點位", style={
                                 'padding': '0vw 1vw', 'font-size': '1.1vw'}),
                        dcc.Dropdown(
                            id='machine-tag-dropdown',
                            style={'backgroundColor': 'white',
                                   'color': 'black', 'width': '20vw'}
                        ),
                        html.Div("開始時間", style={
                                 'padding': '0vw 1vw', 'font-size': '1.1vw'}),
                        dcc.Dropdown(
                            options=[{'label': dt.strftime(
                                '%Y-%m-%d %H:%M:%S'), 'value': dt} for dt in chdf.index],
                            value=datetime.strftime(
                                chdf.index[0], time_format),
                            id='start',
                            style={'width': '20vw'}
                        ),
                        html.Div("結束時間", style={
                                 'padding': '0vw 1vw', 'font-size': '1.1vw'}),

                        dcc.Dropdown(
                            options=[{'label': dt.strftime(
                                '%Y-%m-%d %H:%M:%S'), 'value': dt} for dt in chdf.index],
                            value=datetime.strftime(
                                chdf.index[-1], time_format),
                            id='end',
                            style={'width': '20vw'}
                        ),
                        html.Button('Submit', id='health-submit-val',
                                    n_clicks=0, style={"backgroundColor": '#6E6E6E'}),
                    ], style={'display': 'flex', 'flex-wrap': 'wrap'},
                ),
                # 趨勢圖
                html.Div(
                    children=[
                        dcc.Graph(
                            id='line-chart',
                            figure={
                                'layout':
                                {
                                    "paper_bgcolor": theme['primary'],
                                    "plot_bgcolor":theme['primary']
                                }
                            }
                        ),
                        dcc.Loading(html.Div(id="loading")),
                        dcc.ConfirmDialog(
                            id='no-data-dialog',
                            message='時間形式有誤/時間區段內無資料'
                        ),
                    ], style={'margin': '1vw', 'background': theme['primary']}
                )
            ]
        )]
    elif tab == 'safe-page':
        # 另一頁面呈現
        return [html.Div(
            children=[
                html.Div("區段選擇", style={"font-size": '1.5vw'}),
                dcc.Dropdown(
                    id='safescore-dropdown',
                    options=['區段甲', '區段乙'],
                    value='區段甲',
                    style={'backgroundColor': 'white',
                           'color': 'black', 'width': '15vw'}
                ),
                html.Button('Submit', id='safescore-submit-val',
                            n_clicks=0, style={}),

                dcc.Loading(
                    id='safescore-loading',  # loading id 無應用在其他處
                    children=[
                        html.Div([], id='safescore-table',
                                 style={'width': '50%'})  # error table
                    ],
                    type="circle"
                )
            ], style={'margin': '1vw'}
        )]


@app.callback(
    Output("machine-tag-dropdown", "options"),
    Output("machine-tag-dropdown", "value"),
    Input("machine", "value")
)
def update_machine_pitag_(machine):
    if not machine:
        raise PreventUpdate
    elif machine in ['機台1', '機台2', '機台3', '機台4', '機台5', '機台6', '機台C', '機台8']:
        choosen_taglist = ['點位_' + str(i) for i in range(1, 88)]

    return choosen_taglist, choosen_taglist[0]


@app.callback(
    Output('yachu_score', 'value'),
    Output('yachu_err', 'children'),
    Output('roll_score', 'value'),
    Output('roll_err', 'children'),
    Output('inch_score', 'value'),
    Output('inch_err', 'children'),
    Input('machine_sure', 'n_clicks'),
    State('machine', 'value'))
def update_table(n_clicks, selected_machine):
    y_score = 60.625
    r_score = 99.56929336500002
    i_score = 99.69512382500001

    return round(y_score, 2), build_table(a_df), round(r_score, 2), build_table(b_df), round(i_score, 2), build_table(c_df
)

# dash input output 只能 傳 string 型態 而不是 datetime
@app.callback([Output('line-chart', 'figure'),
               Output('loading', 'children'),
               Output('no-data-dialog', 'displayed')],
              [Input('health-submit-val', 'n_clicks')],
              [State('start', 'value'),
               State('end', 'value'),
               State('machine-tag-dropdown', 'value')],
              prevent_initial_call=True)
def update_linechart(n_clicks, start, end, ch_tag):
    global chdf
    if start is None or end is None:
        return dash.no_update, dash.no_update, False
    # 檢查 start 和 end 是否在索引中存在
    if start not in chdf.index or end not in chdf.index:
        return dash.no_update, dash.no_update, False
    # 使用 pd.to_datetime 轉換日期時間格式
    start = pd.to_datetime(start)
    end = pd.to_datetime(end)

    # 時間處理
    if start != None and end != None:
        timed_df = chdf.loc[start:end, :]
        fig = make_subplots()
        fig.add_trace(
            go.Scatter(
                x=timed_df.index,
                y=timed_df[ch_tag],
                name=ch_tag
            ),
            secondary_y=False
        )
        return fig, "Figure update success", False

    else:
        return dash.no_update, dash.no_update, False


@app.callback([Output('safescore-table', 'children')],
              [Input('safescore-submit-val', 'n_clicks')],
              [State('safescore-dropdown', 'value')])
def update_safescore(n_clicks, part):

    global safetag_df # 假資料

    # part 是甲  / 乙
    part_df = safetag_df[safetag_df['區段'] == part]
    return [dash_table.DataTable(
        part_df.to_dict('records'),
        [
            {'name': '時間', 'id': '時間'},
            {'name': '區段', 'id': '區段'},
            {'name': '點位', 'id': '點位'},
            {'name': '偵測數值', 'id': '偵測數值'},
            {'name': '預警值', 'id': '預警值'},
            {'name': '允差值', 'id': '允差值'},
            {'name': '狀態', 'id': '狀態'}
        ],
        fill_width=True,
        style_data_conditional=[
            {
                'if': {
                    'filter_query': '{狀態} != "安全"',
                    'column_id': '狀態'
                },
                'backgroundColor': '#FF4136',
                'color': 'white',
            },
        ]
    )]


# ===============================
if __name__ == '__main__':
    app.run_server(debug=True)
