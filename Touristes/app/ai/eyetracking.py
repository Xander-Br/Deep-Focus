import cv2
import dlib
import numpy as np

# Code based on https://towardsdatascience.com/real-time-eye-tracking-using-opencv-and-dlib-b504ca724ac6

def shape_to_np(shape, dtype="int"):
    # initialize the list of (x, y)-coordinates
    coords = np.zeros((68, 2), dtype=dtype)
    # loop over the 68 facial landmarks and convert them
    # to a 2-tuple of (x, y)-coordinates
    for i in range(0, 68):
        coords[i] = (shape.part(i).x, shape.part(i).y)
    # return the list of (x, y)-coordinates
    return coords


def eye_on_mask(mask, side):
    points = [shape[i] for i in side]
    points = np.array(points, dtype=np.int32)
    mask = cv2.fillConvexPoly(mask, points, 255)
    return mask


def contouring(thresh, mid, img, right=False):
    cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    try:
        cnt = max(cnts, key=cv2.contourArea)
        #print(cnt, ' # ')
        M = cv2.moments(cnt)
        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])
        #print(cnt, ' # ', mid)
        if right:
            cx += mid
        cv2.circle(img, (cx, cy), 4, (0, 0, 255), 2)
        return [cx, cy, cnt]

    except:
        pass



detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('../resources/models/shape_predictor_68_face_landmarks.dat')

left = [36, 37, 38, 39, 40, 41]
right = [42, 43, 44, 45, 46, 47]

cap = cv2.VideoCapture(0)


kernel = np.ones((9, 9), np.uint8)
glance = ""

while (True):
    ret, img = cap.read()
    #img = cv2.imread('../resources/translL.jpg')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 1)
    # rect = Position des yeux, pas de l'iris
    for rect in rects:
        shape = predictor(gray, rect)
        shape = shape_to_np(shape)
        mask = np.zeros(img.shape[:2], dtype=np.uint8)
        mask = eye_on_mask(mask, left)
        mask = eye_on_mask(mask, right)
        mask = cv2.dilate(mask, kernel, 5)
        eyes = cv2.bitwise_and(img, img, mask=mask)
        mask = (eyes == [0, 0, 0]).all(axis=2)
        eyes[mask] = [255, 255, 255]
        midx = (shape[42][0] + shape[39][0]) // 2
        midy = (shape[27][1] + shape[27][1]) // 2
        eyes_gray = cv2.cvtColor(eyes, cv2.COLOR_BGR2GRAY)
        threshold = 100
        _, thresh = cv2.threshold(eyes_gray, threshold, 255, cv2.THRESH_BINARY)
        thresh = cv2.erode(thresh, None, iterations=2)  # 1
        thresh = cv2.dilate(thresh, None, iterations=4)  # 2
        thresh = cv2.medianBlur(thresh, 3)  # 3
        thresh = cv2.bitwise_not(thresh)
        # Trace les iris en rouge
        Lefteye = contouring(thresh[:, 0:midx], midx, img)
        Righteye = contouring(thresh[:, midx:], midx, img, True)

        cv2.circle(img, (midx, midy), 4, (255, 0, 0), 2)



        if abs(Righteye[0]-midx) > abs(Lefteye[0]-midx)+10:
            glance = "Left"
        elif abs(Lefteye[0]-midx) > abs(Righteye[0]-midx)+10:
            glance = "Right"
        elif Righteye[1] < midy - 2 and Lefteye[1] < midy - 2:
            glance = "Up"
        elif Righteye[1] > midy + 4 and Lefteye[1] > midy + 4:
            glance = "Down"
        elif abs(Righteye[0]-midx) <= abs(Lefteye[0]-midx)+10 and abs(Lefteye[0]-midx) <= abs(Righteye[0]-midx)+10 and Righteye[1] >= midy - 2 and Righteye[1] <= midy + 4 and Lefteye[1] >= midy-2 and Lefteye[1] <= midy+4 :
            glance = "Front"
        # for (x, y) in shape[36:48]:
        #     cv2.circle(img, (x, y), 2, (255, 0, 0), -1)
    # show the image with the face detections + facial landmarks
    cv2.imshow('eyes', img)

    if cv2.waitKey(5) & 0xFF == ord('c'):

        print(glance)
        #print('Left : [', Lefteye[0], ' ; ', Lefteye[1], ']')
        #print('Right : [', Righteye[0], ' ; ', Righteye[1], ']')
        #print('Middle : [', midx, ' ; ', midy, ']\n -------------------------- ')

    elif cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()


"""Recupérer la variable glance pour le calcul du score d'attention"""