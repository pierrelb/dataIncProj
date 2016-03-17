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

@app.route('/index',methods=['GET','POST'])
def index():
    if request.method == 'GET':
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
    else:
        return redirect('/league_effect') 

@app.route('/league_effect')
def leagues():
    df = pd.read_csv('wc_squads.csv')
    grouped = df.groupby('WC_Year')
    club_country = df.Club_Country.unique()
    club_country.sort()
    df2 = pd.DataFrame({"club_country":club_country})
    df2 = df2.set_index("club_country")
    
    for year in df.WC_Year.unique():
        country_to_club = grouped.Club_Country.value_counts()[year] / grouped.Country.value_counts()[year]
        df2 = df2.join(country_to_club.to_frame(year))
        
    df2 = df2.fillna(0) # If NaN, country league not represented at the world cup
    df2 = df2.T
    
    TOOLS="pan,wheel_zoom,box_zoom,reset,save"
    
    plot = figure(tools=TOOLS,
                  title='Countries with Professional Leagues with Most World Cup Players',
                  x_axis_label='World Cup Year'
                  )
    
    # take the top 11 countries and plot
    for num, country in enumerate(df2.sum().sort_values(ascending=False).head(11).index):
        plot.scatter(df2.index, df2[country],legend=country,color=Spectral19[num])
    
    script, div = components(plot)
    
    return render_template('league.html', script=script, div=div)

@app.route('/player_props')
def players():
    df = pd.read_csv('wc_squads_clean.csv')
    df.DoB = pd.to_datetime(df.DoB)
    df['birth_month'] = df.DoB.map(lambda x: month_map.get(x.month))
    grouped = df.groupby('WC_Year')


if __name__ == '__main__':
  app.run(port=33507)