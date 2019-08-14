import requests
from bs4 import BeautifulSoup
import re
import json

url="http://xueshu.baidu.com/usercenter/data/authorchannel?cmd=inject_page"
headers={
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
}
params={
    "cmd":"search_author",
    "_token":"",
    "_ts":"",
    "_sign":"",
    "author":"张元鸣",
    "affiliate":"浙江工业大学",
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

#手动初始化参数
author_name_list=['张元鸣',"李伟"]

#搜索学者
author_url_list=[]
search_url="http://xueshu.baidu.com/usercenter/data/authorchannel"
session=requests.session()
for author in author_name_list:
    params['author']=author
    response = session.get(search_url, headers=headers, params=params)
    content=response.content.decode('unicode_escape').encode('utf-8').decode("utf-8")
    #print("content="+str(content))
    soup=BeautifulSoup(content,"lxml")
    result_list = soup.select('.personInstitution.color_666')
    url_list = soup.select('.searchResult_take')
    for result,url in zip(result_list,url_list):
        author_url_dict = {}
        if result.get_text().startswith("浙江工业大学"):
            url=url.get("href").replace("\\","")
            author_url="http://xueshu.baidu.com"+url
            author_url_dict['author']=author
            author_url_dict['url']=author_url
            author_url_list.append(author_url_dict)

author_list=[]


for author in author_url_list:
    no_journal = 0
    author_content_dict = {}
    author_article_list = []
    author_doMain_list=[]
    print("开始解析："+author['author']+"的资料；")
    author_content_dict['author']=author['author']
    response=requests.get(author['url'],headers=headers)
    content=response.content.decode("utf-8")
    with open("Test06_use.html","w",encoding="utf-8")as f:
        f.write(content)
    pattern = re.compile("entity_id: '(.*)'")
    entity_id = pattern.findall(content)[0]
    print("entity_id="+entity_id)
    soup=BeautifulSoup(content,"lxml")
    maxPageCount = soup.select(".res-page span")
    maxPageCount = maxPageCount[len(maxPageCount) - 1].get_text()
    affiliate=soup.select(".p_affiliate")[0].get_text()
    scholarId=soup.select(".p_scholarID_id")[0].get_text()
    doMain_list=soup.select(".person_domain.person_text a")
    for doMain in doMain_list:
        author_doMain_list.append(doMain.get_text())
    author_content_dict["maxPageCount"]=maxPageCount
    author_content_dict["affiliate"]=affiliate
    author_content_dict["scholarId"]=scholarId
    author_content_dict["doMain"]=author_doMain_list
    author_content_dict["entity_id"]=entity_id
    article_result=soup.select(".result")
    for article in article_result:
        author_article_dict = {}
        author_article_partner_list=[]
        author_article_dict['title']=article.select_one('.res_t a').get_text()
        author_article_dict['year']=article.select_one('.res_year').get_text()
        author_article_dict['citeCount']=article.select_one('.cite_cont').get_text()
        journal=article.select('.res_info a')
        print("这是jorunal+======"+str(journal))
        print(len(journal))
        if int(len(journal)) == 4 and int(str(article.select_one('.cite_cont').get_text())) == 0:
            author_article_dict['journal'] = journal[len(journal) - 1].get_text().replace("《", "").replace("》", "")
        elif int(len(journal)) == 5:
            author_article_dict['journal'] = journal[len(journal) - 2].get_text().replace("《", "").replace("》", "")
        else:
            print("3." + "len(journal)不等于4也不等于5")
            pattern = re.compile(
                '</span>((&nbsp;-&nbsp;)|(\s-\s))([a-zA-Z\u2E80-\u9FFF《》].*?)((&nbsp;-&nbsp;)|(\s-\s))<span class="res_cite">')
            print("3.55555====" + str(no_journal))
            confirmResult = pattern.findall(str(article))
            print("4." + "confirmResult====" + str(confirmResult))
            if confirmResult:
                print("4.1111=-==" + str(confirmResult[0][int(len(confirmResult[0]) / 2)]))
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
    author_list.append(author_content_dict)

print(json.dumps(author_list))
print("----------------------------------------------\n-------------------------------\n")

url = "http://xueshu.baidu.com/usercenter/data/author"

for author in author_list:
    no_journal = 0
    print("翻页搜索中；；"+str(author['author']))
    maxPageCount = author['maxPageCount']

    print("maxPageCount="+str(maxPageCount))
    for j in range(2,int(maxPageCount)+1):
        page_params['curPageNum'] = j
        page_params['entity_id']=author['entity_id']
        session = requests.session()
        response = session.post(url, headers=headers, data=page_params)
        content = response.content.decode("utf-8")
        print("content来了来了来了来了："+content)
        soup = BeautifulSoup(content, "lxml")
        article_result = soup.select(".result")
        for article in article_result:
            print(str(article))
            author_article_dict = {}
            author_article_partner_list = []
            author_article_dict['title'] = article.select_one('.res_t a').get_text()
            if article.select_one('.res_year'):
                author_article_dict['year'] = article.select_one('.res_year').get_text()
            author_article_dict['citeCount'] = article.select_one('.cite_cont').get_text()
            journal = article.select('.res_info a')
            print("1.这是jorunal+======" + str(journal))
            print("2."+str(len(journal)))
            if int(len(journal)) == 4 and int(str(article.select_one('.cite_cont').get_text()))==0:
                author_article_dict['journal'] = journal[len(journal) - 1].get_text().replace("《", "").replace("》", "")
            elif int(len(journal)) == 5:
                author_article_dict['journal'] = journal[len(journal) - 2].get_text().replace("《", "").replace("》", "")
            else:
                print("3."+"len(journal)不等于4也不等于5")
                pattern = re.compile(
                    '</span>((&nbsp;-&nbsp;)|(\s-\s))([a-zA-Z\u2E80-\u9FFF《》].*?)((&nbsp;-&nbsp;)|(\s-\s))<span class="res_cite">')
                print("3.55555===="+str(no_journal))
                confirmResult=pattern.findall(str(article))
                print("4."+"confirmResult===="+str(confirmResult))
                if confirmResult :
                    print("4.1111=-=="+str(confirmResult[0][int(len(confirmResult[0])/2)]))
                    no_journal += 1
                    author_article_dict['journal'] = confirmResult[0][int(len(confirmResult[0])/2)].replace("《", "").replace("》", "")

            i = 0
            for partner in article.select(".res_info span a"):
                if int(i) == 3:
                    break
                author_article_partner_list.append(partner.get_text())
                i = i + 1
            author_article_dict['partner'] = author_article_partner_list

            print("6."+str(author_article_dict))
            author['article'].append(author_article_dict)


print(json.dumps(author_list))





