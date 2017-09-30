# encoding: UTF-8

import ftpmanager
import scanpdf
import json
import os
import copy

from PyQt5.QtWidgets import qApp, QTextEdit,QDesktopWidget,QGridLayout,QApplication, QComboBox,QVBoxLayout,QDialog,QTableWidgetItem,QWidget, QTableWidget, QPushButton,QMainWindow, QFileDialog, QLabel, QAction, QMenu
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtGui import QIcon
import sys
import webbrowser

MANUALURL = 'http://www.jianshu.com/p/1a5933d391ad'

reload(sys)
sys.setdefaultencoding('utf8')

class LabelingMainWindow(QWidget):

    def __init__(self):
        super(LabelingMainWindow, self).__init__()
        self.folderText = scanpdf.ROOT_PATH
        self.initUI()
        self.initAction()

        self.typeList = ['title','author','body']
        self.initTempData()
        self.ftp = ftpmanager.ftpconnect(ftpmanager.FTPIP, ftpmanager.FTPUSER, ftpmanager.FTPPASSWD)


    def initTempData(self):
        self.titleDic = {}
        self.authorDic = {}
        self.bodyDict = {}
        self.NADict = {}
        self.resultDic = {}
        self.rows = []
        self.stringList = []
        self.pathList = []
        self.realPathList = []
        self.pdfstring = ''
        self.index = 0
        self.pageList = []
        self.saveIndex = 0

    def initAction(self):
        self.titleAction = QAction(QIcon('icon.png'), 'Mark', self)
        self.titleAction.setShortcut('Ctrl+T')
        self.titleAction.triggered.connect(self.saveTitle)
        self.addAction(self.titleAction)
        self.authorAction = QAction(QIcon('icon.png'), 'Mark', self)
        self.authorAction.setShortcut('Ctrl+A')
        self.authorAction.triggered.connect(self.saveAuthor)

        self.bodyAction = QAction(QIcon('icon.png'), 'Mark', self)
        self.bodyAction.setShortcut('Ctrl+B')
        self.bodyAction.triggered.connect(self.savebody)
        self.addAction(self.titleAction)
        self.addAction(self.authorAction)
        self.addAction(self.bodyAction)

    def initUI(self):
        infoLabel = QLabel(self)
        infoLabel.move(20,20)
        infoLabel.setText('PDF文件夹:')
        infoLabel.adjustSize()
        self.folderLabel = QLabel(self)
        self.folderLabel.setText('还未选择文件夹 ！')
        selectbtn = QPushButton('选择文件夹', self)
        selectbtn.clicked.connect(self.selectDirectory)
        qbtn = QPushButton('开始提取', self)
        qbtn.clicked.connect(self.scanpdffolder)
        qbtn.resize(qbtn.sizeHint())
        self.qblabel = QLabel(self)
        self.qblabel.setText('请先选择文件夹 ！')
        self.qblabel.adjustSize()
        nextbtn = QPushButton('下一个', self)
        nextbtn.clicked.connect(self.nextPDF)
        nextbtn.resize(nextbtn.sizeHint())
        lastbtn = QPushButton('上一个', self)
        lastbtn.clicked.connect(self.lastPDF)
        lastbtn.resize(lastbtn.sizeHint())
        savebtn = QPushButton('保存已选内容', self)
        savebtn.clicked.connect(self.creatJSONString)
        savebtn.resize(savebtn.sizeHint())

        submitbtn = QPushButton('提交此页内容', self)
        submitbtn.clicked.connect(self.uploadfile)
        submitbtn.resize(submitbtn.sizeHint())


        desktop = QDesktopWidget()
        screenRect = desktop.screenGeometry()
        manualbtn = QPushButton('点击打开使用手册',self)
        manualbtn.clicked.connect(self.openUrl)
        manualbtn.resize(manualbtn.sizeHint())
        clearbtn = QPushButton('清除标签标记内容', self)
        clearbtn.resize(submitbtn.sizeHint())
        clearbtn.clicked.connect(self.clearAction)
        self.MyTable = QTableWidget(1,1)
        self.MyTable.setColumnWidth(0, (screenRect.width()-100) / 2 - 20)
        self.MyTable.setShowGrid(False)
        item = QTableWidgetItem('0/0')
        self.MyTable.setHorizontalHeaderItem(0, item)
        self.previewTable = QTableWidget(1,1)
        self.previewTable.setColumnWidth(0, (screenRect.width() - 100) / 2 - 20)
        self.previewTable.setShowGrid(False)
        self.previewTable.verticalHeader().setVisible(False)
        previewItem = QTableWidgetItem('标记内容预览')
        self.previewTable.setHorizontalHeaderItem(0, previewItem)
        # self.previewTextEdit = QTextEdit(self)
        # self.previewTextEdit.textChanged[str].connect(self.onChanged)
        layout = QGridLayout()
        layout.setHorizontalSpacing(50)
        layout.setVerticalSpacing(30)
        layout.addWidget(selectbtn, 0, 0, 1, 1)
        layout.addWidget(self.folderLabel,0, 5, 1 ,4)
        layout.addWidget(self.qblabel,1,5,1, 4)
        layout.addWidget(manualbtn, 0, 8, 1, 1)
        layout.addWidget(qbtn, 1, 0, 1, 1)
        layout.addWidget(lastbtn,2,0, 1, 1)
        layout.addWidget(nextbtn, 2, 5, 1, 1)
        layout.addWidget(self.MyTable, 3, 0, 8, 5 )
        layout.addWidget(self.previewTable, 3, 5,8,5)
        layout.addWidget(savebtn, 12, 0, 1, 1)
        layout.addWidget(clearbtn, 12, 4, 1, 1)
        layout.addWidget(submitbtn, 12, 5, 1, 1)
        self.setLayout(layout)
        self.setGeometry(50, 50, screenRect.width()-100, screenRect.height()-100)
        self.setWindowTitle('Marker')
        self.show()

    def openUrl(self):
    #     webbrowser.open(MANUALURL, new=0, autoraise=True)
    #     webbrowser.open_new(MANUALURL)
        webbrowser.open_new_tab(MANUALURL)
    def clearAction(self):
        self.submitDialog = submitDialog(title='请选择需要清除标记的标签 :')
        self.submitDialog.surebtn.clicked.connect(self.clearData)
        self.submitDialog.show()
    def clearData(self):
        key = self.typeList[self.submitDialog.MyCombo.currentIndex()]
        if self.resultDic.has_key(key):
            self.resultDic.pop(key)
            self.setPreViewData()
        self.submitDialog.close()

    def onChanged(self, text):
        dic = json.loads(text)
        self.resultDic = dic



    def creatJSONString(self):
        if self.MyTable.selectedItems():
            self.submitDialog = submitDialog(title=None)
            self.submitDialog.surebtn.clicked.connect(self.saveSelectData)
            self.submitDialog.show()

    def returnJson(self):
        # dataDict = {}
        try:
            self.saveIndex = self.submitDialog.MyCombo.currentIndex()
        except AttributeError:
            pass
        if self.saveIndex == 0:
            self.setDataWithDict(self.titleDic)
            return self.titleDic
        elif self.saveIndex == 1:
            self.setDataWithDict(self.authorDic)
            return self.authorDic
        elif self.saveIndex == 2:
            self.setDataWithDict(self.bodyDict)
            return self.bodyDict


    def setDataWithDict(self,dataDict):
        for item in self.MyTable.selectedItems():
            dataDict[str(item.row())] = item.text()
            self.rows.append(item.row())



    def getOtherRowData(self):
        for index, text in enumerate(self.pageList):
            realIndex = index + 1
            if (realIndex) not in self.rows:
                self.NADict[str(realIndex)] = text


    def saveTitle(self):
        self.saveData(0)

    def saveAuthor(self):
        self.saveData(1)

    def savebody(self):
        self.saveData(2)

    def saveSelectData(self):
        self.saveData(self.submitDialog.MyCombo.currentIndex())
        self.submitDialog.close()

    def saveData(self, index):
        self.saveIndex = index
        if self.MyTable.selectedItems():
            self.resultDic[self.typeList[index]] = self.returnJson()
            self.setPreViewData()


    def uploadfile(self):

        if self.resultDic:
            self.getOtherRowData()
            self.resultDic['NA'] = self.NADict
            resultString = json.dumps(self.resultDic)
            pathString = self.pathList[self.index]+'.txt'
            f = open(pathString, 'w')
            f.write(resultString)
            f.close()
            try:
                self.submitDialog.close()
            except AttributeError:
                pass
            ftpmanager.uploadfile(self.ftp, "~/result/"+pathString, pathString)
            os.remove(pathString)
            self.setQLabelText(pathString + ' 已提交完成!')
        else:
            dia = HintDialog(title='非法json格式，请重新检查提交内容')
            dia.show()

    def setPreViewData(self):
        previewData = self.jsonToList(self.resultDic)
        self.previewTable.setRowCount(len(previewData))
        for index, string in enumerate(previewData):
            newItem = QTableWidgetItem(string)
            self.previewTable.setItem(index, 0, newItem)

    def jsonToList(self, dic):
        jsonList = []
        for key, value in dic.items():
            if str(key).isdigit():
                index = int(key) + 1
                jsonList.append(str(str(index) + '  ' + value))

            else:
                jsonList.append(str(key))
                if type(value) == dict:
                    jsonList.extend(self.jsonToList(value))
                else:
                    jsonList.append(str(value))

        return jsonList

    def lastPDF(self):
        if self.index > 0:
            self.index -= 1
            self.scanpdffolder()
    def nextPDF(self):
        self.index += 1
        self.scanpdffolder()

    def showScanPDFText(self):
        if len(self.pathList) == 0:
            return
        self.MyTable.setRowCount(len(self.pageList))
        headerstr = str(self.index + 1) + '/' + str(len(self.pathList))
        headerItem = QTableWidgetItem(headerstr)
        self.MyTable.setHorizontalHeaderItem(0,headerItem)
        for index,string in enumerate(self.pageList):
            newItem = QTableWidgetItem(string)
            self.MyTable.setItem(index,0,newItem)


    def scanpdffolder(self):
        self.resultDic = {}
        self.authorDic = {}
        self.bodyDict = {}
        self.titleDic = {}
        
        self.setPreViewData()
        if self.index < len(self.realPathList):
            self.setQLabelText('提取文本中···请稍后')
            self.pdfstring = scanpdf.scanPDF(self.realPathList[self.index])
            strList = self.pdfstring.split('\n')
            for text in strList:
                if len(text) > 1:
                    self.pageList.append(text)
            self.setQLabelText(self.pathList[self.index] + ' 已提取完成')
            self.showScanPDFText()

    def sureFolder(self):
        self.initTempData()
        self.folderLabel.setText(self.folderText)
        self.folderLabel.adjustSize()
        self.realPathList, self.pathList = scanpdf.getFileList(self.folderText)
        if len(self.pathList) == 0:
            self.setQLabelText('此文件夹无PDF文件')
        else:
            self.setQLabelText('已扫描到PDF文件，请点击 开始提取 ')

        headerstr = str(self.index + 1) + '/' + str(len(self.pathList))
        headerItem = QTableWidgetItem(headerstr)
        self.MyTable.setHorizontalHeaderItem(0,headerItem)
        self.dialog.close()

    def selectDirectory(self):
        filename = QFileDialog.getExistingDirectory(self,directory='~/Desktop')
        if filename:
            self.folderText = filename
            self.dialog = InfoDialog(title=filename)
            self.dialog.surebtn.clicked.connect(self.sureFolder)
            self.dialog.show()

    def setQLabelText(self, text):
        self.qblabel.setText(text)
        self.qblabel.adjustSize()


