#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import os
import sys
import MeCab
import collections
from gensim import models
from gensim.models.doc2vec import TaggedDocument
import re
import time
OUTPUT_MODEL = 'doc2vec.model'

# 文章から単語に分解して返す
def split_into_words(doc, name=''):
    mecab = MeCab.Tagger("-Ochasen")
    lines = mecab.parse(doc).splitlines()
    words = []
    for line in lines:
        chunks = line.split('\t')
        if len(chunks) > 3 and  (chunks[3].startswith('形容詞') or (chunks[3].startswith('名詞') and not chunks[3].startswith('名詞-数'))):
            words.append(chunks[0])
    return TaggedDocument(words=words, tags=[name])

# データから単語のリストを取得
def corpus_to_sentences(corpus):
    for idx,doc in enumerate(corpus.iterrows()):
        sys.stdout.write('\r前処理中 {} / {}'.format(idx, len(corpus)))
#        yield split_into_words(str(df[2][idx])+re.sub("駅|京成","",str(df[9][idx]))+str(df[11][idx])+str(df[12][idx])+str(df[13][idx])+str(df[5][idx]), df[5][idx])
        yield split_into_words(str(df[2][idx])+re.sub("駅|京成","",str(df[9][idx]))+str(df[11][idx])+str(df[12][idx])+str(df[13][idx])+str(df[14][idx])[:5]+str(df[5][idx]), df[5][idx])

# 学習
def train(sentences):
    model = models.Doc2Vec(dm=1,vector_size=300, sample=5e-5, min_count=0, workers=15,window=1,epochs=600,hs=1,negative=5)
    model.build_vocab(sentences)
    model.train(sentences, total_examples = model.corpus_count, epochs = model.epochs)
    ranks = []
    for doc_id in range(int(sum([len(sentence) for (sentence) in (sentences)])/2)):
        inferred_vector = model.infer_vector(sentences[doc_id].words)
        sims = model.docvecs.most_similar([inferred_vector], topn=len(model.docvecs))
        rank = [docid for docid, sim in sims].index(sentences[doc_id].tags[0])
        ranks.append(rank)
    print(collections.Counter(ranks))
    return model

if __name__ == '__main__':
    df = pd.read_csv('c:/users/SHINYA HARADA/Desktop/list_out_2.csv', header=None)
    sentences = list(corpus_to_sentences(df))
    start = time.time()
    model = train(sentences)
    elapsed_time = time.time() - start
    model.save(OUTPUT_MODEL)
    print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")