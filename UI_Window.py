
import json
import os.path
from tkinter import *
from tkinter import filedialog

import customtkinter
import threading
import queue

import nltk
from pydantic import  BaseModel
from typing import  Optional

import UI_button_option_set


class ui_setting(BaseModel):
    window_title:Optional[str]=None
    window_geometry:Optional[str]=None
    window_color:Optional[str]=None
    window_component_color:Optional[str]=None
    window_icon:Optional[str]=None

    subtitle_font_size:Optional[int]=None
    subtitle_font_style:Optional[str]=None


class ui_entity:
    def __init__(self):
        self.root=customtkinter.CTk()
        self.text_queue=queue.Queue()
        self.text_var=StringVar(self.root)
        self.font_style= ("Helvetica", 25)
        self.label = customtkinter.CTkLabel(master=self.root, textvariable=self.text_var, font=self.font_style,wraplength=800)
        self.stop_event=threading.Event()
        self.transcription_thread = None
        self.config_setting=ui_setting()


        #button_option_menu_sets
        self.button_option_sets=dict()



        #method
        self.create_default_config()
        self.init_widget()


        #callback list
        self.end_call_back_lists=list()

        import nltk
        try:
            nltk.data.find('tokenizers/punkt')
            print(f"'{'tokenizers/punkt'}' has been downloaded.")
        except LookupError:
            print(f"'{'tokenizers/punkt'}' need download")
            nltk.download('punkt')


        self.temp_str = ""



    def create_default_config(self):
        config="./config/ui_config.json"
        if not os.path.isfile(config):
            with open(config, 'w',encoding='utf-8') as file:
                self.config_setting.window_title = "TSP Window"
                self.config_setting.window_icon='./icon/icon.ico'
                self.config_setting.window_color="dark"
                self.config_setting.window_component_color="green"
                self.config_setting.window_geometry="600x100"
                self.config_setting.subtitle_font_size=35
                self.config_setting.subtitle_font_style="Helvetica"
                print(self.config_setting.json())
                json.dump(self.config_setting.dict(),file,indent=4)
        else:
            with open(config,'r', encoding='utf-8') as file:
                data=file.read()
                self.config_setting=ui_setting(**json.loads(data))





    def init_widget(self):
        customtkinter.set_appearance_mode(self.config_setting.window_color)
        customtkinter.set_default_color_theme(self.config_setting.window_component_color)
        self.root.geometry(self.config_setting.window_geometry)
        self.root.title(self.config_setting.window_title)
        self.root.iconbitmap(self.config_setting.window_icon)
        self.root.attributes('-topmost', True)

        self.label.pack_forget()


    def refresh_to_show_setting_page(self,command,transcript_command=None):


        self.default_button = customtkinter.CTkButton(self.root, text="Save and Start",command=command)
        self.default_button.pack(side='bottom', pady=20)
        self.WavFileReader_UI=WavFileReader_UI(self.root,transcript_command,self.disable_setting_page)


    def refresh_to_show__basic_setting_button_sets(self,option_list:list,name,comment):

        option_button_set=UI_button_option_set.option_button_set(self.root,option_list,name,comment)
        self.button_option_sets[name]=option_button_set
        return option_button_set





    def refresh_to_transcription__widget(self,transcription,micro,temp_queue):
        self.disable_setting_page()
        self.disable_wav_ui()
        self.root.geometry("600x100")
        self.label.pack(expand=True,padx=10, pady=10)
        self.text_var.set("ready for transcription")
        self.transcription_thread=threading.Thread(target=transcription, args=(self.stop_event,micro,temp_queue,self.text_queue,))
        self.transcription_thread.start()

    def disable_setting_page(self):
        for option in self.button_option_sets.values():
            option.group_frame.pack_forget()
        self.default_button.pack_forget()

    def disable_wav_ui(self):
        self.WavFileReader_UI.disable_all()




    def update_text(self):
        try:
            while True:

                temp = self.temp_str
                new_text = self.text_queue.get_nowait()

                self.temp_str = temp + new_text

                tokens=nltk.word_tokenize(self.temp_str)
                #result = " ".join(tokens[-15:-30]) + '\n' + " ".join(tokens[-30:])
                self.text_var.set(tokens[-20:])
                self.text_queue.task_done()



        except queue.Empty:
            pass

        self.root.after(1000, self.update_text)



    def on_closing(self):
        self.stop_event.set()
        if self.transcription_thread is not None:
            if self.transcription_thread.is_alive():
                self.transcription_thread.join()

        for func, kwargs in self.end_call_back_lists:
            func(**kwargs)

        self.root.destroy()

    def start_UI_widget(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.after(100, self.update_text)
        self.root.mainloop()


class WavFileReader_UI:
    """
    currently, need use "save and start" first cause this entity needs to load config
    """

    def __init__(self,root:customtkinter.ctk_tk,transcription_command,disable_command):
        #
        self.conversion_button = customtkinter.CTkButton(root, text="Conversion", command=self.open_conversion_page)
        self.conversion_button.pack(side='bottom', pady=20,anchor='s')

        self.open_button = customtkinter.CTkButton(root, text="Please select your WAV file",command=self.open_wav_file)
        self.start_button=customtkinter.CTkButton(root, text="Start conversion")
        self.text_box = customtkinter.CTkTextbox(root, height=200, width=300)

        self.transcription_command=transcription_command
        self.disable_command=disable_command


    def open_conversion_page(self):
        self.conversion_button.pack_forget()
        self.open_button.pack(pady=30)
        self.text_box.pack(pady=20)
        self.start_button.pack(pady=10)
        self.disable_command()

    def disable_all(self):
        self.conversion_button.pack_forget()
        self.open_button.pack_forget()
        self.text_box.pack_forget()
        self.start_button.pack_forget()




    def open_wav_file(self):
        import  wave
        # 打开文件选择对话框
        file_path = filedialog.askopenfilename(
            title="Select a wave file",
            filetypes=(("WAV files", "*.wav"), ("All files", "*.*"))
        )

        if file_path:
            try:

                with wave.open(file_path, 'rb') as wav_file:
                    num_channels = wav_file.getnchannels()
                    sample_width = wav_file.getsampwidth()
                    frame_rate = wav_file.getframerate()
                    num_frames = wav_file.getnframes()

                    self.text_box.delete("1.0", customtkinter.END)
                    self.text_box.insert(customtkinter.END, f"File: {file_path}\n")
                    self.text_box.insert(customtkinter.END, f"Channels: {num_channels}\n")
                    self.text_box.insert(customtkinter.END, f"Sample Width: {sample_width} bytes\n")
                    self.text_box.insert(customtkinter.END, f"Frame Rate: {frame_rate} Hz\n")
                    self.text_box.insert(customtkinter.END, f"Total Frames: {num_frames}\n")

            except wave.Error as e:
                print(f"Error reading WAV file: {str(e)}")

            self.start_button.configure(command=lambda: self.transcription(file_path))


    def transcription(self,path):
        self.transcription_command(path)
        self.text_box.insert(customtkinter.END, f"Conversion Success")