class HintDialog(QWidget):
        def __init__(self, title=None):
            super(InfoDialog, self).__init__()
            self.initSubViews(title)
        def initSubViews(self,title=''):
            infoLabel = QLabel(self)
            infoLabel.move(50, 50)
            infoLabel.setText(title)
            infoLabel.adjustSize()
            self.surebtn = QPushButton('确定', self)
            self.surebtn.resize(self.surebtn.sizeHint())
            self.surebtn.move(140, 170)
            self.surebtn.clicked.connect(self.close)
            desktop = QDesktopWidget()
            screenRect = desktop.screenGeometry()
            x = (screenRect.width()-100 - 300) /  2
            self.setGeometry(x, 300, 300, 200)
            self.setWindowTitle('提示')

class InfoDialog(QWidget):
    def __init__(self, title=None):
        super(InfoDialog, self).__init__()
        self.initSubViews(title)
    def initSubViews(self,title=''):
        textLabel = QLabel(self)
        textLabel.move(50, 30)
        textLabel.setText('是否扫描此文件夹：')
        textLabel.adjustSize()
        infoLabel = QLabel(self)
        infoLabel.move(50, 50)
        infoLabel.setText(title)
        infoLabel.adjustSize()
        self.surebtn = QPushButton('确定', self)
        self.surebtn.resize(self.surebtn.sizeHint())
        self.surebtn.move(50, 150)
        exitbtn = QPushButton('取消', self)
        exitbtn.clicked.connect(self.close)
        exitbtn.resize(exitbtn.sizeHint())
        exitbtn.move(150, 150)
        desktop = QDesktopWidget()
        screenRect = desktop.screenGeometry()
        x = (screenRect.width()-100 - 300) /  2
        self.setGeometry(x, 300, 300, 200)
        self.setWindowTitle('提示')


