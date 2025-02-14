# Data Visualization README
## Table of contents
1. [Performances using ground averages](#groundavg)
2. [Strengths and weakness insights using win loss analysis](#plots123)
3. [World Cup win loss and average Analysis](#wcstats)
4. [Win Loss Analysis](#winloss)


### ground_averages.py<a name=groundavg></a>

#### Description

This file contains 3 functions which compute the following metrics in various conditions as well as specific customisations, as described below:

* Function ground_averages -> prepares the data to find the ground average for all stadiums for every year from 2016-2022 for all T20I matches played:
    * First innings and second innings batting score
    * First innings and second innings wickets lost

* Function batting_bowling_performances -> computes the batting and bowling performance for both the teams playing a match in all T20s played between 2016-2022 based on:
    * A team scores higher than the ground averages (batting first) or scores enough to win the game (batting second)
    * A team holds the opposing team under the ground average (bowling first) or limits the batting team enough to win the game (bowling second)

* Function create_team_visualizations -> computes the win percentage graphs split by batting, bowling and both performances contributing to a win for the final 4 teams in the T20 WC 2022 against the other teams participating in the WC

* Function world_map_visualization -> using the average score innings for a stadium, we plot a world heatmap for ground averages in a particular country in all T20s played between 2016-2022

#### Input-output

**def ground_averages(db)** 

Input : 
param db: Database ; pandas Dataframe

Output:
param avg_db: Database ; pandas Dataframe
param db: Database ; pandas Dataframe

**def batting_bowling_performances(avg_db, utd_db)** 

Input : 
param avg_db: Database ; pandas Dataframe
param utd_db: Database ; pandas Dataframe

Output:
param ds: Database ; pandas Dataframe

**def create_team_visualizations(ds)** 

Input : 
param ds: Database ; pandas Dataframe

Output:
![](plots/England_vs_other_teams.png)
![](plots/India_vs_other_teams.png)
![](plots/New_Zealand_vs_other_teams.png)
![](plots/Pakistan_vs_other_teams.png)

**def world_map_visualization(avg_db)** 

Input : 
param avg_db: Database ; pandas Dataframe

Output:
![](plots/world_map_for_ground_averages.jpg)

#### Requirements

Follow the instructions mentioned under "Requirements" and "Running Code" in the Readme file on the root directory page. You can also refer to the Jupyter notebook at https://github.com/jvolheim/ECE-143/blob/main/DataVisualization/ECE143_Group_15.ipynb, to understand how to run the visualisation files for plots. 

### plots_1_2_3.py<a name=plots123></a>

#### Description

This file contains 3 functions which compute the following metrics in various conditions as well as specific customisations, as described below:

* Function make_plots_1 -> computes the win-loss % for a team for every year from 2016-2022 for 3 conditions:
    * across all T20I matches played since 2016
    * across all T20I matches in which the team batted first since 2016
    * across all T20I matches in which the team batted second since 2016
    
    You can choose to compute this metric for a team against all opponents in this time frame, or against a specific opponent in this time frame, by mentioning the specific argument
    
* Function make_plots_2 -> computes the average runs scored and wickets conceded for a team for every year from 2016-2022 for 3 conditions:
    * across all T20I matches played since 2016
    * across all T20I matches in which the team batted first since 2016
    * across all T20I matches in which the team batted second since 2016
    
    You can choose to compute this metric for a team against all opponents in this time frame, or against a specific opponent in this time frame, by mentioning the specific argument
    
* Function make_plots_3 -> computes the average runs scored and wickets conceded in every phase of the match for a team for every year from 2016-2022 for 3 conditions:
    * across all T20I matches played since 2016
    * across all T20I matches in which the team batted first since 2016
    * across all T20I matches in which the team batted second since 2016
    
    You can choose to compute this metric for a team against all opponents in this time frame, or against a specific opponent in this time frame, by mentioning the specific argument
    
#### Input-output

**def make_plots_1(db, team_1, team_2 = "All")** 

Input : 
param db: Database ; pandas Dataframe
param team_1: Team for which win-loss is to be calculated; str
param team_2: Team against which win-loss is to be calculated; str; default value = all

Output:

India against all oppositions
![image](https://user-images.githubusercontent.com/64548290/205230518-472b1602-9d87-4ecd-b599-ffd30f12736d.png)

India against England
![image](https://user-images.githubusercontent.com/64548290/205231512-7d91d328-cf29-4166-b697-d3ce552ce0d8.png)

**def make_plots_2(db, team_1, team_2 = "All")**

Input : 
param db: Database ; pandas Dataframe
param team_1: Team for which the metrics are to be calculated; str
param team_2: Team against which the metrics are to be calculated; str; default value = all

Output:

India against all oppositions
![](plots/Avg_runs_wickets_overall_India_All.png)
![](plots/Avg_runs_wickets_bat_first_India_All.png)
![](plots/Avg_runs_wickets_bat_second_India_All.png)

India against England
![](plots/Avg_runs_wickets_overall_India_England.png)
![](plots/Avg_runs_wickets_bat_first_India_England.png)
![](plots/Avg_runs_wickets_bat_second_India_England.png)

**def make_plots_3(db, team_1, team_2 = "All")**

Input : 
param db: Database ; pandas Dataframe
param team_1: Team for which the metrics are to be calculated; str
param team_2: Team against which the metrics are to be calculated; str; default value = all

Output:

India against all oppositions
![](plots/Phases_runs_wickets_overall_India_All.png)
![](plots/Phases_runs_wickets_bat_first_India_All.png)
![](plots/Phases_runs_wickets_bat_second_India_All.png)

India against England
![](plots/Phases_runs_wickets_overall_India_England.png)
![](plots/Phases_runs_wickets_bat_first_India_England.png)
![](plots/Phases_runs_wickets_bat_second_India_England.png)

#### Requirements

Follow the instructions mentioned under "Requirements" and "Running Code" in the Readme file on the root directory page. You can also refer to the Jupyter notebook at https://github.com/jvolheim/ECE-143/blob/main/DataVisualization/ECE143_Group_15.ipynb, to understand how to run the visualisation files for plots. 

### wc_stats.py <a name=wcstats></a>

This file is used to analyse the performance of teams during the world cup. Different functions are:
1. seperate_wc()  
This function seperates the world cup matches related data from complete data

2. average_inng_total()  
This function is to find average innings score for each team for a particular innings. Innings number can be passed as parameter.

3. plot_avg_scores()  
This function plots the average score of both innings for all teams into stacked horizontal bar chart

4. win_loss_inn_wise()    
This functions returns team wise statistics for world cup (matches played, wins, win percent)


5. win_loss_compare()  
This function analyses win loss percentage for world cup playing teams and plots them. Since the data was quite small (maximum 7 matches per team, we decided to skip this plot in the presentation)


#### Running this file
Please run this file from the root directory using 
```
python .\DataVisualization\wc_stats.py
```


#### Plots
![world_cup_average_scores](plots/avg_wc_scores.png)
![world-cup win loss percentage](plots/wc_win_loss.png)


### win_loss.py <a name=winloss></a>

This file just has a single function winloss() that takes in complete data and plots wins and losses for each team and also prints out win percent. 

#### Running this file
Please run this file from the root directory using following command. 
```
python .\DataVisualization\winloss.py
```

#### Plots
![overall win loss percentage](plots/win-loss.png)
