import pandas as pd
import os
import seaborn as sns
import numpy as np

import matplotlib.pyplot as plt

def seperate_wc(df:pd.DataFrame):
    """
    Function to seperate the world cup matches from complete dataset
    :params:
        - df: complete datafram
    
    :returns:
        Dataframe that only has information about matches played during this year's world cup
    """

    assert isinstance(df, pd.DataFrame)

    wc_df = df[(df['event'] == "ICC Men's T20 World Cup") & (df['year'] == 2022) & (df['id'] >= '1298147A')].reset_index()
    return wc_df

def average_inng_total(df, innings_number='A'):
    """
    function to find the average innings score for all the teams
    :param:
        - df: complete datafram
        - innings_number: "A" for first innings and "B" for second innings
    
    :returns:
        Dataframe with average 1st/2nd innings score for each team
    """

    assert isinstance(df, pd.DataFrame)
    assert (innings_number == "A") or (innings_number == "B")
    innings_scores = df[df['innings_number'] == innings_number]
    innings_scores = innings_scores[['team_A', 'Total_Score_A']]
    avg_inn_score = innings_scores.groupby('team_A').mean().reset_index()
    avg_inn_score.rename(columns={"team_A": "Team Name"}, inplace=True)
    # avg_inn_score = avg_inn_score.sort_values(by="Total_Score_A", axis=0, ascending=False)
    if innings_number == "A":
        avg_inn_score['innings_number'] = "First"
    else:
        avg_inn_score['innings_number'] = "Second"
    return avg_inn_score


def plot_avg_scores(avg_inn_score):
    """
    function to plot average innings score of both innings for each team
    :param:
        - avg_inn_score: Dataframe that contains average score for all teams segregated into 2 innings using innings_number column
        an example input is shown below
        ---------------------------------------------------------
        |   Team Name   |   Total_Score_A   |   innings_number  |
        ---------------------------------------------------------
        |   India       |   100             |   "First"         |
        |   Australia   |   150             |   "Second"        |
            .
            .
    """

    assert isinstance(avg_inn_score, pd.DataFrame)

    f, ax = plt.subplots(figsize=(12, 6))
    sns.set_color_codes("pastel")
    sns.barplot(x="Total_Score_A", y=f"Team Name", data=avg_inn_score, hue='innings_number')

    # for adding the win percent text
    for i in range(12):
        p1 = ax.patches[i]
        p2 = ax.patches[i+12]
        f_avg = np.round(avg_inn_score.iloc[i].Total_Score_A, 2)
        s_avg = np.round(avg_inn_score.iloc[i+12].Total_Score_A, 2)
        ax.text(p1.get_width()+0.15, p1.get_y() + p1.get_height()/ 2, f_avg, ha='left', va='center', fontsize=10)
        ax.text(p2.get_width()+0.15, p2.get_y() + p2.get_height()/ 2, s_avg, ha='left', va='center', fontsize=10)

    plt.xlabel("Average Score")
    plt.title("Average First and Second Innings scores by different teams during WC")
    # SAVE_PATH = os.path.join(os.getcwd(), 'DataVisualization', 'plots', 'avg_wc_scores.png')
    # plt.show()
    # plt.savefig("avg_wc_scores.png")
    return


