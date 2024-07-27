# HEADER
TITLE = "Anomalies Tracking"
WELCOME_MESSAGE = '''Welcome to the analytical app'''
INTRODUCTION = '''This is a v1.0.0 project to analyse the anomalies in the stocks market, choosing a group of stocks and making some data calculus to evaluate the relative risk and the anomalies. The data is taken of yahoo finance in each page recharge and the calculus is made with the controls below.'''
# BODY
GRAPH_12_TEXT = ["""The market volume chart displays the quantity of shares traded over a period of time. High volume can indicate increased interest and activity in the market, while low volume may suggest reduced participation. Elevated volume can influence volatility and, consequently, the assessment of anomalies.""",

"""The adjusted price chart shows a stock's closing prices after accounting for corporate events such as dividends, stock splits, or mergers. These adjusted prices reflect the true investment value, considering changes in the company's capital structure. Adjusted prices are essential for calculating returns and volatility.""",

"""To analyze anomalies, the z-score is employed. It measures the distance between a stock's current performance and its historical mean, normalized by volatility. If adjusted prices or market volume experience significant changes, the z-score can be affected."""]

HEATMAP_TEXT = """The correlation chart visually displays which anomalies among the selected stocks are related. Those correlations far from zero indicate a strong relationship between market events during the chosen period. However, actions with few anomalies within the specified time range won't be shown."""

PIECHART_TEXT = """The pie chart displays the contribution to group risk from each individual stock. When hovering over each segment of the chart, the investment risk for that specific stock (measured by the Z-score) is shown. Keep in mind that the calculations will vary based on the selected stocks, the method's sensitivity, and the chosen time period."""

BARCHART_TEXT = """The bar chart provides a comparison of volatility values within the group of stocks. These values are measured by the standard deviation of each stock. Naturally, those with higher standard deviations will be more volatile. Stocks that exhibit missing data or anomalies will display a value of zero."""