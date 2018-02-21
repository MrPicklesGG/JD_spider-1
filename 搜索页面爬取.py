# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 17:58:15 2018

@author: YIFAN
"""

import requests
from lxml import etree 
import urllib
import pandas as pd
import numpy as np
import time
import xlrd
import xlutils.copy
import os
def links_crawl(html):
    p_links=html.xpath('//div[@class="gl-i-wrap"]/div[@class="p-img"]/a/@href')
    return p_links
    
def imgs_crawl(html):
    p_imgs=html.xpath('//div[@class="gl-i-wrap"]/div[@class="p-img"]/a/img[1]/@src')
    return p_imgs

def prices_crawl(html):
    p_prices=html.xpath('//div[@class="gl-i-wrap"]/div[@class="p-price"]/strong')
    tmp_prices=[]
    i=0
    for ind,x in enumerate(p_prices):
        if x.xpath("./i/text()")!=[]:
            tmp_prices.append(x.xpath("./i/text()")[0])
        else:
            if i==0:
                print("存在反爬虫攻击！")
                i+=1
            print(ind)
            tmp_prices.append(x.xpath("./@data-price")[0])
    p_prices=tmp_prices
    return p_prices
    
def descs_crawl(html):
    p_descs=[' '.join(x.xpath("./text()")).strip().replace("@","") for x in html.xpath('//div[@class="gl-i-wrap"]/div[@class="p-name p-name-type-2"]//em')]
    return p_descs
    
def scores_crawl(html):
    p_scores=html.xpath('//div[@class="gl-i-wrap"]/div[@class="p-commit"]')
    tmp_scores=[]
    for ind,x in enumerate(p_scores):
            if x.xpath(".//em/text()")!=[]:
                tmp_scores.append(x.xpath(".//em/text()")[0])
            else:
                tmp_scores.append("0")
    p_scores=tmp_scores
    return  p_scores

def shops_crawl(html):
    p_shops=html.xpath('//div[@class="gl-i-wrap"]/div[@class="p-shop"]')
    tmp_shops=[]
    for ind,x in enumerate(p_shops):
        if x.xpath(".//a//@title")!=[]:
            tmp_shops.append(x.xpath(".//a//@title")[0])
        else:
            tmp_shops.append("")
    p_shops=tmp_shops
    return p_shops
    
def shops_links_crawl(html):
    p_shops_links=html.xpath('//div[@class="gl-i-wrap"]/div[@class="p-shop"]')
    tmp_shops_links=[]
    for ind,x in enumerate(p_shops_links):
        if x.xpath(".//a//@href")!=[]:
            tmp_shops_links.append(x.xpath(".//a//@href")[0])
        else:
            tmp_shops_links.append("")
    p_shops_links=tmp_shops_links
    return p_shops_links
    
def spyder(query,p_n):
    url = 'https://search.jd.com/Search'
    url2 = 'https://search.jd.com/s_new.php'
    kw = {'keyword':query,
          "qrst":"1",
          "rt":"1",
          "stop":"1",
          "vt":"2",
          'enc':'utf-8',
          "stock":"1",
          "psort":"3",
          "page":str(p_n*2-1)}
    kw2={"keyword":query,
         "qrst":"1",
         "rt":"1",
         "stop":"1",
         "vt":"2",
         'enc':'utf-8',
         "stock":"1",
         "psort":"3",
         "page":str(p_n*2),
         "scrolling":"y"
         }
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"}
    get_query=urllib.parse.urlencode(kw)
    headers2 = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36",
               "Host": "search.jd.com",
               "Referer":"https://search.jd.com/Search?"+get_query
               }
    print("页面爬取开始")   
    
    try:
        r = requests.get(url, params = kw, headers=headers)
        r.encoding=r.apparent_encoding
        r2 = requests.get(url2, params = kw2,headers=headers2)
        r2.encoding=r2.apparent_encoding
        print("页面解析开始")
        html = etree.HTML(r.text+r2.text)
        p_links=links_crawl(html)
        print("产品链接获取成功")
        p_imgs=imgs_crawl(html)
        print("产品图片获取成功")
        p_prices=prices_crawl(html)
        print("产品价格获取成功")
        p_descs=descs_crawl(html)
        print("产品描述获取成功")
        p_scores=scores_crawl(html)
        print("产品得分获取成功")
        p_shops=shops_crawl(html)
        print("产品商店获取成功")
        p_shops_links=shops_links_crawl(html)
        print("产品商店链接获取成功")
        print("连接状态")
        print(r.raise_for_status())
        print("编码类型")
        print(r.encoding)
    except:
        print("对不起爬取失败")
    results=(p_links,p_prices,p_descs,p_scores,p_shops,p_shops_links)
    return results

def std_r(results):
    std_results=[(a,b,c,d,e,f) for a,b,c,d,e,f in zip(*results)]
    std_results=list(set(std_results))
    std_results=sorted(std_results,key=lambda item:item[3],reverse=True)
    return std_results
    
def excel_handler(q,y):
     df = pd.DataFrame(np.transpose(np.array(y)),columns=['商品链接','商品价格','商品描述','商品评分','商品店铺','商品店铺链接'])
     df.to_excel('p_data\\'+q+'.xls', sheet_name='Sheet1',index=False)
     workbook = xlrd.open_workbook('p_data\\'+q+'.xls')
     workbook = xlutils.copy.copy(workbook)
     sheet = workbook.get_sheet(0)
     first_col=sheet.col(0)
     first_col.width=256*30
     third_col=sheet.col(2)
     third_col.width=256*100
     fifth_col=sheet.col(4)
     fifth_col.width=256*30
     workbook.save('p_data\\'+q+'.xls')
def main():
    query=input("请输入搜索关键词:")
    page_num=input("请输入爬取页面,格式如下:1-5:")
    std_opt=input("是否启动标准化功能,如果是请按T:")
    p_s,p_f=page_num.split("-")
    p_links,p_prices,p_descs,p_scores,p_shops,p_shops_links=[],[],[],[],[],[]
    pages=list(range(int(p_s),int(p_f)+1))
    for p_n in pages:
        print("正在爬取第"+str(p_n)+"页")
        t_p_links,t_p_prices,t_p_descs,t_p_scores,t_p_shops,t_p_shops_links=spyder(query,p_n)
        p_links=p_links+t_p_links
        p_prices=p_prices+t_p_prices
        p_descs=p_descs+t_p_descs
        p_scores=p_scores+t_p_scores
        p_shops=p_shops+t_p_shops
        p_shops_links=p_shops_links+t_p_shops_links
    results=(p_links,p_prices,p_descs,p_scores,p_shops,p_shops_links)
    if std_opt=="T":
        results=std_r(results)
    return query,results

if __name__ == "__main__":
     t0=time.time()
     if os.path.exists("p_data")!=True:
         os.mkdir("p_data")
     q,y=main()
     y=list(y)
     excel_handler(q,y)
     t1 = time.time()
     print ("Total time running: %s seconds" %
        (str(t1-t0))
        )
     
