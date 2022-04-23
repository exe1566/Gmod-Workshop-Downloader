import requests
import os
import os.path
import tkinter
import tkinter.messagebox
import customtkinter
import threading
import sys 


#Change this settings 
api_key = "API_KEY" # https://steamcommunity.com/dev/apikey get your api key
output_dir = "output dir" #example "C:/Users/dagge/Desktop/steamworkshops/outputs"

#Dont Change this settings
download_dir = "downloads"
gmod_id = "4000"
download_dir_path = "{}/steamapps/workshop/content/{}".format(download_dir, gmod_id)
steam_cmd = "steamcmd.exe"

# for debug  
def env_defined(key: str):
    return key in os.environ and len(os.environ[key]) > 0

def debug(message: str):
    if env_defined('DEBUG') and os.environ['DEBUG'] == '1':
        print(message)

# we call the arguments in the command line
def call_steamcmd(params: str):
    debug('steamcmd {}'.format(params))
    os.system("{} {}".format(steam_cmd, params))

def download_workshop_mod(self, mod):
    steam_cmd_params = " +force_install_dir {}".format(download_dir)
    steam_cmd_params += " +login anonymous"
    steam_cmd_params += " +workshop_download_item {} {}".format(gmod_id, mod)
    steam_cmd_params += " +quit"
    app.change_status(5)
    #call steamcmd function on new thread
    call_steamcmd(steam_cmd_params)
    app.change_status(50)

    workshop_id = mod
    name = make_request(workshop_id)
    # remove spaces in the name and convert to lowercase
    name = name.replace(" ", "_").lower()

    for file in os.listdir("{}/{}".format(download_dir_path, mod)):
        if file.endswith(".gma"):
            inputdir = download_dir_path + "/" + mod + "/" + file
            outputdir = output_dir + "/" + name
            os.system("gmad.exe extract -file {} -out {}".format(inputdir, outputdir ))

    # remove downloads folder 
    os.system("rmdir /S /Q {}".format("downloads"))
    app.downloading = False
    app.change_status(100)

def make_request(workshop_id):
    payload = {"itemcount": 1, "publishedfileids[0]": [str(workshop_id)]}
    r = requests.post("https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/", data=payload)
    data = r.json()
    name = data["response"]["publishedfiledetails"][0]["title"]
    return name

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class App(customtkinter.CTk):

    WIDTH = 800
    HEIGHT = 520

    def __init__(self):
        super().__init__()

        self.downloading = False
        self.title("Steam Workshop Downloader")
        self.iconbitmap("steam.ico")
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        # self.minsize(App.WIDTH, App.HEIGHT)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # call .on_closing() when app gets closed

        # configure grid layout (2x1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(master=self,width=180,corner_radius=0)
        self.frame_left.grid(row=0, column=0, sticky="nswe")
        
        # ============ frame_left ============

        # configure grid layout (1x11)
        self.frame_left.grid_rowconfigure(0, minsize=10)   # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(5, weight=1)  # empty row as spacing
        self.frame_left.grid_rowconfigure(8, minsize=20)    # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(11, minsize=10)  # empty row with minsize as spacing

        self.label_1 = customtkinter.CTkLabel(master=self.frame_left, text="Made by exe", text_font=("Roboto Medium", -16))  # font name and size in px
        self.label_1.grid(row=1, column=0, pady=10, padx=10)

        self.button_1 = customtkinter.CTkButton(master=self.frame_left,text="Single Download", fg_color=("gray75", "gray30"), command=self.button_event)
        self.button_1.grid(row=2, column=0, pady=10, padx=20)

        self.switch_2 = customtkinter.CTkSwitch(master=self.frame_left,text="Dark Mode", command=self.change_mode)
        self.switch_2.grid(row=10, column=0, pady=10, padx=20, sticky="w")

        # ============ frame_right ============

        self.frame_right = customtkinter.CTkFrame(master=self)
        self.frame_right.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

        self.frame_right.rowconfigure((0, 1, 2, 3), weight=2)
        self.frame_right.rowconfigure(7, weight=10)
        #self.frame_right.rowconfigure(8, weight=1)
        self.frame_right.columnconfigure((0, 1), weight=1)
        self.frame_right.columnconfigure(2, weight=0)

        # add a text entry to top frame right 
        self.text_1 = customtkinter.CTkEntry(master=self.frame_right, width=400, height=50, placeholder_text="Steam Workshop ID", fg_color=("gray75", "gray30"), text_font=("Roboto Medium", -16))
        self.text_1.grid(row=5, column=0, sticky="nswe", padx=100, pady=10)

        self.downloadbut = customtkinter.CTkButton(master=self.frame_right, text="Download", fg_color=("gray75", "gray30"),command=self.single_download)
        self.downloadbut.grid(row=6, column=0, pady=10, padx=20)

        # add a text label
        self.label_2 = customtkinter.CTkLabel(master=self.frame_right, text="Please Insert The Workshop Id You Want To Download!", text_font=("Roboto Medium", -16), )  # font name and size in px
        self.label_2.grid(row=4, column=0, pady=0, padx=20)

    def button_event(self):
        print("Button pressed")
    
    def single_download(self):
        if self.downloading:
            return 

        file_to_download = self.text_1.get()
        if file_to_download == "":
            tkinter.messagebox.showerror("Error", "Please enter a valid workshop ID")
            self.downloading = False
            return

        self.progressbar = customtkinter.CTkProgressBar(master=self.frame_right)
        self.progressbar.grid(row=7, column=0, sticky="ew", padx=15, pady=0)
        self.progressbar.set(0)

        self.downloading = True

        # start thread
        threading.Thread(target=download_workshop_mod, args=(self, file_to_download)).start()
        #download_workshop_mod(file_to_download)

    def change_mode(self):
        if self.switch_2.get() == 1:
            customtkinter.set_appearance_mode("dark")
        else:
            customtkinter.set_appearance_mode("light")

    def change_status(self, status):
        self.progressbar.set(status)
        if status == 100: 
            self.label_2 = customtkinter.CTkLabel(master=self.frame_right, text="Download Finished!", text_font=("Roboto Medium", -16), )  # font name and size in px
            self.label_2.grid(row=8, column=0, pady=50, padx=20)

    def on_closing(self, event=0):
        self.destroy()
        sys.exit()

    def start(self):
        self.mainloop()

if __name__ == "__main__":
    app = App()
    app.start()

#download_workshop_mod(list_to_download)