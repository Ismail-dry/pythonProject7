import sys,os
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDateTime,Qt,QEvent,pyqtSignal
from influxdb_client import InfluxDBClient
from PyQt5.QtGui import QStandardItem,QIcon,QFont
from datetime import datetime, timedelta
import locale
import xlsxwriter
import pandas as pd
import certifi
import json
from cryptography.fernet import Fernet

#
class CheckableComboBox(QComboBox): #ComboBox sınıfı checkable olarak oluşturuldu.
    activated_custom = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self.closeOnLineEditClick = False

        self.lineEdit().installEventFilter(self)
        self.view().viewport().installEventFilter(self)
        self.model().dataChanged.connect(self.updateLineEditField)

    def eventFilter(self, widget, event):
        if widget == self.lineEdit():
            if event.type() == QEvent.MouseButtonRelease:
                if self.closeOnLineEditClick:
                    self.hidePopup()
                else:
                    self.showPopup()
                return True

            return super().eventFilter(widget, event)
        if widget == self.view().viewport():
            if event.type() == QEvent.MouseButtonRelease:
                indx = self.view().indexAt(event.pos())
                item = self.model().item(indx.row())

                if item.checkState() == Qt.Checked:
                    item.setCheckState(Qt.Unchecked)
                else:
                    item.setCheckState(Qt.Checked)

                self.activated_custom.emit(self.model().item(indx.row()).text())

                return True
            return super().eventFilter(widget, event)

    def hidePopup(self):
        super().hidePopup()
        self.startTimer(100)

    def addItems(self, items, itemList=None):
        for indx, text in enumerate(items):
            try:
                data = itemList[indx]
            except (TypeError, IndexError):
                data = None
            self.addItem(text, data)

    def addItem(self, text, userData=None):
        item = QStandardItem()
        item.setText(text)
        if userData is not None:
            item.setData(userData)

        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
        item.setData(Qt.Unchecked, Qt.CheckStateRole)
        self.model().appendRow(item)

    def updateLineEditField(self):
        text_container = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.Checked:
                text_container.append(self.model().item(i).text())
        text_string = ','.join(text_container)
        self.lineEdit().setText(text_string)


class WindowAdminPanel(QMainWindow):

    def __init__(self):
        super().__init__()
        self.tabWidget()
        self.Widgets()
        self.layouts()
        self.setWindowTitle("InfluxDB Sorgulama 2.1")
        self.setWindowIcon(QIcon('x.ico'))
        self.setGeometry(50,50,1080,640)
        self.show()
        #InfluxDB Localimize ulaşmak için gereken token org bilgilerini tanımlandı.
        self.query=""
        self.token = ""
        self.org = ""
        self.url = ""
        self.bucket = ""
