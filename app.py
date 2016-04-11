import locale
import calendar
import random
import pandas as pd
import numpy as np

from flask import Flask, render_template, request, redirect

from bokeh.plotting import figure
from bokeh.charts import Bar
from bokeh.embed import components
from bokeh.models import ColumnDataSource, FactorRange, HBox, VBoxForm
from bokeh.resources import INLINE
from bokeh.models.widgets import Select, Slider
from bokeh.palettes import RdBu11, YlGn9
from bokeh.io import curdoc, vform

app = Flask(__name__)

df_rank = pd.read_csv('wc_rankings.csv')
# Germany considers West Germany as a part of their footballing history (not East Germany)
df_rank = df_rank.replace(to_replace="West Germany", value="Germany")

locale.setlocale(locale.LC_NUMERIC, '')
df_tranfer = pd.read_csv("record_transfers.csv")
df_tranfer['fee_pounds'] = df_tranfer.fee_pounds.apply(locale.atof)

df_squads = pd.read_csv('wc_squads.csv')
df_squads = df_squads.replace(to_replace="Korea Republic", value="South Korea")
df_squads = df_squads.replace(to_replace="West Germany", value="Germany")
df_squads = df_squads.replace(to_replace="Dutch East Indies (Indonesia)", value="Dutch East Indies")
df_squads.dob = pd.to_datetime(df_squads.dob)
df_squads['birth_month'] = df_squads.dob.map(lambda x: x.month)

df_league_data = pd.read_csv("top_five_leagues.csv")

df_prob_win_fifa_rank = pd.read_csv('prob_win.csv')
df_prob_draw_fifa_rank = pd.read_csv('prob_draw.csv')

# Clear poor probs (determined on sparse data)
rem_idx = []
rem_idx += df_prob_win_fifa_rank[df_prob_win_fifa_rank.rank_diff < -150][df_prob_win_fifa_rank[df_prob_win_fifa_rank.rank_diff < -150].prob > 0.1].index.tolist()
rem_idx += df_prob_win_fifa_rank[df_prob_win_fifa_rank.rank_diff > 150][df_prob_win_fifa_rank[df_prob_win_fifa_rank.rank_diff > 150].prob < 0.9].index.tolist()

df_prob_win_fifa_rank = df_prob_win_fifa_rank.drop(df_prob_win_fifa_rank.index[rem_idx])

df_fifa_latest_rank = pd.read_csv('latest-fifa-world-ranking.csv')

js_resources = INLINE.render_js()

TOOLS=""

@app.route('/')
def main():

    return redirect('/index')

@app.route('/index')
def index():
    plot_pVic = figure(tools=TOOLS,
                  x_axis_label='How much higher is your team ranked',
                  y_axis_label='Probability of Winning',
                  toolbar_location=None
                  )
                  
    plot_pVic.scatter(df_prob_win_fifa_rank.rank_diff, df_prob_win_fifa_rank.prob, color='blue', size=8, alpha=0.5)
    
    plot_pDrw = figure(tools=TOOLS,
                  x_axis_label='Difference in team rankings',
                  y_axis_label='Probability of a Draw',
                  toolbar_location=None
                  )
    
    plot_pDrw.scatter(df_prob_draw_fifa_rank.rank_diff,df_prob_draw_fifa_rank.prob, color='red', size=8, alpha=0.5) 
    
    plot_dict = {"W_Prob":plot_pVic, "D_Prob":plot_pDrw}
    
    script, div = components(plot_dict)
    
    return render_template('index.html', js_resources=js_resources, script=script, div=div)

