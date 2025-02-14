# -*- coding: utf-8 -*-
import os
import pandas as pd
import seaborn as sns
import matplotlib.colors
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import numpy as np


def ground_averages(db):
    """
    param db: Database ; pandas Dataframe
    """

    assert isinstance(db, pd.DataFrame)
    
    # Some more cleaning
    missing_cities = {'Harare Sports Club':'Harare',
                    'Sylhet International Cricket Stadium':'Sylhet',
                    'Dubai International Cricket Stadium':'Dubai',
                    'Sydney Cricket Ground':'Sydney',
                    'Sylhet Stadium':'Sylhet',
                    'Pallekele International Cricket Stadium':'Kandy',
                    'Sharjah Cricket Stadium':'Sharjah',
                    'Melbourne Cricket Ground':'Melbourne',
                    'Moara Vlasiei Cricket Ground':'Ilfov County',
                    'Rawalpindi Cricket Stadium':'Rawalpindi',
                    'Adelaide Oval':'Adelaide',
                    'Mombasa Sports Club Ground':'Mombasa',
                    'Carrara Oval':'Carrara'
                    }

    db['updated_city'] = db.apply(lambda x: missing_cities[x['updated_venue']] \
                                  if str(x['updated_venue']) in missing_cities.keys() \
                                  else x['update_city'], axis=1
                                  )
    
    # Finding various averages 
    avg_db = db.groupby(['updated_venue', 'updated_city', 'innings_number']).agg({
            'Total_Score_A':['sum', 'count'], 'Total_Wicket_A':'sum', 'Runs_in_Death_overs':'sum',
            'Runs_in_middle_overs':'sum' 
    }).reset_index()
    
    # Renaming columns
    avg_db.columns = [col[0] if col[1] == "" else '_'.join(col) for col in avg_db.columns.values]

    # Creating average columns
    avg_cols = ['avg_score', 'avg_wickets', 'avg_death_over_score', 'avg_middle_over_score']
    total_cols = ['Total_Score_A_sum', 'Total_Wicket_A_sum', 'Runs_in_Death_overs_sum',
                  'Runs_in_middle_overs_sum']

    for idx in range(len(avg_cols)):
        avg_db[avg_cols[idx]] = avg_db.apply(lambda row: row[total_cols[idx]] // \
                                       row['Total_Score_A_count'], axis=1)

    # # Average score 
    # # Conditions 1) First innings 2) Total matched >= 10
    # avg_db_1 = avg_db[(avg_db['Total_Score_A_count'] >= 10) & 
    #           (avg_db['innings_number'].str.strip() == 'A')
    #           ].sort_values(by=['avg_score','Total_Score_A_count'], 
    #                         ascending=False)
    return avg_db, db


