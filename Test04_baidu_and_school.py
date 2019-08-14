
#去除了所有重复学者的名字爬取的数据
import requests
from bs4 import BeautifulSoup
import re
import json
import openpyxl
import csv
import random
import time

excel=openpyxl.load_workbook("distinct.xlsx")
sheet=excel["Sheet1"]
author_name_list=[]
for no,name in zip(sheet['A'],sheet['B']):
    author_info_dict={}
    author_info_dict['name']=name.value
    author_info_dict['no']=no.value
    author_name_list.append(author_info_dict)
print("author_name_list:"+str(author_name_list))

# author_name_list=['张元鸣',"高飞"]
url="http://xueshu.baidu.com/usercenter/data/authorchannel?cmd=inject_page"
headers={
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
}
user_agent_list = ['Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1464.0 Safari/537.36',
                       'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.16 Safari/537.36',
                       'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.3319.102 Safari/537.36',
                       'Mozilla/5.0 (X11; CrOS i686 3912.101.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36',
                       'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36',
                       'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36',
                       'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:17.0) Gecko/20100101 Firefox/17.0.6',
                       'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1468.0 Safari/537.36',
                       'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36',
                       'Mozilla/5.0 (X11; CrOS i686 3912.101.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36']

params={
    "cmd":"search_author",
    "_token":"",
    "_ts":"",
    "_sign":"",
    "author":"XXX",
    "affiliate":"XXXX",
    'curPageNum':1
}

page_params={
    "_token":"",
    "_ts":"",
    "_sign":"",
    "cmd":"academic_paper",
    "entity_id":"514188501fef395f3c5dd5f6006b27b7",
    "bsToken":"c0d0383a763c57e25972a903594c3175",
    "sc_sort":"sc_time",
    'curPageNum':2,
}
#获取请求参数
response=requests.get(url,headers=headers)
content=response.content.decode("utf-8")
soup = BeautifulSoup(content, "lxml")
param_text = soup.select('script[type="text/javascript"]')[1]
pattern=re.compile("\"(.*?)\"")
text=pattern.findall(str(param_text))
params["_ts"]=text[1]
params["_token"]=text[2]
params["_sign"]=text[3]
params['curPageNum'] = 1

page_params["_ts"]=text[1]
page_params["_token"]=text[2]
page_params["_sign"]=text[3]
page_params['curPageNum'] = 2

#搜索学者,获得详情页url
author_url_csv_fp=open("author_url_list.csv",'w')
author_url_csv_fp_writer=csv.writer(author_url_csv_fp)
author_url_csv_sheet_title=['no','name','url']
author_url_csv_fp_writer.writerow(author_url_csv_sheet_title)
author_url_list=[]
author_old_url_list=[]
search_url="http://xueshu.baidu.com/usercenter/data/authorchannel"
session=requests.session()
j=0
fact_len=0
isFirstGet=True;
author_nourl_list=[]
while len(author_name_list)!=0:
    print("url:第" + str(j) + "次尝试")
    try:
        print("[")
        for author_dict in author_name_list:
            author_nourl_list.append(author_dict)
            fact_len+=1
            print(str(author_dict['name']))
            # time.sleep(random.random())
            headers['User-Agent'] = random.choice(user_agent_list)
            params['author']=author_dict['name']
            response = session.get(search_url, headers=headers, params=params)
            content=response.content.decode('unicode_escape').encode('utf-8').decode("utf-8")
            soup=BeautifulSoup(content,"lxml")
            result_list = soup.select('.personInstitution.color_666')
            url_list = soup.select('.searchResult_take')
            isFirst=True
            for result,url in zip(result_list,url_list):
                author_url_dict = {}
                if result.get_text().startswith("浙江工业大学"):
                    if isFirst:
                        author_nourl_list.pop()
                        isFirst=False
                    url=url.get("href").replace("\\","")
                    author_url="http://xueshu.baidu.com"+url
                    print(author_url)
                    author_url_dict['no']=author_dict['no']
                    author_url_dict['name']=author_dict['name']
                    author_url_dict['url']=author_url
                    author_old_url_list.append(author_url_dict)
                    # print("{\"no\":\""+author_dict['no']
                    #       +"\",\"name\":\""+str(author_dict['name']).encode("unicode_escape").decode('utf-8')+"\","
                    #       +"\"url\":\""+author_url+"\"},")
        del author_name_list[0:fact_len]
        for data in author_old_url_list:
            author_url_list.append(data)
        author_old_url_list.clear()
        print("]")
        print("爬取url正常结束")
        print("author_nourl_list="+str(author_nourl_list))
        print("author_nourl_list尝试捡漏")
        if isFirstGet:
            for rest in author_nourl_list:
                author_name_list.append(rest)
            print("开始捡漏")
            isFirstGet=False
        # json.dump(author_url_list, open("./normal/author_url_list.json", "a", encoding="utf-8"))
    except Exception as e:
        print("len=" + str(fact_len))
        print(e)
        print()
        j += 1
        del author_name_list[0:fact_len-1]
        for data in author_old_url_list:
            author_url_list.append(data)
        author_old_url_list.clear()
        print("！！！爬取url不正常结束")
        fact_len=0
        print("author_nourl_list="+str(author_nourl_list))
        # json.dump(author_url_list, open("./normal/author_url_list.json", "a", encoding="utf-8"))
        # print(str(e))

