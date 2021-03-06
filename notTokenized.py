import http.client
import zipfile
import os
import io
import base64
import json
import requests
from pandas.io.json import json_normalize
import numpy as np
import pandas as pd
import chardet
import nltk
from nltk.probability import FreqDist
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import sent_tokenize
from nltk import word_tokenize
from google.cloud import bigquery
import pickle

df=pd.read_csv('C:/Users/jcooke/PycharmProjects/qualtrics/MyQualtricsDownload/NuSkin.com Feedback Tab v5.1.csv')
df.columns = df.iloc[1]
df = df.drop([0,1])
df = df.reset_index(drop=True)

df = df.applymap(str)

df = df.replace('nan', '')

df1 = df[['{\"ImportId\":\"startDate\",\"timeZone\":\"Z\"}', '{\"ImportId\":\"_recordId\"}', '{\"ImportId\":\"QID29_TEXT_TRANSLATEDeneqqpuqm\"}', '{\"ImportId\":\"QID3_TEXT_TRANSLATEDenayfj8yo\"}', '{\"ImportId\":\"QID83_TEXT_TRANSLATEDeneh72e33\"}']]

#df["q29TextToken"] = df.apply(lambda x: nltk.word_tokenize(x[44]), axis=1)
#df{"ImportId":"QID29_TEXT_TRANSLATEDeneqqpuqm"}



df1["q29TextToken"] = df.apply(lambda x: nltk.word_tokenize(x[2]), axis=1)
df1["q3TextToken"] = df.apply(lambda x: nltk.word_tokenize(x[3]), axis=1)
df1["q83TextToken"] = df.apply(lambda x: nltk.word_tokenize(x[4]), axis=1)


q29Text = ''.join(df1.iloc[:,2].tolist())
q3Text = ''.join(df1.iloc[:,3].tolist())
q83Text = ''.join(df1.iloc[:,4].tolist())

#df = df.rename(index = lambda x: x + 1)



### stuff for testing
'''
train = [("Great place to be when you are in Bangalore.", "pos"),
  ("The place was being renovated when I visited so the seating was limited.", "neg"),
  ("Loved the ambience, loved the food", "pos"),
  ("The food is delicious but not over the top.", "neg"),
  ("Service - Little slow, probably because too many people.", "neg"),
  ("The place is not easy to locate", "neg"),
  ("Mushroom fried rice was spicy", "pos"),
]
dictionary = set(word.lower() for passage in train for word in word_tokenize(passage[0]))
#print("dictionary")
#print(dictionary)
#print(type(train))
#print(train[1])
# Step 3
t = [({word: (word in word_tokenize(x[0])) for word in dictionary}, x[1]) for x in train]
#print("t")
#print(t)
# Step 4 – the classifier is trained with sample data
classifier = nltk.NaiveBayesClassifier.train(t)
test_data = "Manchurian was hot and spicy"
test_data_features = {word.lower(): (word in word_tokenize(test_data.lower())) for word in dictionary}
#print(classifier.classify(test_data_features))
'''
### end stuff for testing

