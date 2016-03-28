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
        df_tranfer = pd.read_csv("record_transfers.csv")
        locale.setlocale(locale.LC_NUMERIC, '')
        df_tranfer['fee_pounds'] = df_tranfer.fee_pounds.apply(locale.atof)
        
        plot = figure(tools=TOOLS,
                          title='World Record Soccer Transfer Fee',
                          x_axis_label='Year',
                          y_axis_label=u"Fee (\u00A3)",
                          toolbar_location="below"
                          )
        
        plot.line(df_tranfer['yr'], df_tranfer['fee_pounds'],color=RdBu11[0],line_width=4)
        
        script, div = components(plot)
        return render_template('index.html', js_resources=js_resources, css_resources=css_resources, script=script, div=div)
    else:
        if request.form['submit'] == "Professional League Data":
            return redirect('/league_data') 
        elif request.form['submit'] == "Player Data":
            return redirect('/player_data') 

@app.route('/league_data',methods=['GET','POST'])
def leagues():
    if request.method == 'GET':
        
        df_rank = pd.read_csv('wc_rankings.csv')
        # Germany considers West Germany as a part of their footballing history (not East Germany)
        df_rank = df_rank.replace(to_replace="West Germany", value="Germany")

        team_avg_ranking = df_rank.groupby('team').ranking.mean().to_frame()
        team_num_wc = df_rank.team.value_counts().head(50).to_frame()
        
        df_team_rank = team_avg_ranking.join(team_num_wc)
        df_team_rank = df_team_rank.dropna()
        
        plot1 = figure(tools=TOOLS,
                      title='Soccer history affects team performance',
                      x_axis_label='Number of World Cups',
                      y_axis_label='Average World Cup Ranking',
                      toolbar_location="below"
                      )
        
        plot1.scatter(df_team_rank.team, df_team_rank.ranking, color='blue', size=8, alpha=0.5)
        
        
        df_squads = pd.read_csv('wc_squads.csv')
        grouped = df_squads.groupby('WC_Year')
        club_country = df_squads.Club_Country.unique()
        club_country.sort()
        df_clb_ctry = pd.DataFrame({"club_country":club_country})
        dfdf_clb_ctry2 = df_clb_ctry.set_index("club_country")
        
        for year in df.WC_Year.unique():
            country_to_club = grouped.Club_Country.value_counts()[year] / grouped.Country.value_counts()[year]
            df_clb_ctry = df_clb_ctry.join(country_to_club.to_frame(year))
            
        df_clb_ctry = df_clb_ctry.fillna(0) # If NaN, country league not represented at the world cup
        df_clb_ctry = df_clb_ctry.T
        
        plot2 = figure(tools=TOOLS,
                      title='Soccer Leagues with Most WC Players',
                      x_axis_label='World Cup Year',
                      toolbar_location="below"
                      )
        
        # take the top 11 countries and plot
        for num, country in enumerate(ddf_clb_ctryf2.sum().sort_values(ascending=False).head(11).index):
            plot2.scatter(df_clb_ctry.index, df_clb_ctry[country],legend=country,color=RdBu11[num],size=8, alpha=0.5)
        
        plot2.legend.location = "top_left"
        
        df_league_data = pd.read_csv("top_five_leagues.csv")
        
        df_expats = df_league_data[df_league_data.nation!=df_league_data.nationality]
        
        for season in df_expats.season.unique():
            nationality_expats = df_expats.groupby('season').nationality.value_counts()[season].head(10)
            nation_expats = df_expats.groupby('season').nation.value_counts()[season]
        
        plot3 = Bar(nationality_expats, toolbar_location="below")
        plot3.x_range = FactorRange(factors=nationality_expats.index.tolist())
        
        plot_dict = {"history":plot1, "nations":plot2, "nationality":plot3}
        
        script, div = components(plot_dict)
        
        return render_template('league.html', js_resources=js_resources, css_resources=css_resources, script=script, div=div)
    else:
        if request.form['submit'] == "Player Data":
            return redirect('/player_data') 
        else:
            return redirect('/index')

@app.route('/player_data',methods=['GET','POST'])
def players():
    if request.method == 'GET':
        month_map = {k: v for k,v in enumerate(calendar.month_abbr)}
        
        df_squads = pd.read_csv('wc_squads.csv')
        df_squads.DoB = pd.to_datetime(df.DoB)
        df_squads['birth_month'] = df_squads.DoB.map(lambda x: x.month)
        df_mth = df_squads.birth_month.value_counts().sort_index()
        df_mth.index = df_mth.index.map(lambda x: month_map[x])
        
        grouped = df_squads.groupby('WC_Year')
        
        avg_age = df_squads.groupby('WC_Year').Age.mean().to_frame()
        
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
        
    else:
        if request.form['submit'] == "Professional League Data":
            return redirect('/league_data') 
        else:
            return redirect('/index') 
if __name__ == '__main__':
  app.run(port=33507)
  