#        self.tokenKontrol()
        self.list2=[]
        self.key=""
        self.bucket_list=[]
        self.bucket_list = set()
        self.menubar()
        #Tarih seçme kısmı için takvim ekranı en başta görünmez olarak tanımlandı.
        self.start_time_label.setVisible(False)
        self.stop_time_label.setVisible(False)
        self.datetime_edit.setVisible(False)
        self.datetime_edit2.setVisible(False)
        self.button.setVisible(False)
    #Kullandığımız Widget ekranı için oluşturulan Tablar
    def tabWidget(self):
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.tab1 = QWidget()
        self.tab2=QWidget()

        self.tabs.addTab(self.tab1, "Main")
        self.tabs.addTab(self.tab2, "Main2")


    def Widgets(self):
        # tabMain left
        #tarih seçmek için comboBox oluşturuldu.
        self.comboForDate = QComboBox(self)
        #Tarih kısayolları için liste oluşturuldu
        dateList = ["Dün", "3 Gün Önce", "1 Hafta Önce", "15 Gün Önce", "1 Ay Önce", "3 Ay Önce", "6 Ay Önce",
                    "Tarih Belirle"]
        #liste tarih comboBoxuna atandı.
        self.comboForDate.addItems(dateList)
        self.comboForDate.activated[str].connect(self.newDateFunc)
        self.today = datetime.today()
        self.yesterday = self.today - timedelta(days=1)
        self.globalDate = datetime.today()
        self.lastThreeDays = self.today - timedelta(days=3)
        self.lastWeek = self.today - timedelta(days=7)
        self.lastFifteen = self.today - timedelta(days=15)
        self.datetime_edit = QDateTimeEdit(self, calendarPopup=True)
        self.datetime_edit2 = QDateTimeEdit(self, calendarPopup=True)
        self.datetime_edit.setDateTime(QDateTime.currentDateTime())
        self.datetime_edit2.setDateTime(QDateTime.currentDateTime())
        min_date = QDateTime(2020, 1, 1, 0, 0)
        max_date = QDateTime(2025, 1, 1, 0, 0)
        self.datetime_edit.setMinimumDateTime(min_date)
        self.datetime_edit.setMaximumDateTime(max_date)
        self.datetime_edit2.setMinimumDateTime(min_date)
        self.datetime_edit2.setMaximumDateTime(max_date)

        #Arayüz için Widget tanımları
       # self.tokenLabel=QLabel("Token:",self)
        # self.tokenText=QTextEdit("",self)

        # self.tokenText.setFixedHeight(50)
        #self.tokenButton=QPushButton("Token Kaydet",self)

        #self.tokenButton.clicked.connect(self.tokenSave)
        #self.tokenUpdateButton=QPushButton("Token Güncelle",self)
        # self.tokenUpdateButton.clicked.connect(self.TokenUpdate)
        #  self.tokenUpdateButton.setVisible(False)
        self.button = QPushButton("DateButton", self)
        self.button.clicked.connect(self.update)
        self.start_time_label = QLabel("Start:", self)
        self.stop_time_label = QLabel("Stop:", self)
        self.bucketLabel = QLabel("Bucket:", self)
        self.measurementLabel = QLabel("Measurement:", self)
        self.fieldsLabel = QLabel("Fields:", self)
        self.businessLabel = QLabel("Business Units:", self)
        self.locationLabel = QLabel("Location:", self)
        self.matelabel = QLabel("Mate:", self)
        self.processLabel = QLabel("Process:", self)
        self.robotLabel = QLabel("Robots:", self)
        self.typeLabel = QLabel("Type:", self)
        self.comboBucket = QComboBox(self)

        #Localimizdeki bucket ismini aldık.



        #self.comboBucket.addItems(self.bucket_list)
        self.comboBucket.activated[str].connect(self.onChanged_bucket)

        self.comboMeas = CheckableComboBox()
        self.comboMeas.addItems([])
        self.comboMeas.activated_custom.connect(self.onChanged_measurement)

        self.comboField =CheckableComboBox()
        self.comboField.addItems([])
        self.comboField.activated_custom.connect(self.onChanged_field)

        self.comboUnit = CheckableComboBox()
        self.comboUnit.addItems([])
        self.comboUnit.activated_custom.connect(self.onChanged_unit)

        self.comboLocation = CheckableComboBox()
        self.comboLocation.addItems([])
        self.comboLocation.activated_custom.connect(self.onChanged_location)

        self.comboMate = CheckableComboBox()
        self.comboMate.addItems([])
        self.comboMate.activated_custom.connect(self.onChanged_mate)

        self.comboProcess = CheckableComboBox()
        self.comboProcess.addItems([])
        self.comboProcess.activated_custom.connect(self.onChanged_process)

        self.comboRobot = CheckableComboBox()
        self.comboRobot.addItems([])
        self.comboRobot.activated_custom.connect(self.onChanged_robot)

        self.comboType =CheckableComboBox()
        self.comboType.addItems([])
        self.comboType.activated_custom.connect(self.onChanged_type)

        # tab2 mid
        #Query oluşturan RadioButtonların tanımlanması
        self.rad1 = QRadioButton("Sirali Calisma Raporu", self)
        self.rad2 = QRadioButton("AylikKumuleRapor_RobotBazli", self)
        self.rad3 = QRadioButton("AylikKumuleRapor_DepartmanBazli", self)
        self.rad4 = QRadioButton("Aylik Kümüle Rapor", self)
        self.rad1.setChecked(True)
        self.button1 = QPushButton("Create Query", self)
        self.button1.clicked.connect(self.createQuery)


        # tab2 right
        self.resultList = QListWidget(self)
        self.clearButton=QPushButton("Clear List",self)
        self.clearButton.clicked.connect(self.clearList)
        self.export_button=QPushButton("Export to CSV",self)
        self.export_button.clicked.connect(self.save_csv)




        #tab1 left





    def createQuery2(self):
        pass
    def getFileName(self):

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.file_path = QFileDialog.getExistingDirectory(self, "Klasör Seç",
                                                   options=options)
        self.file_path+="/"
        if self.file_path:
            print("Seçilen dosya yolu:", self.file_path)
            self.root=self.file_path
        else :
            message = QMessageBox()

            message.setText("You should select a data path!")
            message.setWindowTitle("Error")
            message.setStandardButtons(QMessageBox.Ok)
            message.exec_()

    def export_csv(self):
        # raporları csv dosyasına gönderme

        with open("RobotsInfo.csv", mode="w") as myFile:
            myFile.write(str(self.value1))
            myFile.write("\n")
            myFile.write(str(self.value2) + '\n')

            for index in range(self.resultList.count()):
                item = self.resultList.item(index)
                myFile.write(item.text() + '\n')

    def save_csv(self):
        # options = QFileDialog.Options()
        # root = "home\\ismailturkan\\influxdb\\"
        # root = QFileDialog.getSaveFileName(self, "Save CSV file", "", "CSV files (.csv);;All Files(*)",options=options)
        self.getFileName()
        if self.rad1.isChecked():

            sheetname = "SiraliCalismaRaporu"

            self.root = self.file_path
            now = datetime.now().strftime(("%d%m%Y"))
            filename = self.root + "RobotCalismaRaporu_" + str(now) + ".xlsx"

            client = InfluxDBClient(
                url=self.url,
                org=self.org,
                bucket=self.bucket,
                token=self.token,
                ssl_ca_cert=certifi.where()
            )

            client.api_client.configuration.verify_ssl = False

            query_api = client.query_api()

            query = self.deneme_query1 + '''|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'''

            data_frame = query_api.query_data_frame(query)

            data_frame['jobtime'] = (round(data_frame['jobtime'] / 60, 2))

            jobtimeSecond = data_frame['jobtime'].sum()
            data_frame.loc['Toplam (Saat)', 'jobtime'] = round(jobtimeSecond / 60, 2)

            columns = ['result', 'table', '_start', '_stop', '_time', '_measurement', 'location', 'mate', 'type']
            data_frame.drop(columns, inplace=True, axis=1)

            data_frame = data_frame.rename(columns={'businessunit': 'Departman'})
            data_frame = data_frame.rename(columns={'process': 'Süreç İsmi'})
            data_frame = data_frame.rename(columns={'robot': 'Çalıştığı Robot'})
            data_frame = data_frame.rename(
                columns={'jobtime': 'Çalışma Süresi (Dakika)'})  # Kolon ismi ayarlamalari yapilir.

            writer = pd.ExcelWriter(filename, engine='xlsxwriter')
            data_frame.to_excel(writer, sheet_name=sheetname)

            workbook = writer.book
            worksheet = writer.sheets[sheetname]

            header_format = workbook.add_format(
                {'bold': True, 'text_wrap': True, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#008080',
                 'font_color': '#ffffff', 'border': 1, 'border_color': '#646464'})
            light_gray_format = workbook.add_format(
                {'bg_color': '#F4F4F4', 'border_color': '#646464', 'valign': 'vcenter', 'border': 1})
            white_format = workbook.add_format(
                {'bg_color': '#FFFFFF', 'border_color': '#646464', 'valign': 'vcenter', 'border': 1})
            lastrow_format = workbook.add_format(
                {'bold': True, 'text_wrap': True, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#008080',
                 'font_color': '#ffffff', 'border': 1, 'border_color': '#646464'})

            row_count = len(data_frame)
            column_count = len(data_frame.columns)

            lastcolumn_index = xlsxwriter.utility.xl_col_to_name(column_count)
            custom_range = "A1:" + lastcolumn_index + str(row_count)
            lastrow_range = "A" + str(row_count + 1) + ":" + lastcolumn_index + str(row_count + 1)

            worksheet.conditional_format(custom_range, {'type': 'formula',
                                                        'criteria': '=ROW()=1',
                                                        'format': header_format})

            worksheet.conditional_format(custom_range, {'type': 'formula',
                                                        'criteria': '=EVEN(ROW())=ROW()',
                                                        'format': white_format})

            worksheet.conditional_format(custom_range, {'type': 'formula',
                                                        'criteria': '=ODD(ROW())=ROW()',
                                                        'format': light_gray_format})

            worksheet.conditional_format(lastrow_range, {'type': 'formula',
                                                         'criteria': '=ROW()=' + str(row_count + 1),
                                                         'format': lastrow_format})

            worksheet.autofit()
            writer.close()

        if self.rad2.isChecked():
            # locale.setlocale(locale.LC_ALL, 'turkish')

            token = self.token
            org = "osmangazi"
            url = "http://localhost:8086"
            bucket = self.bucket
            sheetname = "AylikKumuleRapor_RobotBazli"

            self.root = self.file_path
            now = datetime.now().strftime(("%d%m%Y"))
            filename = self.root + "RobotCalismaRaporu_Aylik_" + str(now) + ".xlsx"

            client = InfluxDBClient(
                url=self.url,
                org=self.org,
                bucket=self.bucket,
                token=self.token,
                ssl_ca_cert=certifi.where()
            )

            client.api_client.configuration.verify_ssl = False

            query_api = client.query_api()
            year = datetime.now().year

            query = self.deneme_query1 + '''|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'''

            data_frame = query_api.query_data_frame(query)

            data_frame['_time'] = pd.to_datetime(data_frame['_time']).dt.strftime("%d.%m.%Y")

            columns = ['result', 'table', '_start', '_stop', '_measurement', 'location', 'mate', 'type', 'businessunit',
                       'process']
            data_frame.drop(columns, inplace=True, axis=1)

            data_frame['_time'] = pd.to_datetime(data_frame['_time'], dayfirst=True)

            data_frame = data_frame.pivot_table("jobtime", index="_time", columns="robot", aggfunc='sum').reset_index()

            grouped_data = data_frame.groupby(pd.Grouper(key='_time', freq='ME'))
            data_frame = grouped_data.sum().reset_index()

            data_frame['_time'] = pd.to_datetime(data_frame['_time']).dt.strftime("%B")
            # data_frame = data_frame/3600

            data_frame = data_frame.rename(columns={'_time': 'AY/ROBOT (Saat)'})

            for excelcolumn in data_frame.columns:
                data_frame[excelcolumn] = data_frame[excelcolumn].apply(
                    lambda x: round(x / 3600, 2) if pd.notnull(x) and isinstance(x, (int, float)) else x)

            writer = pd.ExcelWriter(filename, engine='xlsxwriter')
            data_frame.to_excel(writer, sheet_name=sheetname, index=False)
            workbook = writer.book
            worksheet = writer.sheets[sheetname]

            light_gray_format = workbook.add_format(
                {'bg_color': '#F4F4F4', 'border_color': '#646464', 'valign': 'vcenter', 'border': 1})
            white_format = workbook.add_format(
                {'bg_color': '#FFFFFF', 'border_color': '#646464', 'valign': 'vcenter', 'border': 1})

            row_count = len(data_frame) + 1
            column_count = len(data_frame.columns) - 1

            lastcolumn_index = xlsxwriter.utility.xl_col_to_name(column_count)
            custom_range = "A1:" + lastcolumn_index + str(row_count)
            chart_range = xlsxwriter.utility.xl_col_to_name(column_count + 3)

            header_format = workbook.add_format({'bold': True,
                                                 'text_wrap': True,
                                                 'align': 'center',
                                                 'valign': 'vcenter',
                                                 'bg_color': '#008080',
                                                 'font_color': '#ffffff',
                                                 'border': 1,
                                                 'border_color': '#646464'})

            worksheet.conditional_format(custom_range, {'type': 'formula',
                                                        'criteria': '=ROW()=1',
                                                        'format': header_format})

            worksheet.conditional_format(custom_range, {'type': 'formula',
                                                        'criteria': '=EVEN(ROW())=ROW()',
                                                        'format': white_format})

            worksheet.conditional_format(custom_range, {'type': 'formula',
                                                        'criteria': '=ODD(ROW())=ROW()',
                                                        'format': light_gray_format})

            chart = workbook.add_chart({"type": "column"})

            startcolumn_index = 1

            for columnindex in data_frame.columns:

                columnletter = xlsxwriter.utility.xl_col_to_name(startcolumn_index)

                chart.add_series(
                    {
                        "name": "=" + sheetname + "!$" + columnletter + "$1",
                        "categories": "=" + sheetname + "!$A$2:$A$13",
                        "values": "=" + sheetname + "!$" + columnletter + "$2:$" + columnletter + "$13",
                    }
                )

                startcolumn_index = startcolumn_index + 1
                if len(data_frame.columns) - startcolumn_index == 0:
                    break

            chart.set_title({"name": "Robot Doluluk Analizi"})
            chart.set_x_axis({"name": "Aylar"})
            chart.set_y_axis({"name": "Saat"})

            worksheet.insert_chart(chart_range + "2", chart, {'x_scale': 1.50, 'y_scale': 1})
            worksheet.autofit()
            writer.close()

        if self.rad3.isChecked():
            # locale.setlocale(locale.LC_ALL, 'turkish')

            token = self.token
            org = "osmangazi"
            url = "http://localhost:8086"
            bucket = self.bucket
            filename = "RobotCalismaRaporu_Departman.xlsx"
            sheetname = "AylikKumuleRapor_DepartmanBazli"

            self.root = "/home"
            now = datetime.now().strftime(("%d%m%Y"))
            filename = self.root + "RobotCalismaRaporu_Departman_" + str(now) + ".xlsx"

            client = InfluxDBClient(
                url=self.url,
                org=self.org,
                bucket=self.bucket,
                token=self.token,
                ssl_ca_cert=certifi.where()
            )

            client.api_client.configuration.verify_ssl = False

            query_api = client.query_api()
            year = datetime.now().year

            query = self.deneme_query1 + '''|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'''

            data_frame = query_api.query_data_frame(query)

            data_frame['_time'] = pd.to_datetime(data_frame['_time']).dt.strftime("%d.%m.%Y")

            columns = ['result', 'table', '_start', '_stop', '_measurement', 'location', 'mate', 'robot', 'type',
                       'process']
            data_frame.drop(columns, inplace=True, axis=1)

            data_frame['_time'] = pd.to_datetime(data_frame['_time'], dayfirst=True)

            data_frame = data_frame.pivot_table("jobtime", index="_time", columns="businessunit",
                                                aggfunc='sum').reset_index()

            grouped_data = data_frame.groupby(pd.Grouper(key='_time', freq='ME'))
            data_frame = grouped_data.sum().reset_index()

            data_frame['_time'] = pd.to_datetime(data_frame['_time']).dt.strftime("%B")

            data_frame = data_frame.rename(columns={'_time': 'AY/DEPARTMAN (Saat)'})

            for excelcolumn in data_frame.columns:
                data_frame[excelcolumn] = data_frame[excelcolumn].apply(
                    lambda x: round(x / 3600, 2) if pd.notnull(x) and isinstance(x, (int, float)) else x)

            writer = pd.ExcelWriter(filename, engine='xlsxwriter')
            data_frame.to_excel(writer, sheet_name=sheetname, index=False)
            workbook = writer.book
            worksheet = writer.sheets[sheetname]

            light_gray_format = workbook.add_format(
                {'bg_color': '#F4F4F4', 'border_color': '#646464', 'valign': 'vcenter', 'border': 1})
            white_format = workbook.add_format(
                {'bg_color': '#FFFFFF', 'border_color': '#646464', 'valign': 'vcenter', 'border': 1})

            row_count = len(data_frame) + 1
            column_count = len(data_frame.columns) - 1

            lastcolumn_index = xlsxwriter.utility.xl_col_to_name(column_count)
            custom_range = "A1:" + lastcolumn_index + str(row_count)
            chart_range = xlsxwriter.utility.xl_col_to_name(column_count + 3)

            header_format = workbook.add_format({'bold': True,
                                                 'text_wrap': True,
                                                 'align': 'center',
                                                 'valign': 'vcenter',
                                                 'bg_color': '#008080',
                                                 'font_color': '#ffffff',
                                                 'border': 1,
                                                 'border_color': '#646464'})

            worksheet.conditional_format(custom_range, {'type': 'formula',
                                                        'criteria': '=ROW()=1',
                                                        'format': header_format})

            worksheet.conditional_format(custom_range, {'type': 'formula',
                                                        'criteria': '=EVEN(ROW())=ROW()',
                                                        'format': white_format})

            worksheet.conditional_format(custom_range, {'type': 'formula',
                                                        'criteria': '=ODD(ROW())=ROW()',
                                                        'format': light_gray_format})

            chart = workbook.add_chart({"type": "column"})

            startcolumn_index = 1

            for columnindex in data_frame.columns:

                columnletter = xlsxwriter.utility.xl_col_to_name(startcolumn_index)

                chart.add_series(
                    {
                        "name": "=" + sheetname + "!$" + columnletter + "$1",
                        "categories": "=" + sheetname + "!$A$2:$A$13",
                        "values": "=" + sheetname + "!$" + columnletter + "$2:$" + columnletter + "$13",
                    }
                )

                startcolumn_index = startcolumn_index + 1
                if len(data_frame.columns) - startcolumn_index == 0:
                    break

            chart.set_title({"name": "Departmanlara Göre Robot Çalışma Analizi"})
            chart.set_x_axis({"name": "Aylar"})
            chart.set_y_axis({"name": "Saat"})
            worksheet.insert_chart(chart_range + "2", chart, {'x_scale': 2, 'y_scale': 2})
            worksheet.autofit()
            writer.close()

        if self.rad4.isChecked():
            self.root = self.file_path
            sheetname = "AylikKumuleRapor"
            print("ozan")
            now = datetime.now().strftime(("%d%m%Y"))
            print("ozan")
            filename = self.root + "RobotCalismaRaporu_Aylik_Toplu_" + str(now) + ".xlsx"
            print('OZan')
            client = InfluxDBClient(
                url=self.url,
                org=self.org,
                bucket=self.bucket,
                token=self.token,
                ssl_ca_cert=certifi.where()
            )  # Client ayarlari bu sekilde yapilir.
            print('OZan')

            client.api_client.configuration.verify_ssl = False

            query_api = client.query_api()
            year = datetime.now().year
            print('OZan')
            query = self.deneme_query1 + '''|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'''  # Query bu kisima yazilir.
            print('OZan')
            data_frame = query_api.query_data_frame(
                query)  # Pandas Dataframe formatinda donmesi icin bu kod kullanilir. Bundan sonraki aciklamalarda tablo yerine Dataframe terimi kullanilacaktir.

            data_frame['_time'] = pd.to_datetime(data_frame['_time']).dt.strftime(
                "%d.%m.%Y")  # Dataframe'in _time kolonundaki tarih formatini ayarlar.

            columns = ['result', 'table', '_start', '_stop', '_measurement', 'location', 'mate', 'type', 'businessunit',
                       'process']  # Dataframe'de istenmeyen kolonlardan liste olusturulur.
            data_frame.drop(columns, inplace=True, axis=1)  # İstenmeyen kolonlar atilir.
            print('OZan')

            data_frame['_time'] = pd.to_datetime(data_frame['_time'],
                                                 dayfirst=True)  # _time kolonu Pandas formatina gore datetime'a cevrilir.

            grouped_data = data_frame.groupby(
                pd.Grouper(key='_time', freq='ME'))  # _time kolonunda aylara gore gruplama yapilir.
            aggregated_data = grouped_data[
                'jobtime'].sum().reset_index()  # gruplamadan sonra jobtime'ların toplami alinir.

            aggregated_data['_time'] = pd.to_datetime(aggregated_data['_time']).dt.strftime(
                "%B")  # Gruplamadan sonra ay ismi yazdirilir.
            aggregated_data['jobtime'] = (
                round(aggregated_data['jobtime'] / 3600, 2))  # Saniye cinsinden gelen jobuptime verisi saate cevrilir.

            print('OZan')
            aggregated_data = aggregated_data.rename(columns={'_time': 'AY/ROBOT (Saat)'})
            aggregated_data = aggregated_data.rename(
                columns={'jobtime': 'Çalışma Süresi'})  # Kolon ismi ayarlamalari yapilir.

            writer = pd.ExcelWriter(filename, engine='xlsxwriter')
            aggregated_data.to_excel(writer, sheet_name=sheetname, index=False)
            self.resultList.addItems(aggregated_data)
            workbook = writer.book
            worksheet = writer.sheets[sheetname]

            light_gray_format = workbook.add_format(
                {'bg_color': '#F4F4F4', 'border_color': '#646464', 'valign': 'vcenter', 'border': 1})
            white_format = workbook.add_format(
                {'bg_color': '#FFFFFF', 'border_color': '#646464', 'valign': 'vcenter', 'border': 1})
            print('OZan')
            row_count = len(aggregated_data) + 1
            column_count = len(aggregated_data.columns) - 1

            lastcolumn_index = xlsxwriter.utility.xl_col_to_name(column_count)
            custom_range = "A1:" + lastcolumn_index + str(row_count)
            chart_range = xlsxwriter.utility.xl_col_to_name(column_count + 3)
            print('OZan')
            header_format = workbook.add_format({'bold': True,
                                                 'text_wrap': True,
                                                 'align': 'center',
                                                 'valign': 'vcenter',
                                                 'bg_color': '#008080',
                                                 'font_color': '#ffffff',
                                                 'border': 1,
                                                 'border_color': '#646464'})

            worksheet.conditional_format(custom_range, {'type': 'formula',
                                                        'criteria': '=ROW()=1',
                                                        'format': header_format})

            worksheet.conditional_format(custom_range, {'type': 'formula',
                                                        'criteria': '=EVEN(ROW())=ROW()',
                                                        'format': white_format})

            worksheet.conditional_format(custom_range, {'type': 'formula',
                                                        'criteria': '=ODD(ROW())=ROW()',
                                                        'format': light_gray_format})

            chart = workbook.add_chart({"type": "column"})
            chart.add_series(
                {
                    "name": "=" + sheetname + "!$B$1",
                    "categories": "=" + sheetname + "!$A$2:$A$13",
                    "values": "=" + sheetname + "!$B$2:$B$13",
                }
            )
            chart.set_title({"name": "Aylara Göre Robot Doluluk Analizi"})
            chart.set_x_axis({"name": "Saat"})
            chart.set_y_axis({"name": "Ay"})

            worksheet.insert_chart(chart_range + "2", chart, {'x_scale': 1.50, 'y_scale': 1})

            worksheet.autofit()
            print("ozan")
            writer.close()

    def clearList(self):
        #clear buttonu methodu
        self.resultList.clear()
    def clearList2(self):
        #clear buttonu methodu
        self.resultList2.clear()

    def update(self):

        # tarih seçme için Takvimdeki DateButton için hazırlanan fonksiyon
        self.value1 = self.datetime_edit.dateTime().toPyDateTime()
        self.value2 = self.datetime_edit2.dateTime().toPyDateTime()
        self.query = f'''from(bucket: "{self.bucket}")'''
        print(self.bucket)
        self.query+= f"|> range(start: {self.value1.strftime('%Y-%m-%dT%H:%M:%SZ')}, stop: {self.value2.strftime('%Y-%m-%dT%H:%M:%SZ')})"
        print(self.query)

    def tokenSave(self):
        self.writeJSON()
        self.readJSON()




    def writeJSON(self):
        self.key = Fernet.generate_key()
        self.chipher=Fernet(self.key)
        self.veri=self.tokenText.toPlainText()
        self.encr_token=self.chipher.encrypt(self.veri.encode()).decode()
        with open("ucgen.json","w") as json_file:
            json.dump({"encrypted token":self.encr_token,"key":self.key.decode()},json_file)

        self.tokenText.setText("Configured")
        self.tokenText.setReadOnly(True)
        self.tokenButton.setVisible(False)
        self.tokenUpdateButton.setVisible(True)
        message=QMessageBox()

        message.setText("Token is configured")
        message.setWindowTitle("Message")
        message.setStandardButtons(QMessageBox.Ok)
        message.exec_()



    def readJSON(self):

        with open("ucgen.json","r") as json_file:
            self.data=json.load(json_file)
            self.enc_data=self.data["encrypted token"].encode()
            self.key=self.data["key"].encode()
            self.chipher=Fernet(self.key)
            self.decr_token=self.chipher.decrypt(self.enc_data).decode()
            self.token=self.decr_token

        return self.token
    def TokenUpdate(self):
        self.tokenText.setReadOnly(False)
        self.tokenUpdateButton.setVisible(False)
        self.tokenButton.setVisible(True)
        self.tokenText.setText("")
        if os.path.exists("ucgen.json"):
            os.remove("ucgen.json")
            self.token=" "
            print("a")

   # def tokenKontrol(self):
    #    try:
     #       self.kontrol=self.readJSON()