## original header processing
'''
use_cols = [
            0, 1, 4, 5, 6
            , 7, 8, 15, 16, 17
            , 18, 19, 20, 24, 25
            , 26, 27, 28, 29, 30
            , 31, 32, 33, 34, 35
            , 37, 38, 39, 40, 41
            , 42, 43, 44, 45, 46
            , 47, 48, 49, 50, 51
            , 52, 53, 54, 55, 56
            , 57, 58, 59, 60, 61
            , 62, 63, 64, 67, 68
            , 69, 70, 71, 72, 73
        ]
df=pd.read_csv('C:/Users/jcooke/PycharmProjects/qualtrics/MyQualtricsDownload/NuSkin.com Feedback Tab v5.1.csv', usecols=use_cols)
print(df.columns)
df.columns = [
    'startDate','endDate','progress','duration','finished'
    ,'recordedDT','responseId','distChannel','language','q28'
    ,'q3Text','q29Text','q30Text','browser','browserVersion'
    ,'os','resolution','Q2','Q3','Q4'
    ,'timeOnSite','totPages','uniquePages','domain','qLanguage'
    ,'distId','support','browserLanguage','loginStatus','browserLocCode'
    ,'pageCatogory','currUrl','pageCategory','siteLanguage','siteMarket'
    ,'test','market','subRegion','region','subArea'
    ,'area','reason','qDataPolicyViolations','mislabeledId','q29translated'
    ,'q30Translated','q30TranslatedTopicSentLabel','q30TranslatedTopicSentScore','q30TrasnlatedSentPolarity','q30TranslatedTopics'
    ,'q30TranslatedSentScore','q30TranslatedParentTopic','q30TranslatedSent','q3SentScore','q3Sent'
    ,'q3TopicSentLabel','q3TopicSentScore','q3Topic','q3Translated','q83Translated']
#remove original headers and leave only headers we like. original headers are saved ad dfOrigHeaders
dfOrigHeaders = df[0:2]
df = df.drop([0,1,2])
#print(df.head())
print("head 44")
print(df.iloc[:,[59]])
for col in df.columns:
    print(col)
#print('Complete')
df = df.applymap(str)
#df = df.to_string()
#print(type(df))
#print(dir(df))
#dfTokenize = df[['q29Translated','q3Translated', 'q83Translated']]
#print(dfTokenize)
df = df.replace('nan', '')
df["q29TextToken"] = df.apply(lambda x: nltk.word_tokenize(x[44]), axis=1)
df["q3TextToken"] = df.apply(lambda x: nltk.word_tokenize(x[58]), axis=1)
df["q83TextToken"] = df.apply(lambda x: nltk.word_tokenize(x[59]), axis=1)
print(df.iloc[:,[44,58,59]])
q29Text = ''.join(df.iloc[:,44].tolist())
q3Text = ''.join(df.iloc[:,58].tolist())
q83Text = ''.join(df.iloc[:,59].tolist())
'''
### end original header processing



# Processing data for q29 word analysis
q29TextTokenized = word_tokenize(q29Text)
q29TextTokenized = [word for word in q29TextTokenized if word.isalpha()]
stop_words = set(stopwords.words('english'))
q29TextTokenized = [w for w in q29TextTokenized if not w in stop_words]
q29TextTokenized = [i for i in q29TextTokenized if len(i) > 1]
lemmatizer = WordNetLemmatizer()
q29TextTokenized = [lemmatizer.lemmatize(word) for word in q29TextTokenized]
#print(FreqDist(q29TextTokenized).most_common(30))

# Processing data for q3 Word Analysis
q3TextTokenized = word_tokenize(q3Text)
q3TextTokenized = [word for word in q3TextTokenized if word.isalpha()]
stop_words = set(stopwords.words('english'))
q3TextTokenized = [w for w in q3TextTokenized if not w in stop_words]
q3TextTokenized = [i for i in q3TextTokenized if len(i) > 1]
lemmatizer = WordNetLemmatizer()

q3TextTokenized = [lemmatizer.lemmatize(word) for word in q3TextTokenized]
#print(FreqDist(q3TextTokenized).most_common(30))


#processing data for q83 Word Analysis

q83TextTokenized = word_tokenize(q83Text)
q83TextTokenized = [word for word in q83TextTokenized if word.isalpha()]
stop_words = set(stopwords.words('english'))
q83TextTokenized = [w for w in q83TextTokenized if not w in stop_words]
q83TextTokenized = [i for i in q83TextTokenized if len(i) > 1]

lemmatizer = WordNetLemmatizer()
q83TextTokenized = [lemmatizer.lemmatize(word) for word in q83TextTokenized]

#print(FreqDist(q83TextTokenized).most_common(30))

