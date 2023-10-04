#! python3
import os
from datetime import datetime
from tkinter import messagebox
from urllib.parse import urlparse

import pymysql
import win32com.client
import xlrd
from bs4 import BeautifulSoup
from dateutil.parser import parse
from selenium import webdriver

discardList = ['about us', 'home', 'rss', 'facebook', 'twitter', 'linkedin', 'github', 'email', 'help', 'about fda', 'next page']


def scrapData():
    inputLinks = []
    ResList = []
    dbLinks = []
    master_urls = []
    db = pymysql.connect("localhost", 'root', "root123", "scraper")
    cursor = db.cursor()
    masterData = "select * from scrapdata_urlmaster"
    cursor.execute(masterData)
    AllData = cursor.fetchall()

    for rec in AllData:
        input_urls = {'URL_Id': rec[0], "URL": rec[2]}
        master_urls.append(input_urls)
    # input_urls = {'URL_Id': 'URL_01', "URL":  'https://www.gov.uk/search/guidance-and-regulation?organisations%5B%5D=health-research-authority&organisations%5B%5D=healthcare-uk&organisations%5B%5D=medicines-and-healthcare-products-regulatory-agency&order=updated-newest'}
    # master_urls.append(input_urls)
    query = "select * from scrapdata_scrapdata"
    cursor.execute(query)
    records = cursor.fetchall()
    for record in records:
        db_dict = {'URL': record[3], 'Content': record[4]}
        dbLinks.append(db_dict)

    for urlItm in master_urls:  # inputLinks:
        dbfound = False
        found = False
        data = []
        url = urlItm['URL'].strip()
        # print(os.path.abspath(os.path.join(url, os.pardir)))
        parsed_uri = urlparse(url)
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        domain = domain[:-1]
        driver = webdriver.Chrome("chromedriver.exe")
        driver.get(url)
        content = driver.page_source
        soup = BeautifulSoup(content, features="html.parser")
        all_links = soup.findAll('a')
        linkText = ""
        tagContent = ""
        for link in all_links:
            dbfound = False
            found = False
            dataDict = {
                "URL_id": "",
                "Link": "",
                "Content": "",
                "Date": "",
            }
            if 'href' in link.attrs:
                linkText = link.attrs['href']
                if linkText != "":
                    if linkText[0] != '#':
                        if linkText[0] != 'h':
                            if linkText[0] != '/':
                                linkText = "/" + linkText.replace("\\", "/")
                    tagContent = link.text.replace("'", "").strip()
            if 'https://extranet.who.int/prequal' in linkText:
                print("Hi")
            if linkText != "":
                if linkText[0] != '#' and '@' not in linkText and linkText != '/':
                    if len(data) > 0:
                        for itm in data:
                            if bool(urlparse(linkText).netloc):
                                if linkText == itm['Link']:  # and tagContent.upper() == itm["Content"].upper:
                                    found = True
                                # if found:
                                #     if tagContent.strip() != "" and itm['Content'].strip() == "":
                                #         itm['Link'] = linkText
                                #         itm['Content'] = tagContent
                                #         itm['Date'] = str(parse(str(datetime.now()), fuzzy=False).strftime("%d/%m/%Y"))
                                #         break
                            else:
                                if (domain + linkText) == itm['Link']:
                                    found = True
                                # if found:
                                #     if tagContent.strip() != "" and itm['Content'].strip() == "":
                                #         itm['Link'] = domain + linkText
                                #         itm['Content'] = tagContent
                                #         itm['Date'] = str(parse(str(datetime.now()), fuzzy=False).strftime("%d/%m/%Y"))
                                #         break
                    if len(dbLinks) > 0:
                        for itm in dbLinks:
                            if bool(urlparse(linkText).netloc):
                                if linkText == itm['URL'] and tagContent.upper() == itm['Content'].upper():
                                    dbfound = True
                                    break
                            else:
                                if (domain + linkText) == itm['URL'] and tagContent.upper() == itm['Content'].upper():
                                    dbfound = True
                                    break

                    if not found and not dbfound:
                        if not bool(urlparse(linkText).netloc):
                            if linkText[0] != '#' and '@' not in linkText and "javascript:" not in linkText:
                                linkText = domain + linkText
                        if "javascript:" not in linkText and tagContent.strip().lower() not in discardList:
                            dataDict['URL_id'] = urlItm["URL_Id"]
                            dataDict['Link'] = linkText
                            dataDict['Content'] = tagContent.strip()
                            dataDict['Date'] = str(parse(str(datetime.now()), fuzzy=False).strftime("%d/%m/%Y"))
                            data.append(dataDict)
        if len(data) > 0:
            ResList.append(data)
        driver.close()
    if len(ResList) > 0:
        StoreToDB(ResList)
        ExportToExcel(ResList)
        # messagebox.showinfo("Saved", "Data Saved Successfully")
    else:
        messagebox.showinfo("", "No Links found")


def StoreToDB(ResList):
    db = pymysql.connect("localhost", 'root', "root123", "scraper")
    cursor = db.cursor()
    query = ''
    for itms in ResList:
        for itm in itms:
            cursor.execute("SELECT * FROM `scrapdata_scrapdata`")
            cursor.fetchall()
            rc = str(cursor.rowcount + 1 + 389)
            contentVal = itm['Content'].replace("'", "")

            query = "INSERT INTO scrapdata_scrapdata VALUES (" + "'" + rc + "'" + "," + "'" + itm['URL_id'] + "'" + "," + "'" + itm['Date'] + "'" + "," + "'" + itm['Link'] + "'" + "," + "'" + contentVal + "'" + ")"
            # query = "INSERT INTO test_scraper VALUES (" + "'" + rc + "'" + "," + "'" + itm['URL_id'] + "'" + "," + "'" + \
            #         itm['Date'] + "'" + "," + "'" + itm['Link'] + "'" + "," + "'" + contentVal + "'" + ")"
            cursor.execute(query)
    db.commit()


def ExportToExcel(ResList):
    path = os.getcwd().replace('\'', '\\') + '\\'
    URLbook = xlrd.open_workbook(path + 'results.xlsx')
    max_nb_row = 0
    for sheet in URLbook.sheets():
        max_nb_row = max(max_nb_row, sheet.nrows)
    xl = win32com.client.Dispatch("Excel.Application")
    # xl.Interactive = False
    NewBook = xl.Workbooks.Open(path + 'results.xlsx')
    ws = NewBook.ActiveSheet
    ws.Cells(max_nb_row + 3, 2).ColumnWidth = 26
    ws.Cells(max_nb_row + 3, 3).ColumnWidth = 42
    ws.Cells(max_nb_row + 3, 4).ColumnWidth = 76
    if max_nb_row == 1:
        k = 2  # max_nb_row + 4
    else:
        k = max_nb_row + 4
    for itms in ResList:
        if k != 2:
            k = k + 2
        for itm in itms:
            ws.Cells(k, 2).Value = itm['Date']
            # ws.Cells(k, 2).Alignment = Alignment(horizontal='center')
            ws.Cells(k, 3).Value = itm['Link']
            ws.Cells(k, 4).Value = itm['Content']
            # ws.Cells(k, 3).WrapText = True
            # ws.Cells(k, 4).WrapText = True
            k = k + 1
    NewBook.Save()
    messagebox.showinfo("Saved", "Data Saved Successfully")
    xl.Visible = True