@app.route('/match_predict',methods=['GET','POST'])
def predict():
    
    def weighted_choice(choices):
        total = sum(w for c, w in choices)
        r = random.uniform(0, total)
        upto = 0
        for c, w in choices:
            if upto + w >= r:
                return c
            upto += w
        assert False, "Shouldn't get here"
    
    df_fifa_latest_rank
    
    z = np.polyfit(df_prob_win_fifa_rank.rank_diff, df_prob_win_fifa_rank.prob, 4)
    p_win = np.poly1d(z)
    
    # p_win(_some_rank)
    
    z = np.polyfit(df_prob_draw_fifa_rank.rank_diff.values, df_prob_draw_fifa_rank.prob.values, 3)
    p_draw = np.poly1d(z)
    
    country_codes = {
        "Albania": "ALB",
        "Austria": "AUT",
        "Belgium": "BEL",
        "Croatia": "CRO",
        "Czech Republic": "CZE",
        "England": "ENG",
        "France": "FRA",
        "Germany": "GER",
        "Hungary": "HUN",
        "Iceland": "ISL",
        "Italy": "ITA",
        "Northern Ireland": "NIR",
        "Poland": "POL",
        "Portugal": "POR",
        "Republic of Ireland": "IRL",
        "Romania": "ROU",
        "Russia": "RUS",
        "Slovakia": "SVK",
        "Spain": "ESP",
        "Sweden": "SWE",
        "Switzerland": "SUI",
        "Turkey": "TUR",
        "Ukraine": "UKR",
        "Wales": "WAL",
    }
    
    country_from_codes = {
        "ALB": "Albania",
        "AUT": "Austria",
        "BEL": "Belgium",
        "CRO": "Croatia",
        "CZE": "Czech Republic",
        "ENG": "England",
        "FRA": "France",
        "GER": "Germany",
        "HUN": "Hungary",
        "ISL": "Iceland",
        "ITA": "Italy",
        "NIR": "Northern Ireland",
        "POL": "Poland",
        "POR": "Portugal",
        "IRL": "Republic of Ireland",
        "ROU": "Romania",
        "RUS": "Russia",
        "SVK": "Slovakia",
        "ESP": "Spain",
        "SWE": "Sweden",
        "SUI": "Switzerland",
        "TUR": "Turkey",
        "UKR": "Ukraine",
        "WAL": "Wales",
    }
    
    grp_A_matches = [
        ['2016-06-10', 'France', 'Romania'],
        ['2016-06-11', 'Albania', 'Switzerland'],
        ['2016-06-15', 'Romania', 'Switzerland'],
        ['2016-06-15', 'France', 'Albania'],
        ['2016-06-19', 'Switzerland', 'France'],
        ['2016-06-19', 'Romania', 'Albania'],
    ]
    
    grp_B_matches = [
        ['2016-06-11', 'Wales', 'Slovakia'],
        ['2016-06-11', 'England', 'Russia'],
        ['2016-06-15', 'Russia', 'Slovakia'],
        ['2016-06-16', 'England', 'Wales'],
        ['2016-06-20', 'Slovakia', 'England'],
        ['2016-06-20', 'Russia', 'Wales'],
    ]
    
    grp_C_matches = [
        ['2016-06-12', 'Poland', 'Northern Ireland'],
        ['2016-06-12', 'Germany', 'Ukraine'],
        ['2016-06-16', 'Ukraine', 'Northern Ireland'],
        ['2016-06-16', 'Germany', 'Poland'],
        ['2016-06-21', 'Northern Ireland', 'Germany'],
        ['2016-06-21', 'Ukraine', 'Poland'],
    ]
    
    grp_D_matches = [
        ['2016-06-12', 'Turkey', 'Croatia'],
        ['2016-06-13', 'Spain', 'Czech Republic'],
        ['2016-06-17', 'Czech Republic', 'Croatia'],
        ['2016-06-17', 'Spain', 'Turkey'],
        ['2016-06-21', 'Croatia', 'Spain'],
        ['2016-06-21', 'Czech Republic', 'Turkey'],
    ]
    
    grp_E_matches = [
        ['2016-06-13', 'Republic of Ireland', 'Sweden'],
        ['2016-06-13', 'Belgium', 'Italy'],
        ['2016-06-17', 'Italy', 'Sweden'],
        ['2016-06-18', 'Belgium', 'Republic of Ireland'],
        ['2016-06-22', 'Sweden', 'Belgium'],
        ['2016-06-22', 'Italy', 'Republic of Ireland'],
    ]
    
    grp_F_matches = [
        ['2016-06-14', 'Austria', 'Hungary'],
        ['2016-06-14', 'Portugal', 'Iceland'],
        ['2016-06-18', 'Iceland', 'Hungary'],
        ['2016-06-18', 'Portugal', 'Austria'],
        ['2016-06-22', 'Iceland', 'Austria'],
        ['2016-06-22', 'Hungary', 'Portugal'],
    ]
    
    grp_matchs = grp_A_matches + grp_B_matches + grp_C_matches + grp_D_matches + grp_E_matches + grp_F_matches
    
    df_ctry_codes = df_fifa_latest_rank.country_code
    probailities = []
    plot_dict = {}
    prediction_dict = {}
    results = {}
    for k, match in enumerate(grp_matchs,1):
        rank_diff = df_fifa_latest_rank[df_ctry_codes==country_codes[match[1]]].ranking.values - df_fifa_latest_rank[df_ctry_codes==country_codes[match[2]]].ranking.values
        probs = [p_win(rank_diff*-1)[0], p_draw(abs(rank_diff))[0], p_win(rank_diff)[0]]
        probs = [float(i)/sum(probs) for i in probs]
        probailities = [country_codes[match[1]], 'DRAW', country_codes[match[2]]] + probs
        choices = [(country_codes[match[1]], probs[0]), ('DRAW', probs[1]), (country_codes[match[2]], probs[2])]
        
        prediction = weighted_choice(choices)
        if prediction=='DRAW':
            prediction_dict["match_{0}".format(k)] = prediction
        else:
            prediction_dict["match_{0}".format(k)] = country_from_codes[prediction]
        
        df = pd.DataFrame(probailities[3:], probailities[:3])
        df.columns = ['probability']
        plot_probs = Bar(df, toolbar_location=None, plot_width=200, plot_height=200, agg='mean')
        plot_probs.x_range = FactorRange(factors=probailities[:3])
        plot_dict["match_{0}".format(k)] = plot_probs
    
    gp_A = dict.fromkeys(["France","Romania","Albania","Switzerland"], 0)
    gp_B = dict.fromkeys(["England","Russia","Wales","Slovakia"], 0)
    gp_C = dict.fromkeys(["Germany","Ukraine","Poland","Northern Ireland"], 0)
    gp_D = dict.fromkeys(["Spain","Czech Republic","Turkey","Croatia"], 0)
    gp_E = dict.fromkeys(["Belgium","Italy","Republic of Ireland","Sweden"], 0)
    gp_F = dict.fromkeys(["Portugal","Iceland","Austria","Hungary"], 0)
    for k, match in enumerate(grp_A_matches,1):
        result = prediction_dict["match_{0}".format(k)]
        if result == 'DRAW':
            gp_A[match[1]] += 1
            gp_A[match[2]] += 1
        else:
            gp_A[result] += 3
    
    for k, match in enumerate(grp_B_matches,7):
        result = prediction_dict["match_{0}".format(k)]
        if result == 'DRAW':
            gp_B[match[1]] += 1
            gp_B[match[2]] += 1
        else:
            gp_B[result] += 3

    for k, match in enumerate(grp_C_matches,13):
        result = prediction_dict["match_{0}".format(k)]
        if result == 'DRAW':
            gp_C[match[1]] += 1
            gp_C[match[2]] += 1
        else:
            gp_C[result] += 3

    for k, match in enumerate(grp_D_matches,19):
        result = prediction_dict["match_{0}".format(k)]
        if result == 'DRAW':
            gp_D[match[1]] += 1
            gp_D[match[2]] += 1
        else:
            gp_D[result] += 3

    for k, match in enumerate(grp_E_matches,25):
        result = prediction_dict["match_{0}".format(k)]
        if result == 'DRAW':
            gp_E[match[1]] += 1
            gp_E[match[2]] += 1
        else:
            gp_E[result] += 3

    for k, match in enumerate(grp_F_matches,31):
        result = prediction_dict["match_{0}".format(k)]
        if result == 'DRAW':
            gp_F[match[1]] += 1
            gp_F[match[2]] += 1
        else:
            gp_F[result] += 3
            
    all_groups = [gp_A,gp_B,gp_C,gp_D,gp_E,gp_F]
    gp_labels = {1:"A",2:"B",3:"C",4:"D",5:"E",6:"F"}
    table_html = {}
    for k, group in enumerate(all_groups,1):
        table_string = ['      <table style="width:100%">']
        group_standings = {'team':[], 'points':[]}
        for j in xrange(1,len(group)+1):
            table_string.append('        <tr>')
            top = max(group, key=group.get)
            points = group.get(top)
            group_standings['team'].append(top)
            group_standings['points'].append(points)
            group.pop(top)
            table_string.append('          <td>{0}</td>'.format(j))
            table_string.append('          <td>{0}</td>'.format(top))
            table_string.append('          <td>{0}</td>'.format(points))
            table_string.append('        </tr>')
        table_string.append('        </table>')
        table_html["gp_{0}".format(gp_labels[k])] = '\n'.join(table_string) 
    
    script, div = components(plot_dict)
    
    return render_template('euro.html', js_resources=js_resources, script=script, div=div, pred=prediction_dict, table=table_html)

