from ai import MER
from ai.utils import *
import cv2
import torchvision.transforms as transforms
import torch
import ai.MER
import numpy as np
import dlib
import math
from ai.face_detector import get_face_detector, find_faces
from ai.face_landmarks import get_landmark_model, detect_marks
import copy

def Processing(img):
    """ =================== headorientation =================== """

    # Instanciation du modèle DNN à utiliser
    modelFile = "../resources/models/res10_300x300_ssd_iter_140000.caffemodel"
    configFile = "../resources/models/deploy.prototxt.txt"
    net = cv2.dnn.readNetFromCaffe(configFile, modelFile)


    size = img.shape

    face_model = get_face_detector()
    landmark_model = get_landmark_model()

    # 3D model points.
    model_points = np.array([
        (0.0, 0.0, 0.0),  # Nose tip
        (0.0, -330.0, -65.0),  # Chin
        (-225.0, 170.0, -135.0),  # Left eye left corner
        (225.0, 170.0, -135.0),  # Right eye right corne
        (-150.0, -150.0, -125.0),  # Left Mouth corner
        (150.0, -150.0, -125.0)  # Right mouth corner
    ])

    # Camera internals
    focal_length = size[1]
    center = (size[1] / 2, size[0] / 2)
    camera_matrix = np.array(
        [[focal_length, 0, center[0]],
         [0, focal_length, center[1]],
         [0, 0, 1]], dtype="double"
    )

    # Outputs
    orientation = ""

    faces = find_faces(img, face_model)

    for face in faces:
        marks = detect_marks(img, landmark_model, face)
        # mark_detector.draw_marks(img, marks, color=(0, 255, 0))
        image_points = np.array([
            marks[30],  # Nose tip
            marks[8],  # Chin
            marks[36],  # Left eye left corner
            marks[45],  # Right eye right corne
            marks[48],  # Left Mouth corner
            marks[54]  # Right mouth corner
        ], dtype="double")
        dist_coeffs = np.zeros((4, 1))  # Assuming no lens distortion
        (success, rotation_vector, translation_vector) = cv2.solvePnP(model_points, image_points, camera_matrix,
                                                                      dist_coeffs, flags=cv2.SOLVEPNP_UPNP)

        # Project a 3D point (0, 0, 1000.0) onto the image plane.
        # We use this to draw a line sticking out of the nose

        (nose_end_point2D, jacobian) = cv2.projectPoints(np.array([(0.0, 0.0, 1000.0)]), rotation_vector,
                                                         translation_vector, camera_matrix, dist_coeffs)

        p1 = (int(image_points[0][0]), int(image_points[0][1]))
        p2 = (int(nose_end_point2D[0][0][0]), int(nose_end_point2D[0][0][1]))
        x1, x2 = head_pose_points(img, rotation_vector, translation_vector, camera_matrix)

        try:
            m = (p2[1] - p1[1]) / (p2[0] - p1[0])
            ang1 = int(math.degrees(math.atan(m)))
        except:
            ang1 = 90

        try:
            m = (x2[1] - x1[1]) / (x2[0] - x1[0])
            ang2 = int(math.degrees(math.atan(-1 / m)))
        except:
            ang2 = 90

            # print('div by zero error')
        if ang1 >= 20:
            orientation = 'down'
        elif ang1 <= -40:
            orientation = 'up'

        if ang2 >= 35:
            orientation = 'right'
        elif ang2 <= -35:
            orientation = 'left'

        elif (ang2 > -35 and ang2 < 35 and ang1 > -40 and ang1 < 20):
            orientation = 'front'

    # print(orientation) # ======================================================================== The info we need : front, up, down, left, right

    """ =================== eyetracking =================== """

    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor('../resources/models/shape_predictor_68_face_landmarks.dat')

    def eye_on_mask(mask, side):
        points = [shape[i] for i in side]
        points = np.array(points, dtype=np.int32)
        mask = cv2.fillConvexPoly(mask, points, 255)
        return mask

    left = [36, 37, 38, 39, 40, 41]
    right = [42, 43, 44, 45, 46, 47]

    kernel = np.ones((9, 9), np.uint8)
    glance = ""

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

        if abs(Righteye[0] - midx) > abs(Lefteye[0] - midx) + 10:
            glance = 'left'
        elif abs(Lefteye[0] - midx) > abs(Righteye[0] - midx) + 10:
            glance = 'right'
        elif Righteye[1] < midy - 2 and Lefteye[1] < midy - 2:
            glance = 'up'
        elif Righteye[1] > midy + 4 and Lefteye[1] > midy + 4:
            glance = 'down'
        elif abs(Righteye[0] - midx) <= abs(Lefteye[0] - midx) + 10 and abs(Lefteye[0] - midx) <= abs(
                Righteye[0] - midx) + 10 and Righteye[1] >= midy - 2 and Righteye[1] <= midy + 4 and Lefteye[
            1] >= midy - 2 and Lefteye[1] <= midy + 4:
            glance = 'front'

    # print(glance) # ======================================================================== The info we need : front, up, down, left, right

    """ =================== microexpressions =================== """

    # GPU if available, else CPU
    device = MER.get_default_device()
    print("Selected device:", device)

    # Loading pretrained weights
    w = '../resources/models/MERCnn.pth'
    model = MER.to_device(MER.MERCnnModel(), device)
    if str(device) == 'cpu':
        model.load_state_dict(torch.load(w, map_location=torch.device('cpu')))  # use for cpu
    if str(device) == 'gpu':
        model.load_state_dict(torch.load(w, map_location=torch.device('cuda')))  # for GPU

    frame = copy.copy(img)
    width, height = frame.shape[1], frame.shape[2]

    bBox = MER.faceBox(frame)
    if len(bBox) > 0:
        for box in bBox:
            x, y, w, h = int(box.xmin * width), int(box.ymin * height), int(box.width * width), int(box.height * height)
            faceExp = frame[y:y + h, x:x + w]
            try:
                faceExpResized = cv2.resize(faceExp, (80, 80))
                transform = transforms.ToTensor()
                faceExpResizedTensor = transform(faceExpResized)
            except:
                continue
            prediction = MER.predict_image(faceExpResizedTensor, model, device)

        # print(prediction)

    if prediction or glance or orientation:
        if not prediction:
            prediction = 'null'
        elif not glance:
            glance = 'null'
        elif not orientation:
            orientation = 'null'

        datavector = [orientation, glance, prediction]
        print(datavector)

    if datavector:
        return datavector
    else:
        return ['null', 'null', 'null']