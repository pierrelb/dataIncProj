import locale
import calendar
import pandas as pd

from flask import Flask, render_template, request, redirect

from bokeh.plotting import figure
from bokeh.charts import Bar
from bokeh.embed import components
from bokeh.models import FactorRange
from bokeh.resources import INLINE
from bokeh.models.widgets import Select
from bokeh.palettes import RdBu11, YlGn9

app = Flask(__name__)

js_resources = INLINE.render_js()
css_resources = INLINE.render_css()

TOOLS="pan,wheel_zoom,box_zoom,reset,save"

@app.route('/')
def main():
    return redirect('/index')

@app.route('/index',methods=['GET','POST'])
def index():
    if request.method == 'GET':
        df2 = pd.read_csv("record_transfers.csv")
        locale.setlocale(locale.LC_NUMERIC, '')
        df2['fee_pounds'] = df2.fee_pounds.apply(locale.atof)
        
        plot = figure(tools=TOOLS,
                          title='World Record Soccer Transfer Fee',
                          x_axis_label='Year',
                          y_axis_label=u"Fee (\u00A3)",
                          toolbar_location="below"
                          )
        
        plot.line(df2['yr'], df2['fee_pounds'],color=RdBu11[0],line_width=4)
        
        script, div = components(plot)
        return render_template('index.html', js_resources=js_resources, css_resources=css_resources, script=script, div=div)
    else:
        return redirect('/league_effect') 

@app.route('/league_effect',methods=['GET','POST'])
def leagues():
    if request.method == 'GET':
        
        df_rank = pd.read_csv('wc_rankings.csv')
        # Germany considers West Germany as a part of their footballing history (not East Germany)
        df_rank = df_rank.replace(to_replace="West Germany", value="Germany")

        team_avg_ranking = df_rank.groupby('team').ranking.mean().to_frame()
        team_num_wc = df_rank.team.value_counts().head(40).to_frame()
        
        df_team_rank = team_avg_ranking.join(team_num_wc)
        df_team_rank = df_team_rank.dropna()
        
        plot1 = figure(tools=TOOLS,
                      title='Soccer history affects team performance',
                      x_axis_label='Number of World Cups',
                      y_axis_label='Average World Cup Ranking',
                      toolbar_location="below"
                      )
        
        plot1.scatter(df_team_rank.team, df_team_rank.ranking, color='blue', size=8, alpha=0.5)
        
        
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
        
        plot2 = figure(tools=TOOLS,
                      title='Countries with Most WC Players playing professionally',
                      x_axis_label='World Cup Year',
                      toolbar_location="below"
                      )
        
        # take the top 11 countries and plot
        for num, country in enumerate(df2.sum().sort_values(ascending=False).head(11).index):
            plot2.scatter(df2.index, df2[country],legend=country,color=RdBu11[num],size=8, alpha=0.5)
        
        plot2.legend.location = "top_left"
        
        df3 = pd.read_csv("top_five_leagues.csv")
        
        df_expats = df3[df3.nation!=df3.nationality]
        
        for season in df_expats.season.unique():
            nationality_expats = df_expats.groupby('season').nationality.value_counts()[season].head(10)
            nation_expats = df_expats.groupby('season').nation.value_counts()[season]
        
        plot3 = Bar(nationality_expats, toolbar_location="below")
        plot3.x_range = FactorRange(factors=nationality_expats.index.tolist())
        
        plot_dict = {"history":plot1, "nations":plot2, "nationality":plot3}
        
        script, div = components(plot_dict)
        
        return render_template('league.html', js_resources=js_resources, css_resources=css_resources, script=script, div=div)
    else:
        return redirect('/player_props') 

@app.route('/player_props')
def players():
    month_map = {k: v for k,v in enumerate(calendar.month_abbr)}
    
    df = pd.read_csv('wc_squads.csv')
    df.DoB = pd.to_datetime(df.DoB)
    df['birth_month'] = df.DoB.map(lambda x: x.month)
    df_mth = df.birth_month.value_counts().sort_index()
    df_mth.index = df_mth.index.map(lambda x: month_map[x])
    
    grouped = df.groupby('WC_Year')
    
    avg_age = df.groupby('WC_Year').Age.mean().to_frame()
    
    plot1 = figure(tools=TOOLS,
                  title='Average Team Age',
                  x_axis_label='World Cup Year',
                  toolbar_location="below"
                  )
    
    plot1.line(avg_age.index, avg_age.Age.values, color='green', line_width=4, alpha=0.5)
    
    # select = Select(title="World Cup Year:", value="all", options=["all"] + map(str, df.WC_Year.unique().tolist()))
    
    plot2 = Bar(df_mth, toolbar_location="below")
    plot2.x_range = FactorRange(factors=df_mth.index.tolist())
    
    plots = {"plot1": plot1, "plot2": plot2}
    
    script, div = components(plots)
    
    
    return render_template('player.html', js_resources=js_resources, css_resources=css_resources, script=script, div=div)
if __name__ == '__main__':
  app.run(port=33507)
  