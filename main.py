import smtplib
import urllib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import streamlit as st
from time import sleep
import re
import zipfile
from moviepy.editor import VideoFileClip,concatenate_videoclips
from moviepy.editor import concatenate_audioclips, AudioFileClip
from youtube_search import YoutubeSearch
import json
from pytube import Playlist,YouTube
from pytube.exceptions import VideoUnavailable
import os
from pydub import AudioSegment

def download_videos_and_convert_into_audio(singer, n):
    url="https://www.youtube.com/results?search_query=" + singer + " music video"
    url=url.replace(" ","%20")
    html = urllib.request.urlopen(url)
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    temp_videos = ["https://www.youtube.com/watch?v=" + video_id for video_id in video_ids]
    #make list values unique
    temp_videos = list(set(temp_videos))
    videos = []
    idx = 1
    for video in temp_videos:
        if idx > n:
            break
        yt = YouTube(video)
        if yt.length/60 < 5:
            videos.append(video)
            idx += 1
    destination = "Video_files"
    print('downloading...')
    count=1
    for video in videos:
      with st.spinner(text="Downloading song "+ str(count)+ "..."):
        count+=1
        try:
          yt= YouTube(video)
          video_1 =yt.streams.filter(file_extension='mp4',res="360p").first()
          out_file = video_1.download(output_path=destination)
          basePath, extension = os.path.splitext(out_file)
          video = VideoFileClip(os.path.join(basePath + ".mp4"))
        except:
          print('')
    print('downloaded')

def cut_first_y_sec(singer, n, y):
  print('cutting...')
  directory = "Video_files/"
  clips=[]
  for filename in os.listdir(directory):
      if filename.endswith(".mp4"):
        file_path = os.path.join(directory, filename)
        clip=VideoFileClip(file_path).subclip(0,y)
        audioclip=clip.audio
        clips.append(audioclip)
  concat = concatenate_audioclips(clips)
  concat.write_audiofile('concat.mp3')
  print('cutting done')
def zipit(file):
    destination='mashup.zip'
    zip_file=zipfile.ZipFile(destination,'w')
    zip_file.write(file,compress_type=zipfile.ZIP_DEFLATED)
    zip_file.close()
    return destination
def mail(item,em):
    smtp_port = 587          
    smtp_server = "smtp.gmail.com" 
    email_from = st.secrets["mail"]
    email_to = em
    pswd = st.secrets["code"]
    subject = "mashup mail"
    body = f"""
    This mail was sent for mashup assignment program 2
    """
    with st.spinner(text='Creating your mashup...'):
      msg = MIMEMultipart()
      msg['From'] = email_from
      msg['To'] = email_to
      msg['Subject'] = subject
      msg.attach(MIMEText(body, 'plain'))
      filename = item
      attachment= open(filename, 'rb') 
      attachment_package = MIMEBase('application', 'octet-stream')
      attachment_package.set_payload((attachment).read())
      encoders.encode_base64(attachment_package)
      attachment_package.add_header('Content-Disposition', "attachment; filename= " + filename)
      msg.attach(attachment_package)
      text = msg.as_string()
      print("Connecting to server...")
      TIE_server = smtplib.SMTP(smtp_server, smtp_port)
      TIE_server.starttls()
      TIE_server.login(email_from, pswd)
      print("Succesfully connected to server")
      print()
      print(f"Sending email to: {email_to}...")
      TIE_server.sendmail(email_from, email_to, text)
      print(f"Email sent to: {email_to}")
      print()
      TIE_server.quit()
    st.success('Success! Your mashup will shortly arrive in your mailbox :)')
def script(sn,em,no,dur):
    singer = sn
    n = no
    y = dur
    download_videos_and_convert_into_audio(singer, n)
    cut_first_y_sec(singer,n,y)
    file='concat.mp3'
    mail(zipit(file),em)
with st.form(key="form1"):
    singer_name=st.text_input(label="Singer Name",value='')
    no_of_vids=st.number_input(label="\# of videos",value=0)
    dur=st.number_input(label="duration of each video",value=0)
    email=st.text_input(label="Email Id",value='')
    submit=st.form_submit_button(label="Submit")
    pat = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if submit:
      if not singer_name.strip():
        st.error('WARNING: Please enter the name of singer')
      elif int(no_of_vids)==0:
        st.error('WARNING: No video is selected')
      elif int(dur)==0:
        st.error('WARNING: Duration cannot be 0')
      elif not re.match(pat,email):
        st.error('WARNING: Invalid email! Please try again.')
      else:
        with st.spinner(text = 'Extracting information…'):
          sleep(3)
          folder = 'Video_files'
          for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)  
            if os.path.isfile(file_path) or os.path.islink(file_path): 
              os.unlink(file_path)
        script(singer_name,email,no_of_vids,dur)
