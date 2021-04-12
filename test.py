import os

if not os.path.exists('/home/java/test.txt'):
    os.mknod('/home/java/test.txt')
