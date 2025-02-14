import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def make_plots_1(db, team_1, team_2 = "All"):
    """
    This function makes the win-loss% plot (for three scenarios - batting first, batting second, and overall) for any of the top 12 teams of T20WC 2022. 
    The overall win-loss% can be computed either for all T20I matches against all other teams or against a particular team.  

    param db: Database ; pandas Dataframe
    param team_1: Team for which win-loss is to be calculated; str
    param team_2: Team against which win-loss is to be calculated; str; default value = all
    """

    assert isinstance(db, pd.DataFrame)
    assert isinstance(team_1, str)
    assert isinstance(team_2, str)

    super_12 = ["India", "Australia", "England", "Pakistan", "South Africa", "Bangladesh", "Afghanistan", "Sri Lanka", "Ireland", "Zimbabwe", "Netherlands", "New Zealand"]
    filter1 = db["team_A"].isin(super_12)
    filter2 = db["year"]>2015
    ref_db = db[filter1 & filter2].reset_index()

    aus_stadiums = ['Sydney Cricket Ground', 'Brisbane Cricket Ground', 'Melbourne Cricket Ground', 'GMHBA Stadium', 'Perth Stadium', 'Manuka Oval', 'Bellerive Oval', 'Carrara Oval', 'Adelaide Oval']
    ref_db_win_loss = ref_db.loc[:, ["id", "year", "updated_venue", "team_A", "team_B", "winner"]]
    ref_db_win_loss["In_Australia"]=ref_db_win_loss["updated_venue"].isin(aus_stadiums)
    ref_db_win_loss = ref_db_win_loss.drop(columns='updated_venue')

    ref_db_win_loss.iloc[:,[2,1,3,0,4,5]]
   
    batting_first = []
    for i in range(ref_db_win_loss.shape[0]):
        var_check = list(ref_db_win_loss["id"])[i][-1]
        batting_first.append("Y" if var_check == "A" else "N")

    ref_db_win_loss["batting_first"]=batting_first
    ref_db_win_loss = ref_db_win_loss.drop(columns=["id"])
    
    winner_add = []
    for i in range(ref_db_win_loss.shape[0]):
        var_check = list(ref_db_win_loss["winner"])[i]
        var_check_2 = list(ref_db_win_loss["team_A"])[i]
        winner_add.append("Y" if var_check == var_check_2 else "N")

    ref_db_win_loss["win"]=winner_add
    ref_db_win_loss = ref_db_win_loss.drop(columns='winner')

    win_loss_record = []

    if team_2 == "All":
        country_data = ref_db_win_loss.loc[(ref_db_win_loss['team_A'] == team_1)]

    else:
        country_data = ref_db_win_loss.loc[(ref_db_win_loss['team_A'] == team_1)]
        country_data = country_data.loc[(country_data['team_B'] == team_2)]

    years = np.sort(list(country_data.year.unique()))    
    for year_ref in years:
        
        year_data = country_data.loc[(country_data['year'] == year_ref)]
        try:
            num_wins_total = sum(year_data['win'] == "Y")
        except:
            num_wins_total = 0
        try:
            num_wins_bat = year_data.groupby(['batting_first','win']).value_counts().Y.Y.sum()
        except:
            num_wins_bat = 0
        try:
            num_wins_ball = year_data.groupby(['batting_first','win']).value_counts().N.Y.sum()
        except:
            num_wins_ball = 0
        total_matches = year_data['win'].size
        try:
            total_matches_bat = year_data.batting_first.value_counts().Y
        except:
            total_matches_bat = 0
        try:
            total_matches_ball = year_data.batting_first.value_counts().N
        except:
            total_matches_ball = 0
        try:
            win_loss_bat = np.round((100*num_wins_bat/total_matches_bat),2)
        except:
            win_loss_bat = 0
        try:
            win_loss_ball=np.round((100*num_wins_ball/total_matches_ball),2)
        except:
            win_loss_ball = 0
        win_loss_record.append((str(year_ref)+" ("+str(total_matches)+")", np.round((100*num_wins_total/total_matches),2), win_loss_bat, win_loss_ball))

    win_loss_df = pd.DataFrame.from_records(win_loss_record, columns=["year", "win_total", "win_bat", "win_ball"])
    win_loss_df = win_loss_df.set_index("year")
    
    set_index = list(win_loss_df.index)
    set_labels = []
    for i in range(3):
        set_labels.append(list(zip(set_index, list(win_loss_df.iloc[:,i]))))

    fig, ax = plt.subplots(figsize = (10,10))
    plt.plot(win_loss_df)
    plt.legend(['Overall win%', 'Win% - Batting first', 'Win% - Bowling first'], loc='best')
    if team_2 == "All":
        plt.title('Win-Loss % across all T20 matches since 2016: '+str(team_1), loc='center')
    else:
        plt.title('Win-Loss % against '+str(team_2)+' since 2016: '+str(team_1), loc='center')
    plt.xlabel("Year (Total matches played)")
    plt.ylabel("Win-Loss (in %)")
    for i in set_labels:
        for j in i:
            plt.text(j[0], j[1], str(j[1]), va='top', ha='center')
    plt.savefig("Win_Loss_%_"+str(team_1)+"_"+str(team_2)+".png")
    plt.show()

