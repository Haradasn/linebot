#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import MeCab
import gensim.models.doc2vec as doc2vec
from gensim import models
from gensim.models.doc2vec import TaggedDocument
from flask import Flask, request, abort
import ssl
import pandas as pd
from linebot import (
   LineBotApi, WebhookHandler
)
from linebot.exceptions import (
   InvalidSignatureError
)
from linebot.models import (
   MessageEvent, TextMessage, TextSendMessage,
)
model = models.Doc2Vec.load('/opt/doc2vec.model')
df = pd.read_csv('/opt/database.csv', header=None)
def trim_doc(doc):
    lines = doc.splitlines()
    valid_lines = []
    is_valid = False
    horizontal_rule_cnt = 0
    break_cnt = 0
    for line in lines:
        if horizontal_rule_cnt < 2 and '-----' in line: 
            is_valid = horizontal_rule_cnt == 2
            continue
            break_cnt += 1
            is_valid = break_cnt != 3
            continue
        break_cnt = 0
        valid_lines.append(line)
    return ''.join(valid_lines)

def split_into_words(doc):
    mecab = MeCab.Tagger("-Ochasen")
    valid_doc = doc
    lines = mecab.parse(valid_doc).splitlines()
    words = []
    #print(lines)
    for line in lines:
        chunks = line.split('\t')
        if len(chunks) > 3 and (chunks[3].startswith('形容詞') or (chunks[3].startswith('名詞') and not chunks[3].startswith('名詞-数'))):
            words.append(chunks[0])
    return words

# 似た文章を探す
def search_similar_texts(words,df):
    x = model.infer_vector(words)
    most_similar_texts = model.docvecs.most_similar([x],topn=3)
    text=[[0 for i in range(4)] for j in range(3)]
    for idx,row in enumerate(df.iterrows()):
        for i,similar_text in enumerate(most_similar_texts):    
            if df[df.columns[4]][idx] == similar_text[0]:
                text[i][0] = similar_text[0]
                text[i][1] = df[df.columns[7]][idx]
                if df[df.columns[2]][idx] == "〇":
                    text[i][2] = "◆紙クーポン使用　　：可"
                else:
                    text[i][2] = "◆紙クーポン使用　　：不可"
                if df[df.columns[3]][idx] == "〇":
                    text[i][3] = "◆電子クーポン使用　：可"
                else:
                    text[i][3] = "◆電子クーポン使用　：不可"
                break
    return text
    #for similar_text in most_similar_texts:
    #    print()

# 似た単語を探す
def search_similar_word(words):
    #print(words)
    for word in words:
        #print(word)
        #print(word + ':')
        for result in model.most_similar(positive=word, topn=10):
            print(result[0])
app = Flask(__name__)
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain('/etc/letsencrypt/live/tsurushi.tk/fullchain.pem', '/etc/letsencrypt/live/tsurushi.tk/privkey.pem')
line_bot_api = LineBotApi('#LINE APIトークンを記載する')
handler = WebhookHandler('#LINE Developersに書いてあるシークレットを記載する。')



@app.route("/callback", methods=['POST'])
def callback():
   # get X-Line-Signature header value
   signature = request.headers['X-Line-Signature']

   # get request body as text
   body = request.get_data(as_text=True)
   app.logger.info("Request body: " + body)

   # handle webhook body
   try:
       handler.handle(body, signature)
   except InvalidSignatureError:
       print("Invalid signature. Please check your channel access token/channel secret.")
       abort(400)

   return 'OK'
@app.route('/')
def hello():
    return 'Hello World!'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    #print("event.message.text=",event.message.text)
    words = split_into_words(event.message.text)
    text = []
    text = search_similar_texts(words,df)
    #print("text",text[0])
    line_bot_api.reply_message(
       event.reply_token,
       [
       TextSendMessage(text="1.こちらはいかがでしょうか\uDBC0\uDC78\n"+text[0][1]+"\n"+text[0][2]+"\n"+text[0][3]),
       TextSendMessage("2.こちらはいかがでしょうか\uDBC0\uDC9D\n"+text[1][1]+"\n"+text[1][2]+"\n"+text[1][3]),
       TextSendMessage("3.こちらはいかがでしょうか\uDBC0\uDC90\n"+text[2][1]+"\n"+text[2][2]+"\n"+text[2][3])
       ]
    )
if __name__ == "__main__":
   app.run(host='0.0.0.0', port=443,ssl_context=context, threaded=True)
#    app.run(host='0.0.0.0',port=80)
