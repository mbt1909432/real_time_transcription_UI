import json
import os.path
import queue
import tempfile
import threading
from typing import Optional

import speech_recognition as sr
import time
import io
from faster_whisper import WhisperModel
from pydantic import BaseModel



class transcription_setting(BaseModel):
    model:Optional[str]=None
    device:Optional[str]=None


class transcription_entity:
    def __init__(self):
        self.config_setting=transcription_setting()
        self.model_directory_path = "./models/"
        self.config_transcription()

        self.byte_sequence = bytes()
        self.temp_file = tempfile.NamedTemporaryFile().name
        self.sequence = sequence = []

        self.model=None


    def config_transcription(self):
        #add cnn to system path
        current_path = os.path.dirname(__file__)
        cnn_path = os.path.join(current_path, "cnn")
        #check whether the path exists
        if cnn_path not in os.environ["PATH"]:
            os.environ["PATH"] += os.pathsep + cnn_path

        config="./config/tsp_config.json"
        if not os.path.isfile(config):
            with open(config, mode="w", encoding='utf-8') as file:
                self.config_setting.model=self.get_model_list()[0]
                self.config_setting.device = 'cuda'
                json.dump(self.config_setting.dict(),file,indent=4)
        else:
            with open(config, mode="r", encoding='utf-8') as file:
                data=json.loads(file.read())
                print(data)
                self.config_setting=transcription_setting(**data)

    def set_model_device(self,model_index:int,device_index:int):
        config = "./config/tsp_config.json"
        with open(config, mode="w", encoding='utf-8') as file:
            self.config_setting.model = self.get_model_list()[model_index]
            self.config_setting.device=self.get_device_list()[device_index]
            json.dump(self.config_setting.dict(), file, indent=4)





    def get_model_list(self):
        model_directories = [name for name in os.listdir(self.model_directory_path) if
                             os.path.isdir(os.path.join(self.model_directory_path, name))]
        return model_directories


    def get_device_list(self):
        return ['cuda','cpu']


    def init_transcription(self):
        model_size = f"{self.model_directory_path}{self.config_setting.model}/"
        device=self.config_setting.device
        if device == 'cuda':
            self.model = WhisperModel(model_size, device=device, compute_type="int8_float16")
        else:
            self.model = WhisperModel(model_size, device = "cpu", compute_type = "int8")




    def transcript_audio_to_text(self,file_path):
        self.init_transcription()#need fix this later

        start=time.time()
        segments, info = self.model.transcribe(
            rf"{file_path}",
            beam_size=5,
            word_timestamps=True,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
            initial_prompt=""
        )

        file_name =  os.path.splitext(os.path.basename(file_path))[0]


        with open(f"./record_history/{file_name}/{file_name}.txt",'w', encoding='utf-8') as file:
            for segment in segments:
                print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
                file.write("[%.2fs -> %.2fs] %s\n" % (segment.start, segment.end, segment.text))


        print(f"Time consumed:{time.time()-start}")




    def start_transcription(self,stop_event:threading.Event(),micro,temp_queue:queue,text_queue:queue):
        """
        :param stop_event:from UI entity
        :param temp_queue: from recorder_entity
        :param micro:from recorder_entity
        :param text_queue: from UI_entity
        :return:
        """
        while not stop_event.is_set():
            if not temp_queue.empty():
                start = time.time()
                byte_sequence = bytes()
                while not temp_queue.empty():
                    byte_sequence += temp_queue.get()

                audio_data = sr.AudioData(byte_sequence, micro.SAMPLE_RATE, micro.SAMPLE_WIDTH)
                wav_raw_data = io.BytesIO(audio_data.get_wav_data())

                with open(self.temp_file, "w+b") as file:
                    file.write(wav_raw_data.getvalue())
                # https://chattts.com/
                try:
                    segments, info = self.model.transcribe(
                        self.temp_file,
                        beam_size=5,
                        word_timestamps=True,
                        vad_filter=True,
                        vad_parameters=dict(min_silence_duration_ms=500),
                        initial_prompt=""
                    )


                except ValueError as e:
                    print(f"Error during transcription: {e}")
                    language = None
                    continue
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
                    language = None
                    continue

                text = ""
                for segment in segments:
                    text += segment.text


                self.sequence.append(text)
                text_queue.put(text)
                print(self.sequence)
                print(f"end{time.time() - start}")
                time.sleep(0.5)


def Example():
    a = transcription_entity()
    a.init_transcription()
    a.transcript_audio_to_text(r"E:\pycharm_project\real_time_transcription_ui\record_history\audio_20240825_161319\audio_20240825_161319.wav")



if __name__=="__main__":
    Example()
