from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from PIL import ImageFont
from moviepy.editor import *
import gc
import re
import textwrap
from better_profanity import profanity
from profanity_check import predict

import contruct


def generate(text):
    #replace #textbox with nothing
    text = text.replace("#textbox", "")

    #if there is arial tag then use arial font else use oneshot font
    if "#arial" in text:
        contruct.font = ImageFont.truetype("res/arial.ttf", 20)
        text = text.replace("#arial", "")
    else:
        contruct.font = ImageFont.truetype("res/font.ttf", 20)
    
    data = []

    text = text.strip()
    #find all match of dialog face name -> niko: , niko_sad:, etc and store it on data_face
    data_face = re.findall(".*?:",text)

    #split the dialog data content -> niko:       -> ["\n","hello","oh"]
    #                                 hello
    #                                 niko_sad:
    #                                 oh
    data_dialog = re.split(".*?:",text)

    #get rid of that first index
    #["hello","oh"]
    data_dialog.pop(0)

    #this is unlikely to happen but when the dialog data face length is different than data dialog length then raise an exception
    if len(data_face) != len(data_dialog):
        raise Exception("dialog face and data dialog length is not same")

    for i in range(0,len(data_dialog)):

        #replace all whitespaces char with space and split it by space
        data_dialog_arr = re.sub("\s+"," ",data_dialog[i]).split(" ")
        data_dialog_arr_temp = []

        #if there is a word that has a length greather than 47 then split it and add it to temp array
        for index in range(0,len(data_dialog_arr)):
            if len(data_dialog_arr[index]) > 47:
                data_dialog_arr_temp.append(textwrap.wrap(data_dialog_arr[index],2))
            else:
                data_dialog_arr_temp.append(data_dialog_arr[index])
        
        #set the final array to the temp array
        data_dialog_arr = data_dialog_arr_temp

        data_dialog_str = ""
        temp_data_dialog = ""

        for word in data_dialog_arr:
            #auto wrap stuff
            if len(temp_data_dialog + word) > 47:
                data_dialog_str += '\n'
                temp_data_dialog = ""
            
            temp_data_dialog += word + " "
            data_dialog_str += word + " "
        
        #maximum text per dialog
        if len(data_dialog_str.rstrip()) > 188:
            raise Exception("text is too long make new dialog to add more text")

        #just in case strip the string "annas    " -> "annas"
        data_dialog[i] = data_dialog_str.rstrip()
    
    #build the text data replace the : with nothing and also strip it just in case
    for i in range(0,len(data_face)):
        data.append(contruct.TextBoxData(data_face[i].replace(":","").strip(),data_dialog[i].strip()))

    text_combine = ""

    #combine all data dialog for filter checking
    for i in data:
        text_combine += i.text + ' '
    
    #filter text through 2 filters
    if profanity.contains_profanity(text_combine):
        raise Exception("bot detect that there is bad word in your text please delete it")
    elif predict([text_combine])[0] == 1:
        raise Exception("ai detect that there is bad word in your text please delete it")
    
    #maximum text length
    if len(text_combine.replace(" " ,"")) > 1000:
        raise Exception("text is too long maximum characters is 1000")

    #contruct the video
    imgs, audioclips = contruct.generate_textboxes(data)

    data = None
    gc.collect()

    audio = concatenate_audioclips(audioclips)
    clip = ImageSequenceClip(imgs, 30)

    imgs = None
    audioclips = None
    gc.collect()

    clip.audio = audio
    audio = None
    gc.collect()
    
    #write it to a file
    clip.write_videofile("video.mp4",temp_audiofile="temp-audio.m4a", remove_temp=True, codec="libx264",
                         audio_codec="aac",bitrate="300k")
    clip = None
    gc.collect()
