# -*- encoding: utf-8 -*-
# requires python 3.7+

import logging
import time
import os
import threading
import queue
import warnings

from datetime import datetime
#from gtts import gTTS
import pyttsx3
from playsound import playsound
from collections import defaultdict

warnings.filterwarnings(action='ignore')

# Starting : ben's computer:
# INTERFACE_FOLDER = "Steam/steamapps/common/Don't Starve Together/dontstarve_steam.app/Contents/mods/workshop-666155465/"

# Starting : Jae's computer:
INTERFACE_FOLDER = "Steam/steamapps/common/Don't Starve Together/mods/HRI_gamemod_client/"

INTERFACE_FILE = 'test.csv'

INTERFACE_FILEFOLDER = INTERFACE_FOLDER + INTERFACE_FILE

data = dict()
initial_state = dict()
status = defaultdict(list)

# placeholders
HUNGRY = 50  # max
STARVING = 30  # max
INJURED = 50  # max
DYING = 30  # max
SANITY_SAFE = 80
SANITY_DANGER = 30

if not os.path.exists("./logs/"):
    os.mkdir("./logs/")

logging.basicConfig(
    format="%(asctime)s %(levelname)s: %(name)s: %(message)s",
    level=logging.DEBUG,
    filename='./logs/dm.log',
    # encoding='utf-8',
    datefmt="%H:%M:%S",
    # stream=sys.stderr,
)

logger = logging.getLogger("__dm__")
logging.getLogger("chardet.charsetprober").disabled = True

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[2].id)  # us female
# engine.setProperty('voice', voices[0].id) # Korean female
# engine.setProperty('voice', voices[33].id)  # us female
# engine.setProperty('voice', voices[44].id) # Korean female
engine.setProperty('rate', 150)
'''
***
add stuff here
***
'''


def synthesize_utt(utterance):
    # get a text and synthesize it
    print()
    print('**********'*5)
    print('Agent: ', utterance)
    print('**********'*5)
    print()

    logger.info('New utterance is:')
    logger.info(utterance)

    if utterance != None:
        engine.say(utterance)
        engine.runAndWait()

        # soundqueue.put(utterance)
        # tts = gTTS(text=utterance, lang='en', tld='com', lang_check=True, pre_processor_funcs=[])
        # tts = gTTS(text=utterance, lang='ko', tld='com', lang_check=True, pre_processor_funcs=[])  # 'ko' for Korean
        '''
        mp3_fp = BytesIO()
        tts.write_to_fp(mp3_fp)
        # use a player like pygame with mp3_fp
        # check out: https://github.com/pndurette/gTTS/issues/26
        '''
        # or via file system
        #this_soundfile_name = './sounds/' + datetime.now().strftime("%H-%M-%S") + '.mp3'

        # tts.save(this_soundfile_name)
        # soundqueue.put(this_soundfile_name)
        # ToDo: put synthesizer and player in separate threads and queue