def win_loss_inn_wise(wc_df):
    """
    function to find the win loss percentage (segregated by innings) for all teams for matches during the world cup
    :param:
        - wc_df: dataframe having matches from world cup only
    
    :returns:
        2 Dataframes (one for batting first and one for bowling first) 
        with team Name, win percent, number of wins and total matches played colunms
    """

    assert isinstance(wc_df, pd.DataFrame)

    batting_first_wins = wc_df[(wc_df['innings_number'] == 'A') & (wc_df['team_A'] == wc_df['winner'])]
    batting_first_wins_team_wise = batting_first_wins[['team_A', 'id']].groupby('team_A').count().reset_index()
    total_batting_first = wc_df[(wc_df['innings_number'] == 'A')]
    total_batting_first_team_wise = total_batting_first[['team_A', 'id']].groupby('team_A').count().reset_index()
    merged_data = pd.merge(left = batting_first_wins_team_wise, right=total_batting_first_team_wise, how="outer", on="team_A")
    merged_data['win_percent'] = merged_data['id_x'] / merged_data['id_y']
    
    bowling_first_wins = wc_df[(wc_df['innings_number'] == 'A') & (wc_df['team_B'] == wc_df['winner'])]
    bowling_first_wins_team_wise = bowling_first_wins[['team_B', 'id']].groupby('team_B').count().reset_index()
    total_bowling_first = wc_df[(wc_df['innings_number'] == 'A')]
    total_bowling_first_team_wise = total_bowling_first[['team_B', 'id']].groupby('team_B').count().reset_index()
    merged_data2 = pd.merge(left = bowling_first_wins_team_wise, right=total_bowling_first_team_wise, how="outer", on="team_B")
    merged_data2['win_percent'] = merged_data2['id_x'] / merged_data2['id_y']
    return merged_data, merged_data2


def win_loss_compare(wc_df):
    """
    function to find the win loss percentage for all teams for matches during the world cup
    :param:
        - wc_df: dataframe having matches from world cup only
    
    :returns:
        Dataframe with team Name, win percent, number of wins and total matches played colunms
    """

    assert isinstance(wc_df, pd.DataFrame)

    wc_df['teamA_winner'] = (wc_df['team_A'] == wc_df['winner'])
    wins = wc_df[['team_A', 'teamA_winner']].groupby('team_A').sum().reset_index()
    total = wc_df[['team_A', 'teamA_winner']].groupby('team_A').count().reset_index()
    merged_df = pd.merge(left=wins, right=total, how='inner', on='team_A')
    merged_df = merged_df.sort_values(by="teamA_winner_x", axis=0, ascending=False, ignore_index=True)
    merged_df['win_percent'] = merged_df['teamA_winner_x'] / merged_df['teamA_winner_y']

    f, ax = plt.subplots(figsize=(12, 6))
    sns.set_color_codes("pastel")
    sns.barplot(x="teamA_winner_y", y="team_A", data=merged_df, color='r', label="Loss")
    sns.barplot(x="teamA_winner_x", y="team_A", data=merged_df, color='g', label="wins")
    # for adding the win percent text
    for i in range(12):
        win_percent = 100 * merged_df['win_percent'][i] 
        p = ax.patches[i+12]
        width = p.get_width()
        ax.text(width+0.15, p.get_y() + p.get_height()/ 2, f'{win_percent:.2f}%', ha='left', va='center', fontsize=12)
    ax.set(ylabel="Country",xlabel="Number of matches played")
    ax.legend(ncol=2, loc="lower right", frameon=True)
    plt.title('Country wise Win-Loss Record for WC')
    # SAVE_PATH = os.path.join(os.getcwd(), 'DataVisualization', 'plots', 'wc_win_loss.png')
    # plt.show()
    # plt.savefig("wc_win_loss.png")

if __name__ == "__main__":
    BASE_PATH = os.getcwd()
    DATABASE_PATH = os.path.join(BASE_PATH, "DataProcessing", "result_post_step.csv")
    df = pd.read_csv(DATABASE_PATH)
    wc_df = seperate_wc(df)
    avg_inn1_score = average_inng_total(wc_df, 'A')
    avg_inn2_score = average_inng_total(wc_df, 'B')
    avg_inn_score = pd.concat([avg_inn1_score, avg_inn2_score], ignore_index=True)
    # b1, b2 = win_loss_inn_wise(wc_df)
    # print(b1, b2, sep="\n\n")
    plot_avg_scores(avg_inn_score)
    win_loss_compare(wc_df)
    plt.show()