def make_plots_2(db, team_1, team_2 = "All"):
    """
    This function plots the average runs scored and average wickets conceded per match (for three scenarios - batting first, batting second, and overall) for any of the top 12 teams of T20WC 2022. 
    These plots can be generated either for all T20I matches against all other teams or against a particular team.  

    param db: Database ; pandas Dataframe
    param team_1: Team for which said metrics are to be plotted; str
    param team_2: Team against which said metrics are to be plotted; str; default value = all
    """

    assert isinstance(db, pd.DataFrame)
    assert isinstance(team_1, str)
    assert isinstance(team_2, str)

    super_12 = ["India", "Australia", "England", "Pakistan", "South Africa", "Bangladesh", "Afghanistan", "Sri Lanka", "Ireland", "Zimbabwe", "Netherlands", "New Zealand"]
    filter1 = db["team_A"].isin(super_12)
    filter2 = db["year"]>2015
    db = db[filter1 & filter2].reset_index()

    aus_stadiums = ['Sydney Cricket Ground', 'Brisbane Cricket Ground', 'Melbourne Cricket Ground', 'GMHBA Stadium', 'Perth Stadium', 'Manuka Oval', 'Bellerive Oval', 'Carrara Oval', 'Adelaide Oval']
    ref_db_avg_score = db.loc[:, ["id", "year", "updated_venue", "team_A", "team_B", "Total_Score_A", "Total_Wicket_A"]]
    ref_db_avg_score["In_Australia"]=ref_db_avg_score["updated_venue"].isin(aus_stadiums)
    ref_db_avg_score = ref_db_avg_score.drop(["updated_venue"], axis = 1)

    batting_first = []

    for i in range(ref_db_avg_score.shape[0]):
        var_check = list(ref_db_avg_score["id"])[i][-1]
        batting_first.append("Y" if var_check == "A" else "N")

    ref_db_avg_score["batting_first"]=batting_first
    ref_db_avg_score = ref_db_avg_score.drop(columns=["id"])

    avg_score_record = []

    if team_2 == "All":
        country_data = ref_db_avg_score.loc[(ref_db_avg_score['team_A'] == team_1)]
    else:
        country_data = ref_db_avg_score.loc[(ref_db_avg_score['team_A'] == team_1)]
        country_data = country_data.loc[(country_data['team_B'] == team_2)]

    years = np.sort(list(country_data.year.unique())) 
    num_matches = []
    num_matches_bat = []
    num_matches_ball = []

    for year_ref in years:
        year_data = country_data.loc[(country_data['year'] == year_ref)]
        num_score_total = year_data["Total_Score_A"].sum()
        num_wickets_total = year_data["Total_Wicket_A"].sum()
        try:
            num_score_bat = year_data.groupby(["batting_first"])["Total_Score_A"].sum().Y
        except:
            num_score_bat = 0
        try: 
            num_score_ball = year_data.groupby(["batting_first"])["Total_Score_A"].sum().N
        except:
            num_score_ball = 0
        try:
            num_wickets_bat = year_data.groupby(["batting_first"])["Total_Wicket_A"].sum().Y
        except:
            num_wickets_bat = 0
        try: 
            num_wickets_ball = year_data.groupby(["batting_first"])["Total_Wicket_A"].sum().N    
        except:
            num_wickets_ball = 0
        total_matches = year_data['Total_Score_A'].size
        try: 
            total_matches_bat = year_data.batting_first.value_counts().Y
        except:
            total_matches_bat = 0
        try: 
            total_matches_ball = year_data.batting_first.value_counts().N
        except:
            total_matches_ball = 0
        try:
            avg_score_bat = np.round((num_score_bat/total_matches_bat),2)
        except:
            avg_score_bat = 0
        try:
            avg_wickets_bat = np.round(num_wickets_bat/total_matches_bat, 2)
        except:
            avg_wickets_bat = 0
        try:
            avg_score_ball = np.round((num_score_ball/total_matches_ball),2)
        except:
            avg_score_ball = 0
        try:
            avg_wickets_ball = np.round(num_wickets_ball/total_matches_ball,2)
        except:
            avg_wickets_ball = 0
        avg_score_record.append((year_ref, np.round((num_score_total/total_matches),2), np.round(num_wickets_total/total_matches, 2), avg_score_bat, avg_wickets_bat, avg_score_ball, avg_wickets_ball))
        num_matches.append(f"{year_ref} ({total_matches})")
        num_matches_ball.append(f"{year_ref} ({total_matches_ball})")
        num_matches_bat.append(f"{year_ref} ({total_matches_bat})")
    avg_score_df = pd.DataFrame.from_records(avg_score_record, columns=["year", "score_total", "wickets_total", "score_bat", "wickets_bat", "score_ball", "wickets_ball"])
    avg_score_df = avg_score_df.set_index("year")

    set_index = list(avg_score_df.index)
    set_labels_total = list((zip(set_index, list(avg_score_df.iloc[:,0]))))
    set_labels_bat = list((zip(set_index, list(avg_score_df.iloc[:,2]))))
    set_labels_ball = list((zip(set_index, list(avg_score_df.iloc[:,4]))))

    n=len(years)
    r = np.arange(n)
    
    fig, ax = plt.subplots(nrows=2, ncols=1, figsize = (10,10))

    ax[0].plot(r, avg_score_df.iloc[:,0], color = 'b')
    if team_2 == "All":
        ax[0].set_title("Avg. runs scored across all T20 matches since 2016: "+str(team_1), loc='center')
    else:
        ax[0].set_title("Avg. runs scored against "+str(team_2)+" in all T20I matches since 2016: "+str(team_1), loc='center')
    ax[0].set_ylabel('Avg. runs scored')
    ax[0].set_xticks([]) 
    ax[0].set_xticklabels([])

    ax[1].bar(r, avg_score_df.iloc[:,1], color = 'g')
    if team_2 == "All":
        ax[1].set_title('Avg. wickets conceded across all T20 matches since 2016: '+str(team_1), loc='center')
    else:
        ax[1].set_title('Avg. wickets conceded against '+str(team_2)+' in all T20I matches since 2016: '+str(team_1), loc='center')
    ax[1].set_xlabel('Year (Matches played)')
    ax[1].set_ylabel('Avg. wickets conceded')
    ax[1].set_xticks(r) 
    ax[1].set_xticklabels(num_matches)

    k = 0
    for i in set_labels_total:
            ax[0].text(r[k], i[1], str(i[1]), va='top', ha='center')
            k = k+1
    plt.savefig("Avg_runs_wickets_overall_"+str(team_1)+"_"+str(team_2)+".png")
    plt.show()

    fig, ax = plt.subplots(nrows=2, ncols=1, figsize = (10,10))

    ax[0].plot(r, avg_score_df.iloc[:,2], color = 'b')
    if team_2 == "All":
        ax[0].set_title('Avg. runs scored across all T20 matches batting first since 2016: '+str(team_1), loc='center')
    else:
        ax[0].set_title('Avg. runs scored against '+str(team_2)+' in all T20I matches batting first since 2016: '+str(team_1), loc='center')
    ax[0].set_ylabel('Avg. runs scored')
    ax[0].set_xticks([]) 
    ax[0].set_xticklabels([])

    ax[1].bar(r, avg_score_df.iloc[:,3], color = 'g')
    if team_2 == "All":
        ax[1].set_title('Avg. wickets conceded across all T20 matches batting first since 2016: '+str(team_1), loc='center')
    else:
        ax[1].set_title('Avg. wickets conceded against '+str(team_2)+' in all T20I matches batting first since 2016: '+str(team_1), loc='center')
    ax[1].set_xlabel('Years (Matches Played)')
    ax[1].set_ylabel('Avg. wickets conceded')
    ax[1].set_xticks(r) 
    ax[1].set_xticklabels(num_matches_bat)

    k = 0
    for i in set_labels_bat:
            ax[0].text(r[k], i[1], str(i[1]), va='top', ha='center')
            k = k+1
    plt.savefig("Avg_runs_wickets_bat_first_"+str(team_1)+"_"+str(team_2)+".png")
    plt.show()

    fig, ax = plt.subplots(nrows=2, ncols=1, figsize = (10,10))

    ax[0].plot(r, avg_score_df.iloc[:,4], color = 'b')
    if team_2 == "All":
        ax[0].set_title('Avg. runs scored across all T20 matches batting second since 2016: '+str(team_1), loc='center')
    else:
        ax[0].set_title('Avg. runs scored against '+str(team_2)+' in all T20I matches batting second since 2016: '+str(team_1), loc='center')
    ax[0].set_ylabel('Avg. runs scored')
    ax[0].set_xticks([]) 
    ax[0].set_xticklabels([])

    ax[1].bar(r, avg_score_df.iloc[:,5], color = 'g')
    if team_2 == "All":
        ax[1].set_title('Avg. wickets conceded across all T20 matches batting second since 2016: '+str(team_1), loc='center')
    else:
        ax[1].set_title('Avg. wickets conceded against '+str(team_2)+' in all T20I matches batting second since 2016: '+str(team_1), loc='center')
    ax[1].set_xlabel('Years (Matches Played)')
    ax[1].set_ylabel('Avg. wickets conceded')
    ax[1].set_xticks(r) 
    ax[1].set_xticklabels(num_matches_ball)

    k = 0
    for i in set_labels_ball:
            ax[0].text(r[k], i[1], str(i[1]), va='top', ha='center')
            k = k+1
    plt.savefig("Avg_runs_wickets_bat_second_"+str(team_1)+"_"+str(team_2)+".png")
    plt.show()

