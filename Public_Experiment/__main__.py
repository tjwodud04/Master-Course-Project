# -*- coding:utf-8 -*-
'''
this file provides speech capabilities to a character playing "Don't starve together"
this is the startup file
It runs ASR -> State_Changed(Taking data from the game data file) in order
'''

################ load packages
# generaL behavior
import os, threading

# import subdirectories
from Working_code import config as cf
from Working_code import state_changed as sc
from Working_code import asr
################ load packages end

# set logger
logger = cf.logging.getLogger("__dm__")

"""start the speech agent (Both ASR and speaking utterances)"""
if __name__ == "__main__":
    # logger.info('create files/folders')

    # """we need a folder to save TTS as mp3 and play it back"""
    # TODO: avoid using the file system
    # if not os.path.exists("./sounds/"):
    #     os.mkdir("./sounds/")
    #
    # else:
    #     for oldsound in os.listdir("./sounds/"):
    #         os.remove(os.path.join("./sounds/", oldsound))

    asr = asr.listen_micr()
    asr_thread = threading.Thread(target=asr.run)

    logger.info('starting the ASR')

    asr_thread.start()

    logger.info('starting dm program')

    sc.state_changed_withoutHandler()

    asr.terminate()

    logger.info('stopping asr')

    asr_thread.join()

    # final_message = asyncio.run(main())
    logger.info('stopping dm program, DONE')
