import os,sys,shutil
import tensorflow as tf
import numpy as np
import argparse
import cv2,math,glob,random,time
import time
import matplotlib.pyplot as plt
from main import *
from model import *

SAVE_DIR = "modelpre-GT-Proposed-GRL-cx"
OUT_DIR = "outputTest"

def main(folder="val_lr"):
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)
    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)
    folder = folder
    files = os.listdir(folder)

    start = time.time()

    generator = Generator()

    x = tf.placeholder(tf.float32, [1, None, None, 3])
    y = generator.ThermalSR(x,isTraining=False)

    g_vars = [x for x in tf.trainable_variables() if "ThermalSR" in x.name]

    print("%.4e sec took building model"%(time.time()-start))

    sess = tf.Session()
    init = tf.global_variables_initializer()
    sess.run(init)
    saver = tf.train.Saver()

    ckpt = tf.train.get_checkpoint_state(SAVE_DIR)
    if ckpt:
        last_model = ckpt.model_checkpoint_path
        print ("load " + last_model)
        saver.restore(sess, last_model)
        print("succeed restore model")
    else:
        init = tf.global_variables_initializer()
        sess.run(init)

    print("%.4e sec took initializing"%(time.time()-start))

    start = time.time()

    folder=folder
    files = os.listdir(folder)
    for i in range(len(files)):

        print(files[i])
        img = cv2.imread("{}/{}".format(folder,files[i]))
        img = (img-127.5)/127.5

        h,w = img.shape[:2]

        input= img.reshape(1, h, w, 3)

        out = sess.run(y,feed_dict={x:input})

        #X_ = cv2.resize(img,(w*2,h*2),interpolation = cv2.INTER_CUBIC)
        #X_ = cv2.resize(img,(w*4,h*4),interpolation = cv2.INTER_NEAREST)

        Y_ = out.reshape(h*4,w*4,3)
        print("output shape is ",Y_.shape)

        #X_ = (X_ + 1)*127.5
        Y_ = (Y_ + 1)*127.5
        cv2.imwrite("{}/{}".format(OUT_DIR, files[i]), Y_)
        #cv2.imwrite("{}/{}_xval.png".format(OUT_DIR, i), X_)
        #cv2.imwrite("{}/{}_yval.png".format(OUT_DIR, i), Y_)
        #Z_ = np.concatenate((X_,Y_), axis=1)

        #cv2.imwrite("{}/{}_val.png".format(OUT_DIR,i), Z_)

    print("%.4e sec took for predicting" %(time.time()-start))

if __name__ == '__main__':
    folder = "val_lr"
    try:
        folder = sys.argv[1]
    except:
        pass
    main(folder)