# process data without tokenizing the sentences
q29 = df1.iloc[:, [0,1,2]]
q29 = pd.DataFrame(q29)
q29 = q29.rename(columns={
    '{\"ImportId\":\"startDate\",\"timeZone\":\"Z\"}':'start_date'
    , '{\"ImportId\":\"_recordId\"}':'responseID'
    , '{\"ImportId\":\"QID29_TEXT_TRANSLATEDeneqqpuqm\"}':'sentence'
})
q29['sentence'] = q29['sentence'].str.strip()
q29['sentence'].replace('', np.nan, inplace=True)
q29 = q29.dropna(axis=0, subset=['sentence'])
q29.to_csv(r'C:/Users/jcooke/PycharmProjects/qualtrics/q29.csv')
q29["question"] = "q29"

q3 = df1.iloc[:, [0,1,3]]
q3 = pd.DataFrame(q3)
q3 = q3.rename(columns={
    '{\"ImportId\":\"startDate\",\"timeZone\":\"Z\"}':'start_date'
    , '{\"ImportId\":\"_recordId\"}':'responseID'
    , '{\"ImportId\":\"QID3_TEXT_TRANSLATEDenayfj8yo\"}':'sentence'
})

q3['sentence'] = q3['sentence'].str.strip()
q3['sentence'].replace('', np.nan, inplace=True)
q3 = q3.dropna(axis=0, subset=['sentence'])
q3.to_csv(r'C:/Users/jcooke/PycharmProjects/qualtrics/q3.csv')
q3["question"] = "q3"

q83 = df1.iloc[:, [0,1,4]]
q83 = pd.DataFrame(q83)
q83 = q83.rename(columns={
    '{\"ImportId\":\"startDate\",\"timeZone\":\"Z\"}':'start_date'
    , '{\"ImportId\":\"_recordId\"}':'responseID'
    , '{\"ImportId\":\"QID83_TEXT_TRANSLATEDeneh72e33\"}':'sentence'
})

q83['sentence'] = q83['sentence'].str.strip()
q83['sentence'].replace('', np.nan, inplace=True)
q83 = q83.dropna(axis=0, subset=['sentence'])
q83.to_csv(r'C:/Users/jcooke/PycharmProjects/qualtrics/q83.csv')
q83["question"] = "q83"

######processing sentence tokens Q29
'''
sentences = []
for row in q29Sent.itertuples():
    for sentence in sent_tokenize(row[3]):
        sentences.append((row[1], row[2], sentence))
q29Sent_DF = pd.DataFrame(sentences, columns=['start_date', 'responseID', 'sentence'])
q29Sent_DF["question"] = "q29"
#processing sentence for q3
q3Sent = df1.iloc[:, [0,1,3]]
sentences = []
for row in q3Sent.itertuples():
    for sentence in sent_tokenize(row[3]):
        sentences.append((row[1], row[2], sentence))
q3Sent_DF = pd.DataFrame(sentences, columns=['start_date', 'responseID', 'sentence'])
q3Sent_DF["question"] = "q3"
#processing sentence for q83
q83Sent = df1.iloc[:, [0,1,4]]
sentences = []
for row in q83Sent.itertuples():
    for sentence in sent_tokenize(row[3]):
        sentences.append((row[1], row[2], sentence))
q83Sent_DF = pd.DataFrame(sentences, columns=['start_date', 'responseID', 'sentence'])
q83Sent_DF["question"] = "q83"
print("Q29 sent DF")
print(q29Sent_DF)
q29Sent_DF.to_csv(r'C:/Users/jcooke/PycharmProjects/qualtrics/q29Sent_df.csv')
'''

# stack all dataframes on one another

all_dfs = [q29, q3, q83]


for df in all_dfs:
    df.columns = ["start_date", "responseID", "sentence", "question"]
all_dfs = pd.concat(all_dfs).reset_index(drop=True)

all_dfs.to_csv(r'C:/Users/jcooke/PycharmProjects/qualtrics/all_dfs2.csv')
#create training set

training = pd.read_csv('C:/Users/jcooke/PycharmProjects/qualtrics/all_dfs22.csv')
training = training.loc[:, ~training.columns.str.contains('^Unnamed')]


train = training.sample(frac = .8, random_state = 164)
test = training.drop(train.index)