#
 #           if self.kontrol:

  #                  self.token=self.kontrol
   #                 self.tokenText.setText("Configured")
    #                self.tokenText.setReadOnly(True)
     #               self.tokenButton.setVisible(False)
      #              self.tokenUpdateButton.setVisible(True)



#        except FileNotFoundError:
            ##yoksa boş bir dosya olarak oluştur ve fonskiyonu tekrar çağır
 #           print("token.json dosyası bulunamadı.")

  #      except json.decoder.JSONDecodeError:
   #         print("token.json uygunsuz formatta.")



    def createQuery(self):
        #Create Query butonunun methodu
        if self.rad1.isChecked():
            self.newQuery=self.query
            self.newQuery+='''\n|> count()'''

            #influxdb bağlantısı
            client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
            query_api = client.query_api()
            result = query_api.query(org=self.org, query=self.newQuery)

            results = []
            UnitList=[]
            rbtList=[]
            processlist = []
            FieldList=[]

            for table in result:
                for record in table.records:
                    results.append(str(record.get_value()))
                    UnitList.append(record.values["businessunit"])
                    processlist.append(record.values["process"])
                    rbtList.append(record.values["robot"])
                    FieldList.append(record.get_field())
            #üstte serverdan doldurduğumuz listeleri kullanarak arayüzün sağ ekranına rapor oluşumu
            for a,b,c,d,e in zip(processlist,UnitList,rbtList,FieldList,results):
                self.resultList.addItem(f"{b} DEPARTMANINDAKİ \n {c} ADLI ROBOTUN {a},İŞLEMİNDEKİ TOPLAM \n {d} SAYISI {e} dır/dir\n")

        if self.rad2.isChecked():

            query = self.query
            query += '''|> count()'''
            #influxdb bağlantısı
            client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
            query_api = client.query_api()
            result = query_api.query(org=self.org, query=query)

            ProcessList=[]
            RobotList=list()
            FieldList=[]

            for table in result:
                for record in table.records:

                    ProcessList.append(record.values["process"])
                    RobotList.append(record.values["robot"])
                    FieldList.append(record.get_field())
            x=""
            for i,a,j in zip(ProcessList,RobotList,FieldList) :

                if i==x:
                    self.resultList.addItem(f"{j}'ta")
                    self.resultList.addItem(a)
                    self.resultList.addItem(" ")

                else:
                    self.resultList.addItem(f"\n{i} ADLI İŞLEMDE BULUNAN ROBOTLAR\n")
                    self.resultList.addItem(f"{j}'ta")
                    self.resultList.addItem(a)
                    self.resultList.addItem(" ")
                    x=i
        if self.rad3.isChecked():


            self.queryforrad3+=""" |>group(columns: ["robot","process"])\n|> count()"""

            client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
            query_api = client.query_api()
            result = query_api.query(org=self.org, query=self.queryforrad3)

            ProcessList = []
            RobotList = []

            for table in result:
                for record in table.records:
                    ProcessList.append(record.values["process"])
                    RobotList.append(record.values["robot"])
            x = ""
            for i, a in zip(ProcessList, RobotList):

                if a == x:
                    self.resultList.addItem(i)

                else:
                    self.resultList.addItem(f"\n{a} ADLI ROBOTUN ÇALIŞTIĞI PROCESSLER\n")
                    self.resultList.addItem(i)
                    x = a


    def layouts(self):
        self.mainLayout = QHBoxLayout()
        self.leftLayout = QFormLayout()
        self.midLayout = QFormLayout()
        self.rightLayout = QFormLayout()

        # leftLayout
        self.leftLayoutGroupBox = QGroupBox("Server")
        self.leftLayout.addRow(self.comboForDate)
        self.leftLayout.addRow(self.start_time_label)
        self.leftLayout.addRow(self.datetime_edit)
        self.leftLayout.addRow(self.stop_time_label)
        self.leftLayout.addRow(self.datetime_edit2)
        self.leftLayout.addRow(self.button)
        #self.leftLayout.addRow(self.tokenLabel)
        #self.leftLayout.addRow(self.tokenText)
        #self.leftLayout.addRow(self.tokenButton)
        #self.leftLayout.addRow(self.tokenUpdateButton)
        self.leftLayout.addRow(self.bucketLabel)
        self.leftLayout.addRow(self.comboBucket)
        self.leftLayout.addRow(self.measurementLabel)
        self.leftLayout.addRow(self.comboMeas)
        self.leftLayout.addRow(self.fieldsLabel)
        self.leftLayout.addRow(self.comboField)
        self.leftLayout.addRow(self.businessLabel)
        self.leftLayout.addRow(self.comboUnit)
        self.leftLayout.addRow(self.locationLabel)
        self.leftLayout.addRow(self.comboLocation)
        self.leftLayout.addRow(self.matelabel)
        self.leftLayout.addRow(self.comboMate)
        self.leftLayout.addRow(self.processLabel)
        self.leftLayout.addRow(self.comboProcess)
        self.leftLayout.addRow(self.robotLabel)
        self.leftLayout.addRow(self.comboRobot)
        self.leftLayout.addRow(self.typeLabel)
        self.leftLayout.addRow(self.comboType)
        self.leftLayoutGroupBox.setLayout(self.leftLayout)

        # midlayout
        self.midLayoutGroupBox = QGroupBox("Query")
        self.midLayout.addRow(self.rad1)
        self.midLayout.addRow(self.rad2)
        self.midLayout.addRow(self.rad3)
        self.midLayout.addRow(self.rad4)

        self.midLayout.addRow(self.button1)
        self.midLayoutGroupBox.setLayout(self.midLayout)

        # rightlayout
        self.rightLayoutGroupBox = QGroupBox("Result")
        self.rightLayout.addRow(self.resultList)
        self.rightLayout.addRow(self.clearButton)
        self.rightLayout.addRow(self.export_button)
        self.rightLayoutGroupBox.setLayout(self.rightLayout)


        # tab2mainlayout
        self.mainLayout.addWidget(self.leftLayoutGroupBox, 30)
        self.mainLayout.addWidget(self.midLayoutGroupBox, 30)
        self.mainLayout.addWidget(self.rightLayoutGroupBox, 40)
        self.tab2.setLayout(self.mainLayout)





        ##########TAB1########
        font = QFont("Arial", 8)
        font.setWeight(QFont.Bold)

        hbox=QHBoxLayout()
        hbox.addStretch(1)
        self.lbltoken = QLabel("Token:",self)
        self.lbltoken.setFont(font)
        self.txttoken=QLineEdit(self)
        self.txttoken.setStyleSheet(
            "background-color: white; color: black; border: 2px solid red; border-radius: 10px; font-family: Arial; font-size: 8pt;")

        self.txttoken.setFixedWidth(300)
        self.txttoken.setFixedHeight(20)
        hbox.addWidget(self.lbltoken)
        hbox.addWidget(self.txttoken)
        hbox.addStretch(1)


        hbox2=QHBoxLayout()
        hbox2.addStretch(1)
        self.lblorg = QLabel("Org:", self)
        self.lblorg.setFont(font)
        self.txtorg = QLineEdit(self)
        self.txtorg.setStyleSheet("background-color: white; color: black; border: 2px solid red; border-radius: 10px; font-family: Arial; font-size: 8pt;")
        self.txtorg.setFixedWidth(300)
        self.txtorg.setFixedHeight(20)
        hbox2.addWidget(self.lblorg)
        hbox2.addWidget(self.txtorg)
        hbox2.addStretch(1)

        hbox3 = QHBoxLayout()
        hbox3.addStretch(1)
        self.lblurl = QLabel("Url:", self)
        self.lblurl.setFont(font)
        self.txturl = QLineEdit(self)
        self.txturl.setStyleSheet("background-color: white; color: black; border: 2px solid red; border-radius: 10px; font-family: Arial; font-size: 8pt;")

        self.txturl.setFixedWidth(300)
        self.txturl.setFixedHeight(20)
        hbox3.addWidget(self.lblurl)
        hbox3.addWidget(self.txturl)
        hbox3.addStretch(1)


        hbox4= QHBoxLayout()
        hbox4.addStretch(1)
        self.lblbucket = QLabel("Bucket:", self)
        self.lblbucket.setFont(font)
        self.txtbucket = QLineEdit(self)
        self.txtbucket.setStyleSheet("background-color: white; color: black; border: 2px solid red; border-radius: 10px; font-family: Arial; font-size: 8pt;")

        self.txtbucket.setFixedWidth(300)
        self.txtbucket.setFixedHeight(20)
        hbox4.addWidget(self.lblbucket)
        hbox4.addWidget(self.txtbucket)
        hbox4.addStretch(1)


        hbox5=QHBoxLayout()

        self.connectButton=QPushButton("Bilgileri Kaydet")
        self.connectButton.setFixedWidth(100)
        self.connectButton.setFixedHeight(20)
        self.connectButton.setStyleSheet( "background-color: white; color: black; border: 2px solid red; border-radius: 10px; font-family: Arial; font-size: 8pt;")
        self.connectButton.clicked.connect(self.connectInflux)
        self.connectButton.setCursor(Qt.PointingHandCursor)
        hbox5.addStretch(2)
        hbox5.addWidget(self.connectButton)
        hbox5.addStretch(1)



        vbox=QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        vbox.addLayout(hbox4)
        vbox.addLayout(hbox5)

        self.setLayout(vbox)
        self.tab1.setLayout(vbox)

    def connectInflux(self):
        self.token=self.txttoken.text()
        self.org=self.txtorg.text()
        self.url=self.txturl.text()
        self.bucket=self.txtbucket.text()


        self.bucket_list.add(self.bucket)

        #self.comboBucket.addItems(self.bucket_list)
        print("1")


        if self.token == "" or self.bucket=="" or self.org=="" or self.url=="":
            print("5")
            QMessageBox.warning(self,"Hata","Eksik bilgi!")
        else:
            print("6")
            if (self.add_unique_item(self.comboBucket, self.bucket)):
                print("3")
                self.comboBucket.addItem(self.bucket)
                QMessageBox.information(self, "Bilgi", "Bilgiler kaydedildi")



    def add_unique_item(self,combo_box, item):
        # ComboBox'ta aynı öğe olup olmadığını kontrol et
        print("2")

        if item not in [combo_box.itemText(i) for i in range(combo_box.count())]:
             #combo_box.addItems(item)
                print("4")

                return True
        elif self.token==self.txttoken.text():
                QMessageBox.information(self,"Uyarı","Bilgiler güncellendi")
                return False






    def newDateFunc(self,newDate):

        if (newDate=="Tarih Belirle"):



            self.start_time_label.setVisible(True)
            self.stop_time_label.setVisible(True)
            self.datetime_edit.setVisible(True)
            self.datetime_edit2.setVisible(True)
            self.button.setVisible(True)

        elif(newDate=="Dün"):
            self.value1=self.yesterday
            self.value2=self.today
            self.query = f'''from(bucket: "{self.bucket}")'''
            self.query += f"|> range(start: {self.value1.strftime('%Y-%m-%dT%H:%M:%SZ')}, stop: {self.value2.strftime('%Y-%m-%dT%H:%M:%SZ')})"
            print(self.query)

            self.start_time_label.setVisible(False)
            self.stop_time_label.setVisible(False)
            self.datetime_edit.setVisible(False)
            self.datetime_edit2.setVisible(False)
            self.button.setVisible(False)

        elif(newDate=="3 Gün Önce"):
            self.value1=self.lastThreeDays
            self.value2=self.today
            self.query = f'''from(bucket: "{self.bucket}")'''
            self.query += f"|> range(start: {self.value1.strftime('%Y-%m-%dT%H:%M:%SZ')}, stop: {self.value2.strftime('%Y-%m-%dT%H:%M:%SZ')})"
            print(self.query)

            self.start_time_label.setVisible(False)
            self.stop_time_label.setVisible(False)
            self.datetime_edit.setVisible(False)
            self.datetime_edit2.setVisible(False)
            self.button.setVisible(False)

        elif(newDate=="1 Hafta Önce"):
            self.value1 = self.lastWeek
            self.value2 = self.today
            self.query = f'''from(bucket: "{self.bucket}")'''
            self.query += f"|> range(start: {self.value1.strftime('%Y-%m-%dT%H:%M:%SZ')}, stop: {self.value2.strftime('%Y-%m-%dT%H:%M:%SZ')})"
            print(self.query)

            self.start_time_label.setVisible(False)
            self.stop_time_label.setVisible(False)
            self.datetime_edit.setVisible(False)
            self.datetime_edit2.setVisible(False)
            self.button.setVisible(False)
        elif(newDate=="15 Gün Önce"):
            self.value1 = self.lastFifteen
            self.value2 = self.today
            self.query = f'''from(bucket: "{self.bucket}")'''
            self.query += f"|> range(start: {self.value1.strftime('%Y-%m-%dT%H:%M:%SZ')}, stop: {self.value2.strftime('%Y-%m-%dT%H:%M:%SZ')})"
            print(self.query)

            self.start_time_label.setVisible(False)
            self.stop_time_label.setVisible(False)
            self.datetime_edit.setVisible(False)
            self.datetime_edit2.setVisible(False)
            self.button.setVisible(False)
        elif(newDate=="1 Ay Önce"):
            months_to_subtract = 1

            year_diff = months_to_subtract // 12
            month_diff = months_to_subtract % 12

            new_year = self.today.year - year_diff
            new_month = self.today.month - month_diff

            if new_month <= 0:
                new_year -= 1
                new_month += 12

            a_months_ago = self.today.replace(year=new_year, month=new_month)

            self.value1 = a_months_ago
            self.value2 = self.today
            self.query = f'''from(bucket: "{self.bucket}")'''
            self.query += f"|> range(start: {self.value1.strftime('%Y-%m-%dT%H:%M:%SZ')}, stop: {self.value2.strftime('%Y-%m-%dT%H:%M:%SZ')})"
            print(self.query)

            self.start_time_label.setVisible(False)
            self.stop_time_label.setVisible(False)
            self.datetime_edit.setVisible(False)
            self.datetime_edit2.setVisible(False)
            self.button.setVisible(False)
        elif(newDate=="3 Ay Önce"):
            months_to_subtract = 3

            year_diff = months_to_subtract // 12
            month_diff = months_to_subtract % 12

            new_year = self.today.year - year_diff
            new_month = self.today.month - month_diff

            if new_month <= 0:
                new_year -= 1
                new_month += 12

            three_months_ago = self.today.replace(year=new_year, month=new_month)


            self.value1 = three_months_ago
            self.value2 = self.today
            self.query = f'''from(bucket: "{self.bucket}")'''
            self.query += f"|> range(start: {self.value1.strftime('%Y-%m-%dT%H:%M:%SZ')}, stop: {self.value2.strftime('%Y-%m-%dT%H:%M:%SZ')})"
            print(self.query)

            self.start_time_label.setVisible(False)
            self.stop_time_label.setVisible(False)
            self.datetime_edit.setVisible(False)
            self.datetime_edit2.setVisible(False)
            self.button.setVisible(False)
        elif(newDate=="6 Ay Önce"):
            months_to_subtract = 6

            year_diff = months_to_subtract // 12
            month_diff = months_to_subtract % 12

            new_year = self.today.year - year_diff
            new_month = self.today.month - month_diff

            if new_month <= 0:
                new_year -= 1
                new_month += 12

            six_months_ago = self.today.replace(year=new_year, month=new_month)

            self.value1 = six_months_ago
            self.value2 = self.today
            self.query = f'''from(bucket: "{self.bucket}")'''
            self.query += f"|> range(start: {self.value1.strftime('%Y-%m-%dT%H:%M:%SZ')}, stop: {self.value2.strftime('%Y-%m-%dT%H:%M:%SZ')})"
            print(self.query)

            self.start_time_label.setVisible(False)
            self.stop_time_label.setVisible(False)
            self.datetime_edit.setVisible(False)
            self.datetime_edit2.setVisible(False)
            self.button.setVisible(False)

    def onChanged_bucket(self, text_bucket):
        self.bucket = text_bucket
        with InfluxDBClient(url=self.url, token=self.token, org=self.org) as client:
            query_api = client.query_api()
            my_set_measurement = set()


        tables = query_api.query(f'''from(bucket: "{self.bucket}")
  |> range(start: {self.value1.strftime('%Y-%m-%dT%H:%M:%SZ')}, stop: {self.value2.strftime('%Y-%m-%dT%H:%M:%SZ')})
  |> group(columns: ["_measurement"])
  |> aggregateWindow(every: 12h, fn: mean, createEmpty: false)
  |> yield(name: "mean") ''')
        for table in tables:
            for record in table.records:
                my_set_measurement.add(record.values["_measurement"])



        self.measurement = list(my_set_measurement)  # Küme yerine liste olarak saklayın
        self.comboMeas.clear()  # Önceki seçenekleri temizleyin
        self.comboMeas.addItems(self.measurement)



    def onChanged_measurement(self, text_measurement):
        self.measurement = text_measurement
        self.deneme_querym = self.manualQuery(self.comboMeas, "_measurement")
        self.meas_query = self.deneme_querym
        self.meas_query += '''\n|> group(columns: ["_field"])'''
        self.queryforrad3=self.query
        self.deneme_query=self.query
        print(self.query)



        with InfluxDBClient(url=self.url, token=self.token, org=self.org) as client:
            query_api = client.query_api()
            my_set_fields = set()

        tables = query_api.query(self.meas_query)
        for table in tables:
            for record in table.records:
                my_set_fields.add(record.get_field())

        self.field = list(my_set_fields)
        self.comboField.clear()
        self.comboField.addItems(self.field)
    def QueryRad3(self,combo,d):
        txt = combo.currentText()
        parcalar = txt.split(",")
        self.radx = ""
        self.radx = self.queryforrad3
        self.list3 = []

        for parca in parcalar:
            self.list3.append(parca.strip())
        print(self.list3)
        first_iteretion = True
        if len(self.list3) > 1:
            for i in self.list3:
                if first_iteretion:
                    self.radx += f'''\n|> filter(fn: (r) => r["{d}"] == "{i}"'''
                    first_iteretion = False
                else:
                    self.radx += f''' or r["{d}"] == "{i}"'''
        else:
            for i in self.list3:
                if first_iteretion:
                    self.radx += f'''\n|> filter(fn: (r) => r["{d}"] == "{i}"'''
                    first_iteretion = False
        self.radx += ")"
        print(self.list3)
        return self.radx

    def manualQuery(self,combo,d):
        txt = combo.currentText()
        parcalar = txt.split(",")
        self.xxxx=""
        self.xxxx=self.query
        self.list2=[]

        for parca in parcalar:
            self.list2.append(parca.strip())
        print(self.list2)
        first_iteretion=True
        if len(self.list2)>1:
            for i in self.list2:
                if first_iteretion:
                    self.xxxx+=f'''\n|> filter(fn: (r) => r["{d}"] == "{i}"'''
                    first_iteretion=False
                else:
                    self.xxxx+=f''' or r["{d}"] == "{i}"'''
        else:
            for i in self.list2:
                if first_iteretion:
                 self.xxxx+=f'''\n|> filter(fn: (r) => r["{d}"] == "{i}"'''
                 first_iteretion=False
        self.xxxx+=")"
        print(self.list2)
        return self.xxxx

    def onChanged_field(self):
        self.query=self.deneme_querym
        self.deneme_query1 = self.manualQuery(self.comboField,"_field")
        self.field_query=self.deneme_query1
        self.field_query += '''\n|> group(columns: ["businessunit"])'''

        print(self.deneme_query1)
        with InfluxDBClient(url=self.url, token=self.token, org=self.org) as client:
            query_api = client.query_api()
            my_set_unit = set()
        tables = query_api.query(self.field_query)
        for table in tables:
            for record in table.records:
                my_set_unit.add(record.values["businessunit"])

        self.businessunit = list(my_set_unit)
        self.comboUnit.clear()
        self.comboUnit.addItems(self.businessunit)


    def onChanged_unit(self):
        self.query=self.deneme_query1
        self.deneme_query2 = self.manualQuery(self.comboUnit, "businessunit")
        self.unit_query=self.deneme_query2
        self.unit_query += '''\n|> group(columns: ["location"])'''
        print(self.unit_query)

        with InfluxDBClient(url=self.url, token=self.token, org=self.org) as client:
            query_api = client.query_api()
            my_set_location = set()
        tables = query_api.query(self.unit_query)
        for table in tables:
            for record in table.records:
                my_set_location.add(record.values["location"])

        self.location = list(my_set_location)
        self.comboLocation.clear()
        self.comboLocation.addItems(self.location)

    def onChanged_location(self):
        self.query = self.deneme_query2

        self.deneme_query3 = self.manualQuery(self.comboLocation, "location")
        self.location_query=self.deneme_query3
        self.location_query += '''\n|> group(columns: ["mate"])'''
        self.location_query+='''\n|> aggregateWindow(every: 12h, fn: mean, createEmpty: false)'''
        print(self.location_query)
        with InfluxDBClient(url=self.url, token=self.token, org=self.org) as client:
            query_api = client.query_api()
            my_set_mate = set()

        tables = query_api.query(self.location_query)
        for table in tables:
            for record in table.records:
                my_set_mate.add(record.values["mate"])

        self.mate = list(my_set_mate)
        self.comboMate.clear()
        self.comboMate.addItems(self.mate)

    def onChanged_mate(self):
        self.query = self.deneme_query3

        self.deneme_query4 = self.manualQuery(self.comboMate, "mate")
        self.mate_query=self.deneme_query4
        self.mate_query += '''\n|> group(columns: ["process"])'''
        print(self.mate_query)
        with InfluxDBClient(url=self.url, token=self.token, org=self.org) as client:
            query_api = client.query_api()
            my_set_process = set()
        tables = query_api.query(self.mate_query)
        for table in tables:
            for record in table.records:
                my_set_process.add(record.values["process"])

        self.process = list(my_set_process)
        self.comboProcess.clear()
        self.comboProcess.addItems(self.process)

    def onChanged_process(self):
        self.query = self.deneme_query4
        self.deneme_query5 = self.manualQuery(self.comboProcess, "process")
        self.process_query=self.deneme_query5
        self.process_query += '''\n|> group(columns: ["robot"])'''
        print(self.process_query)
        with InfluxDBClient(url=self.url, token=self.token, org=self.org) as client:
            query_api = client.query_api()
            my_set_robot = set()
        tables = query_api.query(self.process_query)
        for table in tables:
            for record in table.records:
                my_set_robot.add(record.values["robot"])

        self.robot = list(my_set_robot)
        self.comboRobot.clear()
        self.comboRobot.addItems(self.robot)

    def onChanged_robot(self):
        self.query = self.deneme_query5
        self.deneme_query6 = self.manualQuery(self.comboRobot, "robot")
        self.robot_query=self.deneme_query6

        self.robot_query += '''\n|> group(columns: ["type"])'''
        print(self.deneme_query)
        with InfluxDBClient(url=self.url, token=self.token, org=self.org) as client:
            query_api = client.query_api()
            my_set_type = set()
        tables = query_api.query(self.robot_query)
        for table in tables:
            for record in table.records:
                my_set_type.add(record.values["type"])

        self.type = list(my_set_type)
        self.comboType.clear()
        self.comboType.addItems(self.type)

    def onChanged_type(self):
        self.query = self.deneme_query6
        self.queryforrad3 = self.QueryRad3(self.comboRobot, "robot")
        self.deneme_query7 = self.manualQuery(self.comboType, "type")
        print(self.deneme_query7)

    def menubar(self):
        bar = self.menuBar()
        file = bar.addMenu("Settings")
        file.addAction("Log Out")
        file.triggered[QAction].connect(self.exit)

    def exit(self):
        from AdminLogin import LoginWindowForAdmin
        self.c = LoginWindowForAdmin()
        self.c.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WindowAdminPanel()
    window.show()
    sys.exit(app.exec_())