def batting_bowling_performances(avg_db, utd_db):
    """
    param db: Database ; pandas Dataframe
    """
        
    assert isinstance(avg_db, pd.DataFrame)
    assert isinstance(utd_db, pd.DataFrame)

    utd_db = utd_db.merge(avg_db[['updated_venue','updated_city', 'innings_number',  'avg_score', 'avg_wickets']], 
                            how='left', 
                            on=['updated_venue', 'updated_city', 'innings_number'])

    # bringing match innings level statistics on a unique match id
    refined_db = utd_db[['match_id', 'updated_venue', 'updated_city', 'winner',
                         'avg_score', 'avg_wickets', 'innings_number', 
                         'team_A', 'team_B', 'Total_Score_A','Total_Wicket_A']]
    
    first_innings = refined_db[utd_db['innings_number'].str.strip() == 'A']
    second_innings = refined_db[utd_db['innings_number'].str.strip() == 'B']

    # Renaming second innings columns
    rename_second_cols = {'team_A': 'team_A2', 'team_B': 'team_B2', 
                          'Total_Score_A':'Total_Score_A2', 'Total_Wicket_A': 'Total_Wicket_A2'}
    second_innings = second_innings.rename(columns=rename_second_cols)

    both_innings = first_innings.merge(second_innings[['match_id', 'updated_venue', 'updated_city',
                                                       'team_A2', 'team_B2',
                                                       'Total_Score_A2','Total_Wicket_A2']],
                                       how='left',
                                       on=['match_id', 'updated_venue', 'updated_city'])
    
    # Creating batting and bowling performance in a particular match for both teams
    both_innings['A_both'] = both_innings.apply(
        lambda row: 1 if (row['Total_Score_A'] >= row['avg_score']) and \
        (row['Total_Score_A2'] < row['Total_Score_A']) else 0, axis=1
    )

    both_innings['B_both'] = both_innings.apply(
        lambda row: 1 if (row['Total_Score_A2'] >= row['Total_Score_A']) and \
        (row['Total_Score_A'] < row['avg_score']) else 0, axis=1
    )

    both_innings['A_batting'] = both_innings.apply(
        lambda row: 1 if (row['Total_Score_A'] >= row['avg_score']) and (row['A_both'] == 0) \
        else 0, axis=1
    )

    both_innings['B_bowling'] = both_innings.apply(
        lambda row: 1 if (row['Total_Score_A'] < row['avg_score']) and (row['B_both'] == 0) else 0, axis=1
    )

    both_innings['B_batting'] = both_innings.apply(
        lambda row: 1 if row['Total_Score_A2'] >= row['Total_Score_A'] and (row['B_both'] == 0) \
        else 0, axis=1
    )

    both_innings['A_bowling'] = both_innings.apply(
        lambda row: 1 if (row['Total_Score_A2'] < row['Total_Score_A']) and (row['A_both'] == 0) else 0, axis=1
    )

    # Splitting by country
    list_1 = both_innings[['team_A', 'team_B', 'winner','A_both', 'A_batting', 'A_bowling' ]]
    list_1['win_or_loss'] = list_1.apply(
        lambda row: 1 if row['team_A'] == row['winner'] else 0, axis=1
    )
    list_2 = both_innings[['team_A2', 'team_B2', 'winner','B_both', 'B_batting', 'B_bowling' ]]
    list_2['win_or_loss'] = list_2.apply(
        lambda row: 1 if row['team_A2'] == row['winner'] else 0, axis=1
    )
    
    # Splitting and concatenating both team matchups as home and opposition to find their overall matchups, wins, losses, and performances
    final_rename_cols = ['home', 'opposition', 'winner', 'both_perf', 'batting_perf', \
                     'bowling_perf', 'win_or_loss']
    list_1.columns = final_rename_cols
    list_2.columns = final_rename_cols

    final_list = pd.concat([list_1, list_2])

    ds = final_list.groupby(['home', 'opposition', 'win_or_loss']).agg({
            'both_perf':['count', 'sum'], 'batting_perf':'sum', \
            'bowling_perf':'sum'}).reset_index()

    ds.columns = [col[0] if col[1] == "" else '_'.join(col) for col in ds.columns.values]
    ds.rename(columns={ ds.columns[3]: "matchups" }, inplace = True)
    ds.rename(columns={ ds.columns[4]: "both_perf" }, inplace = True)
    ds.rename(columns={ ds.columns[5]: "batting_perf" }, inplace = True)
    ds.rename(columns={ ds.columns[6]: "bowling_perf" }, inplace = True)
    
    return ds


