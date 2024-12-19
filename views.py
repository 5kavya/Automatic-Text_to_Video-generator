from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings
import os
import pymysql
from django.core.files.storage import FileSystemStorage
from datetime import datetime
from story import generate_story, save_story
from image import search_images, download_images
from voice import generate_voiceover
from caption import create_caption_images, add_captions_to_video
import moviepy.editor as mpy
import os

import warnings
warnings.filterwarnings('ignore')

global username, story_data, prompt

def process_images(prompt):
    for root, dirs, directory in os.walk("GeneratorApp/static/video_images"):
        for j in range(len(directory)):
            os.remove(root+"/"+directory[j])
    image_urls = search_images(prompt, num_images=5)
    download_images(image_urls, save_dir="GeneratorApp/static/video_images")
    return [f"GeneratorApp/static/video_images/image_{i}.jpg" for i in range(len(image_urls))]

def create_final_video(images, voiceover_path, output_video_path):
    clips = [mpy.ImageClip(img).set_duration(5) for img in images]
    video = mpy.concatenate_videoclips(clips, method="compose")

    audio = mpy.AudioFileClip(voiceover_path)
    video = video.set_audio(audio)
    video.write_videofile(output_video_path, codec="libx264", fps=24)

def GenerateVideo(request):
    if request.method == 'POST':
        global username, story_data, prompt
        story = request.POST.get('t1', False)
        images = process_images(prompt)
        voiceover_path = "GeneratorApp/static/voice.mp3"
        if os.path.exists(voiceover_path):
            os.remove(voiceover_path)
        generate_voiceover(story_data, voiceover_path)
        if os.path.exists("GeneratorApp/static/output_video.mp4"):
            os.remove("GeneratorApp/static/output_video.mp4")    
        create_final_video(images, voiceover_path, "GeneratorApp/static/output_video.mp4")
        context= {'data':'Video Generated Successfully'}
        return render(request, 'PlayVideo.html', context)

def GenerateStoryAction(request):
    if request.method == 'POST':
        global username, story_data, prompt
        prompt = request.POST.get('t1', False)
        story_data = generate_story(prompt)
        if os.path.exists("GeneratorApp/static/story.txt"):
            os.remove("GeneratorApp/static/story.txt")        
        save_story(story_data, "GeneratorApp/static/story.txt")
        output = '<tr><td><font size="3" color="black">Generated&nbsp;Story</td><td><textarea name="t1" rows="10" cols="70">'+story_data+'</textarea></td></tr>'
        context= {'data':output}
        return render(request, 'GenerateVideo.html', context)

def GenerateStory(request):
    if request.method == 'GET':
       return render(request, 'GenerateStory.html', {})

def UserLogin(request):
    if request.method == 'GET':
       return render(request, 'UserLogin.html', {})

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

def Register(request):
    if request.method == 'GET':
       return render(request, 'Register.html', {})    

def RegisterAction(request):
    if request.method == 'POST':
        global username
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        contact = request.POST.get('t3', False)
        email = request.POST.get('t4', False)
        address = request.POST.get('t5', False)
        
        output = "none"
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'video',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select username FROM users")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == username:
                    output = username+" Username already exists"
                    break                
        if output == "none":
            db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'video',charset='utf8')
            db_cursor = db_connection.cursor()
            student_sql_query = "INSERT INTO users VALUES('"+username+"','"+password+"','"+email+"','"+contact+"','"+address+"')"
            db_cursor.execute(student_sql_query)
            db_connection.commit()
            print(db_cursor.rowcount, "Record Inserted")
            if db_cursor.rowcount == 1:
                output = "New User Details Successfully updated to backend"
        context= {'data':output}
        return render(request, 'Register.html', context)

def UserLoginAction(request):
    global username
    if request.method == 'POST':
        global username
        status = "none"
        users = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'video',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select username,password FROM users")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == users and row[1] == password:
                    username = users
                    status = "success"
                    break
        if status == 'success':
            context= {'data':'Welcome '+username}
            return render(request, "UserScreen.html", context)
        else:
            context= {'data':'Invalid username'}
            return render(request, 'UserLogin.html', context)

    
