import customtkinter


class option_button_set:
    def __init__(self,root:customtkinter.CTk,options:list,button_name:str,comment:str):

        self.group_frame=customtkinter.CTkFrame(root)
        self.group_frame.pack(pady=20, padx=20, fill="none", expand=False)

        self.font_style = ("Helvetica", 15)
        self.label = customtkinter.CTkLabel(master=self.group_frame, text=comment, font=self.font_style)
        self.label.pack(side='top', anchor='center', pady=10, padx=20)

        self.selected_option=customtkinter.StringVar(value=options[0])

        self.option_menu=customtkinter.CTkOptionMenu(self.group_frame,variable=self.selected_option,values=options)
        self.option_menu.pack(side='top',anchor='center',pady=10,padx=20)