def create_team_visualizations(ds):
    """
    param db: Database ; pandas Dataframe
    """
    assert isinstance(ds, pd.DataFrame)

    wc_countries = ["New Zealand","England","Australia","Sri Lanka","Ireland","Afghanistan","India","Pakistan","South Africa","Netherlands","Bangladesh","Zimbabwe"]
    final_four = ["New Zealand","England", "India","Pakistan"]
    ds_1 = ds[ds['home'].isin(wc_countries)]
    ds_2 = ds_1[ds_1['opposition'].isin(wc_countries)]
    ds_win = ds_2[(ds['win_or_loss'] == 1)]

    colors = ['tomato', 'limegreen', 'cornflowerblue','#CAE1FF','#FFDEAD']

    # England -----------------------------------------------------------------
    ds_win_1 = ds_2[(ds['win_or_loss'] == 1) & (ds['home']=='England')]
    temp0=ds_win_1['both_perf']+ds_win_1['batting_perf']+ds_win_1['bowling_perf']
    temp1=(ds_win_1['both_perf']/(temp0))*100
    temp2=(ds_win_1['batting_perf']/(temp0))*100 
    temp3=(ds_win_1['bowling_perf']/(temp0))*100

    # The position of the bars on the x-axis
    r = range(len(ds_win_1['opposition'].values.tolist()))
    barWidth = 0.75
    #plot bars
    plt.figure(figsize=(16,9))
    ax1 = plt.bar(r, temp1, bottom=temp2+temp3, color=colors[0], edgecolor='black', width=barWidth, label="Both Perfomance")
    ax2 = plt.bar(r, temp2, bottom=temp3, color=colors[1], edgecolor='black', width=barWidth, label='Batting only')
    ax3 = plt.bar(r, temp3, color=colors[2], edgecolor='black', width=barWidth, label='Bowling only')
    plt.legend()
    plt.title('Performance of England vs the other WC teams')
    plt.xticks(r, ds_win_1['opposition'].values.tolist(), fontweight='bold')
    plt.ylabel("Percentage contribution to wins")

    i = 0
    for r1, r2, r3 in zip(ax1, ax2, ax3):
        h1 = r1.get_height()
        h2 = r2.get_height()
        h3 = r3.get_height()
        a = ds_win_1.iloc[i]['both_perf']
        b = ds_win_1.iloc[i]['batting_perf']
        c = ds_win_1.iloc[i]['bowling_perf']
        i += 1
        if not h1 < 0.0000001:
            plt.text(r1.get_x() + r1.get_width() / 2., h2+h3 + h1 / 2., f'{h1:.1f}%\n{a}', ha="center", va="center", color="black", fontsize=12, fontweight="bold")
        if not h2 < 0.0000001:
            plt.text(r2.get_x() + r2.get_width() / 2., h3 + h2 / 2., f'{h2:.1f}%\n{b}', ha="center", va="center", color="black", fontsize=12, fontweight="bold")
        if not h3 < 0.0000001:
            plt.text(r3.get_x() + r3.get_width() / 2., h3 / 2., f'{h3:.1f}%\n{c}', ha="center", va="center", color="black", fontsize=12, fontweight="bold")

    plt.savefig("England_vs_other_teams.png")

    # India -----------------------------------------------------
    ds_win_1 = ds_2[(ds['win_or_loss'] == 1) & (ds['home']=='India')]
    temp0=ds_win_1['both_perf']+ds_win_1['batting_perf']+ds_win_1['bowling_perf']
    temp1=(ds_win_1['both_perf']/(temp0))*100
    temp2=(ds_win_1['batting_perf']/(temp0))*100 
    temp3=(ds_win_1['bowling_perf']/(temp0))*100

    # The position of the bars on the x-axis
    r = range(len(ds_win_1['opposition'].values.tolist()))
    barWidth = 0.75
    #plot bars
    plt.figure(figsize=(16,9))
    ax1 = plt.bar(r, temp1, bottom=temp2+temp3, color=colors[0], edgecolor='black', width=barWidth, label="Both Perfomance")
    ax2 = plt.bar(r, temp2, bottom=temp3, color=colors[1], edgecolor='black', width=barWidth, label='Batting only')
    ax3 = plt.bar(r, temp3, color=colors[2], edgecolor='black', width=barWidth, label='Bowling only')
    plt.legend()
    plt.title('Performance of India vs the other WC teams')
    plt.xticks(r, ds_win_1['opposition'].values.tolist(), fontweight='bold')
    plt.ylabel("Percentage contribution to wins")

    i = 0
    for r1, r2, r3 in zip(ax1, ax2, ax3):
        h1 = r1.get_height()
        h2 = r2.get_height()
        h3 = r3.get_height()
        a = ds_win_1.iloc[i]['both_perf']
        b = ds_win_1.iloc[i]['batting_perf']
        c = ds_win_1.iloc[i]['bowling_perf']
        i += 1
        if not h1 < 0.0000001:
            plt.text(r1.get_x() + r1.get_width() / 2., h2+h3 + h1 / 2., f'{h1:.1f}%\n{a}', ha="center", va="center", color="black", fontsize=12, fontweight="bold")
        if not h2 < 0.0000001:
            plt.text(r2.get_x() + r2.get_width() / 2., h3 + h2 / 2., f'{h2:.1f}%\n{b}', ha="center", va="center", color="black", fontsize=12, fontweight="bold")
        if not h3 < 0.0000001:
            plt.text(r3.get_x() + r3.get_width() / 2., h3 / 2., f'{h3:.1f}%\n{c}', ha="center", va="center", color="black", fontsize=12, fontweight="bold")

    plt.savefig("India_vs_other_teams.png")

    # New Zealand -----------------------------------------------------
    ds_win_1 = ds_2[(ds['win_or_loss'] == 1) & (ds['home']=='New Zealand')]
    temp0=ds_win_1['both_perf']+ds_win_1['batting_perf']+ds_win_1['bowling_perf']
    temp1=(ds_win_1['both_perf']/(temp0))*100
    temp2=(ds_win_1['batting_perf']/(temp0))*100 
    temp3=(ds_win_1['bowling_perf']/(temp0))*100

    # The position of the bars on the x-axis
    r = range(len(ds_win_1['opposition'].values.tolist()))
    barWidth = 0.75
    #plot bars
    plt.figure(figsize=(16,9))
    ax1 = plt.bar(r, temp1, bottom=temp2+temp3, color=colors[0], edgecolor='black', width=barWidth, label="Both Perfomance")
    ax2 = plt.bar(r, temp2, bottom=temp3, color=colors[1], edgecolor='black', width=barWidth, label='Batting only')
    ax3 = plt.bar(r, temp3, color=colors[2], edgecolor='black', width=barWidth, label='Bowling only')
    plt.legend()
    plt.title('Performance of New Zealand vs the other WC teams')
    plt.xticks(r, ds_win_1['opposition'].values.tolist(), fontweight='bold')
    plt.ylabel("Percentage contribution to wins")

    i = 0
    for r1, r2, r3 in zip(ax1, ax2, ax3):
        h1 = r1.get_height()
        h2 = r2.get_height()
        h3 = r3.get_height()
        a = ds_win_1.iloc[i]['both_perf']
        b = ds_win_1.iloc[i]['batting_perf']
        c = ds_win_1.iloc[i]['bowling_perf']
        i += 1
        if not h1 < 0.0000001:        
            plt.text(r1.get_x() + r1.get_width() / 2., h2+h3 + h1 / 2., f'{h1:.1f}%\n{a}', ha="center", va="center", color="black", fontsize=12, fontweight="bold")
        if not h2 < 0.0000001:
            plt.text(r2.get_x() + r2.get_width() / 2., h3 + h2 / 2., f'{h2:.1f}%\n{b}', ha="center", va="center", color="black", fontsize=12, fontweight="bold")
        if not h3 < 0.0000001:
            plt.text(r3.get_x() + r3.get_width() / 2., h3 / 2., f'{h3:.1f}%\n{c}', ha="center", va="center", color="black", fontsize=12, fontweight="bold")

    plt.savefig("New_Zealand_vs_other_teams.png")

    # Pakistan -----------------------------------------
    ds_win_1 = ds_2[(ds['win_or_loss'] == 1) & (ds['home']=='Pakistan')]
    temp0=ds_win_1['both_perf']+ds_win_1['batting_perf']+ds_win_1['bowling_perf']
    temp1=(ds_win_1['both_perf']/(temp0))*100
    temp2=(ds_win_1['batting_perf']/(temp0))*100 
    temp3=(ds_win_1['bowling_perf']/(temp0))*100
    colors = ['tomato', 'limegreen', 'cornflowerblue','#CAE1FF','#FFDEAD']

    # The position of the bars on the x-axis
    r = range(len(ds_win_1['opposition'].values.tolist()))
    barWidth = 0.75
    #plot bars
    plt.figure(figsize=(16,9))
    ax1 = plt.bar(r, temp1, bottom=temp2+temp3, color=colors[0], edgecolor='black', width=barWidth, label="Both Perfomance")
    ax2 = plt.bar(r, temp2, bottom=temp3, color=colors[1], edgecolor='black', width=barWidth, label='Batting only')
    ax3 = plt.bar(r, temp3, color=colors[2], edgecolor='black', width=barWidth, label='Bowling only')
    plt.legend()
    plt.title('Performance of Pakistan vs the other WC teams')
    plt.xticks(r, ds_win_1['opposition'].values.tolist(), fontweight='bold')
    plt.ylabel("Percentage contribution to wins")

    i = 0
    for r1, r2, r3 in zip(ax1, ax2, ax3):
        h1 = r1.get_height()
        h2 = r2.get_height()
        h3 = r3.get_height()
        a = ds_win_1.iloc[i]['both_perf']
        b = ds_win_1.iloc[i]['batting_perf']
        c = ds_win_1.iloc[i]['bowling_perf']
        i += 1
        if not h1 < 0.0000001:
            plt.text(r1.get_x() + r1.get_width() / 2., h2+h3 + h1 / 2., f'{h1:.1f}%\n{a}', ha="center", va="center", color="black", fontsize=12, fontweight="bold")
        if not h2 < 0.0000001:
            plt.text(r2.get_x() + r2.get_width() / 2., h3 + h2 / 2., f'{h2:.1f}%\n{b}', ha="center", va="center", color="black", fontsize=12, fontweight="bold")
        if not h3 < 0.0000001:
            plt.text(r3.get_x() + r3.get_width() / 2., h3 / 2., f'{h3:.1f}%\n{c}', ha="center", va="center", color="black", fontsize=12, fontweight="bold")

    plt.savefig("Pakistan_vs_other_teams.png")
    
    #Pie charts for the total performances of the final four teams in wins
    good_batting_performance_England=0
    good_bowling_performance_England=0
    both_England=0
    good_batting_performance_India=0
    good_bowling_performance_India=0
    both_India=0
    good_batting_performance_NewZealand=0
    good_bowling_performance_NewZealand=0
    both_NewZealand=0
    good_batting_performance_Pakistan=0
    good_bowling_performance_Pakistan=0
    both_Pakistan=0
    for index, row in ds.iterrows():
        if ((row['home']=='England')&(row['win_or_loss']==1)):  
            good_batting_performance_England+=row['batting_perf']
            good_bowling_performance_England+=row['bowling_perf']
            both_England+=row['both_perf'] 
        elif ((row['home']=='India')&(row['win_or_loss']==1)):  
            good_batting_performance_India+=row['batting_perf']
            good_bowling_performance_India+=row['bowling_perf']
            both_India+=row['both_perf']
        elif ((row['home']=='New Zealand')&(row['win_or_loss']==1)):  
            good_batting_performance_NewZealand+=row['batting_perf']
            good_bowling_performance_NewZealand+=row['bowling_perf']
            both_NewZealand+=row['both_perf']
        elif ((row['home']=='Pakistan')&(row['win_or_loss']==1)):  
            good_batting_performance_Pakistan+=row['batting_perf']
            good_bowling_performance_Pakistan+=row['bowling_perf']
            both_Pakistan+=row['both_perf']
        else:
            continue
    
    Performance_England = np.array([good_batting_performance_England,good_bowling_performance_England,both_England])
    labels=["good batting","good bowling","both"]
    plt.figure(figsize=(16,9))
    plt.pie(Performance_England,labels=labels,autopct='%1.1f%%')
    plt.title("Composition of Wins, England")
    plt.savefig("England_performance.png")

    Performance_India = np.array([good_batting_performance_India,good_bowling_performance_India,both_India])
    labels=["good batting","good bowling","both"]
    plt.figure(figsize=(16,9))
    plt.pie(Performance_India,labels=labels,autopct='%1.1f%%')
    plt.title("Composition of Wins, India")
    plt.savefig("India_performance.png")

    Performance_NewZealand = np.array([good_batting_performance_NewZealand,good_bowling_performance_NewZealand,both_NewZealand])
    labels=["good batting","good bowling","both"]
    plt.figure(figsize=(16,9))
    plt.pie(Performance_NewZealand,labels=labels,autopct='%1.1f%%')
    plt.title("Composition of Wins, New Zealand")
    plt.savefig("NewZealand_performance.png")

    Performance_Pakistan = np.array([good_batting_performance_Pakistan,good_bowling_performance_Pakistan,both_Pakistan])
    labels=["good batting","good bowling","both"]
    plt.figure(figsize=(16,9))
    plt.pie(Performance_Pakistan,labels=labels,autopct='%1.1f%%')
    plt.title("Composition of Wins, Pakistan")
    plt.savefig("Pakistan_performance.png")
       
       
