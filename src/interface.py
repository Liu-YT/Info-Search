#coding=utf-8

import os
import re
import string
import jieba
import math
import json

class info_retrieval:

    file_path = "F:/自然语言与知识图谱/Homework/homework 10/InfoSearch/data"
    
    index_path = "F:/自然语言与知识图谱/Homework/homework 10/InfoSearch/index"

    inverted_index = {}

    word_list = {}

    word_set = set()

    # 建立倒排索引
    def create_index(self): 
        folder = os.listdir(self.file_path)
        for i, file in enumerate(folder):
            path = os.path.join(self.file_path, file)
            if os.path.isfile(path) and path.endswith(".txt"):
                self.word_list[file] = []
                with open(path, 'r', encoding='utf8', errors='ignore') as f:
                    for line in f.readlines():
                        filter_punctuation_words = self.filter_punctuation(jieba.cut(line))
                        for filter_punctuation_word in filter_punctuation_words:
                            self.word_set.add(filter_punctuation_word)
                        self.word_list[file].extend(filter_punctuation_words)
        for word in self.word_set:
            index = []
            for key in self.word_list.keys():
                count = self.word_list[key].count(word)
                if count > 0:
                    index.append({
                        "file": key,
                        "count": count,
                        "total": len(self.word_list[key])
                    })
            self.inverted_index[word] = index
        # 存储索引
        f = open(self.index_path + '/index.json', 'w', encoding='UTF-8')
        f.write(json.dumps(self.inverted_index))
        f.close()

        # 存储词库
        f = open(self.index_path + '/word_set.txt', 'w', encoding='UTF-8')
        f.write(' '.join(list(self.word_set)))
        f.close()

        # 存储文件中间文件
        f = open(self.index_path + '/word_list.json', 'w', encoding='UTF-8')
        f.write(json.dumps(self.word_list))
        f.close()

        # print(self.inverted_index)
    
    def load_inverted_index(self):
        if os.path.isfile(self.index_path + '/index.json'):
            with open(self.index_path + '/index.json', 'r', encoding='UTF-8') as f:
                self.inverted_index = json.load(f)
            f.close()
        # print(self.inverted_index)

        if os.path.isfile(self.index_path + '/word_set.txt'):
            with open(self.index_path + '/word_set.txt', 'r', encoding='UTF-8') as f:
                words = f.read()
                for i in words.split(' '):
                    self.word_set.add(i)
            f.close()
        # print(self.word_set)
        
        if os.path.isfile(self.index_path + '/word_list.json'):
            with open(self.index_path + '/word_list.json', 'r', encoding='UTF-8') as f:
                self.word_list = json.load(f)
            f.close()
        # print(self.word_list)

    # 拼写检查（参考最小编辑距离原理）
    # 返回类型 bool - 是否进行了拼写纠正， list - 纠正结果组合
    def spell_check(self, query):
        query_filter_punctuation_words = self.filter_punctuation(jieba.cut(query))
        check_result = []
        for word in query_filter_punctuation_words:
            if word in self.word_set:
                check_result.append([word])
            else:
                match = []
                for each in self.word_set:
                    if self.minDis(each, word) == 1:
                        match.append(each)
                check_result.append(match)
        # print(check_result)
        # 结果组合
        all_res = [[i] for i in check_result[0]]
        for res in check_result[1:]:
            temp = all_res[:]
            all_res = []
            for j in res:
                for k in range(len(temp)):
                    l = temp[k][:]
                    l.append(j)
                    all_res.append(l)
        # print(all_res)
        if len(all_res) > 1:
            return True, all_res
        else:
            return False, all_res
        # print(all_res)
    
    # 计算最短编辑距离
    def minDis(self, word1, word2):
        m = len(word1) + 1
        n = len(word2) + 1

        dp = [[0 for i in range(n)] for j in range(m)]

        for i in range(n):
            dp[0][i] = i

        for i in range(m):
            dp[i][0] = i

        for i in range(1, m):
            for j in range(1, n):
                if(word1[i-1] == word2[j-1]):
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = min(dp[i][j-1], dp[i-1][j], dp[i-1][j-1]) + 1
        return dp[m-1][n-1]

    # 使用TF/IDF进行文档排序
    def info_search(self, query):
        word_list = self.filter_punctuation(jieba.cut(query))
        score = []
        for file in self.word_list.keys():
            score.append({
                "score": self.if_idf(word_list, file),
                "file": file
            })
        score = sorted(score, key=lambda item: item["score"], reverse=True)
        return score

    # 计算TF/IDF
    def if_idf(self, word_list, file):
        score = 0.0
        for word in word_list:
            if word not in self.inverted_index.keys():
                continue
            for info in self.inverted_index[word]:
                if info["file"] == file:
                    tf = math.log10(1 + info["count"] / info["total"])
                    idf = math.log10(len(self.word_list) / len(self.inverted_index[word]))
                    score += tf * idf
        return score

    # 消除标点符号
    def filter_punctuation(self, words):
        new_words = []
        illegal_char = string.punctuation + '【·！…（）—：“”？《》、；。】'
        pattern = re.compile('[%s]' % re.escape(illegal_char))
        for word in words:
            new_word = pattern.sub(u'', word)
            if not new_word == u'':
                new_words.append(new_word)
        return new_words

                    