def parse_day_subtree(current_state, old_state):
    # parse the game states only for the 'day' and create actions and utterances

    # Starting : Day
    if current_state['Phase'] == 'day':
        status['Phase'].append(current_state['Phase'])

        action = 'day'
        utterance = 'Good morning!'  # en

        if len(status['Phase']) == 1:
            synthesize_utt(utterance)
        elif len(status['Phase']) > 1:
            if status['Phase'][-2] != status['Phase'][-1]:
                synthesize_utt(utterance)
        # elif len(status['Phase']) > 3:
        #     del(status['Phase'][:-3])

    elif current_state['Phase'] == 'dusk':
        status['Phase'].append(current_state['Phase'])

        action = 'dusk'
        utterance = "It's getting dark!"  # en

        if len(status['Phase']) == 1:
            synthesize_utt(utterance)
        elif len(status['Phase']) > 1:
            if status['Phase'][-2] != status['Phase'][-1]:
                synthesize_utt(utterance)
        # elif len(status['Phase']) > 3:
        #     del(status['Phase'][:-3])

    if current_state['Phase'] == 'night':
        status['Phase'].append(current_state['Phase'])

        action = 'night'
        utterance = "It's night!"  # en

        if len(status['Phase']) == 1:
            synthesize_utt(utterance)
        elif len(status['Phase']) > 1:
            if status['Phase'][-2] != status['Phase'][-1]:
                synthesize_utt(utterance)
        # elif len(status['Phase']) > 3:
        #     del(status['Phase'][:-3])

    # Starting : Hunger
    # if int(float(current_state['Hunger'])) < HUNGRY:
    if int(float(current_state['Hunger'])) < STARVING:
        status['Hunger'].append(int(float(current_state['Hunger'])))
        action = 'hunger_is_dangerous'
        utterance = "Almost dying for hunger!"  # en

        if len(status['Hunger']) == 1:
            synthesize_utt(utterance)
        elif len(status['Hunger']) > 1:
            if status['Hunger'][-2] < status['Hunger'][-1] and status['Hunger'][-1] > 25:
                synthesize_utt(utterance)
            elif status['Hunger'][-2] == 29 and status['Hunger'][-1] != 29:
                synthesize_utt(utterance)
        # elif len(status['Hunger']) > 3:
        #     del (status['Hunger'][:-3])

    elif HUNGRY >= int(float(current_state['Hunger'])) > STARVING:
        status['Hunger'].append(int(float(current_state['Hunger'])))

        action = 'hunger_is_quite_low'
        utterance = 'I need foods!'  # en

        if len(status['Hunger']) == 1:
            synthesize_utt(utterance)
        elif len(status['Hunger']) > 1:
            if status['Hunger'][-2] < status['Hunger'][-1] and status['Hunger'][-1] > 45:
                synthesize_utt(utterance)
        # elif len(status['Hunger']) > 3:
        #     del (status['Hunger'][:-3])

    # Starting : Health
    # if int(float(current_state['Health'])) < INJURED:
    if int(float(current_state['Health'])) < DYING:
        status['Health'].append(int(float(current_state['Health'])))

        action = 'Almost_Dying'
        utterance = "I'll die soon!"  # en

        if len(status['Health']) == 1:
            synthesize_utt(utterance)
        elif len(status['Health']) > 1:
            if status['Health'][-2] < status['Health'][-1] and status['Health'][-1] > 25:
                synthesize_utt(utterance)
            elif status['Health'][-2] == 29 and status['Health'][-1] != 29:
                synthesize_utt(utterance)
        # elif len(status['Health']) > 3:
        #     del (status['Health'][:-3])

    elif INJURED > int(float(current_state['Health'])) > DYING:
        status['Health'].append(int(float(current_state['Health'])))

        action = 'Quite_injured'
        utterance = 'Need to recover health!'  # en

        if len(status['Health']) == 1:
            synthesize_utt(utterance)
        elif len(status['Health']) > 1:
            if status['Health'][-2] < status['Health'][-1] and status['Health'][-1] > 45:
                synthesize_utt(utterance)
        # elif len(status['Health']) > 3:
        #     del (status['Health'][:-3])

    # Starting : Sanity
    # if int(float(current_state['Sanity'])) < SANITY_SAFE:
    if int(float(current_state['Sanity'])) < SANITY_DANGER:
        status['Sanity'].append(int(float(current_state['Sanity'])))

        action = 'Mental_Crushed'
        utterance = "Sanity is almost crushed!"  # en

        if len(status['Sanity']) == 1:
            synthesize_utt(utterance)
        elif len(status['Sanity']) > 1:
            if status['Sanity'][-2] < status['Sanity'][-1] and status['Sanity'][-1] > 25:
                synthesize_utt(utterance)
            elif status['Sanity'][-2] == 29 and status['Sanity'][-1] != 29:
                synthesize_utt(utterance)
        # elif len(status['Sanity']) > 3:
        #     del (status['Sanity'][:-3])

    elif 50 > int(float(current_state['Sanity'])) > SANITY_DANGER:
        status['Sanity'].append(int(float(current_state['Sanity'])))

        action = 'Quite_crushed'
        utterance = 'Need to recover Sanity!'  # en

        if len(status['Sanity']) == 1:
            synthesize_utt(utterance)
        elif len(status['Sanity']) > 1:
            if status['Sanity'][-2] < status['Sanity'][-1] and status['Sanity'][-1] > 45:
                synthesize_utt(utterance)
        # elif len(status['Sanity']) > 3:
        #     del (status['Sanity'][:-3])

    # Starting : Equipment
    if current_state['Curr_Equip_Hands'] != 'nil':
        status['Curr_Equip_Hands'].append(current_state['Curr_Equip_Hands'])

        action = 'Equip_a_tool_to_use'
        # en
        utterance = f"I equip {str(current_state['Curr_Equip_Hands'][9:])}!"

        if len(status['Curr_Equip_Hands']) == 1:
            synthesize_utt(utterance)
        elif len(status['Curr_Equip_Hands']) > 1:
            if status['Curr_Equip_Hands'][-2] != status['Curr_Equip_Hands'][-1]:
                synthesize_utt(utterance)
        # elif len(status['Curr_Equip_Hands']) > 3:
        #     del (status['Curr_Equip_Hands'][:-3])

    # Starting : Attacked
    if current_state['Attack_Target'] != 'nil':
        status['Attack_Target'].append(current_state['Attack_Target'])

        action = 'Attacked'
        # en
        utterance = f"Attacking {str(current_state['Attack_Target'][9:])}!"

        if len(status['Attack_Target']) == 1:
            synthesize_utt(utterance)
        elif len(status['Attack_Target']) > 1:
            if status['Attack_Target'][-2] != status['Attack_Target'][-1]:
                synthesize_utt(utterance)
        # elif len(status['Attack_Target']) > 3:
        #     del (status['Attack_Target'][:-3])

    # Starting : Attacking something
    if current_state['Defense_Target'] != 'nil':
        status['Defense_Target'].append(current_state['Defense_Target'])

        action = 'Attacking something'
        # en
        utterance = f"Being attacked by {str(current_state['Defense_Target'][9:])}!"

        if len(status['Defense_Target']) == 1:
            synthesize_utt(utterance)
        elif len(status['Defense_Target']) > 1:
            if status['Defense_Target'][-2] != status['Defense_Target'][-1]:
                synthesize_utt(utterance)
        # elif len(status['Defense_Target']) > 3:
        #     del (status['Defense_Target'][:-3])

    # Starting : Food
    if current_state['Food'] == 'No Food!':
        status['Food'].append(current_state['Food'])

        action = 'Food_is_needed_immediately'
        utterance = 'We have no food now.'  # en

        if len(status['Food']) == 1:
            synthesize_utt(utterance)
        elif len(status['Food']) > 1:
            if status['Food'][-2] != status['Food'][-1]:
                synthesize_utt(utterance)
        # elif len(status['Food']) > 3:
        #     del (status['Food'][:-3])

    elif current_state['Food'] == 'Less Food!':
        status['Food'].append(current_state['Food'])

        action = 'Food_is_needed'
        utterance = 'Foods are not enough!'  # en

        if len(status['Food']) == 1:
            synthesize_utt(utterance)
        elif len(status['Food']) > 1:
            if status['Food'][-2] != status['Food'][-1]:
                synthesize_utt(utterance)
        # elif len(status['Food']) > 3:
        #     del (status['Food'][:-3])

    elif current_state['Food'] == 'Fine!':
        status['Food'].append(current_state['Food'])

        action = 'Food_is_sufficient'
        utterance = "Enough foods for now."  # en

        if len(status['Food']) == 1:
            synthesize_utt(utterance)
        elif len(status['Food']) > 1:
            if status['Food'][-2] != status['Food'][-1]:
                synthesize_utt(utterance)
        # elif len(status['Food']) > 3:
        #     del (status['Food'][:-3])

    # Starting : Resources
    if current_state['Tool'] == 'Less resources':
        status['Tool'].append(current_state['Tool'])

        action = 'resources_are_needed_for_tools'
        utterance = 'Need more to make tools!'  # en

        if len(status['Tool']) == 1:
            synthesize_utt(utterance)
        elif len(status['Tool']) > 1:
            if status['Tool'][-2] != status['Tool'][-1]:
                synthesize_utt(utterance)
        # elif len(status['Tool']) > 3:
        #     del (status['Tool'][:-3])

    elif current_state['Tool'] == 'Only Axe':
        status['Tool'].append(current_state['Tool'])

        action = 'Axe_could_be_made'
        utterance = 'Able to make an axe!'  # en

        if len(status['Tool']) == 1:
            synthesize_utt(utterance)
        elif len(status['Tool']) > 1:
            if status['Tool'][-2] != status['Tool'][-1]:
                synthesize_utt(utterance)
        # elif len(status['Tool']) > 3:
        #     del (status['Tool'][:-3])

    elif current_state['Tool'] == 'One of Axe and Pickaxe':
        status['Tool'].append(current_state['Tool'])

        action = 'One_of_Axe_pickaxe_could_be_made'
        utterance = 'Possible to make a pickaxe!'  # en

        if len(status['Tool']) == 1:
            synthesize_utt(utterance)
        elif len(status['Tool']) > 1:
            if status['Tool'][-2] != status['Tool'][-1]:
                synthesize_utt(utterance)
        # elif len(status['Tool']) > 3:
        #     del (status['Tool'][:-3])

    elif current_state['Tool'] == 'Fine':
        status['Tool'].append(current_state['Tool'])

        action = 'Tools_could_be_made'
        utterance = 'Enough to make a pickaxe and an axe!'  # en

        if len(status['Tool']) == 1:
            synthesize_utt(utterance)
        elif len(status['Tool']) > 1:
            if status['Tool'][-2] != status['Tool'][-1]:
                synthesize_utt(utterance)
        # elif len(status['Tool']) > 3:
        #     del (status['Tool'][:-3])

    # Starting : Lights (making)
    if current_state['Lights'] == 'Less resources' and current_state['Is_Light'] == 'No lights!':
        status['Lights'].append(current_state['Lights'])
        status['Is_Light'].append(current_state['Is_Light'])

        action = 'resources_are_needed_for_lights'
        utterance = "Need more resources to make a torch!"  # en

        if len(status['Lights']) == 1:
            synthesize_utt(utterance)
        elif len(status['Lights']) > 1:
            if status['Lights'][-2] != status['Lights'][-1]:
                synthesize_utt(utterance)
        # elif len(status['Lights']) > 3:
        #     del (status['Lights'][:-3])

    elif current_state['Lights'] == 'Only torch' and current_state['Is_Light'] == 'No lights!':
        status['Lights'].append(current_state['Lights'])
        status['Is_Light'].append(current_state['Is_Light'])

        action = 'resources_are_sufficient_to_make_torch'
        utterance = 'Enough to make a torch!'  # en

        if len(status['Lights']) == 1:
            synthesize_utt(utterance)
        elif len(status['Lights']) > 1:
            if status['Lights'][-2] != status['Lights'][-1]:
                synthesize_utt(utterance)
        # elif len(status['Lights']) > 3:
        #     del (status['Lights'][:-3])

    elif current_state['Lights'] == "It's OK" and current_state['Is_Light'] == 'No lights!':
        status['Lights'].append(current_state['Lights'])
        status['Is_Light'].append(current_state['Is_Light'])

        action = 'resources_are_sufficient_to_make_campfire'
        utterance = 'Sufficient to make a campfire!'  # en

        if len(status['Lights']) == 1:
            synthesize_utt(utterance)
        elif len(status['Lights']) > 1:
            if status['Lights'][-2] != status['Lights'][-1]:
                synthesize_utt(utterance)
        # elif len(status['Lights']) > 3:
        #     del (status['Lights'][:-3])

    elif current_state['Lights'] == 'Fine' and current_state['Is_Light'] == 'No lights!':
        status['Lights'].append(current_state['Lights'])
        status['Is_Light'].append(current_state['Is_Light'])

        action = 'resources_are_sufficient_to_make_fire_pit'
        utterance = 'Possible to make a fire pit!'  # en

        if len(status['Lights']) == 1:
            synthesize_utt(utterance)
        elif len(status['Lights']) > 1:
            if status['Lights'][-2] != status['Lights'][-1]:
                synthesize_utt(utterance)
        # elif len(status['Lights']) > 3:
        #     del (status['Lights'][:-3])

    # Starting : Nearby lights
    if current_state['Is_Light'] == 'Lights nearby' and str(current_state['Curr_Equip_Hands'][9:]) != 'torch(LIMBO)':
        status['Is_Light'].append(current_state['Is_Light'])
        print(str(status['Curr_Equip_Hands'][9:]))

        action = 'torch_is_nearby'
        utterance = 'A light is near!'  # en

        if len(status['Is_Light']) == 1:
            synthesize_utt(utterance)
        elif len(status['Is_Light']) > 1:
            if status['Is_Light'][-2] != status['Is_Light'][-1]:
                synthesize_utt(utterance)
        # elif len(status['Is_Light']) > 3:
        #     del (status['Is_Light'][:-3])

    elif current_state['Is_Light'] == 'Campfire nearby':
        status['Is_Light'].append(current_state['Is_Light'])

        action = 'campfire_nearby'
        utterance = 'Campfire or fire pit is nearby!'  # en

        if len(status['Is_Light']) == 1:
            synthesize_utt(utterance)
        elif len(status['Is_Light']) > 1:
            if status['Is_Light'][-2] != status['Is_Light'][-1]:
                synthesize_utt(utterance)
        # elif len(status['Is_Light']) > 3:
        #     del (status['Is_Light'][:-3])

    # Starting : Monsters
    if current_state['Is_Monster'] == 'Too many monsters':
        status['Is_Monster'].append(current_state['Is_Monster'])

        action = 'monsters_are_lot_nearby'
        utterance = 'Monsters are too many nearby!'  # en

        if len(status['Is_Monster']) == 1:
            synthesize_utt(utterance)
        elif len(status['Is_Monster']) > 1:
            if status['Is_Monster'][-2] != status['Is_Monster'][-1]:
                synthesize_utt(utterance)
        # elif len(status['Is_Monster']) > 3:
        #     del (status['Is_Monster'][:-3])

    elif current_state['Is_Monster'] == 'I see some monsters':
        status['Is_Monster'].append(current_state['Is_Monster'])

        action = 'some_monsters_are_nearby'
        utterance = 'A few monsters are nearby!'  # en

        if len(status['Is_Monster']) == 1:
            synthesize_utt(utterance)
        elif len(status['Is_Monster']) > 1:
            if status['Is_Monster'][-2] != status['Is_Monster'][-1]:
                synthesize_utt(utterance)
        # elif len(status['Is_Monster']) > 3:
        #     del (status['Is_Monster'][:-3])

    elif current_state['Is_Monster'] == 'No monsters nearby':
        status['Is_Monster'].append(current_state['Is_Monster'])

        action = 'No_monsters'
        utterance = 'No monsters nearby!'  # en

        if len(status['Is_Monster']) == 1:
            synthesize_utt(utterance)
        elif len(status['Is_Monster']) > 1:
            if status['Is_Monster'][-2] != status['Is_Monster'][-1]:
                synthesize_utt(utterance)
        # elif len(status['Is_Monster']) > 3:
        #     del (status['Is_Monster'][:-3])
    '''
    ***
    add stuff here
    ***
    '''
    return utterance


