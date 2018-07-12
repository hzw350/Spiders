# coding=utf-8
import requests
import time
import random
import os
import urllib
import json
import jsonpath
from lxml import etree


class LagouSpider():
    def __init__(self, url, headers, proxies_pool, data, city, kd):
        """初始化参数"""
        self.url = url  # 登录界面url
        self.headers = headers  # 面向登录界面的请求头
        self.proxies_pool = proxies_pool  # 代理池
        self.data = data  # 请求参数，包含用户账户及密码 
        self.city = city  # 所找城市
        self.kd = kd  # 搜索职位

    def get_cookie(self):
        """获取拉勾网登录后的cookie值并返回"""
        # 构造requests.session对象
        ssion = requests.session()
        # 从代理池随机获取一个代理ip
        proxies = random.choice(self.proxies_pool)
        # 访问拉勾网登录界面，并留存cookie信息
        ssion.post(self.url,data=self.data,headers=self.headers,proxies=proxies)
        # 返回保有cookie的ssion对象
        return ssion

    def spider_url(self):
        """获取搜索结果界面每页15个结果中的每个的url地址"""
        # 调用方法，获取cookie值
        ssion = self.get_cookie()
        # 使用urllib库，将中文转换成url编码格式
        kw = urllib.urlencode({"city" : self.city})
        # 页码
        page = 1
        first = "true"
        while True:
            if page != 1:
                first = "false"
            formdata = {"first" : first,
                        "pn" : str(page),
                        "kd" : self.kd,
                    }
            print ("-----正在爬取%s市%s职位第%s页内容-----"%(self.city,self.kd,str(page)))
            response = ssion.post('https://www.lagou.com/jobs/positionAjax.json?'+'&'+kw+'&needAddtionalResult=false',data=formdata,headers=self.headers)
            # 将响应内容传给解析方法处理，并获得返回值count,每页15个内容，若count不满15则表示已经到尾页，程序结束
            count = self.url_handle(response,ssion)
            if count == 15:
                page += 1
                continue
            else:
                break
    
    def spider(self,url):
        """根据提取出的url地址，访问详情页"""
        # 构造详情页的请求头
        headers = {"Host" : "www.lagou.com",
                "Connection": "keep-alive",
                "Cache-Control" : "max-age=0",
                "Upgrade-Insecure-Requests" : "1",
                "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
                "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Encoding" : "gzip, deflate, br",
                "Accept-Language" : "zh-CN,zh;q=0.9"}
        # 换ip进进行访问，规避反爬
        ssion = self.get_cookie()
        result = ssion.get(url,headers=headers)
        # 使用lxml库将响应内容转换为XML格式，并用xpath进行解析
        html = etree.HTML(result.text)
        # 职位
        position = html.xpath('//div[@class="job-name"]/span[@class="name"]/text()')[0].encode('utf-8')
        # 公司
        company = html.xpath('//div[@class="job-name"]/div[@class="company"]/text()')[0].encode('utf-8')
        # 薪酬
        salary = html.xpath('//dd[@class="job_request"]/p/span[1]/text()')[0].encode('utf-8')
        # 经验
        experience = html.xpath('//dd[@class="job_request"]/p/span[3]/text()')[0].encode('utf-8') 
        # 学历
        education = html.xpath('//dd[@class="job_request"]/p/span[4]/text()')[0].encode('utf-8') 
        # 全职或兼职或其他
        state = html.xpath('//dd[@class="job_request"]/p/span[5]/text()')[0].encode('utf-8')
        # 应聘要求
        description_list = html.xpath('//dd[@class="job_bt"]/div[1]//p/text()')[0:]
        description = ''
        for i in range(len(description_list)):
            description = description + description_list[i].encode('utf-8')
        
        # 以字典形式存储
        data = {"position":position,
                "company":company,
                "salary":salary,
                "experience":experience,
                "education":education,
                "state":state,
                "description":description,
                }
        # 转换为json文件
        data = json.dumps(data,ensure_ascii=False)
        # 存储数据
        with open("./lagou.json","a") as f:
            f.write(data)
            f.write("\n")

    def url_handle(self,response,ssion):
        """对搜索页内容进行解析，提取详情页url"""
        html = response.text
        jsonbj = json.loads(html)
        # 用jsonpath提取获得的json文件
        result = jsonpath.jsonpath(jsonbj,"$.content.hrInfoMap")
        # 反向获取键，键为url的一个构成部分，返回对的num_list为列表形式
        for i in range(len(result)):
            num_list = result[i-1].keys()
       
        # 提取num_list中的值，拼接成url地址
        for num in num_list:
            print num
            url = "https://www.lagou.com/jobs/" + str(num) + ".html"
            self.spider(url)
            # 为规避拉钩反爬虫机制，休眠一个随机秒数
            seconds = random.randint(15,30)
            time.sleep(seconds)
        
        return len(num_list) 


def main():
    # 代理池，伪造ip地址进行访问
    proxies_pool = [{"http" : "http://61.135.217.7"},
                    {"http" : "http://18.190.95.43"},
                    {"http" : "http://121.31.101.115"},
                    {"http" : "http://118.190.95.43"},
                    {"http" : "http://27.40.156.136"},
                    {"http" : "http://122.114.31.177"},
                    {"http" : "http://125.64.17.100 808"}
                ]
    # 拉钩网站登录界面url
    url = 'https://passport.lagou.com/login/'
    # 请求头
    headers = {"Accept" : "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding" : "gzip, deflate, br",
            "Accept-Language" : "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Content-Length" : "25",
            "Content-Type" : "application/x-www-form-urlencoded; charset=UTF-8",
            
            "Host": "www.lagou.com",
            "Origin": "https://www.lagou.com",
            "Referer": "https://www.lagou.com/jobs/list_python?labelWords=sug&fromSearch=true&suginput=p",
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
            "X-Anit-Forge-Code": "0",
            "X-Anit-Forge-Token": "None",
            "X-Requested-With": "XMLHttpRequest"}
    
    # 请求参数
    data = {"isValidate" : "true",
            "username" : username, # 账号
            "password" : password, # 密码
            "request_form_verifyCode" : "",
            "submit" : ""
        }
    # 搜索要爬取字段
    kd = raw_input("请输入要爬取的内容：")
    # 所在城市
    city = raw_input("请输入要爬取的城市:")

    lagou = LagouSpider(url, headers, proxies_pool, data, city, kd)
    lagou.spider_url()


if __name__ == "__main__":
    main()
