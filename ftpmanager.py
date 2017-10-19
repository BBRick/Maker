# !/usr/bin/python
# -*- coding: utf-8 -*-
import time
import tarfile
import os
from ftplib import FTP


FTPIP = '120.26.221.145'
FTPUSER = 'shower'
FTPPASSWD = 'libingqing'
FTPROOTPATH = '"~/result/'
    
def ftpconnect(host, username, password):
    ftp = FTP()
    # ftp.set_debuglevel(2)
    ftp.connect(host, 21)
    ftp.login(username, password)
    return ftp

#从ftp下载文件
def downloadfile(ftp, remotepath, localpath):
    bufsize = 1024
    fp = open(localpath, 'wb')
    ftp.retrbinary('RETR ' + remotepath, fp.write, bufsize)
    ftp.set_debuglevel(0)
    fp.close()

#从本地上传文件到ftp
def uploadfile(ftp, remotepath, localpath):
    bufsize = 1024
    fp = open(localpath, 'rb')
    ftp.storbinary('STOR ' + remotepath, fp, bufsize)
    ftp.set_debuglevel(0)
    fp.close()

if __name__ == "__main__":
    ftp = ftpconnect(FTPIP, FTPUSER, FTPPASSWD)
    uploadfile(ftp, "~/result/icon.png", "icon.png")
    ftp.quit()
