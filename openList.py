"""openList

This program downloads an entire playlist from YouTube 
and converts it to the more portable MP3 format. 

Autor: Jefferson Lopes
Version: v1.0
Email: jefferson.lopes@ee.ufcg.edu.br
"""
import moviepy_build_fix # needed to build on windows
import customtkinter as ctk
from pytube import YouTube
from pytube import Playlist
import moviepy.editor as mp
from threading import Thread
from time import sleep
import os
import re

# set style
ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('dark-blue') 

class App(ctk.CTk):
    def __init__(self : ctk.CTk):
        """config app window"""

        super().__init__()

        # create variables
        self.playlist = None
        self.path = None
        self.link = ''
        self.size = None
        self.id = ''

        # setting window dimensions
        self.geometry("700x540")

        # setting app title
        self.title("openList")

        # do not resize
        self.resizable(False, False)

        # define fonts
        self.title_font = ctk.CTkFont(family='Alphamalemodern', size=56)
        self.label_font = ctk.CTkFont(family='Brion Light', size=16, weight='bold')
        self.text_font = ctk.CTkFont(family='Brion Light', size=12, weight='bold')

        # create widgets
        self.__create_widgets()

    def __create_widgets(self):
        """create widgets on the frame

        :return: if successful, true; otherwise, false 
        """

        # base values
        PADX = 30
        PADY = 20
        RADIUS = 7

        # main frame
        self.frame = ctk.CTkFrame(self)
        self.frame.pack(pady=20, padx=50, expand=True)

        # label - title
        self.title_label = ctk.CTkLabel(
            self.frame, 
            text='openList', 
            font=self.title_font
        )
        self.title_label.grid(column=0, row=0, columnspan=2, pady=2*PADY, padx=PADX)

        # entry - add playlist link
        self.link_entry = ctk.CTkEntry(
            self.frame, 
            placeholder_text='playlist link', 
            justify='center',
            height=30,
            width=300,
            corner_radius=RADIUS,
            font=self.label_font
        )
        self.link_entry.grid(column=0, row=1, pady=PADY/2, padx=PADX)

        # button - choose directory
        self.get_path_button = ctk.CTkButton(
            self.frame, 
            text='choose download folder', 
            command=self.get_path_callback, 
            height=30,
            width=220,
            corner_radius=RADIUS,
            state=ctk.NORMAL,
            font=self.label_font
        )
        self.get_path_button.grid(column=0, row=2, pady=PADY/2, padx=PADX)

        # button - start download
        self.start_button = ctk.CTkButton(
            self.frame, 
            text='start download', 
            command=self.start_callback, 
            height=60,
            width=160,
            corner_radius=2*RADIUS,
            state=ctk.NORMAL,
            font=self.label_font
        )
        self.start_button.grid(column=1, row=1, rowspan=2, pady=PADY, padx=PADX)

        # text box - progress messages
        self.progress_text = ctk.CTkTextbox(
            self.frame,
            height=140,
            width=400,
            corner_radius=2*RADIUS,
            font=self.text_font
        )
        self.progress_text.grid(column=0, row=3, columnspan=2, sticky='wens', pady=PADY, padx=PADX)

        self.progress_bar = ctk.CTkProgressBar(
            self.frame,
            height=7,
            width=300,
            border_width=0,
            corner_radius=RADIUS,
            orientation='horizontal',
            mode='indeterminate',
            indeterminate_speed=1
        )
        self.progress_bar.grid(column=0, row=4, columnspan=2, pady=PADY, padx=PADX)
        self.progress_bar.start()

        return True
        
    def get_path_callback(self):
        """button get path callback

        :return: path string
        """

        # get path
        path = ctk.filedialog.askdirectory()
        
        # convert string
        self.path = path.replace('C:', '')

        # update progress text box
        self.print(F'Download path  :  {self.path}\n')

        return True

    def start_callback(self):
        """button start download callback, check 
        for input errors then starts the download

        :return: if successful, true; otherwise, false 
        """

        # get link string from entry widget
        link = self.link_entry.get()

        # check for empty link
        if link == '':
            self.print(F'ERROR: empty link\n')
            return False
        else:
            self.link = link

        # check for empty path
        if self.path is None or self.path == "":
            self.print(F'ERROR: empty path\n')
            return False
        else:
            # check for valid link id
            if self.get_id():
                # create download separate thread
                t1 = Thread(target=self.start)
                t1.start()
            else:
                self.print(F'ERROR: playlist id not found\n')

        return True

    def get_id(self):
        # find playlist ID inside the link
        for peace in re.split('[&?]', self.link):
            if 'list=' in peace:
                self.id = peace.split('=')[1] # remove 'list=' from string
                return True
        else:
            self.id = ''
            return False

    def get_size(self):
        if self.playlist is not None:
            self.size = len(self.playlist)
            return True
        else:
            self.size = None
            return False

    def update_bar(self, percent):
        if percent < 0:
            #undefined mode
            self.progress_bar.configure(mode='indeterminate')
            self.progress_bar.start()
            return False
        elif percent < 100:
            # print value
            self.progress_bar.stop()
            self.progress_bar.configure(mode='determinate')
            self.progress_bar.set(percent)
            return True
        else:
            #print 100%
            self.progress_bar.stop()
            self.progress_bar.configure(mode='determinate')
            self.progress_bar.set(100)
            return True

    def clean(self) -> None:
        """clean global variables"""
        self.path = None
        self.link = ''
        self.id = ''

    def start(self):
        """start multithread process

        :return: if successful, true; otherwise, false 
        """

        # disable start button
        self.start_button.configure(state=ctk.DISABLED)
        self.get_path_button.configure(state=ctk.DISABLED)

        self.print('\n-------------------------  start downloading  -------------------------\n')
        self.download()

        self.print('\n\n--------------------------  start converting  --------------------------\n')
        self.convert()
        
        self.print('\n\n--------------------------  download finish  --------------------------\n')
        
        self.clean()

        self.thanks()
        
        # enable start button
        self.start_button.configure(state=ctk.NORMAL)
        self.get_path_button.configure(state=ctk.NORMAL)

        return True

    def download(self):
        """download the playlist as a MP4 audio only file

        :return: if successful, true; otherwise, false 
        """

        # start download
        self.playlist = Playlist("https://www.youtube.com/playlist?list=" + self.id)

        counter = 0
        self.get_size()

        # check link
        try:
            title = self.playlist.title
        except:
            self.print('ERROR: broken link\n')
            return False
        else:
            self.print(F'Playlist: {title}\n')

        # start downloading audio as MP4
        self.update_bar(0)
        for url, video in zip(self.playlist, self.playlist.videos):
            video_title = video.title

            counter += 1
            percent = counter / (self.size * 2)

            try:
                YouTube(url).streams.filter(only_audio=True).first().download(self.path)
            except:
                self.print(F'\nERROR on {video_title} - download skipped\n')
            else:
                self.print(F'\n[{counter}/{self.size * 2}] {video_title}')
                self.update_bar(percent)

        return True

    def convert(self):
        """convert MP4 files to MP3

        :return: if successful, true; otherwise, false 
        """
        
        counter = self.size

        # search for mp4 files then convert to mp3
        for file in os.listdir(self.path):
            if re.search('mp4', file):
                counter += 1
                percent = counter / (self.size * 2)

                self.print(F'\n[{counter}/{self.size * 2}] {file} to MP3')
                self.update_bar(percent)

                mp4_path = os.path.join(self.path, file)
                mp3_path = os.path.join(self.path, os.path.splitext(file)[0]+'.mp3')
                new_file = mp.AudioFileClip(mp4_path)
                new_file.write_audiofile(mp3_path)
                os.remove(mp4_path)

        self.update_bar(-1)        

        return True

    def thanks(self):
        """print thanks message on the GUI

        :return: if successful, true; otherwise, false 
        """

        # thanks message
        sleep(0.5)
        self.print('\nFollow me on github.com/jefferson-lopes')
        sleep(0.5)
        self.print('\nand linkedin.com/in/lopes-jefferson\n')
        sleep(0.5)
        self.print('\nPlease let me know if you spotted any bugs or have any')
        sleep(0.5)
        self.print('\nrecommendations at github.com/jefferson-lopes/openList')

        return True

    def print(self, msg : str):
        """print's wrapper to GUI

        :return: if successful, true; otherwise, false 
        """
        self.progress_text.insert('end', msg)
        self.progress_text.see("end")

        return True

if __name__ == "__main__":
    # create app object
    app = App()

    # mainloop to run application infinitely
    app.mainloop()