from utils import *
import cv2
import torchvision.transforms as transforms
import torch
import MER
import numpy as np
import dlib
import math
from face_detector import get_face_detector, find_faces
from face_landmarks import get_landmark_model, detect_marks

""" =================== headorientation =================== """

# Instanciation du modèle DNN à utiliser
modelFile = "../resources/models/res10_300x300_ssd_iter_140000.caffemodel"
configFile = "../resources/models/deploy.prototxt.txt"
net = cv2.dnn.readNetFromCaffe(configFile, modelFile)

img = cv2.imread('../resources/test.jpg')
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
    (success, rotation_vector, translation_vector) = cv2.solvePnP(model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_UPNP)

    # Project a 3D point (0, 0, 1000.0) onto the image plane.
    # We use this to draw a line sticking out of the nose

    (nose_end_point2D, jacobian) = cv2.projectPoints(np.array([(0.0, 0.0, 1000.0)]), rotation_vector, translation_vector, camera_matrix, dist_coeffs)

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
        orientation = "down"
    elif ang1 <= -40:
        orientation = "up"

    if ang2 >= 35:
        orientation = "right"
    elif ang2 <= -35:
        orientation = "left"

    elif (ang2 > -35 and ang2 < 35 and ang1 > -40 and ang1 < 20) :
        orientation = "front"

print(orientation) # ======================================================================== The info we need : front, up, down, left, right


""" =================== eyetracking =================== """





""" =================== microexpressions =================== """