@app.route('/country_data',methods=['GET','POST'])
def country():
    team_avg_ranking = df_rank.groupby('team').ranking.mean().to_frame()
    team_num_wc = df_rank.team.value_counts().head(50).to_frame()
    
    df_team_rank = team_avg_ranking.join(team_num_wc)
    df_team_rank = df_team_rank.dropna()
    
    plot_num_wcs = figure(tools=TOOLS,
                  x_axis_label='Number of World Cups',
                  y_axis_label='Average World Cup Ranking',
                  toolbar_location="below"
                  )
    
    plot_num_wcs.scatter(df_team_rank.team, df_team_rank.ranking, color='blue', size=8, alpha=0.5)
    
    plot_dict = {"history":plot_num_wcs}
    
    script, div = components(plot_dict)
    
    return render_template('country.html', js_resources=js_resources, script=script, div=div)

@app.route('/league_data',methods=['GET','POST'])
def leagues():
    grouped = df_squads.groupby('year')
    club_country = df_squads.club_country.unique()
    club_country.sort()
    df_clb_ctry = pd.DataFrame({"club_country":club_country})
    
    for year in df_squads.year.unique():
        country_to_club = grouped.club_country.value_counts()[year] / grouped.team.value_counts()[year]
        df_clb_ctry = df_clb_ctry.join(country_to_club.to_frame(year))
        
    df_clb_ctry = df_clb_ctry.fillna(0) # If NaN, country league not represented at the world cup
    df_clb_ctry = df_clb_ctry.T
    
    plot_nat_leagues = figure(tools=TOOLS,
                  x_axis_label='World Cup Year',
                  toolbar_location=None
                  )
    
    # take the top 11 countries and plot
    for num, country in enumerate(df_clb_ctry.sum().sort_values(ascending=False).head(11).index):
        plot_nat_leagues.scatter(df_clb_ctry.index, df_clb_ctry[country],legend=country,color=RdBu11[num],size=8, alpha=0.5)
    
    plot_nat_leagues.legend.location = "top_left"
    
    df_expats = df_league_data[df_league_data.nation!=df_league_data.nationality]
    
    seasons = df_expats.season.unique()
    
    min = int(seasons[0].split('-')[0])
    max = int(seasons[-1].split('-')[0])
    
    wc_year_slider = Slider(start=min, end=max, value=max, step=1, title="Soccer Season")
    
    for season in seasons:
        nationality_expats = df_expats.groupby('season').nationality.value_counts()[season].head(5)
        nation_expats = df_expats.groupby('season').nation.value_counts()[season]
    
    plot_expats = Bar(nationality_expats, toolbar_location=None)
    plot_expats.x_range = FactorRange(factors=nationality_expats.index.tolist())
    
    plot_dict = {"nations":plot_nat_leagues, "expats":plot_expats}
    
    script, div = components(plot_dict)
    
    return render_template('league.html', js_resources=js_resources, script=script, div=div)

