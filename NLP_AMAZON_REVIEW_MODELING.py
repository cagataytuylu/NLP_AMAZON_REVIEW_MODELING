##################################################
# Introduction to Text Mining and Natural Language Processing
##################################################

##################################################
# Sentiment Analysis and Sentiment Modeling for Amazon Reviews
##################################################


# 1. Text Preprocessing
# 2. Text Visualization
# 3. Sentiment Analysis
# 4. Feature Engineering
# 5. Sentiment Modeling


from warnings import filterwarnings
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, GridSearchCV, cross_validate
from sklearn.preprocessing import LabelEncoder
from textblob import Word, TextBlob
from wordcloud import WordCloud


filterwarnings('ignore')
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)
pd.set_option('display.float_format', lambda x: '%.2f' % x)



##################################################
# 1. Text Preprocessing
##################################################

df = pd.read_csv("datasets/amazon_reviews.csv", sep=",")
df.head()
df.info()

###############################
# Normalizing Case Folding
###############################

df['reviewText'] = df['reviewText'].str.lower()


###############################
# Punctuations
###############################

df['reviewText'] = df['reviewText'].str.replace('[^\w\s]', '')


###############################
# Numbers
###############################

df['reviewText'] = df['reviewText'].str.replace('\d', '')


###############################
# Stopwords
###############################

# nltk.download('stopwords')
sw = stopwords.words('english')
df['reviewText'] = df['reviewText'].apply(lambda x: " ".join(x for x in str(x).split() if x not in sw))


###############################
# Rarewords
###############################

drops = pd.Series(' '.join(df['reviewText']).split()).value_counts()[-1000:]

df['reviewText'] = df['reviewText'].apply(lambda x: " ".join(x for x in x.split() if x not in drops))


###############################
# Tokenization
###############################

# nltk.download("punkt")
df["reviewText"].apply(lambda x: TextBlob(x).words).head()


###############################
# Lemmatization / Stemming
###############################

# nltk.download('wordnet')
df['reviewText'] = df['reviewText'].apply(lambda x: " ".join([Word(word).lemmatize() for word in x.split()]))


##################################################
# 2. Text Visualization
##################################################

###############################
# Terim Frekanslarının Hesaplanması
###############################

tf = df["reviewText"].apply(lambda x: pd.value_counts(x.split(" "))).sum(axis=0).reset_index()

tf.columns = ["words", "tf"]


tf.shape

tf["words"].nunique()

tf["tf"].describe([0.05, 0.10, 0.25, 0.50, 0.75, 0.80, 0.90, 0.95, 0.99]).T

tf.sort_values("tf", ascending=False)


###############################
# Barplot
###############################


tf[tf["tf"] > 500].plot.bar(x="words", y="tf")
plt.show()



###############################
# Wordcloud
###############################

text = " ".join(i for i in df.reviewText)

wordcloud = WordCloud().generate(text)
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()


wordcloud = WordCloud(max_font_size=50,
                      max_words=100,
                      background_color="white").generate(text)
plt.figure()
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()

wordcloud.to_file("wordcloud.png")



###############################
# Şablonlara Göre Wordcloud
###############################


vbo_mask = np.array(Image.open("notes/HAFTA_11/img/tr.png"))


wc = WordCloud(background_color="white",
               max_words=1000,
               mask=vbo_mask,
               contour_width=3,
               contour_color="firebrick")

wc.generate(text)
plt.figure(figsize=[10, 10])
plt.imshow(wc, interpolation="bilinear")
plt.axis("off")
plt.show()

wc.to_file("vbo.png")



##################################################
# 3. Sentiment Analysis
##################################################

# NLTK already has a built-in, pretrained sentiment analyzer
# called VADER (Valence Aware Dictionary and sEntiment Reasoner).


df.head()
# nltk.download('vader_lexicon')

sia = SentimentIntensityAnalyzer()
sia.polarity_scores("The film was awesome")

sia.polarity_scores("I liked this music but it is not good as the other one")

df["reviewText"].apply(lambda x: x.upper())

df["reviewText"][0:10].apply(lambda x: sia.polarity_scores(x))


df["reviewText"][0:10].apply(lambda x: sia.polarity_scores(x)["compound"])


df["polarity_score"] = df["reviewText"].apply(lambda x: sia.polarity_scores(x)["compound"])





##################################################
# 4. Sentiment Modeling
##################################################

###############################
# Feature Engineering
###############################

###############################
# Target'ın Oluşturulması
###############################


df["reviewText"][0:10].apply(lambda x: "pos" if sia.polarity_scores(x)["compound"] > 0 else "neg")


df["sentiment_label"] = df["reviewText"].apply(lambda x: "pos" if sia.polarity_scores(x)["compound"] > 0 else "neg")


df["sentiment_label"].value_counts()

df.groupby("sentiment_label")["overall"].mean()

df["sentiment_label"] = LabelEncoder().fit_transform(df["sentiment_label"])


X = df["reviewText"]
y = df["sentiment_label"]


# Count Vectors: frekans temsiller
# TF-IDF Vectors: normalize edilmiş frekans temsiller
# Word Embeddings (Word2Vec, GloVe, BERT)


# words
# kelimelerin nümerik temsilleri

