# -*- coding:utf-8 -*-
'''
Based on the 'state_changed.py' file, this file returns appropriate utterances for the game situation.
('state_changed.py' -> 'parse_tree.py' (current file) -> 'tts.py'

Order :
Phase / Hunger / Health / Sanity / Equipment / Attaking something / Attacked by something / Food
Tool / Making Lights / Nearby Lights / Monsters / Generic expression
'''
import ast
import random
import re
import threading
import time

from Working_code import config as cf
from Working_code import tts

# set logger
logger = cf.logging.getLogger("__parser__")

# Randomly choose utterances from 'en-US/ko-KR_utterances.txt' files
def get_utterance_from_abstract(abstract):
    # return selected utterance only if current score is lower than 'CHATTINESS' placeholder
    if cf.priority_utterance_score[abstract] <= cf.CHATTINESS:
        # Evaluating safely the called utterance from the config file and get utterances as a list
        utt_list = ast.literal_eval(cf.RESPONSE_UTTS[abstract])

        return random.choice(utt_list)

    # If the socre is higher, then pass
    else:
        pass

# Set up Repetition Delay. Based on the cf.REP_DELAY_AMT, If utterances print out third times, silent for 3 seconds
def repetition_delay(text):
    cf.LOCAL_REP_DELAY_AMT = cf.LOCAL_REP_DELAY_AMT - 1   # Reducing 1 'LOCAL_REP_DELAY_AMT' number

    cf.rep_delay_states[text] = cf.LOCAL_REP_DELAY_AMT    # Change 'rep_delay_states' to current 'LOCAL_REP_DELAY_AMT'

    # if 0, silent for 3 seconds
    if cf.rep_delay_states[text] == 0:
        time.sleep(3)

    # If 'LOCAL_REP_DELAY_AMT' is 0, reset the number using 'REP_DELAY_AMT'
    if cf.LOCAL_REP_DELAY_AMT == 0:
        cf.LOCAL_REP_DELAY_AMT = cf.REP_DELAY_AMT