def make_plots_3(db, team_1, team_2 = "All"):
    """
    This function plots the average runs scored (in terms of over rate or runs scored per over in that phase) and average wickets conceded per phase of the match (for three scenarios - batting first, batting second, and overall) for any of the top 12 teams of T20WC 2022. 
    These plots can be generated either for all T20I matches against all other teams or against a particular team.  

    param db: Database ; pandas Dataframe
    param team_1: Team for which said metrics are to be plotted; str
    param team_2: Team against which said metrics are to be plotted; str; default value = all
    """

    assert isinstance(db, pd.DataFrame)
    assert isinstance(team_1, str)
    assert isinstance(team_2, str)

    super_12 = ["India", "Australia", "England", "Pakistan", "South Africa", "Bangladesh", "Afghanistan", "Sri Lanka", "Ireland", "Zimbabwe", "Netherlands", "New Zealand"]
    filter1 = db["team_A"].isin(super_12)
    filter2 = db["year"]>2015
    db = db[filter1 & filter2].reset_index()

    aus_stadiums = ['Sydney Cricket Ground', 'Brisbane Cricket Ground', 'Melbourne Cricket Ground', 'GMHBA Stadium', 'Perth Stadium', 'Manuka Oval', 'Bellerive Oval', 'Carrara Oval', 'Adelaide Oval']
    ref_db_phase_score = db.loc[:, ["id", "year", "updated_venue", "team_A", "team_B", "Runs_in_Powerplay", "Wickets_lost_in_Powerplay", "Runs_in_middle_overs", "Wickets_lost_in_middle_overs", "Runs_in_Death_overs", "Wickets_lost_in_death_overs"]]
    ref_db_phase_score["In_Australia"]=ref_db_phase_score["updated_venue"].isin(aus_stadiums)
    ref_db_phase_score = ref_db_phase_score.drop(["updated_venue"], axis = 1)

    batting_first = []

    for i in range(ref_db_phase_score.shape[0]):
        var_check = list(ref_db_phase_score["id"])[i][-1]
        batting_first.append("Y" if var_check == "A" else "N")

    ref_db_phase_score["batting_first"]=batting_first
    ref_db_phase_score = ref_db_phase_score.drop(columns=["id"])

    phase_score_record = []

    if team_2 == "All":
        country_data = ref_db_phase_score.loc[(ref_db_phase_score['team_A'] == team_1)]
    else:
        country_data = ref_db_phase_score.loc[(ref_db_phase_score['team_A'] == team_1)]
        country_data = country_data.loc[(country_data['team_B'] == team_2)]

    years = np.sort(list(country_data.year.unique()))
    num_matches = []
    num_matches_bat = []
    num_matches_ball = []

    for year_ref in years:

        year_data = country_data.loc[(country_data['year'] == year_ref)]

        try:
            num_score_P_overall = year_data["Runs_in_Powerplay"].sum()
        except:
            num_score_P_overall = 0
        try: 
            num_wickets_P_overall = year_data["Wickets_lost_in_Powerplay"].sum()
        except:
            num_wickets_P_overall = 0
        try: 
            num_score_M_overall = year_data["Runs_in_middle_overs"].sum()
        except:
            num_score_M_overall = 0
        try: 
            num_wickets_M_overall = year_data["Wickets_lost_in_middle_overs"].sum()
        except:
            num_wickets_M_overall = 0
        try: 
            num_score_D_overall = year_data["Runs_in_Death_overs"].sum()
        except:
            num_score_D_overall = 0
        try:
            num_wickets_D_overall = year_data["Wickets_lost_in_death_overs"].sum()
        except:
            num_wickets_D_overall = 0

        try:
            num_score_P_bat = year_data.groupby(["batting_first"])["Runs_in_Powerplay"].sum().Y
        except:
            num_score_P_bat = 0
        try:
            num_score_M_bat = year_data.groupby(["batting_first"])["Runs_in_middle_overs"].sum().Y
        except:
            num_score_M_bat = 0
        try:
            num_score_D_bat = year_data.groupby(["batting_first"])["Runs_in_Death_overs"].sum().Y
        except:
            num_score_D_bat = 0
        try:
            num_wickets_P_bat = year_data.groupby(["batting_first"])["Wickets_lost_in_Powerplay"].sum().Y
        except:
            num_wickets_P_bat = 0
        try: 
            num_wickets_M_bat = year_data.groupby(["batting_first"])["Wickets_lost_in_middle_overs"].sum().Y
        except:
            num_wickets_M_bat = 0    
        try: 
            num_wickets_D_bat = year_data.groupby(["batting_first"])["Wickets_lost_in_death_overs"].sum().Y    
        except:
            num_wickets_D_bat = 0

        try:
            num_score_P_ball = year_data.groupby(["batting_first"])["Runs_in_Powerplay"].sum().N
        except:
            num_score_P_ball = 0
        try: 
            num_score_M_ball = year_data.groupby(["batting_first"])["Runs_in_middle_overs"].sum().N
        except:
            num_score_M_ball =  0
        try: 
            num_score_D_ball = year_data.groupby(["batting_first"])["Runs_in_Death_overs"].sum().N
        except:
            num_score_D_ball = 0
        try:
            num_wickets_P_ball = year_data.groupby(["batting_first"])["Wickets_lost_in_Powerplay"].sum().N
        except:
            num_wickets_P_ball = 0
        try: 
            num_wickets_M_ball = year_data.groupby(["batting_first"])["Wickets_lost_in_middle_overs"].sum().N
        except:
            num_wickets_M_ball = 0
        try:
            num_wickets_D_ball = year_data.groupby(["batting_first"])["Wickets_lost_in_death_overs"].sum().N
        except:
            num_wickets_D_ball = 0

        total_matches_overall = year_data['Runs_in_Powerplay'].size
        try:
            total_matches_bat = year_data.batting_first.value_counts().Y
        except:
            total_matches_bat = 0
        try: 
            total_matches_ball = year_data.batting_first.value_counts().N
        except:
            total_matches_ball = 0

        try: 
            avg_runs_P_overall = np.round((num_score_P_overall/(6*total_matches_overall)),2)
        except:
            avg_runs_P_overall = 0
        try: 
            avg_wickets_P_overall = np.round((num_wickets_P_overall/total_matches_overall),2)
        except:
            avg_wickets_P_overall = 0
        try: 
            avg_runs_M_overall = np.round((num_score_M_overall/(total_matches_overall*10)),2)
        except:
            avg_runs_M_overall = 0
        try: 
            avg_wickets_M_overall = np.round((num_wickets_M_overall/total_matches_overall),2)
        except:
            avg_wickets_M_overall = 0
        try: 
            avg_runs_D_overall = np.round((num_score_D_overall/(4*total_matches_overall)),2)
        except:
            avg_runs_D_overall = 0
        try: 
            avg_wickets_D_overall = np.round((num_wickets_D_overall/total_matches_overall),2)
        except:
            avg_wickets_D_overall = 0

        try: 
            avg_runs_P_bat = np.round((num_score_P_bat/(6*total_matches_bat)),2)
        except:
            avg_runs_P_bat = 0
        try: 
            avg_wickets_P_bat = np.round((num_wickets_P_bat/total_matches_bat),2)
        except:
            avg_wickets_P_bat = 0
        try: 
            avg_runs_M_bat = np.round((num_score_M_bat/(10*total_matches_bat)),2)
        except:
            avg_runs_M_bat = 0
        try: 
            avg_wickets_M_bat = np.round((num_wickets_M_bat/total_matches_bat),2)
        except:
            avg_wickets_M_bat = 0
        try: 
            avg_runs_D_bat = np.round((num_score_D_bat/(4*total_matches_bat)),2)
        except:
            avg_runs_D_bat = 0
        try: 
            avg_wickets_D_bat = np.round((num_wickets_D_bat/total_matches_bat),2)
        except:
            avg_wickets_D_bat = 0

        try: 
            avg_runs_P_ball = np.round((num_score_P_ball/(6*total_matches_ball)),2)
        except:
            avg_runs_P_ball = 0
        try: 
            avg_wickets_P_ball = np.round((num_wickets_P_ball/total_matches_ball),2)
        except:
            avg_wickets_P_ball = 0
        try: 
            avg_runs_M_ball = np.round((num_score_M_ball/(10*total_matches_ball)),2)
        except:
            avg_runs_M_ball = 0
        try: 
            avg_wickets_M_ball = np.round((num_wickets_M_ball/total_matches_ball),2)
        except:
            avg_wickets_M_ball = 0
        try: 
            avg_runs_D_ball = np.round((num_score_D_ball/(4*total_matches_ball)),2)
        except:
            avg_runs_D_ball = 0
        try: 
            avg_wickets_D_ball = np.round((num_wickets_D_ball/total_matches_ball),2)
        except:
            avg_wickets_D_ball = 0

        phase_score_record.append((year_ref, avg_runs_P_overall, avg_wickets_P_overall, avg_runs_M_overall, avg_wickets_M_overall, avg_runs_D_overall, avg_wickets_D_overall, avg_runs_P_bat, avg_wickets_P_bat, avg_runs_M_bat, avg_wickets_M_bat, avg_runs_D_bat, avg_wickets_D_bat, avg_runs_P_ball, avg_wickets_P_ball, avg_runs_M_ball, avg_wickets_M_ball, avg_runs_D_ball, avg_wickets_D_ball))
        num_matches.append(f"{year_ref} ({total_matches_overall})")
        num_matches_bat.append(f"{year_ref} ({total_matches_bat})")
        num_matches_ball.append(f"{year_ref} ({total_matches_ball})")
    phase_score_df = pd.DataFrame.from_records(phase_score_record, columns=["year", "avg_score_P_overall", "avg_wickets_P_overall", "avg_score_M_overall", "avg_wickets_M_overall", "avg_score_D_overall", "avg_wickets_D_overall", "avg_score_P_bat", "avg_wickets_P_bat", "avg_score_M_bat", "avg_wickets_M_bat", "avg_score_D_bat", "avg_wickets_D_bat", "avg_score_P_ball", "avg_wickets_P_ball", "avg_score_M_ball", "avg_wickets_M_ball", "avg_score_D_ball", "avg_wickets_D_ball"])
    phase_score_df = phase_score_df.set_index("year")

    n=len(years)
    r = np.arange(n)
    width = 0.25

    fig, ax = plt.subplots(nrows=2, ncols=1, figsize = (10,10))

    ax[0].bar(r, phase_score_df.iloc[:,0], width=width, label = 'Powerplay', color = 'tab:blue')
    ax[0].bar(r+width, phase_score_df.iloc[:,2], width=width, label = 'Middle Overs', color = 'tab:green')
    ax[0].bar(r+(2*width), phase_score_df.iloc[:,4], width=width, label = 'Death Overs', color = 'tab:red')
    if team_2 == "All":
        ax[0].set_title('Phase wise breakdown of avg. runs per over scored across all T20 matches since 2016: '+str(team_1), loc='center')
    else:
        ax[0].set_title('Phase wise breakdown of avg. runs per over scored against '+str(team_2)+' in all T20I matches since 2016: '+str(team_1), loc='center')
    ax[0].set_ylabel('Avg. runrate per over')
    ax[0].set_xticks([]) 
    ax[0].set_xticklabels([])
    ax[0].legend(loc = 'best')

    ax[1].bar(r, phase_score_df.iloc[:,1], width=width, label = 'Powerplay', color = 'tab:blue')
    ax[1].bar(r+width, phase_score_df.iloc[:,3], width=width, label = 'Middle Overs', color = 'tab:green')
    ax[1].bar(r+(2*width), phase_score_df.iloc[:,5], width=width, label = 'Death Overs', color = 'tab:red')
    if team_2 == "All":
        ax[1].set_title('Phase wise breakdown of avg. wickets conceded across all T20 matches since 2016: '+str(team_1), loc='center')
    else:
        ax[1].set_title('Phase wise breakdown of avg. wickets conceded against '+str(team_2)+' in all T20I matches since 2016: '+str(team_1), loc='center')
    ax[1].set_xlabel('Year (Matches Played)')
    ax[1].set_ylabel('Avg. wickets conceded')
    ax[1].set_xticks(r+width)
    ax[1].set_xticklabels(num_matches)
    ax[1].legend(loc = 'best')

    plt.savefig("Phases_runs_wickets_overall_"+str(team_1)+"_"+str(team_2)+".png")
    plt.show()

    fig, ax = plt.subplots(nrows=2, ncols=1, figsize = (10,10))

    ax[0].bar(r, phase_score_df.iloc[:,6], width=width, label = 'Powerplay', color = 'tab:blue')
    ax[0].bar(r+width, phase_score_df.iloc[:,8], width=width, label = 'Middle Overs', color = 'tab:green')
    ax[0].bar(r+(2*width), phase_score_df.iloc[:,10], width=width, label = 'Death Overs', color = 'tab:red')
    if team_2 == "All":
        ax[0].set_title('Phase wise breakdown of avg. runs per over scored across all T20 matches batting first since 2016: '+str(team_1), loc='center')
    else:
        ax[0].set_title('Phase wise breakdown of avg. runs per over scored against '+str(team_2)+' in all T20I matches batting first since 2016: '+str(team_1), loc='center')
    ax[0].set_ylabel('Avg. runrate per over')
    ax[0].set_xticks([]) 
    ax[0].set_xticklabels([])
    ax[0].legend(loc = 'best')

    ax[1].bar(r, phase_score_df.iloc[:,7], width=width, label = 'Powerplay', color = 'tab:blue')
    ax[1].bar(r+width, phase_score_df.iloc[:,9], width=width, label = 'Middle Overs', color = 'tab:green')
    ax[1].bar(r+(2*width), phase_score_df.iloc[:,11], width=width, label = 'Death Overs', color = 'tab:red')
    if team_2 == "All":
        ax[1].set_title('Phase wise breakdown of avg. wickets conceded across all T20 matches batting first since 2016: '+str(team_1), loc='center')
    else:
        ax[1].set_title('Phase wise breakdown of avg. wickets conceded against '+str(team_2)+' in all T20I matches batting first since 2016: '+str(team_1), loc='center')
    ax[1].set_xlabel('Year (Matches Played)')
    ax[1].set_ylabel('Avg. wickets conceded')
    ax[1].set_xticks(r+width)
    ax[1].set_xticklabels(num_matches_bat)
    ax[1].legend(loc = 'best')

    plt.savefig("Phases_runs_wickets_bat_first_"+str(team_1)+"_"+str(team_2)+".png")
    plt.show()

    fig, ax = plt.subplots(nrows=2, ncols=1, figsize = (10,10))

    ax[0].bar(r, phase_score_df.iloc[:,12], width=width, label = 'Powerplay', color = 'tab:blue')
    ax[0].bar(r+width, phase_score_df.iloc[:,14], width=width, label = 'Middle Overs', color = 'tab:green')
    ax[0].bar(r+(2*width), phase_score_df.iloc[:,16], width=width, label = 'Death Overs', color = 'tab:red')
    if team_2 == "All":
        ax[0].set_title('Phase wise breakdown of avg. runs per over scored across all T20 matches batting second since 2016: '+str(team_1), loc='center')
    else:
        ax[0].set_title('Phase wise breakdown of avg. runs per over scored against '+str(team_2)+' in all T20I matches batting second since 2016: '+str(team_1), loc='center')
    ax[0].set_ylabel('Avg. runrate per over')
    ax[0].set_xticks([]) 
    ax[0].set_xticklabels([])
    ax[0].legend(loc = 'best')

    ax[1].bar(r, phase_score_df.iloc[:,13], width=width, label = 'Powerplay', color = 'tab:blue')
    ax[1].bar(r+width, phase_score_df.iloc[:,15], width=width, label = 'Middle Overs', color = 'tab:green')
    ax[1].bar(r+(2*width), phase_score_df.iloc[:,17], width=width, label = 'Death Overs', color = 'tab:red')
    if team_2 == "All":
        ax[1].set_title('Phase wise breakdown of avg. wickets conceded across all T20 matches batting second since 2016: '+str(team_1), loc='center')
    else:
        ax[1].set_title('Phase wise breakdown of avg. wickets conceded against '+str(team_2)+' in all T20I matches batting second since 2016: '+str(team_1), loc='center')
    ax[1].set_xlabel('Year (Matches Played)')
    ax[1].set_ylabel('Avg. wickets conceded')
    ax[1].set_xticks(r+width)
    ax[1].set_xticklabels(num_matches_ball)
    ax[1].legend(loc = 'best')

    plt.savefig("Phases_runs_wickets_bat_second_"+str(team_1)+"_"+str(team_2)+".png")
    plt.show()