def parse_decision_tree(current_state, old_state):
    # parse the decision tree to find the right action for the current state
    # synthesize the utterance and play it back
    action = None
    utterance = None

    if current_state['Phase'] == 'day':  # == 'day'
        logger.info(' parse day tree ')
        parse_day_subtree(current_state, old_state)

    elif current_state['Phase'] == 'dusk':  # == 'dusk'
        logger.info(' parse dusk tree')
        parse_day_subtree(current_state, old_state)

    elif current_state['Phase'] == 'night':  # == 'night'
        logger.info(' parse night tree ')
        parse_day_subtree(current_state, old_state)

    else:
        logger.error(' no daytime info available ')

    t_synth = threading.Thread(target=synthesize_utt, args=[
                               utterance], daemon=True)
    t_synth.start()
    # t_synth.join()


def state_changed_withoutHandler():
    # check csv file for game updates and process it to new representation (if necessary)
    # then execute the decision tree for the virtual player
    # creating empty old_state

    initial_state['Phase'] = ''
    initial_state['Hunger'] = ''
    initial_state['Health'] = ''
    initial_state['Sanity'] = ''
    initial_state['Curr_Active_Item'] = ''
    initial_state['Curr_Equip_Hands'] = ''
    initial_state['Attack_Target'] = ''
    initial_state['Defense_Target'] = ''
    initial_state['Food'] = ''
    initial_state['Tool'] = ''
    initial_state['Lights'] = ''
    initial_state['Is_Light'] = ''
    initial_state['Is_Monster'] = ''

    logger.info('opening the csv file and regularly check for added lines')

    try:
        with open(INTERFACE_FOLDER + INTERFACE_FILE, 'r', encoding='utf-8') as csvfile:
            # get the number of columns to check later, if each newline is completely written
            csvheader = csvfile.readline().strip().split(',')

            global no_columns_csv

            no_columns_csv = len(csvheader)-1

            logger.debug(' printing all header names: ')

            for i in range(no_columns_csv):
                logger.debug('%s : %s', i, csvheader[i])

            # start reading all new lines
            update_data_from_csv(csvfile, initial_state)

    except Exception as e:
        logger.error(' error during opening csv file: %s', e)


