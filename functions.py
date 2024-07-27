from scipy.stats import zscore
import yfinance as yf
import pandas as pd
# Functions 
def detect_anomalies(df, column,sigma):
    df_copy = df.copy()
    df_copy['Z_score'] = zscore(df_copy[column])

    anomalies = df_copy[abs(df_copy['Z_score'])>sigma]
    return anomalies

def update_data(end_date,start_date,Z, selected_shares):
    data = None
    data = yf.download(tickers=selected_shares, group_by='Ticker', end=end_date, start=start_date, progress=False)
    data = data.stack(level=0).rename_axis(['Date', 'Ticker']).reset_index(level=1)
    stock_data = data.reset_index()
    stock_data['Date'] = pd.to_datetime(stock_data['Date'])
    stock_data.set_index('Date', inplace=True)

    adj_close_df = pd.DataFrame()
    volume_df = pd.DataFrame()
    anomalies_adj_close = pd.DataFrame()
    anomalies_volume = pd.DataFrame()
    Z_adj_close = pd.DataFrame()
    Z_volume = pd.DataFrame()
    ticks = stock_data['Ticker'].unique()
    for tick in ticks:
        subset = stock_data[stock_data['Ticker']==tick]

        adj_close_anomalies = detect_anomalies(subset,'Adj Close',Z)
        volume_anomalies = detect_anomalies(subset, 'Volume',Z)

        anomalies_adj_close = pd.concat([anomalies_adj_close,adj_close_anomalies['Adj Close']], axis=1)
        anomalies_volume = pd.concat([anomalies_volume,volume_anomalies['Volume']],axis=1)

        Z_adj_close = pd.concat([Z_adj_close, adj_close_anomalies[['Ticker','Z_score']]])
        Z_volume = pd.concat([Z_volume, volume_anomalies[['Ticker', 'Z_score']]])

        adj_close_df = pd.concat([adj_close_df,subset['Adj Close']],axis=1)
        volume_df = pd.concat([volume_df,subset['Volume']], axis=1)

    adj_close_df.columns = ticks
    volume_df.columns = ticks
    anomalies_volume.columns=ticks
    anomalies_adj_close.columns=ticks

    return adj_close_df, volume_df, anomalies_adj_close, anomalies_volume, Z_adj_close, Z_volume

def update_correlation_matrix(anomalies_adj_close, anomalies_volume):
    all_anomalies_adj_close = anomalies_adj_close.melt(ignore_index=False, var_name='Ticker',value_name='Adj Close Anomaly').dropna()
    all_anomalies_volume = anomalies_volume.melt(ignore_index=False, var_name='Ticker', value_name='Volume Anomaly').dropna()

    all_anomalies_adj_close['Adj Close Anomaly'] = 1
    all_anomalies_volume['Volume Anomaly'] = 1

    adj_close_pivot = all_anomalies_adj_close.pivot_table(index=all_anomalies_adj_close.index, columns='Ticker', fill_value=0, aggfunc='sum')
    volume_pivot = all_anomalies_volume.pivot_table(index=all_anomalies_volume.index, columns='Ticker', fill_value=0, aggfunc='sum')

    adj_close_pivot.columns = adj_close_pivot.columns.get_level_values(1)
    volume_pivot.columns = volume_pivot.columns.get_level_values(1)

    combined_anomalies = pd.concat([adj_close_pivot, volume_pivot],axis=1, keys=['Adj Close Anomaly', 'Volume Anomaly'])

    correlation_matrix = combined_anomalies.corr()
    correlation_matrix.index.names = ['Anomaly Type', 'Ticker']

    correlation_matrix.columns = correlation_matrix.columns.to_flat_index()
    correlation_matrix.columns = [(' '.join(col) if type(col) is tuple else col) for col in correlation_matrix.columns]
    correlation_matrix = correlation_matrix.reset_index()

    correlation_matrix.index = correlation_matrix['Anomaly Type'].str.cat(correlation_matrix['Ticker'], sep=' ')
    correlation_matrix = correlation_matrix.drop(columns=['Anomaly Type','Ticker'])
    
    return correlation_matrix

def update_risk_rating(anomalies_adj_close, anomalies_volume):
    adj_close_risk = anomalies_adj_close.groupby('Ticker')['Z_score'].apply(lambda x : abs(x).mean())
    
    volume_risk = anomalies_volume.groupby('Ticker')['Z_score'].apply(lambda x: abs(x).mean())

    total_risk = adj_close_risk + volume_risk

    risk_rating = (total_risk - total_risk.min())/ (total_risk.max() - total_risk.min())
    
    return total_risk, risk_rating