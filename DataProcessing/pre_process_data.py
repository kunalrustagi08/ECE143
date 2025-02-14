import pandas as pd
import os


def run_wickets(df, over):
    '''
    # calculate score for each over based on runs, extras and innings
    :param df:  full dataframe
    :param over: descriptor of [1,2,3] representing power, middle, and death overs
    :return: (sum of runs + sum of extras, sum of wickets) for designated over
    '''
    # load ball data to parse dataframe on ie1==[0,6.1) 2 == [6.1,16.1) 3 == [16.1,end)
    field = df['ball']

    # switch on over
    if over == 1:
        # find index of all balls indexes less than 6.1
        A = field[field < 6.1].index.tolist()
        # remove all balls of above index from ball column leaving (balls >= 6.1)
        field = field.drop(index=A)

    elif over == 2:

        # find index of all balls over 16.1
        A = field[field < 16.1].index.tolist()
        B = set(A) - set(field[field < 6.1].index.tolist())

        # remove all balls of above index from ball column leaving (balls >= 16.1 and balls < 6.1)
        field = field.drop(index=B)

    else:
        # find index of all balls over 16.1
        A = field[field >= 16.1].index.tolist()
        # remove all balls of above index from ball column leaving (balls < 16.1)
        field = field.drop(index=A)

    # All remaining balls in the field are outside the over so find index of them
    A = field[field > 0].index.tolist()

    # load wicket, run and extra data from dataframe
    wick = df['wicket_type']
    run = df['runs_off_bat']
    ex = df['extras']

    # Use indexes based on "A" to remove values from wicket, run and extra data
    wick = wick.drop(index=A).astype(str)
    wick = wick.apply(lambda x: len(x) > 3) * 1  # convert text to int
    run = run.drop(index=A)
    ex = ex.drop(index=A)

    # find sum of all values in each remaining column
    w = wick.sum()
    r = run.sum()
    e = ex.sum()

    # return sum of runs and extras if first column and sum of wickets in second column
    return [[r + e], [w]]


def inning(dataf, half_value):
    '''
    pull data for each inning of the game
    :param dataf: full dataframe
    :param half_value: which inning of the game we are looking at
    :return:
    '''
    # pull inning data
    field = dataf["innings"]
    # find index of the inning data based on first or second inning of game
    A = field[field != half_value].index.tolist()
    # drop data from opposite inning
    df = dataf.drop(index=A)
    # reset index
    df = df.reset_index()
    # initiate dictionary to hold result
    result = {}

    # load data into results dictionary
    result['team_A'] = [df["batting_team"][0]]
    result['team_B'] = [df["bowling_team"][0]]
    result['Runs_in_Powerplay'], result['Wickets_lost_in_Powerplay'] = run_wickets(df, 1)
    result['Runs_in_middle_overs'], result['Wickets_lost_in_middle_overs'] = run_wickets(df, 2)
    result['Runs_in_Death_overs'], result['Wickets_lost_in_death_overs'] = run_wickets(df, 3)

    # add all overs score to calculate total score and wickets
    result['Total_Score_A'] = int(result['Runs_in_Powerplay'][0]) + \
                              int(result['Runs_in_middle_overs'][0]) + \
                              int(result['Runs_in_Death_overs'][0])

    result['Total_Wicket_A'] = int(result['Wickets_lost_in_Powerplay'][0]) + \
                               int(result['Wickets_lost_in_middle_overs'][0]) + \
                               int(result['Wickets_lost_in_death_overs'][0])

    # return result dictionary
    return result


