import random

from flask import Flask, request, send_file, make_response
import base64
import json

app = Flask(__name__)
users = {}


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