train = pd.DataFrame(train)
train = train.reset_index(drop=True)
stop_words = set(stopwords.words('english'))
train['sentence'] = train['sentence'].str.replace("[^\w\s]", "").str.lower()
train['sentence'] = train['sentence'].apply(lambda x: ' '.join([item for item in x.split() if item not in stop_words]))
w_tokenizer = nltk.tokenize.WhitespaceTokenizer()
lemmatizer = WordNetLemmatizer()

def lemmatize_text(text):
    return [lemmatizer.lemmatize(w) for w in w_tokenizer.tokenize(text) ]

train['sentenceLemmatized'] = train.sentence.apply(lemmatize_text)
train = pd.DataFrame(train)
train['sentenceLemmatized'] = [','.join(map(str, l)) for l in train['sentenceLemmatized']]
train['sentenceLemmatized'] = train['sentenceLemmatized'].str.replace(',', ' ')
train = train[['sentenceLemmatized', 'sentiment']].apply(tuple, axis=1)

## process test

test = pd.DataFrame(test)

test = test.reset_index(drop=True)
stop_words = set(stopwords.words('english'))
test['sentence'] = test['sentence'].str.replace("[^\w\s]", "").str.lower()
test['sentence'] = test['sentence'].apply(lambda x: ' '.join([item for item in x.split() if item not in stop_words]))
test['sentenceLemmatized'] = test.sentence.apply(lemmatize_text)
test = pd.DataFrame(test)
test['sentenceLemmatized'] = [','.join(map(str, l)) for l in test['sentenceLemmatized']]
test['sentenceLemmatized'] = test['sentenceLemmatized'].str.replace(',', ' ')
test = test[['sentenceLemmatized', 'sentiment']].apply(tuple, axis=1)
testNonPairs = [(a) for a, b in test]
print("this is test")
print(test)

dictionaryTest = set(word.lower() for passage in test for word in word_tokenize(passage[0]))
print("this is dictionaryTest")
#print(dictionaryTest)
#for x in test:
 #   " ".join(test)


#print(tTest)
#print("directory")
#print(dir(tTest))
#print("tTest")
#testNonPairs = [(a) for a, b in tTest]
#print("test Non Pairs here")
#print(testNonPairs)
#print(type(tTest))
#print(tTest[1])
### end process test


#not sure if needed
###test = test.iloc[:, [2]]
###test = test.values.tolist()
#test = test.str.lower()
#test = "Brian is the best boss in nuskin dont right small first algebra amazing necessary understand"
# end not sure if needed





#dictionary = word_tokenize(list(train['sentence']))



testFeatures = []

#for x in test:
 #   " ".join(test)
dictionary = set(word.lower() for passage in train for word in word_tokenize(passage[0]))
dictExport = pd.DataFrame(dictionary)
dictExport.to_csv("dictExport.csv")
print("dictionary here")
print(dictionary)
print(type(dictionary))
t = [({word: (word in word_tokenize(x[0])) for word in dictionary}, x[1]) for x in train]

tTest = [({word: (word in word_tokenize(x[0])) for word in dictionary}, x[1]) for x in test]
print('tTest is below')
print(tTest[:1])
classifier = nltk.NaiveBayesClassifier.train(t)


#added trying to check classifier accuracy
print("Naive Bayes Algo Accuracy Percent:", (nltk.classify.accuracy(classifier, tTest))*100)



#### sample
sample = training.sample(frac = .1, random_state = 147)
sample = pd.DataFrame(sample)
sample = sample.reset_index(drop=True)
sample['sentence'] = sample['sentence'].str.replace("[^\w\s]", "").str.lower()
sample['sentence'] = sample['sentence'].apply(lambda x: ' '.join([item for item in x.split() if item not in stop_words]))
sample['sentenceLemmatized'] = sample.sentence.apply(lemmatize_text)
sample = pd.DataFrame(sample)
sample['sentenceLemmatized'] = [','.join(map(str, l)) for l in sample['sentenceLemmatized']]
sample['sentenceLemmatized'] = sample['sentenceLemmatized'].str.replace(',', ' ')
sample = sample.drop(['sentiment'], axis=1)
sample = sample[['sentenceLemmatized']].apply(tuple, axis=1)
print("sample below")
print(sample[:10])
#print(list(sample.columns.values))
print(sample.head())


