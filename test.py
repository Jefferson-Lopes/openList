from pytube import YouTube
from pytube import Playlist
import moviepy.editor as mp
import os
import re

# playlist link or one video link of the playlist
link = 'https://www.youtube.com/playlist?list=PL0ACAD8FCBB343FE3'
folder = "/Users/jeff7/Área de Trabalho/playlist"

# find playlist ID inside the link
for peace in re.split('[&?]', link):
    if 'list=' in peace:
        global id 
        id = peace.split('=')[1] # remove 'list=' from string
        print(F'\nPlaylist ID: {id}')
        break
else:
    raise Exception('playlist id not found')

# create playlist object
playlist = Playlist("https://www.youtube.com/playlist?list=" + id)

# start downloading
print(f'\nPlaylist Name: {playlist.title}')
print('\nDownloading Videos . . .\n')
for url, video in zip(playlist, playlist.videos):
    video_title = video.title

    try:
        YouTube(url).streams.filter(only_audio=True).first().download(folder)
    except:
        print(F'ERROR on {video_title} - download skipped')
    else:
        print(video_title)

# convert files from MP4 to MP3
print('\nConverting to MP3 . . .\n')
for file in os.listdir(folder):
  if re.search('mp4', file):
    mp4_path = os.path.join(folder, file)
    mp3_path = os.path.join(folder, os.path.splitext(file)[0]+'.mp3')
    new_file = mp.AudioFileClip(mp4_path)
    new_file.write_audiofile(mp3_path)
    os.remove(mp4_path)