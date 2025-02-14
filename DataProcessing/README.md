## Data Processing

### Description

    The preprocessing file takes an input directory path to the Raw data directory which contains
    the data for each match played and an output path to store the processed data in. This can be 
    seen in the Results.csv file.

    Some manual processing via google and excel is required to check for cities and/or stadiums 
    that were renamed. The results of this processing can be seen in the results_post_step.csv file 
### Resultant processed fields 
    
    id,
    year,
    venue,
    team_A,
    team_B,
    Runs_in_Powerplay,
    Wickets_lost_in_Powerplay,
    Runs_in_middle_overs,
    Wickets_lost_in_middle_overs,
    Runs_in_Death_overs,
    Wickets_lost_in_death_overs,
    Total_Score_A,
    Total_Wicket_A,
    toss_winner,
    toss_decision,
    city,
    winner,
    event,
    match_id,
    innings_number
    

### Requirements 
    - Raw cricsheet data stored in directory
    - pandas module
    - os module

### Usage example
    
    Running this code inside the repository stucture should require nothing more than 
    running the pre_process_data.py file.

    For running the code as a module follow the example code in the if __main__: section 
    found at the bottom of pre_process_data.py

### Useful resource links

- [pandas](https://pandas.pydata.org/pandas-docs/stable/reference/index.html)
