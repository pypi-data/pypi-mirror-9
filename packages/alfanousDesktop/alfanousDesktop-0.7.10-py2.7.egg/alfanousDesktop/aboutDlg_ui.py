# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './src/alfanous-desktop/UI/aboutDlg.ui'
#
# Created: Fri Feb 27 23:30:24 2015
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog.resize(545, 441)
        Dialog.setFocusPolicy(QtCore.Qt.NoFocus)
        Dialog.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtGui.QTabWidget(Dialog)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtGui.QWidget()
        self.tab.setObjectName("tab")
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.tab)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.o_about = QtGui.QTextBrowser(self.tab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.o_about.sizePolicy().hasHeightForWidth())
        self.o_about.setSizePolicy(sizePolicy)
        self.o_about.setMinimumSize(QtCore.QSize(300, 25))
        self.o_about.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.o_about.setFont(font)
        self.o_about.setProperty("cursor", QtCore.Qt.IBeamCursor)
        self.o_about.setToolTip("")
        self.o_about.setAutoFillBackground(False)
        self.o_about.setStyleSheet("background-color:Transparent;")
        self.o_about.setFrameShape(QtGui.QFrame.WinPanel)
        self.o_about.setFrameShadow(QtGui.QFrame.Sunken)
        self.o_about.setLineWidth(2)
        self.o_about.setDocumentTitle("")
        self.o_about.setUndoRedoEnabled(False)
        self.o_about.setReadOnly(True)
        self.o_about.setHtml("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Arial\'; font-size:12pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'ArabeyesQr\'; font-size:14pt; font-weight:600; color:#ff0000;\">AlfanousDesktop </span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'ArabeyesQr\'; font-size:14pt;\">version </span><span style=\" font-family:\'ArabeyesQr\'; font-size:14pt; font-weight:600;\">0.7</span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'ArabeyesQr\'; font-size:14pt;\">release </span><span style=\" font-family:\'ArabeyesQr\'; font-size:14pt; font-weight:600;\">Kahraman</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'ArabeyesQr\'; font-size:14pt; font-weight:600;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'ArabeyesQr\'; font-size:10pt;\">(c) 2010-2015 Alfanous Team. </span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'ArabeyesQr\'; font-size:10pt;\">All rights reserved under </span><span style=\" font-family:\'ArabeyesQr\'; font-size:10pt; font-weight:600;\">AGPL </span><span style=\" font-family:\'ArabeyesQr\'; font-size:10pt;\">license</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-size:10pt; font-weight:600; color:#000000;\">Website </span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"http://www.alfanous.org\"><span style=\" text-decoration: underline; color:#0000ff;\">www.alfanous.org</span></a></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans\'; font-size:10pt;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-size:10pt; font-weight:600; color:#000000;\">Mailinglist</span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"http://groups.google.com/group/alfanous/\"><span style=\" text-decoration: underline; color:#0000ff;\">alfanous@googlegroup.com </span></a></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:1; text-indent:0px; font-family:\'Sans\'; font-size:10pt;\"><br /></p></body></html>")
        self.o_about.setOverwriteMode(False)
        self.o_about.setAcceptRichText(True)
        self.o_about.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.o_about.setOpenExternalLinks(True)
        self.o_about.setOpenLinks(True)
        self.o_about.setObjectName("o_about")
        self.verticalLayout_3.addWidget(self.o_about)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.tab_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.o_about_2 = QtGui.QTextBrowser(self.tab_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.o_about_2.sizePolicy().hasHeightForWidth())
        self.o_about_2.setSizePolicy(sizePolicy)
        self.o_about_2.setMinimumSize(QtCore.QSize(300, 25))
        self.o_about_2.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.o_about_2.setFont(font)
        self.o_about_2.setProperty("cursor", QtCore.Qt.IBeamCursor)
        self.o_about_2.setToolTip("")
        self.o_about_2.setAutoFillBackground(False)
        self.o_about_2.setStyleSheet("background-color:Transparent;")
        self.o_about_2.setFrameShape(QtGui.QFrame.WinPanel)
        self.o_about_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.o_about_2.setLineWidth(2)
        self.o_about_2.setDocumentTitle("")
        self.o_about_2.setUndoRedoEnabled(False)
        self.o_about_2.setReadOnly(True)
        self.o_about_2.setHtml("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Arial\'; font-size:12pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:15px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; font-size:24pt; font-weight:600; color:#333333;\">Author</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:15px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\">Assem Chelli &lt;assem[DOT]ch[AT]gmail.com&gt;</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a name=\"contributors\"></a><span style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; font-size:24pt; font-weight:600; color:#333333;\">C</span><span style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; font-size:24pt; font-weight:600; color:#333333;\">ontributors</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a name=\"coding\"></a><span style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; font-size:16pt; font-weight:600; color:#333333;\">C</span><span style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; font-size:16pt; font-weight:600; color:#333333;\">oding</span></p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:15px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">API &amp; JSON interface:Assem Chelli</li>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Desktop Interface: Assem Chelli, Sohaib Afifi</li>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Web Interface: Assem Chelli , Walid Ziouche, Abdellah Chelli , Mouad Debbar, Mennouchi Islam Azeddine, Muslih al aqaad, Tedjeddine Meabeo , Ahmed Ramadan</li>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Firefox toolbar: Zakaria Smahi</li>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:15px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">PyArabic(Integrated): Taha Zerrouki, Assem Chelli, Ahimta~</li></ul>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a name=\"research\"></a><span style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; font-size:16pt; font-weight:600; color:#333333;\">R</span><span style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; font-size:16pt; font-weight:600; color:#333333;\">esearch</span></p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:15px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">2009-2010: Engineer Thesis</span></li>\n"
"<ul type=\"circle\" style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 2;\"><li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Title</span>: Développement d\'un moteur de recherche et d\'indexation dans les documents coraniques</li>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">University</span>: ESI - Algiers</li>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Collaborators</span>: Assem Chelli (Student), Merouane Dahmani (Student), Taha Zerrouki ( Supervisor), Pr. Amar Balla ( Supervisor)</li></ul>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">March 2011: Arabic Research paper</span></li>\n"
"<ul type=\"circle\" style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 2;\"><li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Title</span>: An Application Programming Interface for indexing and search in Noble Quran</li>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Conference</span>: NITS 2011 KSA</li>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Collaborators</span>: Assem Chelli, Merouane Dahmani, Taha Zerrouki, Pr. Amar Balla</li></ul>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:15px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">May 2012: English Research paper</span></li></ul>\n"
"<ul type=\"circle\" style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 2;\"><li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Title</span>:. Advanced Search in Quran: Classification and Proposition of All Possible Features</li>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Conference</span>: A pre-conference workshop in LREC 2012 Turkey which is about ”LRE-Rel: Language Resource and Evaluation for Religious Texts”</li>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Collaborators</span>: Assem Chelli, Taha Zerrouki, Pr. Amar Balla</li></ul>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a name=\"graphics--design\"></a><span style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; font-weight:600; color:#333333;\">G</span><span style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; font-weight:600; color:#333333;\">raphics &amp; Design</span></p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:15px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Icons,Logos: Abdellah Chelli, Muslih Al-Aqaad, Ahmed Ramadan, Moussa Drihem</li>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Wallpapers: Aji Fatwa, Abd Madjid Kemari</li>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:15px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Joomla Template: Muslih Al-aqaad</li></ul>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a name=\"packaging\"></a><span style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; font-size:16pt; font-weight:600; color:#333333;\">P</span><span style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; font-size:16pt; font-weight:600; color:#333333;\">ackaging</span></p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:15px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Windows NSIS installer: Assem Chelli</li>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Ubuntu/Sabily DEB package: Ahmed Almahmoudy</li>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Fedora/OpenSuse/Ojuba RPM package: Muhammad Shaban</li>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:15px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Arch-linux package: Walid Ziouche, Sohaib Afifi</li></ul>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a name=\"resource-enriching\"></a><span style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; font-size:16pt; font-weight:600; color:#333333;\">R</span><span style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; font-size:16pt; font-weight:600; color:#333333;\">esource Enriching</span></p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:15px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Word index: Taha Zerrouki, Assem Chelli, Asmaa Mhimeh, Rahma Maaref</li>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Aya index: {Tanzil Project}, Taha Zerrouki (Subjects), Muhi-uddin (Indian mushaf pages)</li>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:15px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Translations: {Tanzil Project},</li></ul>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a name=\"documentation\"></a><span style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; font-size:16pt; font-weight:600; color:#333333;\">D</span><span style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; font-size:16pt; font-weight:600; color:#333333;\">ocumentation</span></p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:15px; margin-bottom:15px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Wiki: Assem Chelli, Abdellah Chelli</li></ul>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a name=\"writing\"></a><span style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; font-size:16pt; font-weight:600; color:#333333;\">W</span><span style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; font-size:16pt; font-weight:600; color:#333333;\">riting</span></p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:15px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">News : Mohamed M Sayed, Yasser Ghemit, Kacem Boukraa, Asmaa Mhimeh,</li>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:15px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Blog posts: Muslih Al-aqaad, Ahmed Jumal, Aji Fatwa</li></ul>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a name=\"community-management\"></a><span style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; font-size:16pt; font-weight:600; color:#333333;\">C</span><span style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; font-size:16pt; font-weight:600; color:#333333;\">ommunity Management</span></p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; font-size:16pt; color:#333333;\" style=\" margin-top:15px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Yasmine Hoadjli</span></li>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Zineb Laouici</li>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:15px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Meriem Bounif</li></ul>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a name=\"translation\"></a><span style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; font-size:16pt; font-weight:600; color:#333333;\">T</span><span style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; font-size:16pt; font-weight:600; color:#333333;\">ranslation</span></p>\n"
"<p style=\" margin-top:15px; margin-bottom:15px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\">( to help in translation, contact us in the mailing list &lt;alfanous[at]googlegroups[dotcom]&gt; )</span></p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:15px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Desktop application</li>\n"
"<ul type=\"circle\" style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 2;\"><li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">(we\'ll write about that as soon as we manage the translations made to the desktop application)</li></ul>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Main Web Interface</li>\n"
"<ul type=\"circle\" style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 2;\"><li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Arabic: Assem Chelli, Yasmine Houadjli</li>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">French: Zineb Pub, Yasmine Houadjli, Abdelkarim Aries, Nassim rehali, Nasreddine Cheniki</li>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Indonesian: Ahmed Jumal , Amy cidra, Mahyuddin Susanto</li>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Japanese: Abdelkarim Aries</li>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Spanish: Khireddine Chekraoui</li>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Portuguese: Jonathan Da Fonseca</li>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">German: Dennis Baudys</li>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Malay: \'abuyop\'</li>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Kurdish:</li>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Malayalam: \'STyM Alfazz\'</li></ul>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:15px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Mobile Web interface</li></ul>\n"
"<ul type=\"circle\" style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 2;\"><li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Bosnian: Armin Kazi</li>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Brazilian Portuguese: Aieon.corp(LP)</li>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">French: Karim Oulad Chalha, \'yass-pard\'</li>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Indonesian: Mahyuddin Susanto,</li>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Italian: \'Guybrush88\'</li>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Japanese: Abdelkarim Aries</li>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Malay: \'abuyop\'</li></ul>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a name=\"test--support\"></a><span style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; font-size:16pt; font-weight:600; color:#333333;\">T</span><span style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; font-size:16pt; font-weight:600; color:#333333;\">est &amp; Support</span></p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:15px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Test: Walid Ziouche</li>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Bugs: Oussama Chammam, Ahmed Salem, xsoh, Yacer~, Jounathan~, BenSali~ , Many persons from the community, thanks to all.</li>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:0px; margin-bottom:15px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Vulns: Jalil~</li></ul>\n"
"<p style=\" margin-top:0px; margin-bottom:15px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; font-size:20pt; font-weight:600; color:#333333;\">Acknowledgment</span></p>\n"
"<p style=\" margin-top:15px; margin-bottom:15px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\">We gratefully acknowledge the following:</span></p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:15px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Sabily team</li>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:15px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Linux Arab Community</li>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:15px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">It Scoop</li>\n"
"<li style=\" font-family:\'Helvetica,arial,freesans,clean,sans-serif\'; color:#333333;\" style=\" margin-top:15px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Tech Echo</li></ul>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>")
        self.o_about_2.setOverwriteMode(True)
        self.o_about_2.setAcceptRichText(True)
        self.o_about_2.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.o_about_2.setOpenExternalLinks(False)
        self.o_about_2.setOpenLinks(False)
        self.o_about_2.setObjectName("o_about_2")
        self.verticalLayout_2.addWidget(self.o_about_2)
        self.tabWidget.addTab(self.tab_2, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.pushButton = QtGui.QPushButton(Dialog)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.pushButton)

        self.retranslateUi(Dialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.pushButton, QtCore.SIGNAL("clicked()"), Dialog.accept)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "About", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("Dialog", "About", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QtGui.QApplication.translate("Dialog", "Credits", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("Dialog", "OK", None, QtGui.QApplication.UnicodeUTF8))

