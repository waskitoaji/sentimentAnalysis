#!/usr/bin/env python
# coding: utf-8

# In[8]:


# nama : waskito aji
# email : waskitoaji46@gmail.com


# In[1]:


def auth():
    import tweepy
    #change with data from your twitter developer account
    consumer_key = "your_twitter_consumer_key"
    consumer_secret = "your_twitter_consumer_secretkey"
    access_token = "your_twitter_access_token"
    access_token_secret = "your_twitter_access_token_secret"
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    return api


# In[2]:


def updateData():
    import tweepy
    import re
    import pandas as pd
    from datetime import datetime, timedelta
    from nltk.tokenize import word_tokenize
    from string import punctuation
    import sqlite3
    
    d = datetime.today() - timedelta(days=2)
    date=d.strftime("%Y-%m-%d")
    api=auth()
    #keyword='jouska'
    keyword='vaksin covid OR vaksin COVID OR Vaksin Covid OR Vaksin COVID OR vaksin korona OR vaksin COVID-19 OR vaksin covid-19'
    new_search = keyword + " -filter:retweets"
    tweets = tweepy.Cursor(api.search, q=new_search, lang="id", since=date,tweet_mode='extended').items() 
    items = []
    for tweet in tweets:
        item = []
        item.append (tweet.user.screen_name)
        item.append (tweet.created_at)
        teks=tweet.full_text
        #case folding
        teks=teks.lower()
        #remove punctuation
        tokens=word_tokenize(teks)
        tokens=[token for token in tokens if token not in punctuation]
        gabung=' '.join(tokens)
        #===================
        item.append (' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", gabung).split()))
        initSen=0
        item.append(initSen)
        items.append(item)
    hasil = pd.DataFrame(data=items, columns=['user', 'date', 'tweet','sentimen'])
    #sql
    conn= sqlite3.connect('finalprojectDB.db')
    c = conn.cursor()
    hasil.to_sql('tweetData', conn, if_exists='append', index=False)
    #filter data sama
    df=pd.read_sql('select * from tweetData', conn)
    df=df.drop_duplicates(subset=['user','date','tweet'], keep='first')
    df.to_sql('tweetData', conn, if_exists='replace', index=False)
    print('jumlah data: ', len(items))
    print('data sudah berhasil update')
    return df
    
    


# In[3]:


def UpdateSentimen():
    import pandas as pd
    import sqlite3

    conn= sqlite3.connect('finalprojectDB.db')
    c = conn.cursor()
    df=pd.read_sql('select * from tweetData', conn)

    tweets=df[['tweet']]
    sentimen=[]
    for i in range(len(tweets)) : 
        tweet=df.loc[i, "tweet"]

        pos_list= open("data/kata_positif.txt","r")
        pos_kata = pos_list.readlines()
        neg_list= open("data/kata_negatif.txt","r")
        neg_kata = neg_list.readlines()

        count_p = 0
        count_n = 0
        for kata_pos in pos_kata:
            if kata_pos.strip() in tweet:
                count_p +=1
        for kata_neg in neg_kata:
            if kata_neg.strip() in tweet:
                count_n +=1
        nilai=count_p-count_n
        #print ("positif: "+str(count_p))
        #print ("negatif: "+str(count_n))
        sentimen.append(nilai)

        #print ("-----------------------------------------------------")
    df=df.drop(df.columns[3], axis=1)
    df['sentimen']=sentimen
    df.tail()
    df.to_sql('tweetData', conn, if_exists='replace', index=False)
    print('berhasil melakukan update sentimen')


# In[4]:


def LihatData(startDate,endDate):
    import pandas as pd
    import sqlite3
    conn= sqlite3.connect('finalprojectDB.db')
    c = conn.cursor()
    df=pd.read_sql('select * from tweetData', conn)

    c.execute("select user,date,tweet from tweetData where date >= ? and date <= ?",(startDate,endDate,))
    hsl=c.fetchall()
    hsl= pd.DataFrame(data=hsl, columns=['user','date','tweet'])
    return hsl


# In[5]:


def Visualisasi(startDate,endDate):
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import sqlite3

    conn= sqlite3.connect('finalprojectDB.db')
    c = conn.cursor()
    df=pd.read_sql('select * from tweetData', conn)

    c.execute("select * from tweetData where date >= ? and date <= ?",(startDate,endDate,))
    hsl=c.fetchall()
    hsl= pd.DataFrame(data=hsl, columns=['user','date','tweet','sentimen'])
    X=df[['sentimen']]
    X.head()
    sentimens=np.array(X,dtype='int64')
    print ("Nilai rata-rata: "+str(np.mean(sentimens)))
    print ("Standar deviasi: "+str(np.std(sentimens)))
    print ("median: "+str(np.median(sentimens)))
    labels, counts = np.unique(sentimens, return_counts=True)
    plt.bar(labels, counts, align='center')
    plt.ylabel('jumlah')
    plt.xlabel('nilai sentimen')
    plt.gca().set_xticks(labels)
    plt.title('grafik sentimen tweet')
    plt.show()


# In[6]:


def FinalProject():
    print("Apa yang anda ingin lakukan")
    print("1. update data")
    print("2. update nilai sentimen")
    print("3. lihat data")
    print("4. visualisasi hasil")
    print("5. keluar")
    x = input('   Input anda:')
    if x=='1':
        updateData()
    elif x=='2':
        UpdateSentimen()
    elif x=='3':
        awal = input('dari (yyyy-mm-dd): ')
        akhir = input('sampai(yyyy-mm-dd): ')
        hasil=LihatData(awal,akhir)
        print(hasil)
    elif x=='4':
        awal = input('dari (yyyy-mm-dd): ')
        akhir = input('sampai(yyyy-mm-dd): ')
        Visualisasi(awal,akhir)
    elif x=='5':
        print('keluar dari program')
    else :
        print('input salah')
   


# In[11]:


FinalProject()


# In[ ]:









