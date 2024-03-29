#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import base64
import hashlib
import numpy as np
import cv2
import pandas as pd
from sklearn.linear_model import LinearRegression
from Crypto.Cipher import AES
from Crypto.Random import new as Random
from hashlib import sha256
from base64 import b64encode, b64decode

# Reading input Image and encoding it using base64
with open("pics/test2.jpeg", "rb") as img_file:
    BI = base64.b64encode(img_file.read())
print(BI)
BI = BI.decode("utf-8")

# My key
K = ""
f = open('keys/mykey.txt', 'r')
for i in f:
    K += i
f.close()
K = 'WELCOME'  # Note: Updated 'K' here for testing purpose
print(K)

SK = hashlib.sha256(K.encode())
print("The hexadecimal equivalent of SHA256 is : ")
print(SK.hexdigest())

# AES 256 in OFB mode
class AESCipher:
    def __init__(self, data, key):
        self.block_size = 16
        self.data = data
        self.key = sha256(key.encode()).digest()[:32]
        self.pad = lambda s: s + (self.block_size - len(s) % self.block_size) * chr(self.block_size - len(s) % self.block_size)
        self.unpad = lambda s: s[:-ord(s[len(s) - 1:])]

    def encrypt(self):
        plain_text = self.pad(self.data)
        iv = Random().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_OFB, iv)
        return b64encode(iv + cipher.encrypt(plain_text.encode())).decode()

# Encrypting image using base64 encoded text and hashed key - SHA256 AES-256
c = AESCipher(BI, SK.hexdigest()).encrypt()
print(c)

w = 255
h = len(K)

# creating new Image C of size(w,h) initializing as blank
C = np.ones((h, w, 1), dtype='uint8')

# Filling pixels in C
for i in range(h):
    j = ord(K[i])
    for k in range(w):
        if k < j:
            C[i][k][0] = 0
        else:
            break

# Dividing C into R and P initializing R and P of same size as C
R = np.ones((h, w, 3), dtype='uint8')
P = np.ones((h, w, 3), dtype='uint8')

# filling the pixels of R
for i in range(h):
    for j in range(w):
        r = np.random.normal(0, 1, 1)
        R[i][j][0] = r

# filling the pixels of P
for i in range(h):
    for j in range(w):
        p = R[i][j][0] ^ C[i][j][0]
        P[i][j][0] = p

filename = 'ToBeSent for Decryption/P.png'
cv2.imwrite(filename, P)

xdf = pd.DataFrame(columns=['1', '2'])
a = []
b = []

for i in P:
    k = 0
    n1 = []
    n2 = []
    for j in i:
        if k % 2 == 0:
            n1.append(np.sum(j))
        else:
            n2.append(np.sum(j))
        k += 1
    a.append(sum(n1))
    b.append(sum(n2))

xdf['1'] = a
xdf['2'] = b

ydf = pd.DataFrame(columns=['1', '2'])
a = []
b = []

for i in R:
    k = 0
    n1 = []
    n2 = []
    for j in i:
        if k % 2 == 0:
            n1.append(np.sum(j))
        else:
            n2.append(np.sum(j))
        k += 1
    a.append(sum(n1))
    b.append(sum(n2))

ydf['1'] = a
ydf['2'] = b

LRmodel = LinearRegression()
LRmodel.fit(xdf, ydf)

# z is for prediction
zdf = pd.DataFrame(columns=['1', '2'])
a = []
b = []

for i in C:
    k = 0
    n1 = []
    n2 = []
    for j in i:
        if k % 2 == 0:
            n1.append(np.sum(j))
        else:
            n2.append(np.sum(j))
        k += 1
    a.append(sum(n1))
    b.append(sum(n2))

zdf['1'] = a
zdf['2'] = b

predict = LRmodel.predict([[sum(zdf['1']), sum(zdf['2'])]])
x = round(predict[0][0]) % 26
y = round(predict[0][1]) % 26
txt = []
for each in c:
    ch = ord(each) + x - y
    txt.append(int(ch))

text = ""
for t in txt:
    text += chr(t) + " "

f = open("ToBeSent for Decryption/cipher2.txt", 'a', encoding='utf-8')
f.write(text)
f.close()

