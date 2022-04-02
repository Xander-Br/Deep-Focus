import cv2
import numpy as np
import tensorflow as tf
from tensorflow import keras

# Code from https://towardsdatascience.com/real-time-head-pose-estimation-in-python-e52db1bc606a

""" =================== Modèle reconnaissance faciale =================== """

# Instanciation du modèle DNN à utiliser
modelFile = "../resources/models/res10_300x300_ssd_iter_140000.caffemodel"
configFile = "../resources/models/deploy.prototxt.txt"
net = cv2.dnn.readNetFromCaffe(configFile, modelFile)

img = cv2.imread('../resources/test.jpg') # Load image de test => remplacer par frames par la suite
h, w = img.shape[:2] # Récupère dimensions de l'image
# On donne l'image au DNN (resize à 300x300 pour que ça fonctionne mieux)
blob = cv2.dnn.blobFromImage(cv2.resize(img, (300, 300)), 1.0, (300, 300), (104.0, 117.0, 123.0))
net.setInput(blob)
# Recupère les visages identifiés
faces = net.forward()


# Pour dessiner les visages sur l'image
for i in range(faces.shape[2]):
        confidence = faces[0, 0, i, 2]
        if confidence > 0.5:
            box = faces[0, 0, i, 3:7] * np.array([w, h, w, h])
            (x, y, x1, y1) = box.astype("int")
            cv2.rectangle(img, (x, y), (x1, y1), (0, 0, 255), 2)

# test affichage image
cv2.imshow("Test_image", img)
cv2.waitKey(0)


""" Modèle reconnaissance orientation de la tête """














