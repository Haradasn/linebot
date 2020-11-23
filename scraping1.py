import csv
import time
import pprint
import requests
import urllib3
import pandas as pd
from bs4 import BeautifulSoup
import re
from requests.exceptions import Timeout
def connect_url(url,df,idx):
    stand_by_sec = 5
    try:
        print(f"\nurl: {url}\tへ接続開始...")
        u = requests.get(url, timeout=3.5)
        soup = BeautifulSoup(u.content, "lxml")
        elems = soup.find_all("a",href=re.compile('^.*tabelog.com/chiba'))
        if not elems:
            print("Nothing")
        else:
            for elem in elems:
                if re.search(r'^https://.*/[0-9]{8}/',elem['href'][7:]) :
                    print(re.search(r'^https://.*/[0-9]{8}/',elem['href'][7:]).group())
                    urlName = re.search(r'^.*/[0-9]{8}/',elem['href'][7:]).group()
                    df[df.columns[7]][idx]= urlName
                    url = requests.get(urlName)
                    soup = BeautifulSoup(url.content, "lxml")
                    elems = soup.find_all("span",class_="linktree__parent-target-text")
                    for index,elem in enumerate(elems):
                        print(elem.text) 
                        df[df.columns[8+index]][idx]= elem.text
                    break    
    except requests.exceptions.Timeout:
        # タイムアウトした時は2秒待機して再実行
        print(f"\rタイムアウトしました...\n再接続待機中...{stand_by_sec}秒後に再実行します", end="", flush=True)
        time.sleep(stand_by_sec)
        connect_url(url=url,df=df,idx=idx)
      
    except requests.exceptions.ConnectionError:
        # タイムアウトした時は2秒待機して再実行
        print(f"\rタイムアウトしました...\n再接続待機中...{stand_by_sec}秒後に再実行します", end="", flush=True)
        time.sleep(stand_by_sec)
        connect_url(url=url,df=df,idx=idx)
        
        
    except requests.exceptions.HTTPError:
        # タイムアウトした時は2秒待機して再実行
        print(f"\rタイムアウトしました...\n再接続待機中...{stand_by_sec}秒後に再実行します", end="", flush=True)
        time.sleep(stand_by_sec)
        connect_url(url=url,df=df,idx=idx)
    except urllib3.exceptions.ReadTimeoutError:
        # タイムアウトした時は2秒待機して再実行
        print(f"\rタイムアウトしました...\n再接続待機中...{stand_by_sec}秒後に再実行します", end="", flush=True)
        time.sleep(stand_by_sec)
        connect_url(url=url,df=df,idx=idx)
    else:
        # 成功時の処理
        return u,elems
    finally:
        # 後始末
        pass
df = pd.read_csv('千葉県の店舗一覧のCSV', header=None)
df = df.assign(url=0)
df = df.assign(elm1=0)
df = df.assign(elm2=0)
df = df.assign(elm3=0)
df = df.assign(elm4=0)
df = df.assign(elm5=0)
print(df['elm3'][11])
for idx,row in df.iterrows():
    urlName = "https://www.google.com/search?q=" +  re.sub("　","+",re.sub("&","＆",re.sub("-","",row[4])))+ "+" + row[6] + "+食べログ"
    url,elems = connect_url(urlName,df,idx)
df.to_csv("保存先を記載するする")
print("終わり！")