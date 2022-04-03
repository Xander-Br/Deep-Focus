import random

from flask import Flask, request, send_file, make_response
import base64
import json

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

@app.route("/calculateScore", methods = ["POST"])
def calculateScore():
    data = request.form
    if(userExist(data["name"])):
        user_id = getUserIndexByUsername(data["name"])
    else:
        users_list.append(User(data["id"], data["name"], ""))
    print(data["name"])
    return data["name"]


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

