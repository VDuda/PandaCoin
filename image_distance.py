import time
import cv2
import os
import openface
import numpy as np

# Load Models
def load_model():
    dlibModelDir = os.path.join("/opt/openface/models/dlib/")
    openfaceModelDir = os.path.join("/opt/openface/models/openface/")
    start = time.time()
    align = openface.AlignDlib(dlibModelDir + "shape_predictor_68_face_landmarks.dat")
    net = openface.TorchNeuralNet(openfaceModelDir + "nn4.small2.v1.t7", 96)
    print(" Model loading took {} seconds.".format(time.time() - start))
    config = (align, net)
    return config


# Feature Extraction
def getRep(rgbImg, config):

    align, net = config
    start = time.time()
    bb = align.getLargestFaceBoundingBox(rgbImg)
    if bb is None:
        raise Exception("Unable to find a face")
    print("  + Face detection took {} seconds.".format(time.time() - start))

    start = time.time()
    alignedFace = align.align(96, rgbImg, bb,
                              landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
    if alignedFace is None:
        raise Exception("Unable to align image: {}".format(imgPath))

    rep = net.forward(alignedFace)

    return rep



