import pymysql


def connecttDB():
    db = pymysql.connect("localhost", 'root', "root123", "scraper")
    cursor = db.cursor()
    return cursor
