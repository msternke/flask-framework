from flask import Flask, render_template, request, redirect
from alpha_vantage.timeseries import TimeSeries
import pandas as pd
import datetime as dt
from dateutil.relativedelta import relativedelta

from bokeh.plotting import figure, output_file, save
from bokeh.embed import components
from bokeh.io import show


app = Flask(__name__)
app.vars = {}

#defining constants
ALPHA_VANTAGE_API_KEY = '7TT265BSV4JOW900'

# setting initial values
app.vars['stock'] = 'GOOG'
app.vars['start_date'] = '2015-01-01'
app.vars['end_date'] = dt.date.today().strftime('%Y-%m-%d')
app.vars['open'] = ''
app.vars['high'] = ''
app.vars['low'] = ''
app.vars['close'] = 'checked'

prices = ['open', 'high', 'low', 'close']
price_labels = ['Opening price', 'High price', 'Low price', 'Closing price']
colors = ['navy', 'darkgray', 'goldenrod', 'darkred']


def plot_stock_price():

    stock = app.vars['stock']
    start_date = app.vars['start_date']
    end_date = app.vars['end_date']
    open_box = app.vars['open']
    high_box = app.vars['high']
    low_box = app.vars['low']
    close_box = app.vars['close']
    
    ts = TimeSeries(key=ALPHA_VANTAGE_API_KEY, output_format='pandas')
    
    data, meta_data = ts.get_daily(stock, outputsize='full')
    
    data.columns = prices + ['volume']
    
    data['date'] = data.index
    
    stock_price = data[(data['date'] >= start_date) & (data['date'] <= end_date)]
    
    p = figure(width=600, height=400, x_axis_type='datetime')
    
    for i, price in enumerate(prices):
        if app.vars[price] == 'checked':
            p.line(stock_price['date'], stock_price[price], legend_label=price_labels[i], color=colors[i], line_width=2)
    
    #figure settings
    p.title.text = f'{stock} price from {start_date} to {end_date}'
    p.legend.location = 'top_left'
    p.xaxis.axis_label = 'Date'
    p.yaxis.axis_label = 'Price'
    p.axis.axis_label_text_font_style = 'bold'
    
    return components(p)
    
@app.route('/')
def inital_view():
    script, div = plot_stock_price()
    
    return render_template("index.html", script=script, div=div, stock=app.vars['stock'], start=app.vars['start_date'], end=app.vars['end_date'], open=app.vars['open'], high=app.vars['high'], low=app.vars['low'], close=app.vars['close'])


@app.route('/', methods=['GET', 'POST'])
def index():

    app.vars['stock'] = request.form['stock']
    app.vars['start_date'] = request.form['start']
    app.vars['end_date'] = request.form['end']
    
    for price in prices:
        box_check = request.form.get(price)
        if box_check == 'on':
            app.vars[price] = 'checked'
        else:
            app.vars[price] = ''

    script, div = plot_stock_price()

    return render_template("index.html", script=script, div=div, stock=app.vars['stock'], start=app.vars['start_date'], end=app.vars['end_date'], open=app.vars['open'], high=app.vars['high'], low=app.vars['low'], close=app.vars['close'])

if __name__ == '__main__':
  app.run(port=33507, debug=True)