json.dump(author_url_list, open("./normal/author_url_list.json", "a", encoding="utf-8"))

#爬取学者首页
# author_url_list=json.load(open("./normal/author_url_list.json","r"))
print(author_url_list)
print(type(author_url_list))
print(len(author_url_list))
print("！！！！！！author_url_list准备好了")
author_list=[]
author_old_list=[]
j=0
fact_len=0
while len(author_url_list)!=0:
    print("index:第" + str(j) + "次尝试")
    try:
        for author in author_url_list:
            fact_len+=1
            no_journal = 0
            author_content_dict = {}
            author_article_list = []
            author_doMain_list=[]
            print("first:开始解析："+str(author['name'])+"的资料；")
            author_content_dict['name']=author['name']
            author_content_dict['no']=author['no']
            headers['User-Agent'] = random.choice(user_agent_list)
            response=requests.get(author['url'],headers=headers)
            time.sleep(random.random())
            content=response.content.decode("utf-8")
            pattern = re.compile("entity_id: '(.*)'")
            entity_id = pattern.findall(content)[0]
            soup=BeautifulSoup(content,"lxml")
            if soup.select(".res-page span"):
                maxPageCount = soup.select(".res-page span")
                maxPageCount = maxPageCount[len(maxPageCount) - 1].get_text()
            affiliate=soup.select(".p_affiliate")[0].get_text()
            scholarId=soup.select(".p_scholarID_id")[0].get_text()
            doMain_list=soup.select(".person_domain.person_text a")
            for doMain in doMain_list:
                author_doMain_list.append(doMain.get_text())
            if soup.select(".res-page span"):
                author_content_dict["maxPageCount"]=maxPageCount
            author_content_dict["affiliate"]=affiliate
            author_content_dict["scholarId"]=scholarId
            author_content_dict["doMain"]=author_doMain_list
            author_content_dict["entity_id"]=entity_id
            article_result=soup.select(".result")
            for article in article_result:
                # print(article)
                author_article_dict = {}
                author_article_partner_list=[]
                if article.select_one('.res_t a'):
                    author_article_dict['title']=article.select_one('.res_t a').get_text()
                if article.select_one('.res_year'):
                    author_article_dict['year']=article.select_one('.res_year').get_text()
                if article.select_one('.cite_cont'):
                    author_article_dict['citeCount']=article.select_one('.cite_cont').get_text()
                if article.select('.res_info a'):
                    journal=article.select('.res_info a')
                    if int(len(journal)) == 4 and int(str(article.select_one('.cite_cont').get_text())) == 0:
                        author_article_dict['journal'] = journal[len(journal) - 1].get_text().replace("《", "").replace("》", "")
                    elif int(len(journal)) == 5:
                        author_article_dict['journal'] = journal[len(journal) - 2].get_text().replace("《", "").replace("》", "")
                    else:
                        pattern = re.compile(
                            '</span>((&nbsp;-&nbsp;)|(\s-\s))([a-zA-Z\u2E80-\u9FFF《》].*?)((&nbsp;-&nbsp;)|(\s-\s))<span class="res_cite">')
                        confirmResult = pattern.findall(str(article))
                        if confirmResult:
                            no_journal += 1
                            author_article_dict['journal'] = confirmResult[0][int(len(confirmResult[0]) / 2)].replace("《", "").replace("》", "")
                    i=0
                    for partner in article.select(".res_info span a"):
                        if int(i)==3:
                            break
                        author_article_partner_list.append(partner.get_text())
                        i=i+1
                    author_article_dict['partner']=author_article_partner_list
                author_article_list.append(author_article_dict)
            author_content_dict['article']=author_article_list
            author_old_list.append(author_content_dict)
        del author_url_list[0:fact_len]
        for data in author_old_list:
            author_list.append(data)
        author_old_list.clear()
        print("爬取学者首页正常结束")
        # json.dump(author_list, open("./normal/author_index_list.json", "a", encoding="utf-8"))
    except Exception as e:
        j+=1
        print("！！！！！爬取学者首页不正常结束")
        del author_url_list[0:fact_len-1]
        for data in author_old_list:
            author_list.append(data)
        author_old_list.clear()
        fact_len=0
        # json.dump(author_list, open("./normal/author_index_list.json", "a", encoding="utf-8"))
        print(str(e))

