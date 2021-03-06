from helper import get_gpt
import random
import time

import generate_video
import upload
from twitter_api import twitter,auth
import gc
import os
from better_profanity import profanity
from profanity_check import predict
import _thread


#delete a dm function
def send_then_delete_dm(sender_id, message):
    twitter.send_direct_message(sender_id, message).destroy()

def human_generation(thread_name):
    print("thread " + thread_name + " starting")
    while True:
        dms = None
        already_tweeted = []

        try:
            dms = twitter.list_direct_messages(120)
            #keep checking while there's no new message
            while len(dms) == 0:
                time.sleep(120)
                
                dms = twitter.list_direct_messages(120)
            dms.reverse()
        except:
            continue
        
        for dm in dms:
            try:
                #get the dms data
                data = dm.message_create["message_data"]
                text = data["text"]
                sender_id = dm.message_create["sender_id"]

                #check if there's a face tag and just send the img and continue to the next dm
                if "#faces" in text:
                    dm.destroy()
                    media = twitter.media_upload("img.png")
                    faces_dm = twitter.send_direct_message(sender_id, text="", attachment_type="media",
                                                            attachment_media_id=media.media_id)
                    faces_dm.destroy()
                    time.sleep(random.randrange(2, 4))
                    continue

                if "#post" in text:
                    dm.destroy()
                    text = text.replace("#post","").strip()
                    
                    if predict([text])[0] == 1:
                        raise Exception(f"ai detect that there is bad word in your text \"{text}\"")
                    
                    text = f"{text}\n-@{twitter.get_user(dm.message_create['sender_id']).screen_name}"
                    
                    if len(text) > 280:
                        raise Exception("text is too long")
                    
                    
                    send_then_delete_dm(sender_id, "request is accepted please wait for moment for the request to be process")

                    print("patch")

                    twitter.update_status(text)
                    continue

                #if there is no textbox tag then quicky delete the message and moveon
                if not "#textbox" in text or text in already_tweeted:
                    dm.destroy()
                    continue

                #if there's is textbox tag then build the video and send it back to the sender
                dm.destroy()
                already_tweeted.append(text)
                generate_video.generate(text)
                send_then_delete_dm(sender_id, "request is accepted please wait for moment for the request to be process")

                uploader = upload.VideoTweet("video.mp4", auth.apply_auth())
                uploader.upload(f"Requested by @{twitter.get_user(dm.message_create['sender_id']).screen_name}")
                uploader = None
                
                gc.collect()
                os.remove("video.mp4")
            except Exception as ex:
                #if there is error send it to the user and sleep for random 1 - 3 seconds
                message = repr(ex)

                if "that page does not exist" not in message:
                    print(message)
                    response = twitter.send_direct_message(dm.message_create["sender_id"],message)
                    response.destroy()
                    time.sleep(random.randrange(1, 3))

# def ai_generation(thread_name):
#     print("thread " + thread_name + " starting")

#     while True:
#         try:
#             with open("input.txt" ,"r") as file:
#                 input_text = file.read()

#             input_text = input_text.split("\n\n")

#             rand_index = random.randrange(len(input_text))

#             text = get_gpt("\n\n".join(input_text[:rand_index]))
#             generate_video.generate(text)
#             text = None

#             uploader = upload.VideoTweet("video.mp4", auth.apply_auth())
#             uploader.upload("AI tries to continue\n" + input_text[rand_index])
#             uploader = None
            
#             gc.collect()
#             os.remove("video.mp4")
#         except:
#             continue
        
#         time.sleep(60 * 60 * 10)

_thread.start_new_thread(human_generation, ("human",))
# _thread.start_new_thread(ai_generation, ("ai",))

while 1:
    pass