import os
import random
os.chdir('/content/drive/MyDrive/Thermal_Super_Resolution/train_thermal_hr') #Change Directory
file = os.listdir()
ls = []
while len(ls) < len(file):
  rand = random.randint(0,10000)
  if rand not in ls:
    ls.append(rand)
print(ls)

file = os.listdir()
count = 000
for filename in file:
        dst =str(count) +  ".jpg"
        src = filename
        count = count + 1
        
          
        
        os.rename(src, dst)