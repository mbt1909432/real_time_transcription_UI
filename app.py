import UI_Window
import recorder
import transcription
from backup.UI_Window import ui_entity


class app_entry:
    def __init__(self):
        self.ui_entity = UI_Window.ui_entity()
        self.recorder_entity=recorder.recorder_entity()
        self.transcription_entity=transcription.transcription_entity()

        self.micro_list=None
        self.micro_option=None

        self.whisper_model_list=None
        self.whisper_model_option=None
        self.device_list=None
        self.device_option=None






    def load_config_and_initalization(self):



    

        self.micro_list=[(data[0],data[1]) for data in self.recorder_entity.get_device_list()]
        self.micro_option=self.ui_entity.refresh_to_show__basic_setting_button_sets( [str(micro) for micro in self.micro_list], "Microphone", "Microphone Setting")
 

     
        self.whisper_model_list=[model for model in self.transcription_entity.get_model_list()]
        self.whisper_model_option=self.ui_entity.refresh_to_show__basic_setting_button_sets( [model for model in self.whisper_model_list], "Transcription", "Transcription Setting")


      
        self.device_list=[device for device in self.transcription_entity.get_device_list()]
        self.device_option=self.ui_entity.refresh_to_show__basic_setting_button_sets( [device for device in self.device_list], "Device", "Device Setting")


        self.ui_entity.refresh_to_show_setting_page(self.save_and_start_button_command,self.transcription_entity.transcript_audio_to_text)
        self.ui_entity.start_UI_widget()



    def save_and_start_button_command(self):
        micro_index=self.micro_list.index(eval(self.micro_option.option_menu.get()))
        self.recorder_entity.set_config(self.micro_list[micro_index])

        device_index=self.device_list.index(self.device_option.option_menu.get())
        whisper_model_index = self.whisper_model_list.index(self.whisper_model_option.option_menu.get())

        self.transcription_entity.set_model_device(whisper_model_index,device_index)

        print(f"Save Completed，current micro info:{self.micro_list[micro_index]}, current whisper models:{self.whisper_model_list[whisper_model_index]},current device:{self.device_list[device_index]},start transcription")


        result=self.recorder_entity.initMic()
        if result is False:return
        self.recorder_entity.start_listen()
        self.transcription_entity.init_transcription()
        self.ui_entity.refresh_to_transcription__widget(self.transcription_entity.start_transcription,self.recorder_entity.micro_source,self.recorder_entity.temp_queue)


        self.app_exit_event()
        #TODO:need separate "save" and "start" functions, cause wav to text share the "save" function


    def app_exit_event(self):
        print("add microphone record event")
        self.ui_entity.end_call_back_lists.append((self.recorder_entity.audio_saver.save_byte_to_wav_file,{"micro":self.recorder_entity.micro_source}))





new_app=app_entry()
new_app.load_config_and_initalization()