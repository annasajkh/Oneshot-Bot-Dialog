import glob

from PIL import Image, ImageDraw
from moviepy.audio.fx.volumex import volumex
from moviepy.editor import *
from numpy import array

#character that should have robot sound
robot_sound = ["en", "bookbot", "kelvin", "prophet", "proto", "gatekeeper", "rowbot", "silver","bot"]
faces = {}
font = None

#textbox class
class TextBoxData:
    def __init__(self, face_name=None, text=""):
        self.face_name = face_name
        self.text = text

#load the sounds and set the volume
background = Image.open("res/background.png")
normal_dialog = AudioFileClip("res/normal_dialog.wav")
normal_dialog = normal_dialog.fx(volumex, 0.2)
robot_dialog = AudioFileClip("res/robot_dialog.wav")
robot_dialog = robot_dialog.fx(volumex, 0.2)
silent = robot_dialog.fx(volumex, 0)

#get all face name
for infile in glob.glob("res/faces/*.png"):
    faces[infile.split("/")[2].split(".")[0]] = None


def generate_img(face_name=None, text=""):
    #build a frame 
    img = trans_paste(background, faces[face_name], (496, 17))
    draw = ImageDraw.Draw(img)
    draw.multiline_text((20, 14 + (img.size[1] // 2 - background.size[1] // 2)), text, font=font)
    
    return array(img)


def generate_textboxes(data):
    imgs = []
    audioclips = []
    #it there's the face is not loaded yet then load it but if it's already loaded then don't load it again
    for i in data:
        try:
            if faces[i.face_name] == None:
                    faces[i.face_name] = Image.open(f"res/faces/{i.face_name}.png")
        except:
            raise Exception(f"there are no face named {i.face_name}")
    
    #and little more frames to match the sound
    for i in data:
        length = len(i.text)
        if length == 1:
            i.text = i.text + "  "
        elif length == 2:
            i.text = i.text + " "
        elif length % 3 == 1:
            i.text = i.text + "  "
        elif length % 3 == 2:
            i.text = i.text + " "

        text_temp = ""
        is_robot = False

        #checking if it's a robot by checking face name
        for j in robot_sound:
            if j in i.face_name:
                is_robot = True
                break
        #add the talking sound corresponding to the type is it a robot or not 
        for j in range(len(i.text) // 3):
            if is_robot:
                audioclips.append(robot_dialog)
            else:
                audioclips.append(normal_dialog)
        
        #add delay audio
        for j in range(0, 10):
            audioclips.append(silent)
        
        #add frames per character in the text
        for j in range(len(i.text)):
            imgs.append(generate_img(face_name=i.face_name, text=text_temp))
            text_temp += i.text[j]
        
        # add delay frame
        for j in range(0, 30):
            imgs.append(generate_img(face_name=i.face_name, text=text_temp))
    
    #unload all the images so it doesn't eat up memory
    for i in data:
        faces[i.face_name] = None
    
    return imgs, audioclips


def trans_paste(bg_img, fg_img, box):
    #paste the face to the textbox in the correct location 
    bg_img = bg_img.convert("RGBA")
    fg_img = fg_img.convert("RGBA")

    img = Image.new("RGBA", (bg_img.size[0], int(bg_img.size[1] * 1.6)))

    img.paste(bg_img, (0, img.size[1] // 2 - background.size[1] // 2), mask=bg_img)
    img.paste(fg_img, (box[0], box[1] + (img.size[1] // 2 - background.size[1] // 2)), mask=fg_img)

    return img
