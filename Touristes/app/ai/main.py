from ai.genprocess import Processing
import cv2
import time

t0 = time.time()
width, height = 1280, 720
img = cv2.imread('../resources/test3.jpg')
cv2.resize(img, (width, height))
datavect = Processing(img)
print(time.time()-t0)

#poss01 = ['null', 'front', 'up', 'down', 'left', 'right']
#poss2 = ['anger', 'disgust', 'fear', 'happiness', 'neutral', 'sadness', 'surprise']
def attentionCompute(datavect):
    score = 0
    tet = datavect[0]
    reg = datavect[1]
    emo = datavect[2]

    if tet == 'null':
        score = 0

    elif tet == 'up':
        if reg != 'down':
            score = 0
        else:
            if emo == 'happiness' or emo == 'surprise':
                score = 1
            else :
                score = 0.5

    elif tet == 'left':
        if reg != 'right':
            score = 0
        else:
            if emo == 'happiness' or emo == 'neutral' or emo == 'surprise':
                score = 1
            else :
                score = 0.5

    elif tet == 'right':
        if reg != 'left':
            score = 0
        else:
            if emo == 'happiness' or emo == 'neutral' or emo == 'surprise':
                score = 1
            else :
                score = 0.5

    elif tet == 'down':
        if reg == 'left' or reg == 'right':
            score = 0
        else:
            if emo == 'disgust' and reg == 'up':
                score = 1
            elif emo == 'surprise' or emo == 'anger':
                if reg == 'front' or reg == 'up':
                    score = 1
                else:
                    score = 0.5
            elif emo == 'happiness' or emo == 'neutral':
                if reg != 'down':
                    score = 1
                else:
                    score = 0.5
            else:
                score = 0.5

    elif tet == 'front':
        if reg == 'up' or reg == 'right' or reg == 'left':
            score = 0
        else:
            if emo == 'neutral' or emo =='happiness':
                score = 1
            elif emo == 'surprise':
                if reg == 'down':
                    score = 0.5
                else:
                    score = 1
            else:
                score = 0.5

    return score

# test vector
#datavect = ['front', 'front', 'neutral']
print(attentionCompute(datavect))








