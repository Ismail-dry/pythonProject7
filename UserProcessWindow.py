import sys, os
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDateTime, Qt, QEvent, pyqtSignal
from influxdb_client import InfluxDBClient
from PyQt5.QtGui import QStandardItem, QIcon, QFont
from datetime import datetime, timedelta
import locale
import xlsxwriter
import pandas as pd
import certifi
from PyQt5.QtChart import QChart, QChartView, QBarSet, QBarSeries, QBarCategoryAxis
import json
import sqlite3
from cryptography.fernet import Fernet
from influxdb.exceptions import InfluxDBClientError,  InfluxDBServerError
import requests.exceptions



#


class WindowForUserProcess(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setGeometry(50, 50, 1080, 640)
        self.tabWidget()
        self.Widgets()
        self.layouts()
        self.setWindowTitle("InfluxDB Sorgulama 2.1")
        self.setWindowIcon(QIcon('x.ico'))
        self.menubar()
        self.show()
        # InfluxDB Localimize ulaşmak için gereken token org bilgilerini tanımlandı.
        self.query = f'''from(bucket: "ucgen")'''

        self.org = "-"
        self.url = "http://localhost:8086"
        self.list2 = []
        self.key = ""
        # Tarih seçme kısmı için takvim ekranı en başta görünmez olarak tanımlandı.
        self.start_time_label.setVisible(False)
        self.stop_time_label.setVisible(False)
        self.datetime_edit.setVisible(False)
        self.datetime_edit2.setVisible(False)
        self.button.setVisible(False)


    def get_data(self,data_name,data_psw):
        print(data_name)
        #print(data_psw)
        conn = sqlite3.connect('Users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT Username,Password,Key_F,Token,Org,Url,Bucket FROM Users")
        val = cursor.fetchall()

        if len(val) >= 1:

            for x in val:
                enc_name2 = x[0].encode()
                key2 = x[2].encode()
                chipher2 = Fernet(key2)
                decr_name = chipher2.decrypt(enc_name2).decode()

                enc_pw2 = x[1].encode()
                key3 = x[2].encode()
                chipher3 = Fernet(key3)
                decr_pw = chipher3.decrypt(enc_pw2).decode()

                enc_token=x[3].encode()
                key4=x[2].encode()
                chipher4=Fernet(key4)
                decr_token=chipher4.decrypt(enc_token).decode()

                enc_org = x[4].encode()
                key5 = x[2].encode()
                chipher5 = Fernet(key5)
                decr_org = chipher5.decrypt(enc_org).decode()

                enc_url = x[5].encode()
                key6 = x[2].encode()
                chipher6 = Fernet(key6)
                decr_url = chipher6.decrypt(enc_url).decode()

                enc_bucket = x[6].encode()
                key7 = x[2].encode()
                chipher7 = Fernet(key7)
                decr_bucket = chipher7.decrypt(enc_bucket).decode()

                if data_name == decr_name and data_psw == decr_pw:
                    self.token=decr_token
                    self.org=decr_org
                    self.bucket=decr_bucket
                    self.url=decr_url
                    break

                else:
                    pass

    # Kullandığımız Widget ekranı için oluşturulan Tablar
    def tabWidget(self):
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.tab1 = QWidget()

        self.tabs.addTab(self.tab1, "Main")

    def Widgets(self):
        # tabMain left
        # tarih seçmek için comboBox oluşturuldu.
        self.comboForDate = QComboBox(self)
        # Tarih kısayolları için liste oluşturuldu
        dateList = ["Dün", "3 Gün Önce", "1 Hafta Önce", "15 Gün Önce", "1 Ay Önce", "3 Ay Önce", "6 Ay Önce",
                    "Tarih Belirle"]
        # liste tarih comboBoxuna atandı.
        self.comboForDate.addItems(dateList)
        self.comboForDate.setStyleSheet(
            "background-color: white; color black; border: 2px solid grey; border-radius: 5px; font-family: Arial; font-size: 8pt;")
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

        self.button = QPushButton("DateButton", self)
        self.button.clicked.connect(self.update)
        self.start_time_label = QLabel("Start:", self)
        self.stop_time_label = QLabel("Stop:", self)

        # Localimizdeki bucket ismini aldık.

        # tab1 mid
        # Query oluşturan RadioButtonların tanımlanması
        self.rad1 = QRadioButton("Sirali Calisma Raporu2", self)
        self.rad2 = QRadioButton("AylikKumuleRapor_RobotBazli", self)
        self.rad3 = QRadioButton("AylikKumuleRapor_DepartmanBazli", self)
        self.rad4 = QRadioButton("Aylik Kümüle Rapor", self)
        self.rad1.setChecked(True)
        self.button1 = QPushButton("Create Query", self)
        self.button1.setStyleSheet(
            "background-color: white; color black; border: 2px solid grey; border-radius: 5px; font-family: Arial; font-size: 8pt;")
        self.button1.clicked.connect(self.createQuery)

        # tab1 right
        self.resultList = QTableWidget()
        self.clearButton = QPushButton("Clear List", self)
        self.clearButton.setStyleSheet(
            "background-color: white; color black; border: 2px solid grey; border-radius: 5px; font-family: Arial; font-size: 8pt;")
        self.clearButton.clicked.connect(self.clearList)
        self.export_button = QPushButton("Export to CSV", self)
        self.export_button.setStyleSheet(
            "background-color: white; color black; border: 2px solid grey; border-radius: 5px; font-family: Arial; font-size: 8pt;")

        self.export_button.clicked.connect(self.save_csv)

        self.chart_view = QChartView()
        self.series = QBarSeries()
        # self.axis = QBarCategoryAxis()

    def menubar(self):
        bar = self.menuBar()
        file = bar.addMenu("Settings")
        file.addAction("Log Out")
        file.triggered[QAction].connect(self.exit)

    def exit(self):
        from UserLogin import  LoginWindow
        self.c=LoginWindow()
        self.c.show()
        self.close()

    def getFileName(self):

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.file_path = QFileDialog.getExistingDirectory(self, "Klasör Seç",
                                                          options=options)
        if self.file_path:
            self.file_path += "/"
        if self.file_path:
            print("Seçilen dosya yolu:", self.file_path)
            self.root = self.file_path
        else:
            message = QMessageBox()
            print("merhaba")
            message.setText("You should select a data path!")
            message.setWindowTitle("Error")
            message.setStandardButtons(QMessageBox.Ok)
            message.exec_()



    def save_csv(self):

        self.getFileName()
        if not self.file_path:
            return

        if self.rad1.isChecked():
            sheetname = "SiraliCalismaRaporu"

            self.root = self.file_path
            now = datetime.now().strftime(("%d%m%Y"))
            filename = self.root + "RobotCalismaRaporu_" + str(now) + ".xlsx"
            print("ozan")

            try:
                client = InfluxDBClient(
                bucket=self.bucket,
                org=self.org,
                url=self.url,
                token=self.token,
                ssl_ca_cert=certifi.where()
                    )

                client.api_client.configuration.verify_ssl = False

                query_api = client.query_api()
                query = f"""from(bucket: "{self.bucket}")
                             |> range(start: {self.value1.strftime('%Y-%m-%dT%H:%M:%SZ')}, stop: {self.value2.strftime('%Y-%m-%dT%H:%M:%SZ')})
                             |> filter(fn: (r) => r["_field"] == "jobtime")
                             |> filter(fn: (r) => r["_measurement"] == "seeme_VSTL") 
                             |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")"""  # Query bu kisima yazilir.

                data_frame = query_api.query_data_frame(query)
                if not data_frame.empty:
                    data_frame['jobtime'] = (round(data_frame['jobtime'] / 60, 2))

                    jobtimeSecond = data_frame['jobtime'].sum()
                    data_frame.loc['Toplam (Saat)', 'jobtime'] = round(jobtimeSecond / 60, 2)

                    columns = ['result', 'table', '_start', '_stop', '_time', '_measurement', 'location', 'mate',
                               'type']
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
                else:
                    self.pop_message("Sonuç yok")
                    self.clearList()
                    return

            except InfluxDBClientError as e:
                self.pop_message( e)
                return

            except ConnectionError as e:
                self.pop_message(e)
                return

            except Exception as e:
                self.pop_message(e)
                return

            except InfluxDBServerError as e:

                # InfluxDBServerError: InfluxDB sunucusu ile ilgili genel hatalar

                self.pop_message(e)
                return

        if self.rad2.isChecked():
            # locale.setlocale(locale.LC_ALL, 'turkish')


            sheetname = "AylikKumuleRapor_RobotBazli"

            self.root = self.file_path
            now = datetime.now().strftime(("%d%m%Y"))
            filename = self.root + "RobotCalismaRaporu_Aylik_" + str(now) + ".xlsx"
            try:

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

                query = f"""from(bucket: "{self.bucket}")
                             |> range(start: {self.value1.strftime('%Y-%m-%dT%H:%M:%SZ')}, stop: {self.value2.strftime('%Y-%m-%dT%H:%M:%SZ')})
                             |> filter(fn: (r) => r._field == "jobtime")
                             |> filter(fn: (r) => r["_measurement"] == "seeme_VSTL") 
                             |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")"""

                data_frame = query_api.query_data_frame(query)
                if not data_frame.empty:
                    data_frame['_time'] = pd.to_datetime(data_frame['_time']).dt.strftime("%d.%m.%Y")

                    columns = ['result', 'table', '_start', '_stop', '_measurement', 'location', 'mate', 'type',
                               'businessunit',
                               'process']
                    data_frame.drop(columns, inplace=True, axis=1)

                    data_frame['_time'] = pd.to_datetime(data_frame['_time'], dayfirst=True)

                    data_frame = data_frame.pivot_table("jobtime", index="_time", columns="robot",
                                                        aggfunc='sum').reset_index()

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
                else:
                    self.pop_message("Sonuç yok!")
                    self.clearList()
                    return
            except InfluxDBClientError as e:
                self.pop_message(e)
                return


            except ConnectionError as e:
                self.pop_message(e)

                return
            except Exception as e:
                self.pop_message(e)
                return
            except InfluxDBServerError as e:

                # InfluxDBServerError: InfluxDB sunucusu ile ilgili genel hatalar

                self.pop_message(e)
                return

        if self.rad3.isChecked():
           # filename = "RobotCalismaRaporu_Departman.xlsx"
            sheetname = "AylikKumuleRapor_DepartmanBazli"

            self.root = self.file_path
            now = datetime.now().strftime(("%d%m%Y"))
            filename = self.root + "RobotCalismaRaporu_Departman_" + str(now) + ".xlsx"
            try:
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

                query = f"""from(bucket: "{self.bucket}")
                                         |> range(start: {self.value1.strftime('%Y-%m-%dT%H:%M:%SZ')}, stop: {self.value2.strftime('%Y-%m-%dT%H:%M:%SZ')})
                                         |> filter(fn: (r) => r._field == "jobtime")
                                         |> filter(fn: (r) => r._measurement == "seeme_VSTL") 
                                         |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")"""

                data_frame = query_api.query_data_frame(query)
                if not data_frame.empty:
                    data_frame['_time'] = pd.to_datetime(data_frame['_time']).dt.strftime("%d.%m.%Y")

                    columns = ['result', 'table', '_start', '_stop', '_measurement', 'location', 'mate', 'robot',
                               'type',
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
                else:
                    self.pop_message("Sonuç Yok!")
                    self.clearList()
                    return

            except InfluxDBClientError as e:
                self.pop_message(e)
                return

            except ConnectionError as e:
                self.pop_message(e)
                return

            except Exception as e:
                self.pop_message(e)
                return
            except InfluxDBServerError as e:

                # InfluxDBServerError: InfluxDB sunucusu ile ilgili genel hatalar

                self.pop_message(e)
                return

        if self.rad4.isChecked():
            self.root = self.file_path



            sheetname = "AylikKumuleRapor"
            now = datetime.now().strftime(("%d%m%Y"))

            filename = self.root + "RobotCalismaRaporu_Aylik_Toplu_" + str(now) + ".xlsx"
            try:
                client = InfluxDBClient(
                    bucket=self.bucket,
                    org=self.org,
                    url=self.url,
                    token=self.token,
                    ssl_ca_cert=certifi.where()
                )

                client.api_client.configuration.verify_ssl = False

                query_api = client.query_api()
                query = f"""from(bucket: "{self.bucket}")
                                      |> range(start: {self.value1.strftime('%Y-%m-%dT%H:%M:%SZ')}, stop: {self.value2.strftime('%Y-%m-%dT%H:%M:%SZ')})
                                      |> filter(fn: (r) => r["_field"] == "jobtime")
                                      |> filter(fn: (r) => r["_measurement"] == "seeme_VSTL") 
                                      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")"""  # Query bu kisima yazilir. # Query bu kisima yazilir.

                data_frame = query_api.query_data_frame(
                    query)  # Pandas Dataframe formatinda donmesi icin bu kod kullanilir. Bundan sonraki aciklamalarda tablo yerine Dataframe terimi kullanilacaktir.
                if not data_frame.empty:
                    data_frame['_time'] = pd.to_datetime(data_frame['_time']).dt.strftime(
                        "%d.%m.%Y")  # Dataframe'in _time kolonundaki tarih formatini ayarlar.

                    columns = ['result', 'table', '_start', '_stop', '_measurement', 'location', 'mate', 'type',
                               'businessunit',
                               'process']  # Dataframe'de istenmeyen kolonlardan liste olusturulur.
                    data_frame.drop(columns, inplace=True, axis=1)  # İstenmeyen kolonlar atilir.

                    data_frame['_time'] = pd.to_datetime(data_frame['_time'],
                                                         dayfirst=True)  # _time kolonu Pandas formatina gore datetime'a cevrilir.

                    grouped_data = data_frame.groupby(
                        pd.Grouper(key='_time', freq='ME'))  # _time kolonunda aylara gore gruplama yapilir.
                    aggregated_data = grouped_data[
                        'jobtime'].sum().reset_index()  # gruplamadan sonra jobtime'ların toplami alinir.

                    aggregated_data['_time'] = pd.to_datetime(aggregated_data['_time']).dt.strftime(
                        "%B")  # Gruplamadan sonra ay ismi yazdirilir.
                    aggregated_data['jobtime'] = (
                        round(aggregated_data['jobtime'] / 3600,
                              2))  # Saniye cinsinden gelen jobuptime verisi saate cevrilir.

                    timevalue = aggregated_data['jobtime'].values
                    timeMonth = aggregated_data['_time'].values

                    aggregated_data = aggregated_data.rename(columns={'_time': 'AY/ROBOT (Saat)'})
                    aggregated_data = aggregated_data.rename(
                        columns={'jobtime': 'Çalışma Süresi'})  # Kolon ismi ayarlamalari yapilir.

                    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
                    aggregated_data.to_excel(writer, sheet_name=sheetname, index=False)
                    workbook = writer.book
                    worksheet = writer.sheets[sheetname]

                    light_gray_format = workbook.add_format(
                        {'bg_color': '#F4F4F4', 'border_color': '#646464', 'valign': 'vcenter', 'border': 1})
                    white_format = workbook.add_format(
                        {'bg_color': '#FFFFFF', 'border_color': '#646464', 'valign': 'vcenter', 'border': 1})

                    row_count = len(aggregated_data) + 1
                    column_count = len(aggregated_data.columns) - 1

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

                    writer.close()
                else:
                    self.pop_message("Sonuç Yok!")
                    self.clearList()
                    return

            except InfluxDBClientError as e:
                self.pop_message(e)
                return

            except ConnectionError as e:
                self.pop_message(e)
                return

            except Exception as e:
                self.pop_message(e)
                return

            except InfluxDBServerError as e:

                # InfluxDBServerError: InfluxDB sunucusu ile ilgili genel hatalar

                self.pop_message(e)
                return





    def clearList(self):
        # clear buttonu methodu
        self.resultList.clear()
        for i in reversed(range(self.rightLayout2.count())):
            self.rightLayout2.itemAt(i).widget().setParent(None)

    def update(self):

        # tarih seçme için Takvimdeki DateButton için hazırlanan fonksiyon
        self.value1 = self.datetime_edit.dateTime().toPyDateTime()
        self.value2 = self.datetime_edit2.dateTime().toPyDateTime()
        self.query = f'''from(bucket: "{self.bucket}")'''
        self.query += f"|> range(start: {self.value1.strftime('%Y-%m-%dT%H:%M:%SZ')}, stop: {self.value2.strftime('%Y-%m-%dT%H:%M:%SZ')})"




    def createQuery(self):

        if self.rad1.isChecked():
            now = datetime.now().strftime(("%d%m%Y"))
            try:
                client = InfluxDBClient(
                    bucket=self.bucket,
                    org=self.org,
                    url=self.url,
                    token=self.token,
                    ssl_ca_cert=certifi.where()
                )

                client.api_client.configuration.verify_ssl = False

                query_api = client.query_api()
                query = f"""from(bucket: "{self.bucket}")
                            |> range(start: {self.value1.strftime('%Y-%m-%dT%H:%M:%SZ')}, stop: {self.value2.strftime('%Y-%m-%dT%H:%M:%SZ')})
                            |> filter(fn: (r) => r["_field"] == "jobtime")
                            |> filter(fn: (r) => r["_measurement"] == "seeme_VSTL") 
                            |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")"""  # Query bu kisima yazilir.

                data_frame = query_api.query_data_frame(query)
                if not data_frame.empty:
                    data_frame['jobtime'] = (round(data_frame['jobtime'] / 60, 2))

                    jobtimeSecond = data_frame['jobtime'].sum()
                    data_frame.loc['Toplam (Saat)', 'jobtime'] = round(jobtimeSecond / 60, 2)

                    columns = ['result', 'table', '_start', '_stop', '_time', '_measurement', 'location', 'mate',
                               'type']
                    data_frame.drop(columns, inplace=True, axis=1)

                    data_frame = data_frame.rename(columns={'businessunit': 'Departman'})
                    data_frame = data_frame.rename(columns={'process': 'Süreç İsmi'})
                    data_frame = data_frame.rename(columns={'robot': 'Çalıştığı Robot'})
                    data_frame = data_frame.rename(
                        columns={'jobtime': 'Çalışma Süresi (Dakika)'})  # Kolon ismi ayarlamalari yapilir.
                    for i in reversed(range(self.rightLayout2.count())):
                        self.rightLayout2.itemAt(i).widget().setParent(None)

                    headers = list(data_frame.columns)
                    print(headers)
                    data = data_frame.values.tolist()

                    self.resultList.setRowCount(len(data))
                    self.resultList.setColumnCount(len(headers))
                    self.resultList.setHorizontalHeaderLabels(headers)

                    for row_num, row_data in enumerate(data):
                        for col_num, cell_data in enumerate(row_data):
                            self.resultList.setItem(row_num, col_num, QTableWidgetItem(str(cell_data)))

                    self.resultList.setItem(len(data) - 1, 0, QTableWidgetItem(str("TOPLAM(SAAT)")))
                    self.resultList.setItem(len(data) - 1, 1, QTableWidgetItem(str("")))
                    self.resultList.setItem(len(data) - 1, 2, QTableWidgetItem(str("")))
                else:
                    self.clearList()
                    self.pop_message("Sonuç yok!!")
                    return


            except InfluxDBClientError as e:

                # InfluxDBClientError: InfluxDBClient ile ilgili genel hatalar

                self.pop_message(e)
                return


            except InfluxDBServerError as e:

                # InfluxDBServerError: InfluxDB sunucusu ile ilgili genel hatalar

                self.pop_message(e)
                return

            except requests.exceptions.ConnectionError as e:

                # ConnectionError: Bağlantı hatası (sunucuya ulaşılamama gibi)

                self.pop_message(e)
                return

            except Exception as e:

                # Diğer tüm hataları yakala

                self.pop_message(e)
                return
        if self.rad2.isChecked():
            # locale.setlocale(locale.LC_ALL, 'turkish')


            now = datetime.now().strftime(("%d%m%Y"))
            try:
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

                query = f"""from(bucket: "{self.bucket}")
                             |> range(start: {self.value1.strftime('%Y-%m-%dT%H:%M:%SZ')}, stop: {self.value2.strftime('%Y-%m-%dT%H:%M:%SZ')})
                             |> filter(fn: (r) => r._field == "jobtime")
                             |> filter(fn: (r) => r["_measurement"] == "seeme_VSTL") 
                             |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")"""

                data_frame = query_api.query_data_frame(query)
                if not data_frame.empty:
                    data_frame['_time'] = pd.to_datetime(data_frame['_time']).dt.strftime("%d.%m.%Y")
                    robots = set(data_frame['robot'])

                    columns = ['result', 'table', '_start', '_stop', '_measurement', 'location', 'mate', 'type',
                               'businessunit',
                               'process']
                    data_frame.drop(columns, inplace=True, axis=1)

                    data_frame['_time'] = pd.to_datetime(data_frame['_time'], dayfirst=True)

                    data_frame = data_frame.pivot_table("jobtime", index="_time", columns="robot",
                                                        aggfunc='sum').reset_index()

                    grouped_data = data_frame.groupby(pd.Grouper(key='_time', freq='ME'))
                    data_frame = grouped_data.sum().reset_index()

                    data_frame['_time'] = pd.to_datetime(data_frame['_time']).dt.strftime("%B")
                    # data_frame = data_frame/3600

                    data_frame = data_frame.rename(columns={'_time': 'AY/ROBOT (Saat)'})

                    for excelcolumn in data_frame.columns:
                        data_frame[excelcolumn] = data_frame[excelcolumn].apply(
                            lambda x: round(x / 3600, 2) if pd.notnull(x) and isinstance(x, (int, float)) else x)

                    print("timeMonth")
                    timeMonth = data_frame['AY/ROBOT (Saat)'].values

                    chart2 = QChart()
                    serie2 = QBarSeries()

                    for robot_name in robots:
                        print(robot_name)
                        set1 = QBarSet(f"{robot_name}")
                        print(robot_name)
                        robot = data_frame[f'{robot_name}'].values
                        print(robot_name)
                        for i in robot:
                            print(robot_name)
                            set1.append(i)
                        print(robot_name)
                        serie2.append(set1)

                    chart2.addSeries(serie2)

                    chart2.setTitle("Robot Doluluk Analizi")
                    font = QFont("Arial", 18)
                    font.setWeight(QFont.Bold)
                    chart2.setTitleFont(font)

                    axis = QBarCategoryAxis()

                    for i in timeMonth:
                        axis.append(i)

                    chart2.createDefaultAxes()
                    chart2.setAxisX(axis, serie2)

                    chart_view = QChartView(chart2)
                    chart_view.setVisible(True)

                    for i in reversed(range(self.rightLayout2.count())):
                        self.rightLayout2.itemAt(i).widget().setParent(None)

                    self.rightLayout2.addRow(chart_view)

                    headers = list(data_frame.columns)
                    print(headers)
                    data = data_frame.values.tolist()

                    self.resultList.setRowCount(len(data))
                    self.resultList.setColumnCount(len(headers))
                    self.resultList.setHorizontalHeaderLabels(headers)

                    for row_num, row_data in enumerate(data):
                        for col_num, cell_data in enumerate(row_data):
                            self.resultList.setItem(row_num, col_num, QTableWidgetItem(str(cell_data)))
                else:
                    self.clearList()
                    self.pop_message("Sonuç yok!!")
                    return
            except InfluxDBClientError as e:

                # InfluxDBClientError: InfluxDBClient ile ilgili genel hatalar

                self.pop_message(e)
                return


            except InfluxDBServerError as e:

                # InfluxDBServerError: InfluxDB sunucusu ile ilgili genel hatalar

                self.pop_message(e)
                return

            except requests.exceptions.ConnectionError as e:

                # ConnectionError: Bağlantı hatası (sunucuya ulaşılamama gibi)

                self.pop_message(e)
                return

            except Exception as e:

                # Diğer tüm hataları yakala

                self.pop_message(e)
                return

        if self.rad3.isChecked():

            now = datetime.now().strftime(("%d%m%Y"))
            try:
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

                query = f"""from(bucket: "{self.bucket}")
                                        |> range(start: {self.value1.strftime('%Y-%m-%dT%H:%M:%SZ')}, stop: {self.value2.strftime('%Y-%m-%dT%H:%M:%SZ')})
                                        |> filter(fn: (r) => r._field == "jobtime")
                                        |> filter(fn: (r) => r._measurement == "seeme_VSTL") 
                                        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")"""

                data_frame = query_api.query_data_frame(query)
                if not data_frame.empty:
                    data_frame['_time'] = pd.to_datetime(data_frame['_time']).dt.strftime("%d.%m.%Y")

                    departmanlar = set(data_frame['businessunit'])

                    columns = ['result', 'table', '_start', '_stop', '_measurement', 'location', 'mate', 'robot',
                               'type',
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

                    chart3 = QChart()
                    serie3 = QBarSeries()
                    timeMonth = data_frame['AY/DEPARTMAN (Saat)'].values

                    for dep in departmanlar:
                        print(dep)
                        set1 = QBarSet(f"{dep}")
                        print(dep)
                        robot = data_frame[f'{dep}'].values
                        print(dep)
                        for i in robot:
                            print(dep)
                            set1.append(i)
                        print(dep)
                        serie3.append(set1)

                    chart3.addSeries(serie3)

                    chart3.setTitle("Departmanlara Göre Robot Çalışma Analizi")
                    font = QFont("Arial", 18)
                    font.setWeight(QFont.Bold)
                    chart3.setTitleFont(font)

                    axis = QBarCategoryAxis()

                    for i in timeMonth:
                        axis.append(i)

                    chart3.createDefaultAxes()
                    chart3.setAxisX(axis, serie3)

                    chart_view = QChartView(chart3)
                    chart_view.setVisible(True)
                    for i in reversed(range(self.rightLayout2.count())):
                        self.rightLayout2.itemAt(i).widget().setParent(None)
                    self.rightLayout2.addRow(chart_view)

                    headers = list(data_frame.columns)
                    print(headers)
                    data = data_frame.values.tolist()

                    self.resultList.setRowCount(len(data))
                    self.resultList.setColumnCount(len(headers))
                    self.resultList.setHorizontalHeaderLabels(headers)

                    for row_num, row_data in enumerate(data):
                        for col_num, cell_data in enumerate(row_data):
                            self.resultList.setItem(row_num, col_num, QTableWidgetItem(str(cell_data)))
                else:
                    self.clearList()
                    self.pop_message("Sonuç yok!!")
                    return
            except InfluxDBClientError as e:

                # InfluxDBClientError: InfluxDBClient ile ilgili genel hatalar

                self.pop_message(e)
                return


            except InfluxDBServerError as e:

                # InfluxDBServerError: InfluxDB sunucusu ile ilgili genel hatalar

                self.pop_message(e)
                return

            except requests.exceptions.ConnectionError as e:

                # ConnectionError: Bağlantı hatası (sunucuya ulaşılamama gibi)

                self.pop_message(e)
                return

            except Exception as e:

                # Diğer tüm hataları yakala

                self.pop_message(e)
                return

        if self.rad4.isChecked():


            sheetname = "AylikKumuleRapor"
            now = datetime.now().strftime(("%d%m%Y"))
            try:
                client = InfluxDBClient(
                    bucket=self.bucket,
                    org=self.org,
                    url=self.url,
                    token=self.token,
                    ssl_ca_cert=certifi.where()
                )

                client.api_client.configuration.verify_ssl = False

                query_api = client.query_api()

                query = f"""from(bucket: "{self.bucket}")
                                       |> range(start: {self.value1.strftime('%Y-%m-%dT%H:%M:%SZ')}, stop: {self.value2.strftime('%Y-%m-%dT%H:%M:%SZ')})
                                       |> filter(fn: (r) => r["_field"] == "jobtime")
                                       |> filter(fn: (r) => r["_measurement"] == "seeme_VSTL") 
                                       |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")"""  # Query bu kisima yazilir. # Query bu kisima yazilir.

                data_frame = query_api.query_data_frame(
                    query)  # Pandas Dataframe formatinda donmesi icin bu kod kullanilir. Bundan sonraki aciklamalarda tablo yerine Dataframe terimi kullanilacaktir.
                if not data_frame.empty:
                    data_frame['_time'] = pd.to_datetime(data_frame['_time']).dt.strftime(
                        "%d.%m.%Y")  # Dataframe'in _time kolonundaki tarih formatini ayarlar.

                    columns = ['result', 'table', '_start', '_stop', '_measurement', 'location', 'mate', 'type',
                               'businessunit',
                               'process']  # Dataframe'de istenmeyen kolonlardan liste olusturulur.
                    data_frame.drop(columns, inplace=True, axis=1)  # İstenmeyen kolonlar atilir.

                    data_frame['_time'] = pd.to_datetime(data_frame['_time'],
                                                         dayfirst=True)  # _time kolonu Pandas formatina gore datetime'a cevrilir.

                    grouped_data = data_frame.groupby(
                        pd.Grouper(key='_time', freq='ME'))  # _time kolonunda aylara gore gruplama yapilir.
                    aggregated_data = grouped_data[
                        'jobtime'].sum().reset_index()  # gruplamadan sonra jobtime'ların toplami alinir.

                    aggregated_data['_time'] = pd.to_datetime(aggregated_data['_time']).dt.strftime(
                        "%B")  # Gruplamadan sonra ay ismi yazdirilir.
                    aggregated_data['jobtime'] = (
                        round(aggregated_data['jobtime'] / 3600,
                              2))  # Saniye cinsinden gelen jobuptime verisi saate cevrilir.
                    print("o")

                    timevalue = aggregated_data['jobtime'].values
                    timeMonth = aggregated_data['_time'].values
                    print(timeMonth)

                    chart4 = QChart()
                    series4 = QBarSeries()

                    set0 = QBarSet('Çalışma Süresi')

                    for i in timevalue:
                        set0.append(i)

                    series4.append(set0)

                    chart4.addSeries(series4)
                    chart4.setTitle("Aylara Göre Robot Doluluk Analizi")
                    font = QFont("Arial", 18)
                    font.setWeight(QFont.Bold)
                    chart4.setTitleFont(font)

                    axis = QBarCategoryAxis()
                    for i in timeMonth:
                        axis.append(i)

                    chart4.createDefaultAxes()
                    chart4.setAxisX(axis, series4)

                    chart_view = QChartView(chart4)
                    chart_view.setVisible(True)
                    for i in reversed(range(self.rightLayout2.count())):
                        self.rightLayout2.itemAt(i).widget().setParent(None)
                    self.rightLayout2.addRow(chart_view)

                    headers = list(aggregated_data.columns)
                    print(headers)
                    data = aggregated_data.values.tolist()

                    self.resultList.setRowCount(len(data))
                    self.resultList.setColumnCount(len(headers))
                    self.resultList.setHorizontalHeaderLabels(headers)

                    for row_num, row_data in enumerate(data):
                        for col_num, cell_data in enumerate(row_data):
                            self.resultList.setItem(row_num, col_num, QTableWidgetItem(str(cell_data)))
                else:
                    self.clearList()
                    self.pop_message("Sonuç yok!!")

                    return
            except InfluxDBClientError as e:

                # InfluxDBClientError: InfluxDBClient ile ilgili genel hatalar

                self.pop_message("InfluxDBClient hatası:", e)
                return


            except InfluxDBServerError as e:

                # InfluxDBServerError: InfluxDB sunucusu ile ilgili genel hatalar

                self.pop_message(e)
                return

            except requests.exceptions.ConnectionError as e:

                # ConnectionError: Bağlantı hatası (sunucuya ulaşılamama gibi)

                self.pop_message(e)
                return

            except Exception as e:

                # Diğer tüm hataları yakala

                self.pop_message(e)
                return

    def pop_message(self, text):
        msg = QtWidgets.QMessageBox()
        msg.setText("{}".format(text))
        msg.setWindowTitle(" ")
        msg.setWindowIcon(QIcon('x.ico'))
        msg.exec_()
    def layouts(self):
        self.mainLayout = QHBoxLayout()
        self.rightMainLayout = QVBoxLayout()
        self.leftLayout = QFormLayout()
        self.midLayout = QFormLayout()
        self.rightLayout = QFormLayout()
        self.rightLayout2 = QFormLayout()

        # leftLayout
        self.leftLayoutGroupBox = QGroupBox("Server")
        self.leftLayout.addRow(self.comboForDate)
        self.leftLayout.addRow(self.start_time_label)
        self.leftLayout.addRow(self.datetime_edit)
        self.leftLayout.addRow(self.stop_time_label)
        self.leftLayout.addRow(self.datetime_edit2)
        self.leftLayout.addRow(self.button)
        self.leftLayout.addRow(self.rad1)
        self.leftLayout.addRow(self.rad2)
        self.leftLayout.addRow(self.rad3)
        self.leftLayout.addRow(self.rad4)
        self.leftLayout.addRow(self.button1)

        self.leftLayoutGroupBox.setLayout(self.leftLayout)
        # rightlayouttop
        self.rightTopLayoutGroupBox = QGroupBox("Chart")

        self.rightTopLayoutGroupBox.setLayout(self.rightLayout2)

        # rightlayoutbottom
        self.rightLayoutGroupBox = QGroupBox("Result")
        self.rightLayout.addRow(self.resultList)
        self.rightLayout.addRow(self.clearButton)
        self.rightLayout.addRow(self.export_button)
        self.rightLayoutGroupBox.setLayout(self.rightLayout)

        # tab1mainlayout
        self.rightMainLayout.addWidget(self.rightTopLayoutGroupBox, 50)
        self.rightMainLayout.addWidget(self.rightLayoutGroupBox, 50)
        self.mainLayout.addWidget(self.leftLayoutGroupBox, 30)
        # self.mainLayout.addWidget(self.midLayoutGroupBox, 30)
        # self.mainLayout.addWidget(self.rightLayoutGroupBox, 40)
        self.mainLayout.addLayout(self.rightMainLayout, 70)
        self.tab1.setLayout(self.mainLayout)

    def newDateFunc(self, newDate):

        if (newDate == "Tarih Belirle"):

            self.start_time_label.setVisible(True)
            self.stop_time_label.setVisible(True)
            self.datetime_edit.setVisible(True)
            self.datetime_edit2.setVisible(True)
            self.button.setVisible(True)

        elif (newDate == "Dün"):
            self.value1 = self.yesterday
            self.value2 = self.today
            self.query = f'''from(bucket: "{self.bucket}")'''
            self.query += f"|> range(start: {self.value1.strftime('%Y-%m-%dT%H:%M:%SZ')}, stop: {self.value2.strftime('%Y-%m-%dT%H:%M:%SZ')})"
            print(self.query)

            self.start_time_label.setVisible(False)
            self.stop_time_label.setVisible(False)
            self.datetime_edit.setVisible(False)
            self.datetime_edit2.setVisible(False)
            self.button.setVisible(False)

        elif (newDate == "3 Gün Önce"):
            self.value1 = self.lastThreeDays
            self.value2 = self.today
            self.query = f'''from(bucket: "{self.bucket}")'''
            self.query += f"|> range(start: {self.value1.strftime('%Y-%m-%dT%H:%M:%SZ')}, stop: {self.value2.strftime('%Y-%m-%dT%H:%M:%SZ')})"
            print(self.query)

            self.start_time_label.setVisible(False)
            self.stop_time_label.setVisible(False)
            self.datetime_edit.setVisible(False)
            self.datetime_edit2.setVisible(False)
            self.button.setVisible(False)

        elif (newDate == "1 Hafta Önce"):
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
        elif (newDate == "15 Gün Önce"):
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
        elif (newDate == "1 Ay Önce"):
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
        elif (newDate == "3 Ay Önce"):
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
        elif (newDate == "6 Ay Önce"):
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WindowForUserProcess()
    window.show()
    sys.exit(app.exec_())