def world_map_visualization(avg_db):
    """
    param db: Database ; pandas Dataframe
    """
    assert isinstance(avg_db, pd.DataFrame)

    city_country_mapping = {
    'Abu Dhabi':'United Arab Emirates','Adelaide':'Australia','Ahmedabad':'India',
    'Al Amarat':'Oman','Albergaria':'Portugal','Almeria':'Spain','Amstelveen':'Netherlands',
    'Antigua':'Jamaica','Auckland':'New Zealand','Bangalore':'India','Bangi':'Malaysia',
    'Bangkok':'Thailand','Barbados':'Jamaica','Basseterre':'Jamaica','Belfast':'United Kingdom',
    'Belgrade':'Serbia','Bengaluru':'India','Benoni':'South Africa','Birmingham':'United Kingdom',
    'Bloemfontein':'South Africa','Bready':'United Kingdom','Bridgetown':'Jamaica',
    'Brisbane':'Australia','Bristol':'United Kingdom','Brondby':'Denmark','Bulawayo':'Zimbabwe','Canberra':'Australia',
    'Cape Town':'South Africa','Cardiff':'United Kingdom','Carrara':'Australia','Castel':'United Kingdom','Centurion':'South Africa','Chandigarh':'India','Chattogram':'India','Chennai':'India',
    'Chester-le-Street':'United Kingdom','Chittagong':'Bangladesh','Christchurch':'New Zealand',
    'Colombo':'Sri Lanka','Coolidge':'Jamaica','Cuttack':'India','Dehra Dun':'India',
    'Dehradun':'India','Delhi':'India','Derry':'United Kingdom','Deventer':'Netherlands',
    'Dhaka':'Bangladesh','Dharamsala':'India','Dharmasala':'India','Doha':'Qatar',
    'Dominica':'Jamaica','Dubai':'United Arab Emirates','Dublin':'Ireland','Dunedin':'New Zealand',
    'Durban':'South Africa','East London':'South Africa','Edinburgh':'United Kingdom','Entebbe':'Uganda',
    'Episkopi':'Cyprus','Fatullah':'Bangladesh','Geelong':'Australia',
    'Ghent':'Netherlands','Greater Noida':'India',
    'Gros Islet':'Jamaica','Guwahati':'India',
    'Guyana':'Guyana','Hambantota':'Sri Lanka',
    'Hamilton':'Jamaica','Hamilton':'New Zealand',
    'Harare':'Zimbabwe','Hobart':'Australia',
    'Hong Kong':'Hong Kong','Hyderabad':'India',
    'Ilfov County':'Romania','Indore':'India',
    'Jaipur':'India','Jamaica':'Jamaica',
    'Johannesburg':'South Africa','Kampala':'Uganda',
    'Kandy':'Sri Lanka','Kanpur':'India',
    'Karachi':'Pakistan','Kerava':'Finland',
    'Khulna':'Bangladesh','Kigali City':'Rwanda',
    'Kimberley':'South Africa','King City':'Canada',
    'Kingston':'Jamaica','Kirtipur':'Nepal',
    'Kolkata':'India','Krefeld':'Germany',
    'Kuala Lumpur':'Malaysia','Lagos':'Nigeria',
    'Lahore':'India','Lauderhill':'United States of America',
    'Leeds':'United Kingdom','London':'United Kingdom',
    'Londonderry':'United Kingdom','Lucknow':'India',
    'Manchester':'United Kingdom','Marsa':'Malta','Melbourne':'Australia',
    'Mirpur':'Bangladesh','Mount Maunganui':'New Zealand',
    'Mumbai':'India','Murcia':'Spain',
    'Nagpur':'India','Nairobi':'Kenya',
    'Napier':'New Zealand','Nelson':'New Zealand',
    'North Sound':'Jamaica','Nottingham':'United Kingdom',
    'Paarl':'South Africa','Perth':'Australia',
    'Port Elizabeth':'South Africa','Port Moresby':'Papua New Guinea',
    'Port Vila':'Vanuatu','Potchefstroom':'South Africa',
    'Prague':'Czechia','Providence':'Guyana',
    'Pune':'India','Rajkot':'India','Ranchi':'India','Roseau':'Jamaica',
    'Rotterdam':'Netherlands','Sano':'Japan',
    'Sharjah':'United Arab Emirates','Singapore':'Malaysia',
    'Sofia':'Bulgaria','Southampton':'United Kingdom',
    'St George\'s':'Jamaica','St Kitts':'Jamaica','St Lucia':'Jamaica',
    'St Peter Port':'Jamaica','St Vincent':'Jamaica',
    'Sydney':'Australia','Sylhet':'Bangladesh','Tarouba':'Trinidad and Tobago',
    'Taunton':'United Kingdom','The Hague':'Netherlands',
    'Thiruvananthapuram':'India','Townsville':'Australia',
    'Trinidad':'Trinidad and Tobago','Utrecht':'Netherlands',
    'Vantaa':'Finland','Victoria':'Australia','Visakhapatnam':'India',
    'Walferdange':'Luxembourg','Waterloo':'Belgium','Wellington':'New Zealand','Windhoek':'Namibia'
    }

    # Filtering for stadiums where atleast 5 matches have been played
    avg_db_1 = avg_db[(avg_db['Total_Score_A_count'] >= 5) & 
                (avg_db['innings_number'].str.strip() == 'A')
                ].sort_values(by=['avg_score','Total_Score_A_count'], 
                                ascending=False)
    city_country_df = pd.DataFrame(city_country_mapping.items(), columns=['updated_city', 'name'])

    avg_db_2 = avg_db_1.merge(city_country_df[['updated_city', 'name']], 
                        how='left', 
                        on=['updated_city'])
    avg_db_2x = avg_db_2.groupby(['name'])['avg_score'].agg('mean').reset_index()
    
    # Plotting the world map
    world=gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    world = world[(world.pop_est>0) & (world.name!='Antarctica')]

    world = world.merge(avg_db_2x[['name', 'avg_score']], 
                            how='left', 
                            on=['name'])
    world["avg_score"] = world["avg_score"].fillna(100)

    fig, ax = plt.subplots(1, 1)
    fig.set_size_inches(18.5,10.5)
    minimum=0.2
    maximum=1
    n=20
    original=plt.cm.OrRd
    colors=original(np.linspace(minimum,maximum,n))
    new=matplotlib.colors.LinearSegmentedColormap.from_list("new",colors)
    ax.set_axis_off()
    world.plot(column='avg_score', ax=ax, legend=True, cmap=new, legend_kwds={'label': "Ground Averages Across Countries",'orientation': "horizontal"})
    plt.savefig('world.jpg')


if __name__ == "__main__":
    BASE_PATH = os.getcwd()
    DATABASE_PATH = os.path.join(BASE_PATH, "DataProcessing", "result_post_step.csv")
    database = pd.read_csv(DATABASE_PATH)
    avg_db, uptd_db = ground_averages(database)
    final_db = batting_bowling_performances(avg_db, uptd_db)
    create_team_visualizations(final_db)
    world_map_visualization(avg_db)