# characters
# karakterlerin numerik temsilleri

# ngram
a = """Bu örneği anlaşılabilmesi için daha uzun bir metin üzerinden göstereceğim.
N-gram'lar birlikte kullanılan kelimelerin kombinasyolarını gösterir ve feature üretmek için kullanılır"""

TextBlob(a).ngrams(2)


###############################
# Count Vectors
###############################

from sklearn.feature_extraction.text import CountVectorizer

corpus = ['This is the first document.',
          'This document is the second document.',
          'And this is the third one.',
          'Is this the first document?']




vectorizer = CountVectorizer()
X_c = vectorizer.fit_transform(corpus)
vectorizer.get_feature_names()
X_c.toarray()


# n-gram frekans
vectorizer2 = CountVectorizer(analyzer='word', ngram_range=(2, 2))
X_n = vectorizer2.fit_transform(corpus)
vectorizer2.get_feature_names()
X_n.toarray()

# Veriye uygulanması:
vectorizer = CountVectorizer()
X_count = vectorizer.fit_transform(X)

vectorizer.get_feature_names()[10:15]
X_count.toarray()[10:15]

###############################
# TF-IDF
###############################

# word tf-idf
from sklearn.feature_extraction.text import TfidfVectorizer
vectorizer = TfidfVectorizer(analyzer='word')
X_w = vectorizer.fit_transform(corpus)
vectorizer.get_feature_names()
X_w.toarray()


# n-gram tf-idf
from sklearn.feature_extraction.text import TfidfVectorizer
vectorizer = TfidfVectorizer(ngram_range=(2, 3))
X_n = vectorizer.fit_transform(corpus)
vectorizer.get_feature_names()
X_n.toarray()


# Veriye uygulanması:
tf_idf_word_vectorizer = TfidfVectorizer()
X_tf_idf_word = tf_idf_word_vectorizer.fit_transform(X)



# Veriye uygulanması:
tf_idf_ngram_vectorizer = TfidfVectorizer(ngram_range=(2, 3))
X_tf_idf_ngram = tf_idf_word_vectorizer.fit_transform(X)


###############################
# 5. Modeling
###############################

###############################
# Logistic Regression
###############################


log_model = LogisticRegression().fit(X_tf_idf_word, y)

cross_val_score(log_model,
                X_tf_idf_word,
                y, scoring="accuracy",
                cv=5).mean()


yeni_yorum = pd.Series("this product is great")
yeni_yorum = pd.Series("look at that shit very bad")
yeni_yorum = pd.Series("it was good but I am sure that it fits me")


yeni_yorum = CountVectorizer().fit(X).transform(yeni_yorum)

log_model.predict(yeni_yorum)


random_review = pd.Series(df["reviewText"].sample(1).values)


yeni_yorum = CountVectorizer().fit(X).transform(random_review)

log_model.predict(yeni_yorum)



###############################
# Random Forests
###############################

# Count Vectors
rf_model = RandomForestClassifier().fit(X_count, y)
cross_val_score(rf_model, X_count, y, cv=5, n_jobs=-1).mean()

# TF-IDF Word-Level
rf_model = RandomForestClassifier().fit(X_tf_idf_word, y)
print(cross_val_score(rf_model, X_tf_idf_word, y, cv=5, n_jobs=-1).mean())

# TF-IDF N-GRAM
rf_model = RandomForestClassifier().fit(X_tf_idf_ngram, y)
print(cross_val_score(rf_model, X_tf_idf_ngram, y, cv=5, n_jobs=-1).mean())



###############################
# Hiperparametre Optimizasyonu
###############################

rf_model = RandomForestClassifier(random_state=17)

rf_params = {"max_depth": [5, 8, None],
             "max_features": [5, 7, "auto"],
             "min_samples_split": [2, 5, 8, 20],
             "n_estimators": [100, 200, 500]}

rf_best_grid = GridSearchCV(rf_model,
                            rf_params,
                            cv=5,
                            n_jobs=-1,
                            verbose=True).fit(X_count, y)

rf_best_grid.best_params_

rf_final = rf_model.set_params(**rf_best_grid.best_params_, random_state=17).fit(X_count, y)

cv_results = cross_validate(rf_final, X_count, y, cv=3, scoring=["accuracy", "f1", "roc_auc"])

cv_results['test_accuracy'].mean()
cv_results['test_f1'].mean()
cv_results['test_roc_auc'].mean()



###############################
# BONUS: Word Embeddings
###############################

# Google’s Word2Vec (2013)
# Stanford’s GloVe (2014)
# Facebook’s FastText (2016)
# Google’s BERT (Bidirectional Encoder Representations from Transformers, 2018)


# pretrained


# CBOW (Continuous Bag-of-Words): Context'ten tek bir kelimeyi tahmin etmek.
# Skip-gram: Tek bir kelimeden context'i tahmin etmek



# Life is like riding a bicycle. To keep your balance, you must keep moving. Albert Einstein.


# CBOW: Input = [is, like, a, bicycle],  Output = riding

# Skip-gram: Input = riding, Output = [is, like, a, bicycle]


###############################
# Word2Vec vs BERT
###############################


# “He went to the prison cell with his cell phone to extract blood cell samples from inmates”







































