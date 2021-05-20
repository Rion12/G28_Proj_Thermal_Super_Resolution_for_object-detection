import os
os.chdir('D:\Thermal Image datasets\set00\V006\lwir')
direc = os.getcwd()
file = os.listdir()
print('The current directory is {} and there are {} files'.format(direc,len(file)))
for count, filename in enumerate(os.listdir()):
        dst ="S05V00000" + str(count) + ".jpg"
        src = filename
        
          
        # rename() function will
        # rename all the files
        os.rename(src, dst)