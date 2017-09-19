# encoding: UTF-8

import layout_scanner
import json
import requests
import os
# import MySQLdb


NER_URL = 'http://api.bosonnlp.com/ner/analysis'
BOSONNLP_TOKEN = '_EPbyGZu.17527.3863TbIkXwxn'
ROOT_PATH = '/Users/J-bb/Desktop/pdf 2'

def scan_PDF_file(root_path):
    # pages = layout_scanner.get_pages(root_path)
    # string = pages[0]
    # print string
    stringList = []
    palist = []
    pathList = os.listdir(root_path)
    # print pathList
    for i in range(0,len(pathList)):
        path = os.path.join(root_path,pathList[i])
        if os.path.isfile(path):
            if path.endswith('pdf'):
                pages = layout_scanner.get_pages(path)
                string = pages[0]
                stringList.append(string)
                palist.append(pathList[i])
                # s = string.split('\n')
                # print string
                # seaprate_list(s)
    return stringList, palist

def scanPDF(path):
    string = ''
    pages = layout_scanner.get_pages(path)
    if pages:
        string = pages[0]
    return string

def getFileList(root_path):
    returnList = []
    psList = []
    pathList = os.listdir(root_path)
    # print pathList
    for i in range(0,len(pathList)):
        path = os.path.join(root_path,pathList[i])
        if os.path.isfile(path):
            if path.endswith('pdf'):
                psList.append(pathList[i])
                returnList.append(path)
    return returnList, psList
#分割字符串
def seaprate_list(s):
    if len(s) > 100:
        string_list = s[:100]
        analysis_str(string_list)
        seaprate_list(s[101:])
    else:
         analysis_str(s)

def analysis_str(s):
    data = json.dumps(s)
    headers = {'X-Token' : BOSONNLP_TOKEN}
    resp = requests.post(NER_URL, headers=headers, data=data.encode('utf-8'))
    print resp.json()
    for item in resp.json():
        if item.has_key('entity'):
             for entity in item['entity']:
                 print(''.join(item['word'][entity[0]:entity[1]]), entity[2])


# scan_PDF_file(ROOT_PATH)
