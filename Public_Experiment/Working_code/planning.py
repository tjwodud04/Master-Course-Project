# # -*- coding:utf-8 -*-
import time

starting_time = time.time()

import warnings

warnings.filterwarnings(action='ignore')

import math
import csv
import pandas as pd
import numpy as np

np.set_printoptions(precision=8, suppress=True)
pd.options.display.float_format = '{:.8f}'.format

from tensorflow.keras.models import load_model
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras import metrics

from Working_code import config as cf
from Working_code import tts

logger = cf.logging.getLogger("__Planning__")

def planning(row):
    # append the row to the list
    logger.info("Making raw data to list")
    cf.data_list.append(row)
    logger.info("Making raw data to list Done")
    # print(cf.data_list)
    # if the list items are 15 then execute below
    if len(cf.data_list) == 15:
        # start time recording
        start_time = time.time()

        # changing the list to dataframe format
        logger.info("Making 15 items to Dataframe")
        dataframe_list = pd.DataFrame(cf.data_list, columns=cf.columns)

        # insert 'Type', 'RowID', 'Id' to the dataframe
        dataframe_list.insert(0, 'Type', 0)
        dataframe_list.insert(0, 'RowID', 1)
        dataframe_list.insert(0, 'Id', 1)

        # cleaning the dataframe (changing string to numbers, int to float, etc
        logger.info("Transform Dataframe to wanted shape")
        data_cleaning(dataframe_list)

        # Drop the useless columns
        dataframe_list = dataframe_list.drop(columns=cf.drop_column_list, axis=1)

        print(dataframe_list)

        # make the 'RowID' column to the numpy array
        logger.info("Making data to array")
        rowID_list = np.array(dataframe_list['RowID'].drop_duplicates())

        # transform the dataframe and append it to the X (list)
        for rowID in rowID_list:
            tmp_data = dataframe_list[dataframe_list['RowID'] == rowID]
            feature = tmp_data.iloc[:, 4:].apply(pd.to_numeric)
            feature = np.array(feature)
            cf.X.append(feature)

        # changing the X to numpy array
        X_arr = np.array(cf.X)      

        logger.info(f"data shape : {X_arr.shape}")

        # make prediction
        logger.info("Prediction Starts")
        prediction = cf.model.predict(X_arr, verbose=1)
        prediction_list = prediction.tolist()
        prediction_list = sum(prediction_list,[])
        for i in range(len(prediction_list)):
            prediction_list[i] = "{:.5f}".format(prediction_list[i])
        for i in range(len(prediction_list)):
            cf.prediction_result_data.append(float(prediction_list[i]))
        print(cf.prediction_result_data)

        #for i in range(len(cf.prediction_result_data)):
        #    cf.prediction_result_data[i] = format(cf.prediction_result_data[i],'f')

        # get the max value and the index of that max value (if index is 3, then category number is 3)
        value = max(cf.prediction_result_data)
        max_index = cf.prediction_result_data.index(value)
        cf.prediction_result_data.append(max_index)
        cf.prediction_result_data.append(value)

        # Type -Night:0, Resources:1, Monster:2, Build Stuff:3, Social Interaction:4, External Events:5
        # if the score is above 0.8 and index is as 0,1,2,3,4,5 then return synthesized tts
        logger.info("Prediction Result to TTS")
        if cf.prediction_result_data[6] == 0 and cf.prediction_result_data[7] > 0.8:
            tts.synthesize_utt('Night')
            cf.count += 1
        elif cf.prediction_result_data[6] == 1 and cf.prediction_result_data[7] > 0.8:
            tts.synthesize_utt('Resources')
            cf.count += 1
        elif cf.prediction_result_data[6] == 2 and cf.prediction_result_data[7] > 0.8:
            tts.synthesize_utt('Monster')
            cf.count += 1
        elif cf.prediction_result_data[6] == 3 and cf.prediction_result_data[7] > 0.8:
            tts.synthesize_utt('Build Stuff')
            cf.count += 1
        elif cf.prediction_result_data[6] == 4 and cf.prediction_result_data[7] > 0.8:
            tts.synthesize_utt('Social Interaction')
            cf.count += 1
        elif cf.prediction_result_data[6] == 5 and cf.prediction_result_data[1] > 0.8:
            tts.synthesize_utt('External Events')
            cf.count += 1

        # Append count and \n (for identifying previous result and current result at the csv) to the list
        logger.info("Prediction Result to CSV")
        cf.prediction_result_data.append(cf.count)

        # Add the time consumption to the list
        current_time = round((time.time() - start_time), 2)
        cf.total_time = cf.total_time + current_time
        
        cf.prediction_result_data.append(current_time)
        cf.prediction_result_data.append(cf.total_time)
        cf.prediction_result_data.append(int(time.time()))
        # cf.prediction_result_data.append('\n')
        
        # write all the info to the csv file        
        if cf.csvcounter == 1:
            with open("multi_accuracy_result.csv", encoding="utf-8", newline='', mode="w") as f:
                writer = csv.writer(f)
                writer.writerow(['category 1 acc','category 2 acc','category 3 acc', 'category 4 acc', 'category 5 acc', 'category 6 acc','category','top acc','count','time','total time', 'posix time'])
                writer.writerow(cf.prediction_result_data)
                
            cf.csvcounter = cf.csvcounter + 1
            
        elif cf.csvcounter == 2:
            with open("multi_accuracy_result.csv", encoding="utf-8", newline='', mode="a") as f:
                writer = csv.writer(f)
                writer.writerow(cf.prediction_result_data)
                
        if cf.total_time >= 60:
            cf.count = 0
            cf.total_time = 0

        # print(cf.prediction_result_data)

        cf.data_list.clear()
        cf.prediction_result_data.clear()
        cf.X.clear()