json.dump(author_list, open("./normal/author_index_list.json", "a", encoding="utf-8"))

# author_list=json.load(open("./normal/author_index_list.json","r"))
author_old_list=author_list.copy()
url = "http://xueshu.baidu.com/usercenter/data/author"
author_all_list=[]
author_old_all_list=[]
j=0
fact_len=0
while len(author_old_list)!=0:
    print("all:第" + str(j) + "次尝试")
    try:
        for author in author_old_list:
            fact_len+=1
            no_journal = 0
            print("second:翻页搜索中；；"+str(author['name']))
            if(author.get('maxPageCount',None)):
                maxPageCount = author['maxPageCount']
                for j in range(2,int(maxPageCount)+1):
                    page_params['curPageNum'] = j
                    page_params['entity_id']=author['entity_id']
                    session = requests.session()
                    headers['User-Agent'] = random.choice(user_agent_list)
                    response = session.post(url, headers=headers, data=page_params)
                    time.sleep(random.random())
                    content = response.content.decode("utf-8")
                    soup = BeautifulSoup(content, "lxml")
                    article_result = soup.select(".result")
                    for article in article_result:
                        author_article_dict = {}
                        author_article_partner_list = []
                        if article.select_one('.res_t a'):
                            author_article_dict['title'] = article.select_one('.res_t a').get_text()
                        if article.select_one('.res_year'):
                            author_article_dict['year'] = article.select_one('.res_year').get_text()
                        if article.select_one('.cite_cont'):
                            author_article_dict['citeCount'] = article.select_one('.cite_cont').get_text()
                        if article.select('.res_info a'):
                            journal = article.select('.res_info a')
                            if int(len(journal)) == 4 and int(str(article.select_one('.cite_cont').get_text()))==0:
                                author_article_dict['journal'] = journal[len(journal) - 1].get_text().replace("《", "").replace("》", "")
                            elif int(len(journal)) == 5:
                                author_article_dict['journal'] = journal[len(journal) - 2].get_text().replace("《", "").replace("》", "")
                            else:
                                pattern = re.compile(
                                    '</span>((&nbsp;-&nbsp;)|(\s-\s))([a-zA-Z\u2E80-\u9FFF《》].*?)((&nbsp;-&nbsp;)|(\s-\s))<span class="res_cite">')
                                confirmResult=pattern.findall(str(article))
                                if confirmResult :
                                    no_journal += 1
                                    author_article_dict['journal'] = confirmResult[0][int(len(confirmResult[0])/2)].replace("《", "").replace("》", "")

                            i = 0
                            for partner in article.select(".res_info span a"):
                                if int(i) == 3:
                                    break
                                author_article_partner_list.append(partner.get_text())
                                i = i + 1
                            author_article_dict['partner'] = author_article_partner_list
                        author['article'].append(author_article_dict)
            # author_all_list.append(author_list[size])
        for m in range(0,fact_len):
            author_all_list.append(author_old_list[m])
        del author_old_list[0:fact_len]
        print("搜索所有学者正常结束")
        json.dump(author_list, open("./normal/author_all_list.json", "w", encoding="utf-8"))
    except Exception as e:
        j += 1
        for m in range(0,fact_len):
            author_all_list.append(author_old_list[m])
        del author_old_list[0:fact_len-1]
        json.dump(author_list, open("./normal/author_all_list.json", "w", encoding="utf-8"))
        fact_len = 0
        print("搜索所有学者不正常结束")
        print(e)
