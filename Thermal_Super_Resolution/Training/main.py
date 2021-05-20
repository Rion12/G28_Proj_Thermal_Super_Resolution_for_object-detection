import os,sys,shutil
import tensorflow as tf
import numpy as np
import argparse
import cv2,math,glob,random,time
import time
import matplotlib.pyplot as plt
from model import *
from btgen import BatchGenerator
from vgg import *



TRAIN_LR_DIR = "train_lr"
TRAIN_HR_DIR = "train_hr"
VAL_LR_DIR = "val_lr"
VAL_HR_DIR = "val_hr"
VAL_DIR ="val"
TEST_DIR = "test"
SAVEPRE_DIR ="modelpre-GT-Proposed-GRL-cx"
SAVEIM_DIR ="sample-GT-Proposed-GRL-cx"

if not os.path.exists(SAVEIM_DIR):
    os.makedirs(SAVEIM_DIR)

def tileImage(imgs):
    d = int(math.sqrt(imgs.shape[0]-1))+1
    h = imgs[0].shape[0]
    w = imgs[0].shape[1]
    r = np.zeros((h*d,w*d,3),dtype=np.float32)
    for idx,img in enumerate(imgs):
        idx_y = int(idx/d)
        idx_x = idx-idx_y*d
        r[idx_y*h:(idx_y+1)*h,idx_x*w:(idx_x+1)*w,:] = img
    return r

def printParam(scope):
    total_parameters = 0
    for variable in tf.trainable_variables(scope=scope):
        # shape is an array of tf.Dimension
        shape = variable.get_shape()
        variable_parameters = 1
        for dim in shape:
            variable_parameters *= dim.value
        total_parameters += variable_parameters
    print("{} has {} parameters".format(scope, total_parameters))

def foloderLength(folder):
    dir = folder
    paths = os.listdir(dir)
    return len(paths)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--gpu', type=str, default='0', help='Which GPU to use')
    args = parser.parse_args()
    os.environ['CUDA_VISIBLE_DEVICES'] = args.gpu

    img_size = 64
    bs = 4
    trans_lr = 1e-4

    start = time.time()

    batchgen = BatchGenerator(img_size=img_size,LRDir=TRAIN_LR_DIR,HRDir=TRAIN_HR_DIR,aug=True)
    valgen = BatchGenerator(img_size=img_size,LRDir=VAL_LR_DIR,HRDir=VAL_HR_DIR,aug=False)

    #save samples
    IN_ , OUT_ = batchgen.getBatch(4)[:4]
    print(IN_.shape)
    IN_ = tileImage(IN_)
    IN_ = cv2.resize(IN_,(img_size*2*4,img_size*2*4),interpolation = cv2.INTER_CUBIC)
    IN_ = (IN_ + 1)*127.5
    OUT_ = tileImage(OUT_)
    OUT_ = cv2.resize(OUT_,(img_size*4*2,img_size*4*2))
    OUT_ = (OUT_ + 1)*127.5
    Z_ = np.concatenate((IN_,OUT_), axis=1)
    cv2.imwrite("input.png",Z_)
    print("%s sec took sampling"%(time.time()-start))

    start = time.time()

    x = tf.placeholder(tf.float32, [bs, img_size, img_size, 3])
    t = tf.placeholder(tf.float32, [bs, img_size*4, img_size*4, 3])
    lr = tf.placeholder(tf.float32)

    generator = Generator()

    y = generator.ThermalSR(x)
    test_y = generator.ThermalSR(x, reuse=True, isTraining=False)

    # L1 loss function
    L1_loss = tf.losses.absolute_difference(y, t)

    # Contextual loss function
    #vgg_real = build_vgg19(y)
    #vgg_fake = build_vgg19(t)
   # CX_loss_content_list = [w * CX_loss_helper(vgg_real[layer], vgg_fake[layer], config.CX) 
    											#for layer, w in config.CX.feat_content_layers.items()]
    #CX_content_loss = tf.reduce_sum(CX_loss_content_list)
    #CX_content_loss *= config.W.CX_content
    
    # ssim loss function
    ssim_ = tf.reduce_mean(tf.image.ssim(y,t,2.0))
    ssim_loss = 1-ssim_
    
    # Total loss function
    Total_loss = L1_loss + ssim_loss 


    g_loss = tf.train.AdamOptimizer(1e-4,beta1=0.5).minimize(Total_loss, var_list=[
            x for x in tf.trainable_variables() if "ThermalSR"     in x.name])

    print("%.4f sec took building"%(time.time()-start))
    printParam(scope="ThermalSR")
    
    g_vars = [x for x in tf.trainable_variables() if "ThermalSR"     in x.name]

    saver = tf.train.Saver(max_to_keep=15)

    sess = tf.Session()
    sess.run(tf.global_variables_initializer())

    ckpt = tf.train.get_checkpoint_state(SAVEPRE_DIR)

    if ckpt: # is checkpoint exist
        last_model = ckpt.model_checkpoint_path
        #last_model = ckpt.all_model_checkpoint_paths[0]
        print ("load " + last_model)
        saver.restore(sess, last_model) # read variable data
        print("succeed restore model")
    else:
        init = tf.global_variables_initializer()
        sess.run(init)

    print("%.4e sec took initializing"%(time.time()-start))

    hist =[]
    hist_g =[]

    start = time.time()
    print("start pretrain")
    for p in range(50001):
        batch_images_x, batch_images_t = batchgen.getBatch(bs)
        tmp, gen_loss, l1, ssim = sess.run([g_loss, Total_loss, L1_loss, ssim_loss], feed_dict={
            x: batch_images_x,
            t: batch_images_t
        })

        hist.append(gen_loss)
        print("in step %s, pre_loss =%.4e, l1_loss=%.4e, ssim_loss=%.4e" %(p, gen_loss, l1, ssim))

        if p % 100 == 0:
            batch_images_x, batch_images_t = valgen.getBatch(bs)
            out = sess.run(test_y, feed_dict={x:batch_images_x})