def data_cleaning(dataframe_list):
    # Splitting combined columns
    dataframe_list[['Affected_Hunger', 'Affected_Health', 'Affected_Sanity']] = dataframe_list['hunger:health:sanity'].str.split(':', n=2, expand=True)
    dataframe_list[['log', 'rock', 'grass', 'twigs']] = dataframe_list['log:rock:grass:twigs'].str.split(':', n=3, expand=True)
    dataframe_list[['twigs_removed', 'flint']] = dataframe_list['twigs:flint'].str.split(':', n=1, expand=True)

    # Change several columns: String to float/int
    dataframe_list[['Affected_Hunger', 'Affected_Health', 'Affected_Sanity']] = dataframe_list[['Affected_Hunger', 'Affected_Health', 'Affected_Sanity']].astype(float)
    dataframe_list[['log', 'rock', 'grass', 'twigs', 'flint']] = dataframe_list[['log', 'rock', 'grass', 'twigs', 'flint']].astype(int)
    dataframe_list[['Player_Xloc', 'Player_Zloc']] = dataframe_list[['Player_Xloc', 'Player_Zloc']].astype(float)

    # creating ['Motion'], ['agg_Motion']
    dataframe_list[['Motion', 'agg_Motion']] = None
    for i in range(len(dataframe_list)):
        if i % 15 == 0:
            dataframe_list.loc[i, 'Motion'] = 0
            dataframe_list.loc[i, 'agg_Motion'] = 0
        else:
            # ['Motion']
            dx = dataframe_list['Player_Xloc'].iloc[i] - dataframe_list['Player_Xloc'].iloc[i - 1]
            dz = dataframe_list['Player_Zloc'].iloc[i] - dataframe_list['Player_Zloc'].iloc[i - 1]
            dist = math.sqrt((dx ** 2) + (dz ** 2))
            dataframe_list['Motion'].iloc[i] = dist

            # ['agg_Motion']
            dataframe_list['agg_Motion'].iloc[i] = dataframe_list['agg_Motion'].iloc[i - 1] + dist

    for i in range(len(dataframe_list)):
        # Type -Night:0, Resources:1, Monster:2, Build Stuff:3, Social Interaction:4, External Events:5
        # Phase -day:0, dusk:1, night:2
        if dataframe_list.loc[i, 'Phase'] == 'day':
            dataframe_list.loc[i, 'Phase'] = 0
        elif dataframe_list.loc[i, 'Phase'] == 'dusk':
            dataframe_list.loc[i, 'Phase'] = 1
        else:
            dataframe_list.loc[i, 'Phase'] = 2

        # Food -'No Food!':0, 'Less Food!':1, 'Fine!':2
        if dataframe_list.loc[i, 'Food_AVATAR'] == 'No Food!':
            dataframe_list.loc[i, 'Food_AVATAR'] = 0
        elif dataframe_list.loc[i, 'Food_AVATAR'] == 'Less Food!':
            dataframe_list.loc[i, 'Food_AVATAR'] = 1
        else:
            dataframe_list.loc[i, 'Food_AVATAR'] = 2

        # Curr_Active_Item
        if dataframe_list.loc[i, 'Curr_Active_Item_AVATAR'] == 'nil':
            dataframe_list.loc[i, 'Curr_Active_Item_AVATAR'] = 0
        else:
            dataframe_list.loc[i, 'Curr_Active_Item_AVATAR'] = 1

        # Curr_Equip_Hands
        if dataframe_list.loc[i, 'Curr_Equip_Hands_AVATAR'] == 'nil':
            dataframe_list.loc[i, 'Curr_Equip_Hands_AVATAR'] = 0
        else:
            if dataframe_list.loc[i, 'Curr_Equip_Hands_AVATAR'].rsplit('-')[1].lstrip() == 'axe(LIMBO)':
                dataframe_list.loc[i, 'Curr_Equip_Hands_AVATAR'] = 1
            elif dataframe_list.loc[i, 'Curr_Equip_Hands_AVATAR'].rsplit('-')[1].lstrip() == 'pickaxe(LIMBO)':
                dataframe_list.loc[i, 'Curr_Equip_Hands_AVATAR'] = 2
            else:
                dataframe_list.loc[i, 'Curr_Equip_Hands_AVATAR'] = 3

        # Attack_Target
        if dataframe_list.loc[i, 'Attack_Target_AVATAR'] == 'nil':
            dataframe_list.loc[i, 'Attack_Target_AVATAR'] = 0
        else:
            dataframe_list.loc[i, 'Attack_Target_AVATAR'] = 1

        # Defense_Target
        if dataframe_list.loc[i, 'Defense_Target_AVATAR'] == 'nil':
            dataframe_list.loc[i, 'Defense_Target_AVATAR'] = 0
        else:
            dataframe_list.loc[i, 'Defense_Target_AVATAR'] = 1

        # Recent_attacked
        if dataframe_list.loc[i, 'Recent_attacked_AVATAR'] == 'nil':
            dataframe_list.loc[i, 'Recent_attacked_AVATAR'] = 0
        else:
            dataframe_list.loc[i, 'Recent_attacked_AVATAR'] = 1

        # Tool -'Less resources':0, 'Only Axe', 'One of Axe and Pickaxe':1, 'Fine':2
        if dataframe_list.loc[i, 'Tool_AVATAR'] == 'Less resources':
            dataframe_list.loc[i, 'Tool_AVATAR'] = 0
        elif (dataframe_list.loc[i, 'Tool_AVATAR'] == 'Only Axe') | (dataframe_list.loc[i, 'Tool_AVATAR'] == 'One of Axe and Pickaxe'):
            dataframe_list.loc[i, 'Tool_AVATAR'] = 1
        else:
            dataframe_list.loc[i, 'Tool_AVATAR'] = 2

        # Lights -'Less resources':0, 'Only torch':1, 'It's OK', 'Fine':2
        if dataframe_list.loc[i, 'Lights_AVATAR'] == 'Less resources':
            dataframe_list.loc[i, 'Lights_AVATAR'] = 0
        elif dataframe_list.loc[i, 'Lights_AVATAR'] == 'Only torch':
            dataframe_list.loc[i, 'Lights_AVATAR'] = 1
        else:
            dataframe_list.loc[i, 'Lights_AVATAR'] = 2

        # Is_Light -'No lights!':0, 'Lights nearby':1, 'Campfire nearby':2
        if dataframe_list.loc[i, 'Is_Light_AVATAR'] == 'No lights!':
            dataframe_list.loc[i, 'Is_Light_AVATAR'] = 0
        elif dataframe_list.loc[i, 'Is_Light_AVATAR'] == 'Lights nearby':
            dataframe_list.loc[i, 'Is_Light_AVATAR'] = 1
        else:
            dataframe_list.loc[i, 'Is_Light_AVATAR'] = 2

        # Is_Monster -'No monsters nearby':0, 'I see some monsters':1, 'too many monsters':2
        if dataframe_list.loc[i, 'Is_Monster_AVATAR'] == 'No monsters nearby':
            dataframe_list.loc[i, 'Is_Monster_AVATAR'] = 0
        elif dataframe_list.loc[i, 'Is_Monster_AVATAR'] == 'I see some monsters':
            dataframe_list.loc[i, 'Is_Monster_AVATAR'] = 1
        else:
            dataframe_list.loc[i, 'Is_Monster_AVATAR'] = 2

    return dataframe_list
