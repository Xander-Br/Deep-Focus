import io
import random

import cv2
import numpy as np
#from PIL.Image import Image
from flask import Flask, request, send_file, make_response
import base64
import json

from PIL import Image

from ai.genprocess import Processing
from ai.main import attentionCompute
from api.models.user import User


app = Flask(__name__)
users = {}
users_list = []

def userExist(username):
    for user in users_list:
        if username == user.name:
            return True
        return False

def getUserIndexByUsername(username):
    for user in users_list:
        if username == user.name:
            return users_list.index(user)

# Take in base64 string and return PIL image
def stringToImage(base64_string):
    imgdata = base64.b64decode(base64_string)
    return Image.open(io.BytesIO(imgdata))

def toRGB(image):
    return cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)

@app.route("/calculateScore", methods = ["POST"])
def calculateScore():
    data = request.form
    if(userExist(data["name"])):
        user_id = getUserIndexByUsername(data["name"])
        data = stringToImage(data["img"])
        data = toRGB(data)
        score = attentionCompute(Processing(data))
        print(score)
        users_list[user_id].score.append(score)
    else:
        users_list.append(User(data["id"], data["name"], ""))
    return "Done"


@app.route("/put_frame/")
def put_frame():
    user = request.args.get('user')

    frame = base64.b64decode(request.args.get('frame'))

    with open("test.jpeg", "wb") as f:
        f.write(frame)
        # Obtention du score d'attention
        # score = x.compute_score(frame)

    score = random.randint(20, 100)

    if user not in users:
        users[user] = []
    users[user].append(score)

    return "<p>Addend, score : " + str(score) + "</p>"


@app.route("/get_scores/")
def get_scores():

    return json.dumps(users)


if __name__ == "__main__":
    app.run(debug=True)

