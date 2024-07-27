from dash import Dash, html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
import datetime
from constants import TITLE, WELCOME_MESSAGE, INTRODUCTION, GRAPH_12_TEXT, HEATMAP_TEXT, PIECHART_TEXT, BARCHART_TEXT

from functions import *

# Global conf of graphs

px.defaults.height = 400

custom_template = go.layout.Template(
    layout=go.Layout(
        font=dict(family='Roboto, sans-serif', size=12, color='white'),  # Fuente Roboto, tamaño 12, color blanco
        margin=dict(l=20,r=20,t=20,b=20)
    )
)

# Registrar la plantilla personalizada
pio.templates['custom_dark_template'] = custom_template

# Establecer la plantilla personalizada como la plantilla por defecto
pio.templates.default = 'plotly_dark+custom_dark_template'



# Initial Variables
selected_shares=['GOOGL', 'MSFT', 'NVDA', 'TSLA', 'TSM']
shares_list=['GOOGL', 'MSFT', 'NVDA', 'TSLA', 'TSM']
end_date= datetime.date.today()
start_date=(end_date - datetime.timedelta(days=365))


# Initial data and plots
adj_close_df, volume_df, anomalies_adj_close, anomalies_volume, Z_adj_close, Z_volume = update_data(end_date,start_date,2, selected_shares)


#Callbacks
@callback(
    Output('shares-dropdown', 'options'),
    Output('shares-dropdown','value'),
    Input('add-share-button', 'n_clicks'),
    Input('shares-dropdown','value'),
    State('input-share', 'value')
)
def add_share_to_list(n_clicks, selected_value, value):
    if value and (value not in shares_list or value not in selected_value):# or (value not in selected_value):
        shares_list.append(value)
        selected_value.append(value)
    return shares_list,selected_value
##################


@callback(
    Output('adj-close-graph','figure'),
    Output('volume-graph','figure'),
    Output('correlation-heatmap-data','data'), #added a store dependency
    Output('total-risk-plot','figure'),
    Output('rating-risk-plot', 'figure'),
    Input('input-sensibility','value'),
    Input('date-picker-range','start_date'),
    Input('date-picker-range','end_date'),
    [Input('shares-dropdown', 'value')]
)
def update_adj_close_plot(value, start_date, end_date,selected_shares):
    adj_close_df, volume_df, anomalies_adj_close, anomalies_volume, Z_adj_close, Z_volume = update_data(end_date, start_date,value,selected_shares)
    
    adj_close_fig = px.line(adj_close_df)   # Fig Adjusted Close prices
    
    for tick in adj_close_df.columns:
        adj_close_fig.add_traces(
            go.Scatter(x=anomalies_adj_close.index, y = anomalies_adj_close[tick],
                       mode='markers', name=f'Anomaly{tick}')
        )
    adj_close_fig.update_layout(showlegend=False, height=300)
    adj_close_fig.update_yaxes(title_text='Adjusted Close Prices USD')
    adj_close_fig.update_xaxes(title_text='')

    volume_fig = px.line(volume_df)         # Fig Volume
    

    for tick in volume_df.columns:
        volume_fig.add_traces(
            go.Scatter(x=anomalies_volume.index, y = anomalies_volume[tick], 
                   mode='markers', name=f'Anomaly{tick}')
        )
    volume_fig.update_layout(showlegend=False, height=300)
    volume_fig.update_xaxes(title_text='')
    volume_fig.update_yaxes(title_text='Market Volume')

    # Anomalies functions
    total_risk, risk_rating = update_risk_rating(Z_adj_close, Z_volume)


    correlation = update_correlation_matrix(anomalies_adj_close, anomalies_volume)


    # Total risk graph
    risk_rating_graph = px.pie(risk_rating.fillna(0), values='Z_score', names=risk_rating.index, color_discrete_sequence=px.colors.sequential.RdBu)
    risk_rating_graph.update_layout(height=300)
    
    # Risk Rating Graph
    total_risk_graph = px.bar(total_risk.fillna(0)/2, text_auto='.2s')
    total_risk_graph.add_shape( # add a horizontal "target" line
    type="line", line_color="salmon", line_width=3, opacity=1, line_dash="dot",
    x0=0, x1=1, xref="paper", y0=value, y1=value, yref="y"
)
    total_risk_graph.update_layout(showlegend=False, height=300)

    return adj_close_fig, volume_fig, correlation.to_json(date_format='iso',orient='columns'), risk_rating_graph, total_risk_graph


