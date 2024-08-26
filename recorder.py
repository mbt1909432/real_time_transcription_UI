import io
import json
import os.path
import queue
import sys
import tempfile
import threading
import tkinter
from time import sleep

import speech_recognition as sr
import time

from joblib.externals.loky.backend.queues import Queue
from pydantic import BaseModel
from  typing import  Optional

#from test.record_test.recoord import audio_data, wav_data


class recorder_setting(BaseModel):
    microphone:Optional[tuple]=None



class recorder_entity:
    def __init__(self):

        self.recorder = None
        self.micro_source = None

        self.micro_list=self.get_device_list()
        self.config_setting=recorder_setting()
        self.init_config()


        self.temp_queue = queue.Queue()


        self.audio_saver=AudioSaver()



    def get_device_list(self):
        mic_list = sr.Microphone.list_microphone_names()

        device_list=list()
        for index, name in enumerate(mic_list):
            device_list.append((index,name))

        return device_list

    def init_config(self):
        config="./config/mic_config.json"
        if not os.path.isfile(config):
            with open(config, mode="w", encoding='utf-8') as file:
                self.config_setting.microphone=self.micro_list[0]
                json.dump(self.config_setting.dict(),file,indent=4)
        else:
            with open(config, mode="r", encoding='utf-8') as file:
                data=json.loads(file.read())
                tuple_data=dict()
                tuple_data['microphone']=(data['microphone'][0],data['microphone'][1])
                self.config_setting=recorder_setting(**tuple_data)


    def set_config(self,micro:tuple):
        config = "./config/mic_config.json"
        with open(config, mode="w", encoding='utf-8') as file:
            self.config_setting.microphone = micro
            json.dump(self.config_setting.dict(), file, indent=4)



    def initMic(self):
        print(f"initializing: {str(self.config_setting.microphone)}")
        self.recorder = sr.Recognizer()
        self.micro_source = sr.Microphone(device_index=int(self.config_setting.microphone[0]), sample_rate=16000)

        start=time.time()
        try:
            with self.micro_source as source:
                self.recorder.adjust_for_ambient_noise(source)
            print(f"init time：{time.time() - start:.2f}s")
        except sr.RequestError as e:
            print(f"RequestError：{e}")
            return False
        except sr.UnknownValueError as e:
            print(f"UnknownValueError：{e}")
            return False
        except Exception as e:
            print(f"Exception：{e}")
            return False
        return True


    def listen_callback(self,_, data: sr.AudioData):
        print("listening on the background")
        sleep(0.1)
        raw_byte_data = data.get_raw_data()
        self.temp_queue.put(raw_byte_data)

        self.audio_saver.add_byte_sequence(raw_byte_data)




    def start_listen(self):

        self.recorder.listen_in_background(self.micro_source, self.listen_callback, phrase_time_limit=2)



class AudioSaver:
    """
    for global record
    """
    def __init__(self):
        self.byte_sequence=bytes()

    def add_byte_sequence(self,byte_sequence:bytes):
        self.byte_sequence+=byte_sequence

    def save_byte_to_wav_file(self,micro:sr.Microphone):
        audio_data=sr.AudioData(self.byte_sequence,micro.SAMPLE_RATE,micro.SAMPLE_WIDTH)
        wav_data=io.BytesIO(audio_data.get_wav_data())

        from datetime import datetime


        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

        # file name
        filename = f"audio_{current_time}"

        print("Generated filename:", filename)

        # path
        folder_path = f"./record_history/{filename}"

        # create directory
        os.makedirs(folder_path, exist_ok=True)

        print("Generated folder:", filename)


        with open(f'./record_history/{filename}/{filename}.wav','w+b') as file:
            file.write(wav_data.getvalue())