#            out1 = (out + 1)*127.5
#            target1 = (batch_images_t + 1)*127.5

#            p, s = evaluate.test_images(out1, target1)

            X_ = tileImage(batch_images_x[:4])
            Y_ = tileImage(out[:4])
            Z_ = tileImage(batch_images_t[:4])

            X_ = cv2.resize(X_,(img_size*2*4,img_size*2*4),interpolation = cv2.INTER_CUBIC)
            
            X_ = (X_ + 1)*127.5
            Y_ = (Y_ + 1)*127.5
            Z_ = (Z_ + 1)*127.5
            ZZ_ = np.concatenate((X_,Y_,Z_), axis=1)
            
            cv2.imwrite("{0}/pre_{1:06d}.png".format(SAVEIM_DIR,int(p)),ZZ_)

            print("%.4e sec took 100steps" %(time.time()-start))
            start = time.time()
        
        if p % 1000 == 0:
            fig = plt.figure(figsize=(8,6), dpi=128)
            ax = fig.add_subplot(111)
            plt.title("Loss")
            plt.grid(which="both")
            plt.yscale("log")
            ax.plot(hist,label="gen_loss", linewidth = 0.25)
            plt.xlabel('step', fontsize = 16)
            plt.ylabel('loss', fontsize = 16)
            plt.legend(loc = 'upper right')
            plt.savefig("hist_pre.png")
            plt.close()

        if p%5000==0 and p!=0:
            # batch_images_x1, batch_images_t1 = valgen.getBatch(50)
            # out1 = sess.run(test_y, feed_dict={x:batch_images_x1})
            # batch_images_t1 = (batch_images_t1 + 1)*127.5
            # out1 = (out1 + 1)*127.5
            # p1, s1 = evaluate.test_images(batch_images_t1, out1)
            # print('PSNR: %.2f, SSIM: %.4f' %(p1, s1))

            saver.save(sess,os.path.join(SAVEPRE_DIR,"model.ckpt"),p)

if __name__ == '__main__':
    main()
