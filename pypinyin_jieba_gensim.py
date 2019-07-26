from pypinyin import lazy_pinyin, TONE2


def pinyin(q, str):
    res1 = "".join(lazy_pinyin(q, style=TONE2))
    res2 = "".join(lazy_pinyin(str, style=TONE2))
    if res2 in res1:
        return True


# 分词和机器学习，一开始加载项目进尽心词库模型加载，以便在调用时效率高
import jieba
from gensim import corpora
from gensim import models
from gensim import similarities
from settings import MGDB

li = list(MGDB.Content.find())
all_doc_list = []
#对歌名进行分词
for doc in li:
    doc_list = [word for word in jieba.cut_for_search(doc.get("title"))]
    all_doc_list.append(doc_list)
dictionary = corpora.Dictionary(all_doc_list)#生成词袋
corpus = [dictionary.doc2bow(doc) for doc in all_doc_list]#创建语料库
lsi = models.LsiModel(corpus)#建立模型
index = similarities.SparseMatrixSimilarity(lsi[corpus], num_features=len(dictionary.keys()))# 稀疏矩阵相似度 将 主 语料库corpus的训练结果 作为初始值


def similer(q):
    doc_test_list = [word for word in jieba.cut(q)]
    doc_test_vec = dictionary.doc2bow(doc_test_list)
    sim = index[lsi[doc_test_vec]]
    cc = sorted(enumerate(sim), key=lambda item: -item[1])
    if cc[0][1] >= 0.58:
        return li[cc[0][0]]