def id_info_csv(path):
    '''
    Function takes and processes the data for the info.csv format data
    :param path: should be valid path to file
    :return: toss_winner, toss_decision, city, winner
    '''
    assert isinstance(path, str)  # check for valid type input
    # initialize return variable
    result = {}

    try:
        # read data as Length x 1 each row being stored as string in 1 column
        dataframe = pd.read_csv(path, delimiter='\r')
        # split loaded dataframe by comma into list
        s = dataframe.squeeze().str.split(',')
        # Shrink Series to column of fields
        field = s.apply(lambda x: x[1])

        # pull required data index's
        winnerid = field[field == 'toss_winner'].index.tolist()
        decisionid = field[field == 'toss_decision'].index.tolist()
        cityid = field[field == 'city'].index.tolist()
        winner = field[field == 'winner'].index.tolist()
        outcomeid = field[field == 'outcome'].index.tolist()
        eventid = field[field == 'event'].index.tolist()
        # outcome only appears when there is no winner
        if len(outcomeid) == 0:
            outcomeid = 0
            # pull data based on index values
            result['toss_winner'] = [s.at[winnerid[0]][2]]
            result['toss_decision'] = [s.at[decisionid[0]][2]]
            result['city'] = [s.at[cityid[0]][2]]
            result['winner'] = [s.at[winner[0]][2]]
            if len(eventid)>0:
                result['event'] = [s.at[eventid[0]][2]]
            else:
                result['event'] = ['']
        else:
            outcomeid = 1
        # delete dataframe
        del field

        # return field results
        return result, outcomeid
    except Exception as e:
        print(e)
        print('Error Occurred with path: ' + path)
        print(result)


def id_csv(path):
    '''
    Extract data from id_csv
    :param path: should be valid path to file
    :return:
    '''
    assert isinstance(path, str)

    # initialization of first inning dictionary
    first_inning = {}

    try:
        # load data from file
        dataframe = pd.read_csv(path, usecols=["match_id", "start_date", "venue", "innings",
                                               "ball", "batting_team", "bowling_team", "runs_off_bat",
                                               "extras", "wicket_type"])

        # retrieve constant data across the two innings
        first_inning['id'] = str(dataframe["match_id"][0])
        first_inning['year'] = [int(dataframe['start_date'][0].split('-')[0])]
        first_inning['venue'] = [dataframe["venue"][0]]
        second_inning = first_inning.copy()

        # Create unique id for each inning
        first_inning['id'] = [first_inning['id'] + 'A']
        second_inning['id'] = [second_inning['id'] + 'B']

        # Get Data from each inning
        inn_1 = inning(dataframe, 1)
        inn_2 = inning(dataframe, 2)

        # Add all the data together
        first_inning.update(inn_1)
        second_inning.update(inn_2)

        # delete the dataframe
        del dataframe

        # return data from each inning
        return first_inning, second_inning
    except Exception as e:
        print(e)
        print('Error Occurred with path: ' + path)


def pre_process_data(input_directory_path, output_path):
    '''
    Runs the main loop for processing the data in each file and creating the
    resultant data csv file which will be used in analysis

    :param input_directory_path: local path to data directory
    :param output_path: local path to database storage location
    :return:
    '''

    files = os.listdir(input_directory_path)

    # create result dataframe
    frame = pd.DataFrame()

    # Game Count
    k = 0
    # loop over files in directory
    for file in files:
        # check if not an info file and if not a csv file
        if file[-8:-4] != 'info' and file[-3:] == 'csv':  # id.csv

            INFO_FNAME = os.path.join(DATA_PATH, f"{file[:-4]}_info.csv")
            # pull data from id_info.csv
            info, incomplete_game = id_info_csv(INFO_FNAME)
            # skip if game was not finished
            if not incomplete_game:
                CSV_PATH = os.path.join(DATA_PATH, file)

                # pull data from id.csv
                fieldA, fieldB = id_csv(CSV_PATH)

                # combine data from both files
                fieldA.update(info)
                fieldB.update(info)

                # just deleting info for ease of reading debugger
                del info

                # add data to dataframe
                frame = pd.concat([frame, pd.DataFrame(fieldA, index=[k])])
                frame = pd.concat([frame, pd.DataFrame(fieldB, index=[k])])

                # just deleting info for ease of reading debugger
                del fieldA
                del fieldB
                print(k)
                k += 1

    # Updating the frame to remove duplicates
    # Reduce duplications in stadium names using the names preceded by a comma
    frame[['match_id', 'innings_number']] = frame.id.str.extract(r'(.*)(.{1})', expand=True)
    frame['venue'] = frame.venue.str.split(',').str[0]

    frame.to_csv(output_path)

    return True



if __name__ == '__main__':
    # path to directory
    BASE_PATH = os.getcwd()
    DATA_PATH = os.path.join(BASE_PATH, "Raw Data", "t20s_male_csv_files")
    # path to save location
    SAVE_PATH = os.path.join(BASE_PATH, "DataProcessing", "Result.csv")

    pre_process_data(DATA_PATH,SAVE_PATH)