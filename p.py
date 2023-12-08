import pandas as pd
import numpy as np
import dash
from dash import Dash, html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objs as go
import dash_daq as daq
from plotly.subplots import make_subplots
import model
from datetime import date
import datetime
import time
import json

gas_data_link = 'https://raw.githubusercontent.com/alonsomoncayo/CSDA2010-Project-1/main/Ontario_Natural_Gas_Consumption_Jan2016-2023.csv'
df_gas = pd.read_csv(gas_data_link,parse_dates=['Supply and disposition'],dayfirst=True)
df_gas = df_gas.rename(columns={'Supply and disposition':'Date','Residential consumption':'Residential'})
df_gas.set_index('Date',inplace=True)
df_gas=pd.DataFrame(df_gas['Residential'])

temp_data_link = 'https://raw.githubusercontent.com/alonsomoncayo/CSDA2010-Project-1/main/2016-2023_Daily_Toronto_Temperature.csv'
df_temp = pd.read_csv(temp_data_link,parse_dates=['Date/Time'],dayfirst=True)
df_temp = df_temp.rename(columns={'Date/Time':'Date','Mean Temp (°C': 'Mean Temp'})
df_temp.set_index('Date',inplace=True)
df_temp=df_temp['Mean Temp']

df_mean_temp = pd.DataFrame(df_temp.groupby(pd.Grouper(freq="MS")).mean())
join_df = df_gas.join(df_mean_temp)
join_df.reset_index(inplace=True)

fit,forecast,temp_assum = model.fit_model_forecast(join_df,df_mean_temp)


app = Dash(__name__,external_stylesheets=[dbc.themes.ZEPHYR])

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

SIDEBAR_CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H4("Gas consumption time series analysis"),
        html.Hr(),
        html.B(
            "1) Grapg time series", className="lead"
        ),
        html.Br(),
        dbc.Button("Click to graph", color="primary", className="me-1",n_clicks=0,id='button'),
        html.Hr(),
        daq.BooleanSwitch(
        id='switch',
        on=False,
        label="Disabled",
        labelPosition="top",
        disabled=True,
        color='#12239E'
        ),
        html.Hr(),        
        html.H6('Forecast: select a date'),
        dcc.DatePickerSingle(
        id='date_picker',
        date=None,
        display_format='MMMM Y',
        clearable=True,
        min_date_allowed=date(2023, 9, 1),
        max_date_allowed=date(2024, 12, 1),
        disabled=True,
        style={'font-size': '5px'}
        ),
        html.H6('hola',id='forecast')
    ],
    style=SIDEBAR_STYLE,
)
trace1 = go.Scatter(x=None,
                        y=None)
trace2 = go.Scatter(x=None,
                        y=None)
data = [trace1, trace2]
layout = go.Layout(width=1200,
                    height=650)
gra = go.Figure(data=data, layout=layout)

line_graph=dcc.Graph(id="explor",
          figure=gra,
          config={"doubleClick": "reset",
                "displayModeBar": False,
                "watermark": False,
                },)



content = html.Div(children=[line_graph],id="page-content", style=SIDEBAR_CONTENT_STYLE)
app.layout = html.Div([sidebar,content])

@app.callback(
    Output('explor','figure'),
    Output("button", "disabled"),
    Output('switch','disabled'),
    Output('switch','label'),
    Output('date_picker','disabled'),
    Input("button", "n_clicks"),
    Input('switch','on')
)
def graph(n,on):
    if n == 1:
        if on:
            trace1 = go.Scatter(x=join_df['Date'],
                            y=join_df['Residential'],
                            name='Gas consumption',
                            mode='lines',
                            yaxis='y1')
            trace2 = go.Scatter(x=join_df['Date'],
                                y=join_df['Mean Temp'],
                                name='Temperature',
                                mode='lines',
                                yaxis='y2')
            trace3 = go.Scatter(x=forecast['index'],
                            y=forecast['predicted_mean'],
                            name='Gas consumption forecast',
                            mode='lines',
                            yaxis='y1')
            trace4 = go.Scatter(x=temp_assum['index'],
                                y=temp_assum['Mean Temp'],
                                name='Temperature assumption',
                                mode='lines',
                                yaxis='y2')
            data = [trace1, trace2,trace3,trace4]
            layout = go.Layout(title='Mean Temperature and Residential Gas Consumption Over Time and Forecast',
                            yaxis=dict(title='Cubic Meters (Thousands)'),
                            yaxis2=dict(title='Temperature (°C)',
                                        overlaying='y',
                                        side='right'),
                            width=1200,
                            height=650)
            return (go.Figure(data=data, layout=layout),True,False,'Add temperature to the gragh',False)
        else:
            trace1 = go.Scatter(x=join_df['Date'],
                            y=join_df['Residential'],
                            name='Gas consumption',
                            mode='lines')
            trace3 = go.Scatter(x=forecast['index'],
                            y=forecast['predicted_mean'],
                            name='Gas consumption forecast',
                            mode='lines',
                            yaxis='y1')
            data = [trace1,trace3]
            layout = go.Layout(title='Residential Gas Consumption Over Time and Forecast',
                            yaxis=dict(title='Cubic Meters'),
                            width=1200,
                            height=650)
            return (go.Figure(data=data, layout=layout),True,False,'Add temperature to the gragh',False)
    else:
        raise dash.exceptions.PreventUpdate
    
@app.callback(
    Output('forecast','children'),
    Input('date_picker','date'))
def forecast_val(date_value):
    
    
    if date_value is not None:
        # date_object = date_value.fromisoformat(date_value)
        # date_string = date_value.strftime('%B %Y')
        date_time_value = datetime.datetime.strptime(date_value,"%Y-%m-%d")
        month_year = date_time_value.strftime("%B %Y")
        change = date_value[:-3]+'01'
        month_year_data = datetime.datetime.strptime(date_value,"%Y-%m-%d")
        return f'The forcasted gas consumption for {month_year} is: {forecast[forecast["index"]==month_year_data]}'
        
    

if __name__ == '__main__':
    app.run(debug=False, port=8000)