@app.route('/player_data',methods=['GET','POST'])
def players():
    grouped = df_squads.groupby('year')
    
    avg_age = df_squads.groupby('year').age.mean().to_frame()
    
    plot_plyr_age = figure(tools=TOOLS,
                  title='Average Team Age',
                  x_axis_label='World Cup Year',
                  toolbar_location="below"
                  )

    plot_plyr_age.line(avg_age.index, avg_age.age.values, color='green', line_width=4, alpha=0.5)
    
    plots = {"plt_age": plot_plyr_age}
    
    script, div = components(plots)
    
    return render_template('player.html', js_resources=js_resources, script=script, div=div)
            
@app.route('/interesting_stuff',methods=['GET','POST'])
def fun():
    plot_transfer_fee = figure(tools=TOOLS,
                      title='World Record Soccer Transfer Fee',
                      x_axis_label='Year',
                      y_axis_label=u"Fee (\u00A3)",
                      toolbar_location=None
                      )
    
    plot_transfer_fee.line(df_tranfer['year'], df_tranfer['fee_pounds'],color=RdBu11[0],line_width=4)

    month_map = {k: v for k,v in enumerate(calendar.month_abbr)}
    
    df_mth = df_squads.birth_month.value_counts().sort_index()
    df_mth.index = df_mth.index.map(lambda x: month_map[x])
    
    plot_mth_of_birth = Bar(df_mth, toolbar_location=None)
    plot_mth_of_birth.x_range = FactorRange(factors=df_mth.index.tolist())
    
    plots = {"plt_trans_fee": plot_transfer_fee, "plt_mth_birth": plot_mth_of_birth}
    
    script, div = components(plots)
    
    return render_template('interesting.html', js_resources=js_resources, script=script, div=div)

if __name__ == '__main__':
  app.run(port=33507)#debug=True)
  