def get_line_from_csv(csvfile):
    csvfile.seek(0, 2)

    while True:
        line = csvfile.readline()

        if not line:
            time.sleep(0.1)
            continue

        yield line


def update_data_from_csv(csvfile, old_state):
    lines = get_line_from_csv(csvfile)

    for line in lines:
        row = line.split(',')

        try:
            # if the line is not the header line and if it is completely written:
            if row[0] != 'OS_timestamp' and len(row) == no_columns_csv:
                # ToDo : replace indices by generic variable, e.g. from the headers
                data['Phase'] = row[2]
                data['Hunger'] = row[3]
                data['Health'] = row[4]
                data['Sanity'] = row[5]
                data['Curr_Active_Item'] = row[12]
                data['Curr_Equip_Hands'] = row[13]
                data['Attack_Target'] = row[16]
                data['Defense_Target'] = row[17]
                data['Food'] = row[19]
                data['Tool'] = row[21]
                data['Lights'] = row[23]
                data['Is_Light'] = row[25]
                data['Is_Monster'] = row[26]

                # try:
                #     # old_state = current_state
                #
                # except Exception as e:
                #     # in first run there is no current_state
                #     logger.debug(' no current_state yet written available, using empty old_state : %s', e )

                current_state = data

                logger.info("Update state and hand over to decision tree.")
                parse_decision_tree(current_state, old_state)

        except Exception as e:
            logger.error(' error reading current line as data : %s', e)


'''
async def main():
    # await asyncio.gather(system_placeholder_for_game_state_change_csv_file(), state_changed())
    # game_status = await state_changed()
    # await state_changed()
'''
if __name__ == "__main__":
    logger.info('create files/folders')

    if not os.path.exists("./sounds/"):
        os.mkdir("./sounds/")

    else:
        for oldsound in os.listdir("./sounds/"):
            os.remove(os.path.join("./sounds/", oldsound))

    # if not os.path.isfile(INTERFACE_FILEFOLDER):
    #     open(INTERFACE_FILEFOLDER, 'a', encoding='utf-8').close()
    logger.info('starting dm program')

    # start the execution:
    state_changed_withoutHandler()
    # final_message = asyncio.run(main())
    logger.info('stopping dm program, DONE')
