#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import MeCab
import gensim.models.doc2vec as doc2vec
from gensim import models
from gensim.models.doc2vec import TaggedDocument

model = models.Doc2Vec.load('doc2vec.model')
def trim_doc(doc):
    lines = doc.splitlines()
    valid_lines = []
    is_valid = False
    horizontal_rule_cnt = 0
    break_cnt = 0
    for line in lines:
        if horizontal_rule_cnt < 2 and '-----' in line:
            horizontal_rule_cnt += 1
            is_valid = horizontal_rule_cnt == 2
            continue
        if not(is_valid):
            continue
        if line == '':
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
        if len(chunks) > 3 and  (chunks[3].startswith('形容詞') or (chunks[3].startswith('名詞') and not chunks[3].startswith('名詞-数'))):
            words.append(chunks[0])
    print("words=",words)
    return words

# 似た文章を探す
def search_similar_texts(words):
    x = model.infer_vector(words)
    #print(x)
    most_similar_texts = model.docvecs.most_similar([x])
    for similar_text in most_similar_texts:
        print(similar_text)

if __name__ == '__main__':
    print('文字列入力:')
    search_str = input()
    words = split_into_words(search_str)
    search_similar_texts(words)