# Return designated utterance for the appropriate situation
def parse_day_subtree(current_state, initial_state):
    ###############################################################################################
    # Phase starts
    # Phase - Day
    if current_state['Phase'] == 'day':
        cf.status['Phase'].append(current_state['Phase'])

        action = 'day'
        utterance = get_utterance_from_abstract('inform_morning')

        # If it is the first one, speak
        if len(cf.status['Phase']) == 1:
            tts.synthesize_utt(utterance)

        # If it is not the first one, just speak when there's difference occurs
        elif len(cf.status['Phase']) > 1:
            if cf.status['Phase'][-2] != cf.status['Phase'][-1]:
                tts.synthesize_utt(utterance)

    # Phase - Dusk
    elif current_state['Phase'] == 'dusk':
        cf.status['Phase'].append(current_state['Phase'])

        action = 'dusk'
        utterance = get_utterance_from_abstract('inform_evening')

        # If it is the first one, speak
        if len(cf.status['Phase']) == 1:
            tts.synthesize_utt(utterance)

        # If it is not the first one, just speak when there's difference occurs
        elif len(cf.status['Phase']) > 1:
            if cf.status['Phase'][-2] != cf.status['Phase'][-1]:
                tts.synthesize_utt(utterance)

    # Phase - Night
    elif current_state['Phase'] == 'night':
        cf.status['Phase'].append(current_state['Phase'])

        action = 'night'
        utterance = get_utterance_from_abstract('inform_night')

        # If it is the first one, speak
        if len(cf.status['Phase']) == 1:
            tts.synthesize_utt(utterance)

        # If it is not the first one, just speak when there's difference occurs
        elif len(cf.status['Phase']) > 1:
            if cf.status['Phase'][-2] != cf.status['Phase'][-1]:
                tts.synthesize_utt(utterance)
    # Phase ends
    ###############################################################################################

    ###############################################################################################
    # Hunger starts
    # Hunger - very low
    if int(float(current_state['Hunger_AVATAR'])) < cf.STARVING:
        cf.status['Hunger_AVATAR'].append(int(float(current_state['Hunger_AVATAR'])))

        action = 'hunger_is_dangerous'
        utterance = get_utterance_from_abstract('inform_starving')

        # If it is the first one, speak
        if len(cf.status['Hunger_AVATAR']) == 1:
            tts.synthesize_utt(utterance)

        # If it is not the first one, just speak like below situation
        elif len(cf.status['Hunger_AVATAR']) > 1:
            # When there's difference occurs and 'Hunger' status is bigger than 25, then speak
            if cf.status['Hunger_AVATAR'][-2] < cf.status['Hunger_AVATAR'][-1] and cf.status['Hunger_AVATAR'][-1] > 25:
                tts.synthesize_utt(utterance)

            # If the Hunger status is 29, to reduce a bit of repetition (30->29->30->29),
            # Only speaks when the just before the latest one is 29
            elif cf.status['Hunger_AVATAR'][-2] == 29 and cf.status['Hunger_AVATAR'][-1] != 29:
                tts.synthesize_utt(utterance)

    # Hunger - low
    elif cf.HUNGRY >= int(float(current_state['Hunger_AVATAR'])) > cf.STARVING:
        cf.status['Hunger_AVATAR'].append(int(float(current_state['Hunger_AVATAR'])))

        action = 'hunger_is_quite_low'
        utterance = get_utterance_from_abstract('inform_hunger') # en

        # If it is the first one, speak
        if len(cf.status['Hunger_AVATAR']) == 1:
            tts.synthesize_utt(utterance)

        # If it is not the first one and if the Hunger status is 31 ~ 45, speak when there's difference occurs
        elif len(cf.status['Hunger_AVATAR']) > 1:
            if cf.status['Hunger_AVATAR'][-2] < cf.status['Hunger_AVATAR'][-1] and cf.status['Hunger_AVATAR'][-1] > 45:
                tts.synthesize_utt(utterance)
    # Hunger ends
    ###############################################################################################

    ###############################################################################################
    # Health starts
    # Health - very low
    if int(float(current_state['Health_AVATAR'])) < cf.DYING:
        cf.status['Health_AVATAR'].append(int(float(current_state['Health_AVATAR'])))

        action = 'Almost_Dying'
        utterance = get_utterance_from_abstract('inform_dying')  # en

        # If it is the first one, speak
        if len(cf.status['Health_AVATAR']) == 1:
            tts.synthesize_utt(utterance)

        # If it is not the first one, just speak like below situation
        elif len(cf.status['Health_AVATAR']) > 1:
            # When there's difference occurs and 'Health' status is bigger than 25, then speak
            if cf.status['Health_AVATAR'][-2] < cf.status['Health_AVATAR'][-1] and cf.status['Health_AVATAR'][-1] > 25:
                tts.synthesize_utt(utterance)

            # If the Health status is 29, to reduce a bit of repetition (30->29->30->29),
            # Only speaks when the just before the latest one is 29
            elif cf.status['Health_AVATAR'][-2] == 29 and cf.status['Health_AVATAR'][-1] != 29:
                tts.synthesize_utt(utterance)

    # Health - low
    elif cf.INJURED > int(float(current_state['Health_AVATAR'])) > cf.DYING:
        cf.status['Health'].append(int(float(current_state['Health_AVATAR'])))

        action = 'Quite_injured'
        utterance = get_utterance_from_abstract('inform_injured') # en

        # If it is the first one, speak
        if len(cf.status['Health_AVATAR']) == 1:
            tts.synthesize_utt(utterance)

        # If it is not the first one and if the Health status is 31 ~ 45, speak when there's difference occurs
        elif len(cf.status['Health_AVATAR']) > 1:
            if cf.status['Health_AVATAR'][-2] < cf.status['Health_AVATAR'][-1] and cf.status['Health_AVATAR'][-1] > 45:
                tts.synthesize_utt(utterance)
    # Health ends
    ###############################################################################################

    ###############################################################################################
    # Sanity starts
    # Sanity - Very low
    if int(float(current_state['Sanity_AVATAR'])) < cf.SANITY_DANGER:
        cf.status['Sanity_AVATAR'].append(int(float(current_state['Sanity_AVATAR'])))

        action = 'Mental_Crushed'
        utterance = get_utterance_from_abstract('inform_getting_insane') # en # en

        # If it is the first one, speak
        if len(cf.status['Sanity_AVATAR']) == 1:
            tts.synthesize_utt(utterance)

        # If it is not the first one, just speak like below situation
        elif len(cf.status['Sanity_AVATAR']) > 1:
            # When there's difference occurs and 'Sanity' status is bigger than 25, then speak
            if cf.status['Sanity_AVATAR'][-2] < cf.status['Sanity_AVATAR'][-1] and cf.status['Sanity_AVATAR'][-1] > 25:
                tts.synthesize_utt(utterance)

            # If the Sanity status is 29, to reduce a bit of repetition (30->29->30->29),
            # Only speaks when the just before the latest one is 29
            elif cf.status['Sanity_AVATAR'][-2] == 29 and cf.status['Sanity_AVATAR'][-1] != 29:
                tts.synthesize_utt(utterance)

    # Sanity - low
    elif 50 > int(float(current_state['Sanity_AVATAR'])) > cf.SANITY_DANGER :
        cf.status['Sanity_AVATAR'].append(int(float(current_state['Sanity_AVATAR'])))

        action = 'Quite_crushed'
        utterance = get_utterance_from_abstract('inform_low_sanity')  # en

        # If it is the first one, speak
        if len(cf.status['Sanity_AVATAR']) == 1:
            tts.synthesize_utt(utterance)

        # If it is not the first one and if the Sanity status is 31 ~ 45, speak when there's difference occurs
        elif len(cf.status['Sanity_AVATAR']) > 1:
            if cf.status['Sanity_AVATAR'][-2] < cf.status['Sanity_AVATAR'][-1] and cf.status['Sanity_AVATAR'][-1] > 45:
                tts.synthesize_utt(utterance)
    # Sanity ends
    ###############################################################################################

    ###############################################################################################
    # Equipment starts
    # Current Equipment
    if current_state['Curr_Equip_Hands_AVATAR'] != 'nil':
        cf.status['Curr_Equip_Hands_AVATAR'].append(current_state['Curr_Equip_Hands_AVATAR'])

        action = 'Equip_a_tool_to_use'

        # bring the current equipment (format is like '125516 - axe(LIMBO)')
        string = cf.status['Curr_Equip_Hands_AVATAR'][-1]

        # Strip just words from the current equipment
        equip_result = re.findall('[a-z]+', string)

        if len(equip_result) != 1:
            logger.error('equipment list length is not 1')

        # format current equipment as string type
        equip_result = str(equip_result[0])

        # write at the log file
        logger.debug('equipment found ' + equip_result)
        logger.debug('equipment type' + str(type(equip_result)))
        logger.info('equipping with ' + equip_result)

        # bring utterances from data/*_utterances.txt
        utterance = get_utterance_from_abstract('inform_equip')

        # If utterance contains 'something', then change this to current equipment name
        if "something" in utterance:
            utterance = utterance.replace("something", equip_result)

        # If it is the first one, speak
        if len(cf.status['Curr_Equip_Hands_AVATAR']) == 1:
            tts.synthesize_utt(utterance)

        # If it is not the first one, just speak when there's difference occurs
        elif len(cf.status['Curr_Equip_Hands_AVATAR']) > 1:
            if cf.status['Curr_Equip_Hands_AVATAR'][-2] != cf.status['Curr_Equip_Hands_AVATAR'][-1]:
                # Apply repetition delay function for current category (The function starts at line 28)
                repetition_delay('Curr_Equip_Hands_AVATAR')

                # If the rep_delay_states number(count) is not 0, then utterances keep coming out
                if cf.rep_delay_states['Curr_Equip_Hands_AVATAR'] != 0:
                    tts.synthesize_utt(utterance)
    # Equipment ends
    ###############################################################################################

    ###############################################################################################
    # Attack starts
    # Attacking Something
    if current_state['Attack_Target_AVATAR'] != 'nil':
        cf.status['Attack_Target_AVATAR'].append(current_state['Attack_Target_AVATAR'])

        action = 'Attack'

        # bring the current attacking thing (format is like '124017 - tallbird')
        string = cf.status['Attack_Target_AVATAR'][-1]

        # Strip just words from current attacking thing
        attack_result = re.findall('[a-z]+', string)

        if len(attack_result) != 1:
            logger.error('attack list length is not 1')

        # format current attacking thing as string type
        attack_result = str(attack_result[0])

        # write at the log file
        logger.debug('attack found ' + attack_result)
        logger.debug('attack type' + str(type(attack_result)))
        logger.info('attack ' + attack_result)

        utterance = get_utterance_from_abstract('inform_attack')

        # If utterance contains 'something', then change this to current attacking thing's name
        if "something" in utterance:
            utterance = utterance.replace("something", attack_result)

        # If it is the first one, speak
        if len(cf.status['Attack_Target_AVATAR']) == 1:
            tts.synthesize_utt(utterance)

        # If it is not the first one, just speak when there's difference occurs
        elif len(cf.status['Attack_Target_AVATAR']) > 1:
            if cf.status['Attack_Target_AVATAR'][-2] != cf.status['Attack_Target_AVATAR'][-1]:
                # Apply repetition delay function for current category (The function starts at line 28)
                repetition_delay('Attack_Target_AVATAR')

                # If the rep_delay_states number(count) is not 0, then utterances keep coming out
                if cf.rep_delay_states['Attack_Target_AVATAR'] != 0:
                    tts.synthesize_utt(utterance)
    # Attack ends
    ###############################################################################################

    ###############################################################################################
    # Defense starts
    # Being Attacked by something
    if current_state['Defense_Target_AVATAR'] != 'nil':
        cf.status['Defense_Target_AVATAR'].append(current_state['Defense_Target_AVATAR'])

        action = 'Attacked'

        # bring the current being attacked thing (format is like '124017 - tallbird')
        string = cf.status['Defense_Target_AVATAR'][-1]

        # Strip just words from current being attacked thing
        defense_result = re.findall('[a-z]+', string)

        if len(defense_result) != 1:
            logger.error('defense list length is not 1')

        # format current being attacked thing as string type
        defense_result = str(defense_result[0])

        # write at the log file
        logger.debug('defense found ' + defense_result)
        logger.debug('defense type' + str(type(defense_result)))
        logger.info('being attacked by ' + defense_result)

        utterance = get_utterance_from_abstract('inform_defense')

        # If utterance contains 'something', then change this to current being attacked thing's name
        if "something" in utterance:
            utterance = utterance.replace("something", defense_result)

        # If it is the first one, speak
        if len(cf.status['Defense_Target_AVATAR']) == 1:
            tts.synthesize_utt(utterance)

        # If it is not the first one, just speak when there's difference occurs
        elif len(cf.status['Defense_Target_AVATAR']) > 1:
            if cf.status['Defense_Target_AVATAR'][-2] != cf.status['Defense_Target_AVATAR'][-1]:
                # Apply repetition delay function for current category (The function starts at line 28)
                repetition_delay('Defense_Target_AVATAR')

                # If the rep_delay_states number(count) is not 0, then utterances keep coming out
                if cf.rep_delay_states['Defense_Target_AVATAR'] != 0:
                    tts.synthesize_utt(utterance)
    # Defense ends
    ###############################################################################################

    ###############################################################################################
    # Food starts
    # Starting : Food
    # if current_state['Food_AVATAR'] == 'No Food!':
    #     cf.status['Food_AVATAR'].append(current_state['Food_AVATAR'])
    #
    #     action = 'Food_is_needed_immediately'
    #     utterance = get_utterance_from_abstract('inform_no_food')
    #     # utterance = "We have no food now." # en
    #
    #     if len(cf.status['Food_AVATAR']) == 1:
    #         tts.synthesize_utt(utterance)
    #     elif len(cf.status['Food_AVATAR']) > 1:
    #         if cf.status['Food_AVATAR'][-2] != cf.status['Food_AVATAR'][-1]:
    #             tts.synthesize_utt(utterance)

    # Food is not enough
    if current_state['Food_AVATAR'] == 'Less Food!':
        cf.status['Food_AVATAR'].append(current_state['Food_AVATAR'])

        action = 'Food_is_needed'
        utterance = get_utterance_from_abstract('inform_less_food')

        # If it is the first one, speak
        if len(cf.status['Food_AVATAR']) == 1:
            tts.synthesize_utt(utterance)

        # If it is not the first one, just speak when there's difference occurs
        elif len(cf.status['Food_AVATAR']) > 1:
            if cf.status['Food_AVATAR'][-2] != cf.status['Food_AVATAR'][-1]:
                # Apply repetition delay function for current category (The function starts at line 28)
                repetition_delay('Food_AVATAR')

                # If the rep_delay_states number(count) is not 0, then utterances keep coming out
                if cf.rep_delay_states['Food_AVATAR'] != 0:
                    tts.synthesize_utt(utterance)

    # Food is sufficient
    elif current_state['Food_AVATAR'] == 'Fine!':
        cf.status['Food_AVATAR'].append(current_state['Food_AVATAR'])

        action = 'Food_is_sufficient'
        utterance = get_utterance_from_abstract('inform_enough_food')

        # If it is the first one, speak
        if len(cf.status['Food_AVATAR']) == 1:
            tts.synthesize_utt(utterance)

        # If it is not the first one, just speak when there's difference occurs
        elif len(cf.status['Food_AVATAR']) > 1:
            if cf.status['Food_AVATAR'][-2] != cf.status['Food_AVATAR'][-1]:
                # Apply repetition delay function for current category (The function starts at line 28)
                repetition_delay('Food_AVATAR')

                # If the rep_delay_states number(count) is not 0, then utterances keep coming out
                if cf.rep_delay_states['Food_AVATAR'] != 0:
                    tts.synthesize_utt(utterance)
    # Food ends
    ###############################################################################################

    ###############################################################################################
    # Tool starts
    # Tools(Resources) - Less resources
    # if current_state['Tool_AVATAR'] == 'Less resources':
    #     cf.status['Tool_AVATAR'].append(current_state['Tool_AVATAR'])
    #
    #     action = 'resources_are_needed_for_tools'
    #     utterance = get_utterance_from_abstract('inform_no_resources_tool')
    #     # utterance = "Need more to make tools!" # en
    #
    #     if len(cf.status['Tool_AVATAR']) == 1:
    #         tts.synthesize_utt(utterance)
    #     elif len(cf.status['Tool_AVATAR']) > 1:
    #         if cf.status['Tool_AVATAR'][-2] != cf.status['Tool_AVATAR'][-1]:
    #             tts.synthesize_utt(utterance)

    # Tools(Resources) - Axe possible
    if current_state['Tool_AVATAR'] == 'Only Axe' :
        cf.status['Tool_AVATAR'].append(current_state['Tool_AVATAR'])

        action = 'Axe_could_be_made'
        utterance = get_utterance_from_abstract('inform_only_axe')

        # If it is the first one, speak
        if len(cf.status['Tool_AVATAR']) == 1:
            tts.synthesize_utt(utterance)

        # If it is not the first one, just speak when there's difference occurs
        elif len(cf.status['Tool_AVATAR']) > 1:
            if cf.status['Tool_AVATAR'][-2] != cf.status['Tool_AVATAR'][-1]:
                # Apply repetition delay function for current category (The function starts at line 28)
                repetition_delay('Tool_AVATAR')

                # If the rep_delay_states number(count) is not 0, then utterances keep coming out
                if cf.rep_delay_states['Tool_AVATAR'] != 0:
                    tts.synthesize_utt(utterance)

    # Tools(Resources) - Pickaxe possible
    elif current_state['Tool_AVATAR'] == 'One of Axe and Pickaxe' :
        cf.status['Tool_AVATAR'].append(current_state['Tool_AVATAR'])

        action = 'One_of_Axe_pickaxe_could_be_made'
        utterance = get_utterance_from_abstract('inform_axe_or_pickaxe')

        # If it is the first one, speak
        if len(cf.status['Tool_AVATAR']) == 1:
            tts.synthesize_utt(utterance)

        # If it is not the first one, just speak when there's difference occurs
        elif len(cf.status['Tool_AVATAR']) > 1:
            if cf.status['Tool_AVATAR'][-2] != cf.status['Tool_AVATAR'][-1]:
                # Apply repetition delay function for current category (The function starts at line 28)
                repetition_delay('Tool_AVATAR')

                # If the rep_delay_states number(count) is not 0, then utterances keep coming out
                if cf.rep_delay_states['Tool_AVATAR'] != 0:
                    tts.synthesize_utt(utterance)

    # Tools(Resources) - both possible
    elif current_state['Tool_AVATAR'] == 'Fine' :
        cf.status['Tool_AVATAR'].append(current_state['Tool_AVATAR'])

        action = 'Tools_could_be_made'
        utterance = get_utterance_from_abstract('inform_both')

        # If it is the first one, speak
        if len(cf.status['Tool_AVATAR']) == 1:
            tts.synthesize_utt(utterance)

        # If it is not the first one, just speak when there's difference occurs
        elif len(cf.status['Tool_AVATAR']) > 1:
            if cf.status['Tool_AVATAR'][-2] != cf.status['Tool_AVATAR'][-1]:
                # Apply repetition delay function for current category (The function starts at line 28)
                repetition_delay('Tool_AVATAR')

                # If the rep_delay_states number(count) is not 0, then utterances keep coming out
                if cf.rep_delay_states['Tool_AVATAR'] != 0:
                    tts.synthesize_utt(utterance)
    # Tool ends
    ###############################################################################################

    ###############################################################################################
    # Making_light starts
    # Making Lights - Less resources
    # if current_state['Lights_AVATAR'] == 'Less resources' and current_state['Is_Light_AVATAR'] == 'No lights!':
    #     cf.status['Lights_AVATAR'].append(current_state['Lights_AVATAR'])
    #     cf.status['Is_Light_AVATAR'].append(current_state['Is_Light_AVATAR'])
    #
    #     action = 'resources_are_needed_for_lights'
    #     utterance = get_utterance_from_abstract('inform_no_resources_light')
    #     # utterance = "Need more resources to make a torch!" #en
    #
    #     if len(cf.status['Lights_AVATAR']) == 1:
    #         tts.synthesize_utt(utterance)
    #     elif len(cf.status['Lights_AVATAR']) > 1:
    #         if cf.status['Lights_AVATAR'][-2] != cf.status['Lights_AVATAR'][-1]:
    #             tts.synthesize_utt(utterance)

    # Making Lights - only torch
    if current_state['Lights_AVATAR'] == 'Only torch' and current_state['Is_Light_AVATAR'] == 'No lights!' :
        cf.status['Lights_AVATAR'].append(current_state['Lights_AVATAR'])
        cf.status['Is_Light_AVATAR'].append(current_state['Is_Light_AVATAR'])

        action = 'resources_are_sufficient_to_make_torch'
        utterance = get_utterance_from_abstract('inform_torch')

        # If it is the first one, speak
        if len(cf.status['Lights_AVATAR']) == 1:
            tts.synthesize_utt(utterance)

        # If it is not the first one, just speak when there's difference occurs
        elif len(cf.status['Lights_AVATAR']) > 1:
            if cf.status['Lights_AVATAR'][-2] != cf.status['Lights_AVATAR'][-1]:
                # Apply repetition delay function for current category (The function starts at line 28)
                repetition_delay('Lights_AVATAR')

                # If the rep_delay_states number(count) is not 0, then utterances keep coming out
                if cf.rep_delay_states['Lights_AVATAR'] != 0:
                    tts.synthesize_utt(utterance)

    # Making Lights - Campfire possible
    elif current_state['Lights_AVATAR'] == "It's OK" and current_state['Is_Light_AVATAR'] == 'No lights!':
        cf.status['Lights_AVATAR'].append(current_state['Lights_AVATAR'])
        cf.status['Is_Light_AVATAR'].append(current_state['Is_Light_AVATAR'])

        action = 'resources_are_sufficient_to_make_campfire'
        utterance = get_utterance_from_abstract('inform_campfire')

        # If it is the first one, speak
        if len(cf.status['Lights_AVATAR']) == 1:
            tts.synthesize_utt(utterance)

        # If it is not the first one, just speak when there's difference occurs
        elif len(cf.status['Lights_AVATAR']) > 1:
            if cf.status['Lights_AVATAR'][-2] != cf.status['Lights_AVATAR'][-1]:
                # Apply repetition delay function for current category (The function starts at line 28)
                repetition_delay('Lights_AVATAR')

                # If the rep_delay_states number(count) is not 0, then utterances keep coming out
                if cf.rep_delay_states['Lights_AVATAR'] != 0:
                    tts.synthesize_utt(utterance)

    # Making Lights - Firepit possible
    elif current_state['Lights_AVATAR'] == 'Fine' and current_state['Is_Light_AVATAR'] == 'No lights!':
        cf.status['Lights_AVATAR'].append(current_state['Lights_AVATAR'])
        cf.status['Is_Light_AVATAR'].append(current_state['Is_Light_AVATAR'])

        action = 'resources_are_sufficient_to_make_fire_pit'
        utterance = get_utterance_from_abstract('inform_firepit')

        # If it is the first one, speak
        if len(cf.status['Lights_AVATAR']) == 1:
            tts.synthesize_utt(utterance)

        # If it is not the first one, just speak when there's difference occurs
        elif len(cf.status['Lights_AVATAR']) > 1:
            if cf.status['Lights_AVATAR'][-2] != cf.status['Lights_AVATAR'][-1]:
                # Apply repetition delay function for current category (The function starts at line 28)
                repetition_delay('Lights_AVATAR')

                # If the rep_delay_states number(count) is not 0, then utterances keep coming out
                if cf.rep_delay_states['Lights_AVATAR'] != 0:
                    tts.synthesize_utt(utterance)
    # Making_light ends
    ###############################################################################################

    ###############################################################################################
    # Nearby_light starts
    # Nearby lights - something is near
    if current_state['Is_Light_AVATAR'] == 'Lights nearby' and str(current_state['Curr_Equip_Hands_AVATAR'][9:]) != 'torch(LIMBO)':
        cf.status['Is_Light_AVATAR'].append(current_state['Is_Light_AVATAR'])

        action = 'torch_is_nearby'
        utterance = get_utterance_from_abstract('inform_near_light')

        # If it is the first one, speak
        if len(cf.status['Is_Light_AVATAR']) == 1:
            tts.synthesize_utt(utterance)

        # If it is not the first one, just speak when there's difference occurs
        elif len(cf.status['Is_Light_AVATAR']) > 1:
            if cf.status['Is_Light_AVATAR'][-2] != cf.status['Is_Light_AVATAR'][-1]:
                # Apply repetition delay function for current category (The function starts at line 28)
                repetition_delay('Is_Light_AVATAR')

                # If the rep_delay_states number(count) is not 0, then utterances keep coming out
                if cf.rep_delay_states['Is_Light_AVATAR'] != 0:
                    tts.synthesize_utt(utterance)

    # Nearby lights - Campfire/Firepit is near
    elif current_state['Is_Light_AVATAR'] == 'Campfire nearby':
        cf.status['Is_Light_AVATAR'].append(current_state['Is_Light_AVATAR'])

        action = 'campfire_nearby'
        utterance = get_utterance_from_abstract('inform_near_campfire')

        # If it is the first one, speak
        if len(cf.status['Is_Light_AVATAR']) == 1:
            tts.synthesize_utt(utterance)

        # If it is not the first one, just speak when there's difference occurs
        elif len(cf.status['Is_Light_AVATAR']) > 1:
            if cf.status['Is_Light_AVATAR'][-2] != cf.status['Is_Light_AVATAR'][-1]:
                # Apply repetition delay function for current category (The function starts at line 28)
                repetition_delay('Is_Light_AVATAR')

                # If the rep_delay_states number(count) is not 0, then utterances keep coming out
                if cf.rep_delay_states['Is_Light_AVATAR'] != 0:
                    tts.synthesize_utt(utterance)
    # Nearby_light ends
    ###############################################################################################

    ###############################################################################################
    # Monsters start
    # Monsters - a lot (more than 5)
    if current_state['Is_Monster_AVATAR'] == 'Too many monsters':
        cf.status['Is_Monster_AVATAR'].append(current_state['Is_Monster_AVATAR'])

        action = 'monsters_are_lot_nearby'
        utterance = get_utterance_from_abstract('inform_lots_of_monsters')

        # If it is the first one, speak
        if len(cf.status['Is_Monster_AVATAR']) == 1:
            tts.synthesize_utt(utterance)

        # If it is not the first one, just speak when there's difference occurs
        elif len(cf.status['Is_Monster_AVATAR']) > 1:
            if cf.status['Is_Monster_AVATAR'][-2] != cf.status['Is_Monster_AVATAR'][-1]:
                # Apply repetition delay function for current category (The function starts at line 28)
                repetition_delay('Is_Monster_AVATAR')

                # If the rep_delay_states number(count) is not 0, then utterances keep coming out
                if cf.rep_delay_states['Is_Monster_AVATAR'] != 0:
                    tts.synthesize_utt(utterance)

    # Monsters - a few (less than 5)
    elif current_state['Is_Monster_AVATAR'] == 'I see some monsters':
        cf.status['Is_Monster_AVATAR'].append(current_state['Is_Monster_AVATAR'])

        action = 'some_monsters_are_nearby'
        utterance = get_utterance_from_abstract('inform_a_few_monsters')

        # If it is the first one, speak
        if len(cf.status['Is_Monster_AVATAR']) == 1:
            tts.synthesize_utt(utterance)

        # If it is not the first one, just speak when there's difference occurs
        elif len(cf.status['Is_Monster_AVATAR']) > 1:
            if cf.status['Is_Monster_AVATAR'][-2] != cf.status['Is_Monster_AVATAR'][-1]:
                # Apply repetition delay function for current category (The function starts at line 28)
                repetition_delay('Is_Monster_AVATAR')

                # If the rep_delay_states number(count) is not 0, then utterances keep coming out
                if cf.rep_delay_states['Is_Monster_AVATAR'] != 0:
                    tts.synthesize_utt(utterance)
    # Monsters end
    ###############################################################################################

    ###############################################################################################
    # Action suggestion starts
    # Action Suggestions
    # Works 'Player_Xloc' is not 999 (999 means that the player does not participate at the current game)
    if current_state['Player_Xloc'] != '999':
        cf.status['Player_Xloc'].append(float(current_state['Player_Xloc']))

        # At night, the movement is limited, so It works only for 'day' and 'dusk' phase
        if cf.status['Phase'][-1] == 'day' or cf.status['Phase'][-1] == 'dusk':
            # if player's location is same for 25 rows, then speak utterance
            if cf.status['Player_Xloc'][-1] == cf.status['Player_Xloc'][-25]:
                action = 'No_movements_for_a_while'
                utterance = get_utterance_from_abstract('inform_generic_expression')
                # repetition_delay('inform_generic_expression')
                tts.synthesize_utt(utterance)
                del(cf.status['Player_Xloc'])
    # Action suggestion ends
    ###############################################################################################
    '''
    ***
    add stuff here
    ***
    '''
    return utterance

def parse_decision_tree(current_state, initial_state):
    '''
    parse the decision tree to find the right action for the current state
    synthesize the utterance and play it back
    '''
    # Set up action and utterance as None
    action = None
    utterance = None

    # If the current state 'Phase' comes as an input then send the state to 'parse_day_subtree()' function
    if current_state['Phase'] == 'day' or current_state['Phase'] == 'dusk' or current_state['Phase'] == 'night':
        logger.info(' parse day tree ')
        parse_day_subtree(current_state, initial_state)

    # If other state comes as an input, write down to the log file
    else:
        logger.error(' no daytime info available ')

    # Set the thread and start
    t_synth = threading.Thread(target=tts.synthesize_utt, args=[utterance], daemon=True)
    t_synth.start()
    # t_synth.join()