sampleFeatures = [({word: (word in word_tokenize(x[0])) for word in dictionary}) for x in sample]
print("sampleFeatures")
print(sampleFeatures[:1])
print("sample classification below")
sampleWords = "these are sample words to classify but we don't like cheese"
print(classifier.classify_many(sampleFeatures))
saved_model = pickle.dumps(classifier)
pickle.dump(classifier, open("naiveBayesModel.p", "wb"))

naiveBayes = pickle.load(open("naiveBayesModel.p", "rb"))
results = (naiveBayes.classify_many(sampleFeatures))
sampleDf = pd.DataFrame(sample)
sampleDf['results'] = results
sampleDf.to_csv(r'C:/Users/jcooke/PycharmProjects/qualtrics/sampleDf.csv')


dictionarySample = set(word.lower() for passage in sample for word in word_tokenize(passage[0]))
#dictionaryt = {word ()}
dictionaryt = [({word: (word in word_tokenize(x[0])) for word in dictionarySample}, x[1]) for x in sample]
test_sent_features = {word: (word in word_tokenize(test_sentence.lower())) for word in all_words}
print('dictionary tttttttttt')
print(dictionaryt[:10])



print(classifier.classify(sampleFeatures))




saved_model = pickle.dumps(classifier)

naiveBayes = pickle.loads(saved_model)

#print(naiveBayes.classify(tTest))



#for x in test:
 #   word_tokenize(x) for word in dictionary
  #  word: word in word_tokenize(test) for word in dictionary

#test_data_features = [x.lower() for x in test]
#test = lower(test)
#test = [x.lower() for x in test]
#test_data_features = [[word.lower() for word in text.split()] for text in test]
test = pd.DataFrame(test)
#added below
test = [word.lower() for word in test]
#print("test dataframe")
#print(test)
#commented out below and added line below that then commented out
#test = test[['sentenceLemmatized', 'sentiment']].apply(tuple, axis=1)
test = test.apply(tuple, axis=1)
#print(dir(test))
test_data_features = [word.lower() for word in test]
#print('lowercase')
#print(test_data_features)
test_data_features = [word_tokenize(word) for word in test]
#print('tokenized lower')
#print(test_data_features)
#test_data_features = {word.lower(): (word in word_tokenize(test.lower())) for word in dictionary}
#test_data_features = [({word: (word in word_tokenize(x[0])) for word in dictionary}, x[1]) for x in test]
#_data_features = {word: (word in word_tokenize(test)) for word in dictionary}
#for x in test:
 #   print(classifier.classify(test))
#print("test_data_features")
#print(test_data_features)
#print('classifier result')
#print(classifier.classify(test_data_features))
#t1 = test.classifier.classify()
#print(t1)
#print(classifier.classify_many(test))
classifier.show_most_informative_features(20)
#print('train items')
#print(train['sentence'])
#end create training and test

#q29Sent_DFResponse = q29Sent_DF["responseID"].tolist()
#print(q29Sent_DF)

sid = SentimentIntensityAnalyzer()

column_names = {'start_date','responseID', 'sentence', 'compound', 'neg', 'neu', 'pos', 'question'}
column_index = ['start_date', 'responseID', 'sentence', 'compound', 'neg', 'neu', 'pos', 'question']
d = pd.DataFrame(columns = column_names)
d = d.reindex(columns=column_index)
columns = column_index
data = []
for start_date, sentence, responseID, question in zip(q29Sent_DF['start_date'], q29Sent_DF['sentence'], q29Sent_DF['responseID'], q29Sent_DF['question']):
     ss = sid.polarity_scores(sentence)
     values = start_date, responseID, sentence, ss["compound"], ss["neg"], ss["neu"], ss["pos"], question
     zipped = zip(columns, values)
     a_dictionary = dict(zipped)
     data.append(a_dictionary)

