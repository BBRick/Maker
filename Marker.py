# encoding: UTF-8

import sys
import ftpmanager
import scanpdf
import json
import os

from PyQt5.QtWidgets import qApp, QDesktopWidget,QGridLayout,QApplication, QComboBox,QVBoxLayout,QDialog,QTableWidgetItem,QWidget, QTableWidget, QPushButton,QMainWindow, QFileDialog, QLabel, QAction, QMenu
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtGui import QIcon

class LabelingMainWindow(QWidget):

    def __init__(self):
        super(LabelingMainWindow, self).__init__()
        self.folderText = scanpdf.ROOT_PATH
        self.stringList = []
        self.pathList = []
        self.realPathList = []
        self.pdfstring = ''
        self.index = 0
        self.initUI()
        self.typeList = ['title','author','date']
        self.resultDic = {}
        self.ftp = ftpmanager.ftpconnect(ftpmanager.FTPIP, ftpmanager.FTPUSER, ftpmanager.FTPPASSWD)


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
        # nextbtn.move(20, 700)
        savebtn = QPushButton('保存已选内容', self)
        savebtn.clicked.connect(self.creatJSONString)
        savebtn.resize(savebtn.sizeHint())

        submitbtn = QPushButton('提交此页内容', self)
        submitbtn.clicked.connect(self.uploadfile)
        submitbtn.resize(submitbtn.sizeHint())
        self.MyTable = QTableWidget(1,1)
        self.MyTable.setColumnWidth(0, 800)
        self.MyTable.setShowGrid(False)
        item = QTableWidgetItem('0/0')
        self.MyTable.setHorizontalHeaderItem(0, item)
        layout = QGridLayout()
        layout.setHorizontalSpacing(50)
        layout.setVerticalSpacing(30)
        layout.addWidget(selectbtn, 0, 0, 1, 1)
        layout.addWidget(self.folderLabel,0, 4, 1 ,1)
        layout.addWidget(self.qblabel,1,4,1, 1)

        layout.addWidget(qbtn, 1, 0, 1, 1)
        layout.addWidget(lastbtn,2,0, 1, 1)
        layout.addWidget(nextbtn, 2, 4, 1, 1)
        layout.addWidget(self.MyTable, 3, 0, 8, 8 )
        layout.addWidget(savebtn, 12, 0, 1, 1)
        layout.addWidget(submitbtn, 12, 4, 1, 1)
        self.setLayout(layout)
        desktop = QDesktopWidget()
        screenRect = desktop.screenGeometry()
        # print screenRect.width()
        # print screenRect.height()
        self.setGeometry(50, 50, screenRect.width()-100, screenRect.height()-100)
        self.setWindowTitle('标注系统')
        self.show()



    def creatJSONString(self):
        if self.MyTable.selectedItems():
            self.submitDialog = submitDialog(title=None)
            self.submitDialog.surebtn.clicked.connect(self.saveSelectData)
            self.submitDialog.show()

    def returnJson(self):
        dataDict = {}
        for item in self.MyTable.selectedItems():
            dataDict[str(item.row())] = item.text()
        return dataDict

    def saveSelectData(self):
        self.submitDialog.close()
        if self.MyTable.selectedItems():
            self.resultDic[self.typeList[self.submitDialog.MyCombo.currentIndex()]] = self.returnJson()


    def uploadfile(self):
        # self.resultDic = {}
        # print resultDic
        resultString = json.dumps(self.resultDic)
        # print resultString
        pathString = self.pathList[self.index]+'.txt'
        f = open(pathString, 'w')
        f.write(resultString)
        f.close()
        self.submitDialog.close()
        # print pathString
        ftpmanager.uploadfile(self.ftp, "~/result/"+pathString, pathString)
        # os.remove(pathString)
        pass

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
        pageList = self.pdfstring.split('\n')
        self.MyTable.setRowCount(len(pageList))
        headerstr = str(self.index + 1) + '/' + str(len(self.pathList))
        headerItem = QTableWidgetItem(headerstr)
        self.MyTable.setHorizontalHeaderItem(0,headerItem)
        for index,string in enumerate(pageList):
            newItem = QTableWidgetItem(string)
            self.MyTable.setItem(index,0,newItem)

    def scanpdffolder(self):
        self.resultDic = {}
        if self.index < len(self.realPathList):
            self.qblabel.setText('提取文本中···请稍后')
            self.qblabel.adjustSize()
            # self.stringList, self.pathList = scanpdf.scan_PDF_file(self.folderText)
            self.pdfstring = scanpdf.scanPDF(self.realPathList[self.index])
            self.qblabel.setText('提取完成')
            self.qblabel.adjustSize()
            self.showScanPDFText()

    def sureFolder(self):
        self.index = 0
        self.folderLabel.setText(self.folderText)
        self.folderLabel.adjustSize()
        self.realPathList, self.pathList = scanpdf.getFileList(self.folderText)
        if len(self.pathList) == 0:
            self.qblabel.setText('此文件夹无PDF文件')
        else:
            self.qblabel.setText('已扫描到PDF文件，请点击 开始提取 ')
        self.qblabel.adjustSize()

        self.dialog.close()
    def selectDirectory(self):
        filename = QFileDialog.getExistingDirectory(self,directory='~/Desktop')
        if filename:
            self.folderText = filename
            self.dialog = InfoDialog(title=filename)
            self.dialog.surebtn.clicked.connect(self.sureFolder)
            self.dialog.show()




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
        self.setGeometry(350, 300, 300, 200)
        self.setWindowTitle('提示')


class submitDialog(InfoDialog):
    def initSubViews(self,title=''):
        textLabel = QLabel(self)
        textLabel.move(50, 30)
        textLabel.setText('请选择选中内容类型：')
        textLabel.adjustSize()
        self.surebtn = QPushButton('确定', self)
        self.surebtn.resize(self.surebtn.sizeHint())
        self.MyCombo = QComboBox()
        self.MyCombo.addItem("标题")
        self.MyCombo.addItem("作者")
        self.MyCombo.addItem('日期')
        exitbtn = QPushButton('取消', self)
        exitbtn.clicked.connect(self.close)
        exitbtn.resize(exitbtn.sizeHint())
        layout = QVBoxLayout()
        layout.addWidget(textLabel)
        layout.addWidget(self.MyCombo)
        layout.addWidget(self.surebtn)
        layout.addWidget(exitbtn)
        self.setLayout(layout)
        self.setGeometry(550, 500, 200, 200)
        self.setWindowTitle('提示')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = LabelingMainWindow()
    myWindow.setWindowIcon(QIcon('icon.png'))
    sys.exit(app.exec_())
