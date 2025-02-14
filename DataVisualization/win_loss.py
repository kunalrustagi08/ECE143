import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def winloss(full_data: pd.DataFrame):
    """
    function to extract useful data for win-loss record and create corresponding visualization 
    :params:
        - full_data: complete database
    
    :returns:
        plots win-loss percentage for all countries from 2016 sorted by win percent

    """
    assert isinstance(full_data, pd.DataFrame)

    data = full_data[['year', 'team_A', 'team_B', 'winner', 'toss_winner', 'toss_decision']]
    data = data[data['year'] >= 2016]
    wc_countries = ["New Zealand","England","Australia","Sri Lanka","Ireland","Afghanistan","India","Pakistan","South Africa","Netherlands","Bangladesh","Zimbabwe"]
    win_loss_records = []
    for country in wc_countries:
        country_data = data.loc[(data['team_A'] == country)]
        num_wins = sum(country_data['winner'] == country)
        total_matches = country_data['winner'].size
        win_loss_records.append((total_matches, num_wins, country))
    win_loss_records.sort(key=lambda x:x[1]/x[0], reverse=True)
    win_loss_df = pd.DataFrame.from_records(win_loss_records, columns=['total_matches', "num_wins", "country"])
    
    f, ax = plt.subplots(figsize=(12, 6))

    sns.set_color_codes("muted")
    sns.barplot(x="total_matches", y="country", data=win_loss_df,label="Loss", color="r")
    sns.barplot(x="num_wins", y="country", data=win_loss_df,label="Wins", color="g")

    # for adding the win percent text
    for i in range(len(wc_countries), 2*len(wc_countries)):
        total, win, _ = win_loss_records[i-len(wc_countries)]
        win_percent = 100* win / total
        p = ax.patches[i]
        width = p.get_width()
        ax.text(width+1, p.get_y() + p.get_height()/ 2, f'{win_percent:.2f}%', ha='left', va='center', fontsize=12)

    ax.legend(ncol=2, loc="lower right", frameon=True)
    ax.set(ylabel="Country",xlabel="Number of matches played")
    plt.title('Country wise Win-Loss Record')
    sns.despine(left=True, bottom=True)
    plt.show()


if __name__ == "__main__":
    BASE_PATH = os.getcwd()
    DATABASE_PATH = os.path.join(BASE_PATH, "DataProcessing", "result_post_step.csv")
    database = pd.read_csv(DATABASE_PATH)
    winloss(database)