@callback(
    Output('correlation-heatmap', 'figure'),
    Input('correlation-heatmap-data','data'),
    Input('dropdown-correlation','value')
)
def update_heatmap(df, option):
    x_v = ('Volume' if option[:6] == 'Volume' else 'Adj Close')
    y_v = ('Adj Close' if option[7:] =='AdjClo' else 'Volume')
    df = pd.read_json(df, orient='columns')

    x_axe = [row for row in df.index if x_v in row]
    y_axe = [col for col in df.columns if y_v in col]

    heatmap1 = px.imshow(df.fillna(0).loc[x_axe, y_axe],
                        x=[s.replace(f'{x_v} Anomaly','').replace(f'{y_v} Anomaly','') for s in y_axe],
                        y=[s.replace(f'{y_v} Anomaly','').replace(f'{x_v} Anomaly','') for s in x_axe],
                        zmax=1, zmin=-1, labels=dict(y=f'{x_v} Anomalies', x = f'{y_v} Anomalies', color='Correlation'))   # Correlation Heatmap Graph
    heatmap1.update_layout(height=300)

    return heatmap1


# Dashboard front development-------------------------------------------------------------------------------

app = Dash(__name__, suppress_callback_exceptions=True)

app.layout = dbc.Container(
    [
        html.Div([
            html.Div([
                html.H1([TITLE]),
            html.P([
                WELCOME_MESSAGE,
                html.Br(),
                INTRODUCTION
            ])
            ], className='left-texts'),
            html.Div([
                html.Div([
                    dcc.DatePickerRange(
                    id='date-picker-range', className='date-picker-range',                                             #id='date-picker-range'
                    max_date_allowed=datetime.date.today(),
                    initial_visible_month=datetime.date.today(),
                    start_date=(datetime.date.today() - datetime.timedelta(days=365)),  #Output start_date
                    end_date=datetime.date.today()                                      #Output end_date
                ,)
                ], className='picker-period-time'),
                html.Div([
                    dcc.Input(
                    id='input-share',
                    type='text',
                    placeholder='Add a share'
                ),
                html.Button('Submit', id='add-share-button')
                ], className='stocks-input'),
                html.Div([
                    dcc.Dropdown(
                    id='shares-dropdown',           #id='shares-dropdown'
                    options = shares_list,      #Outpu Selected_shares options:selected_shares
                    multi=True,
                    value=selected_shares,
                    placeholder='Select Shares'
                )
                ], className='stocks-list'),
                html.Div([
                    dcc.Slider(1,2.5,0.25,value=2,id='input-sensibility')
                ], className='sigma-range')
            ], className='controls')
        ], className='left-side'),
        html.Div([
            html.Div([
                dcc.Graph(id='adj-close-graph')
            ], className='right Graph-price'),
            html.Div([
                dcc.Graph(id='volume-graph')
            ], className='right Graph-volume'),
            html.Div([
                html.P(GRAPH_12_TEXT[0]),
                html.P(GRAPH_12_TEXT[1]),
                html.P(GRAPH_12_TEXT[2])
            ], className='right graph-texts'),
            html.Div([
                dcc.Store(id='correlation-heatmap-data'),
                dcc.Dropdown(
                id='dropdown-correlation',
                options=['Volume-Volume', 'AdjClo-AdjClo', 'AdjClo-Volume'],
                value='Volume-Volume'
            ),
            dcc.Graph(id='correlation-heatmap')
            ], className='right heatmap-graph'),
            html.Div([
                html.P(HEATMAP_TEXT)
            ], className='right heatmap-explanation',
            ),
            html.Div([
                html.P(PIECHART_TEXT)
            ], className='right pie-explanation'),
            html.Div([
                dcc.Graph(id='total-risk-plot'),
            ],className='right pie-graph'),
            html.Div([
                dcc.Graph(id='rating-risk-plot')
            ], className='right bar-graph'),
            html.Div([
                html.P(BARCHART_TEXT)
            ], className='right bar-explanation')

        ], className='right-side')
    ],
    fluid=True,
    className='dashboard-container'
)

server = app.server

if __name__ == '__main__':
    app.run(debug=True, jupyter_mode='external')


