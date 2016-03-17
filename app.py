import pandas as pd
import locale

from flask import Flask, render_template, request, redirect

from bokeh.plotting import figure
from bokeh.charts import Scatter
from bokeh.embed import components
from bokeh.palettes import Spectral11

import pandas as pd

app = Flask(__name__)

@app.route('/')
def main():
    return redirect('/index')

@app.route('/index')
def index():
    df2 = pd.read_csv("record_transfers.csv")
    locale.setlocale(locale.LC_NUMERIC, '')
    df2['fee_pounds'] = df2.fee_pounds.apply(locale.atof)
    
    TOOLS="pan,box_zoom,reset,save"
    plot = figure(tools=TOOLS,
                      title='World Record Soccer Transfer Fee',
                      x_axis_label='Year',
                      y_axis_label=u"Fee (\u00A3)"
                      )
    plot.line(df2['yr'], df2['fee_pounds'],color=Spectral11[0],line_width=4)
    
    script, div = components(plot)
    
    return render_template('index.html', script=script, div=div)


if __name__ == '__main__':
  app.run(port=33507)