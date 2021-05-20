import os
os.chdir('path') #Replace this path
direc = os.getcwd()
file = os.listdir()
print('The current directory is {} and there are {} files'.format(direc,len(file)))

file = os.listdir()
fin = len(file)
for f in range(fin):
    current = file[f][1:6]
    ct = int(current)
    if ct % 29 ==0:
        continue
    os.remove(file[f])
file = os.listdir()
print(len(file))