class submitDialog(InfoDialog):
    def initSubViews(self,title=None):
        text = '请选择选中内容类型：'
        if title:
            text = title

        textLabel = QLabel(self)
        textLabel.move(50, 30)
        textLabel.setText(text)
        textLabel.adjustSize()
        self.surebtn = QPushButton('确定', self)
        self.surebtn.resize(self.surebtn.sizeHint())
        self.MyCombo = QComboBox()
        self.MyCombo.addItem("标题")
        self.MyCombo.addItem("作者")
        self.MyCombo.addItem('正文摘要')
        exitbtn = QPushButton('取消', self)
        exitbtn.clicked.connect(self.close)
        exitbtn.resize(exitbtn.sizeHint())
        layout = QVBoxLayout()
        layout.addWidget(textLabel)
        layout.addWidget(self.MyCombo)
        layout.addWidget(self.surebtn)
        layout.addWidget(exitbtn)
        self.setLayout(layout)
        desktop = QDesktopWidget()
        screenRect = desktop.screenGeometry()
        x = (screenRect.width()-100 - 300) /  2
        self.setGeometry(x, 500, 300, 200)
        self.setWindowTitle('提示')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = LabelingMainWindow()
    myWindow.setWindowIcon(QIcon('icon.png'))
    sys.exit(app.exec_())
