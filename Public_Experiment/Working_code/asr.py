# -*- coding:utf-8 -*-
'''
ASR (automatic speech recognition)
- Using SDK : MS Azure for python

Listen to the other player's talk and respond to it based on the keyword file
keyword files - located under the data folder (ex. data/en-US_keywords.txt)
'''
import sys

import keyboard
import ast, random, re
import azure.cognitiveservices.speech as speechsdk
from Working_code import config as cf
from Working_code import tts

# set API keys
speech_key, service_region = cf.speech_key, cf.service_region
speech_config = cf.speech_config
audio_config = cf.audio_config

# set logger
logger = cf.logging.getLogger("__asr__")

# ASR function starts
class listen_micr:

    def __init__(self):
        self._running = True

    def terminate(self):
        self._running = False

    def run(self):
        # Set up recognizer (Using MS Azure)
        # Sample codes could be checked
        # https://github.com/Azure-Samples/cognitive-services-speech-sdk/blob/master/quickstart/python/from-microphone/quickstart.py
        # https://github.com/Azure-Samples/cognitive-services-speech-sdk/blob/a5de28baa82f2633d38e2acd49a319b9df2104c3/samples/python/console/speech_sample.py#L225
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, language=cf.THIS_LANGUAGE, audio_config=audio_config)

        while self._running:
            try:
                logger.debug('listening ...')
                # Inform a person to know start of recognition
                print("Say Something!")

                # Recognizing speech through mike / designated speaker
                # result = speech_recognizer.recognize_once()
                result = speech_recognizer.recognize_once_async()
                final_result = result.get()

                # ignore punctuation marks and lower all words
                # ex) I eat foods. -> I eat foods (ignore punctuation) -> i eat foods (lower words)
                user_utt = final_result.text[:-1].lower()

                # print the result to see how the recognizer recognizes
                print("Recognized: {}".format(user_utt))

                logger.info('user said: ' + user_utt)
                self.respond_to_user_utt(user_utt)

                # Force to shut down ASR only
                # pressing ctrl + z shut down ASR
                if ('exit' in user_utt) or ('종료' in user_utt) or (keyboard.is_pressed('esc')):
                    print("Exiting...")
                    sys.exit()

            # If error occurs, pass and do the recognition task again
            # MS Azure recognizer errors are written below as exception
            except final_result.reason == speechsdk.ResultReason.NoMatch:
                pass
            except final_result.reason == speechsdk.ResultReason.Canceled:
                pass

    # Response selection based on the ASR result
    def respond_to_user_utt(self, text):
        try:
            # check all keywords to be contained in the spoken user text
            # keyword : keywords that are written at data/*_keywords.txt file
            # text : input / a sentence that is recognized and return as a result from 'def run(self)' function
            for keyword in cf.ASR_KEYS_UTTS.keys():
                # Answer would be come out only if the score of designated keyword is under 'config.py' file CHATTINESS placeholder
                if cf.priority_keyword_score[keyword] <= cf.CHATTINESS:
                    # if keyword was said, get response and speak it out
                    # For one keywords
                    # If text contains keyword
                    if keyword in text :
                        # Select random answer from data/*_keywords.txt files
                        utterance = random.choice(ast.literal_eval(cf.ASR_KEYS_UTTS[keyword]))
                        # Bring the utterance to speak
                        tts.synthesize_utt(utterance)
                        # Use break for preventing multiple answers come out
                        break
                    # For multiple keywords or phrase
                    else:
                        # compile regular expression and keywords
                        pattern = re.compile(keyword)
                        # Compare keyword and text if the text is in keyword
                        if pattern.search(text):
                            # Select random answer from data/*_keywords.txt files
                            utterance = random.choice(ast.literal_eval(cf.ASR_KEYS_UTTS[keyword]))
                            # Bring the utterance to speak
                            tts.synthesize_utt(utterance)
                            # Use break for preventing multiple answers come out
                            break
                # If designated keyword score is higher than placeholder 'CHATTINESS'
                else:
                    pass

        # If error occurs, write down the error at the logs/dm.log file
        except Exception as err:
            logger.error("user input parsing failed " + str(err))