d = d.append(data, True)
dataQ29 = d



#end sentence analysis for q29
#begin sentence analysis for q3

q3Sent = df.iloc[:, [0,6,58]]
sentences = []
for row in q3Sent.itertuples():
    for sentence in sent_tokenize(row[2]):
        sentences.append((row[1], sentence))
q3Sent_DF = pd.DataFrame(sentences, columns=['responseID', 'sentence'])
q3Sent_DF["question"] = "q3"
#q29Sent_DFResponse = q29Sent_DF["responseID"].tolist()
#print(q3Sent_DF)

sid = SentimentIntensityAnalyzer()

column_names = {'responseID', 'sentence', 'compound', 'neg', 'neu', 'pos', 'question'}
column_index = ['responseID', 'sentence', 'compound', 'neg', 'neu', 'pos', 'question']
d = pd.DataFrame(columns = column_names)
d = d.reindex(columns=column_index)
columns = column_index
data = []
for sentence, responseID, question in zip(q3Sent_DF['sentence'], q3Sent_DF['responseID'], q3Sent_DF['question']):
     ss = sid.polarity_scores(sentence)
     values = responseID, sentence, ss["compound"], ss["neg"], ss["neu"], ss["pos"], question
     zipped = zip(columns, values)
     a_dictionary = dict(zipped)
     data.append(a_dictionary)

d = d.append(data, True)
dataQ3 = d

#end sentence analysis for q3
#begin sentence analysis for q89

q83Sent = df.iloc[:, [6,59]]
sentences = []
for row in q83Sent.itertuples():
    for sentence in sent_tokenize(row[2]):
        sentences.append((row[1], sentence))
q83Sent_DF = pd.DataFrame(sentences, columns=['responseID', 'sentence'])
q83Sent_DF["question"] = "q83"
#q29Sent_DFResponse = q29Sent_DF["responseID"].tolist()
#print(q83Sent_DF)

sid = SentimentIntensityAnalyzer()

column_names = {'responseID', 'sentence', 'compound', 'neg', 'neu', 'pos', 'question'}
column_index = ['responseID', 'sentence', 'compound', 'neg', 'neu', 'pos', 'question']
d = pd.DataFrame(columns = column_names)
d = d.reindex(columns=column_index)
columns = column_index
data = []
for sentence, responseID, question in zip(q83Sent_DF['sentence'], q83Sent_DF['responseID'], q83Sent_DF['question']):
     ss = sid.polarity_scores(sentence)
     values = responseID, sentence, ss["compound"], ss["neg"], ss["neu"], ss["pos"], question
     zipped = zip(columns, values)
     a_dictionary = dict(zipped)
     data.append(a_dictionary)

d = d.append(data, True)
dataQ83 = d

#print(dataQ29)
#print(dataQ3)
#print(dataQ83)

#Join all sentence dataframes together

frames = [dataQ29, dataQ3, dataQ83]

finalDF = pd.concat(frames)

finalDF = finalDF[(finalDF["compound"] + finalDF["neg"] + finalDF["neu"] + finalDF["pos"]) != 0]
#finalDF['date'] =



#export csv
finalDF.to_csv(r'C:/Users/jcooke/PycharmProjects/qualtrics/out.csv')



#i dunno
df.to_csv("dfOutput.csv", index = False, header = True)


'''
#upload data to bigquery
# Construct a BigQuery client object.
client = bigquery.Client()
# TODO(developer): Set table_id to the ID of the table to create.
# table_id = "your-project.your_dataset.your_table_name"
table_id = "nu-skin-corp.REPORTING.DIST_TOOLS"
job_config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.CSV, skip_leading_rows=1, autodetect=True,
)
with open(file_path, "rb") as source_file:
    job = client.load_table_from_file(source_file, table_id, job_config=job_config)
job.result()  # Waits for the job to complete.
table = client.get_table(table_id)  # Make an API request.
print(
    "Loaded {} rows and {} columns to {}".format(
        table.num_rows, len(table.schema), table_id
    )
)
'''