# coding = utf-8
import requests
import jsonpath
import json
import pymysql
import time

# 连接Mysql数据库
conn = pymysql.connect(
    host = "localhost",
    port = 3306,
    user = "root",
    password = "123456",
    database = "spider",
    charset = "utf8"
)
cursor = conn.cursor()

# 爬虫程序
def spider(url):
     headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)Chrome/70.0.3538.110 Safari/537.36'}
     html = requests.get(url,headers=headers)
     print(url)
     time.sleep(1)
     return html

# SQL插入语句
def insert(sql,values):
    try:
        cursor.execute(sql,values)
        conn.commit()
    except:
        conn.rollback()

# 将时间戳转换为xxxx-xx-x xx:xx：xx格式
def stamptotime():
    ts = time.time()
    lt = time.localtime(ts) # 转换为本地时区时间
    now = time.strftime( "%Y-%m-%d %H:%M:%S",lt)
    return now

def main():
    num = 1
    while True:
        html = spider("https://www.douyu.com/gapi/rkc/directory/0_0/%s"%str(num))
        num += 1
        content = json.loads(html.content.decode('utf-8'))['data']['rl']
        for job in content:
            # 解析json文件
            name = jsonpath.jsonpath(job,"$..nn")[0] # 主播名
            hot = jsonpath.jsonpath(job,"$..ol")[0] # 在线人数
            cname = jsonpath.jsonpath(job,"$..c2name")[0] # 直播内容
            room_name = jsonpath.jsonpath(job,"$..od")[0] # 房间名
            url = "http://www.douyu.com" + jsonpath.jsonpath(job,"$..url")[0] # 直播地址
            uid = jsonpath.jsonpath(job,"$..uid")[0] # 主播id
            time = stamptotime()
            # 将字段写入mysql数据库
            sql = """INSERT INTO douyu(uid,name,cname,hot,time,room_name,url) VALUES(%s,%s,%s,%s,%s,%s,%s)"""
            values = (uid,name,cname,hot,time,room_name,url)
            insert(sql,values)

        if len(content) != 120:
            cursor.close()
            conn.close()
            break

if __name__ == '__main__':
    main()
