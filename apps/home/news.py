from duckduckgo_search import DDGS
import pandas as pd
import matplotlib.pyplot as plt

#initialize to store the result of searching
results=[]
keywords =['"warnaartha life"','"asuransi"']
#db_name='../../datasets/news.db'
db_name='./datasets/news.db'
table_name = "news"
    #,'"Pertumbuhan premi"','"Tingkat penetrasi"','"Kinerja perusahaan"','"Regulasi"','"Inovasi produk"']

def drawit(df):
    import plotly.express as px
    # Use directly Columns as argument. You can use tab completion for this!
    fig = px.scatter(x=df.date, y=df.title, labels={'x':'News Timeline', 'y':'Title'}) # override keyword names with labels
    fig.show()


def sentimen_analisis_shopee():
    from google_play_scraper import Sort, reviews
    from google_play_scraper import app
    import numpy as np

    plt.style.use('ggplot')
    result, continuation_token = reviews(
        'com.shopee.id',
        lang='id', 
        country='id',
        sort=Sort.MOST_RELEVANT, 
        count=10000, 
        filter_score_with= None  
    )

    # Dataframe dengan nama 
    dfs = pd.DataFrame(np.array(result),columns=['review'])
    dfs = dfs.join(pd.DataFrame(dfs.pop('review').tolist()))
    dfs.head()

    from nltk.sentiment import SentimentIntensityAnalyzer
    from tqdm.notebook import tqdm
    import nltk
    
    nltk.downloader.download('vader_lexicon')
    sia = SentimentIntensityAnalyzer()

    # Run the polarity score on the entire dataset
    res = {}
    for i, row in tqdm(dfs.iterrows(), total=len(dfs)):
        text = row['content']
        myid = row['reviewId']
        res[myid] = sia.polarity_scores(text)

    vaders = pd.DataFrame(res).T
    vaders.reset_index()
    vaders = vaders.reset_index().rename(columns={'index': 'reviewId'})
    vaders = vaders.merge(dfs, how='left')

    vaders['sentiment'] = np.where(vaders['compound']>0.2 , 'Positive',
                                np.where(vaders['compound']<0 , 'Negative', 'Neutral'))
    ax = vaders['sentiment'].value_counts().sort_index() \
        .plot(kind='bar',
            title='Shopee Review Sentiment',
            figsize=(5, 5))
    ax.set_xlabel('Review Sentiment')
    plt.show()



def sentimen_analisis_NPN_Roberta(df):
    from transformers import AutoTokenizer
    from transformers import AutoModelForSequenceClassification
    from scipy.special import softmax
    from nltk.sentiment import SentimentIntensityAnalyzer
    from tqdm.notebook import tqdm
    import nltk

    import uuid
    import numpy as np
    

    MODEL = f"cardiffnlp/twitter-roberta-base-sentiment"
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL)

    def polarity_scores_roberta(example):
        encoded_text = tokenizer(example, return_tensors='pt')
        output = model(**encoded_text)
        scores = output[0][0].detach().numpy()
        scores = softmax(scores)
        scores_dict = {
            'roberta_neg' : scores[0],
            'roberta_neu' : scores[1],
            'roberta_pos' : scores[2]
        }
        return scores_dict

    dfs = df.copy()
    dfs['uuid'] = [uuid.uuid4() for _ in range(len(dfs.index))]
    dfs.insert(0, 'uuid', dfs.pop('uuid'))

    # Run the polarity score on the entire dataset
    res = {}
    for i, row in tqdm(dfs.iterrows(), total=len(dfs)):
        text = row['body']
        myid = row['uuid']
        res[myid] = polarity_scores_roberta(text)

    vaders = pd.DataFrame(res).T
    vaders.reset_index()
    vaders = vaders.reset_index().rename(columns={'index': 'uuid'})
    print(vaders)
    vaders = vaders.merge(dfs, how='left')
    vaders['sentiment'] = np.where(vaders['compound']==0 , 'Neutral',
                                np.where(vaders['compound']< 0 , 'Negative', 'Positive'))
    
    save_to_db(vaders,'./datasets/news_analysis.db','news_analisis')
    return vaders

def sentimen_analisis_NPN(df):
    from nltk.sentiment import SentimentIntensityAnalyzer
    from tqdm.notebook import tqdm
    import nltk
    import uuid
    import numpy as np

    nltk.downloader.download('vader_lexicon')
    sia = SentimentIntensityAnalyzer()

    dfs = df.copy()
    dfs['uuid'] = [uuid.uuid4() for _ in range(len(dfs.index))]
    dfs.insert(0, 'uuid', dfs.pop('uuid'))

    # Run the polarity score on the entire dataset
    res = {}
    for i, row in tqdm(dfs.iterrows(), total=len(dfs)):
        text = row['body']
        myid = row['uuid']
        res[myid] = sia.polarity_scores(text)

    vaders = pd.DataFrame(res).T
    vaders.reset_index()
    vaders = vaders.reset_index().rename(columns={'index': 'uuid'})
    vaders = vaders.merge(dfs, how='left')
    vaders['sentiment'] = np.where(vaders['compound']==0 , 'Neutral',
                                np.where(vaders['compound']< 0 , 'Negative', 'Positive'))
    
    save_to_db(vaders,'./datasets/news_analysis.db','news_analisis')
    return vaders

def getWordCloudVader(data):

    data['body']=data['body'].astype(str)
    data['body']=data['body'].str.lower()

    import nltk
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    from wordcloud import WordCloud,STOPWORDS
    import json
    import plotly
    import plotly.graph_objs as go

    import re
    import nltk
    import os
    import io
    import base64
    nltk.download('stopwords')
    nltk.download('wordnet')
    nltk.download('omw-1.4')

    #object of WordNetLemmatizer
    lm = WordNetLemmatizer()

    def text_transformation(vaders_col):
        corpus = []
        for item in vaders_col:
            new_item = re.sub('[^a-zA-Z]',' ',str(item))
            new_item = new_item.lower()
            new_item = new_item.split()
            new_item = [lm.lemmatize(word) for word in new_item if word not in set(stopwords.words('indonesian'))]
            corpus.append(' '.join(str(x) for x in new_item))
        return corpus
    corpus = text_transformation(data['body'])
    word_cloud = ""
    for row in corpus:
        for word in row:
            word_cloud+=" ".join(word)

    wordcloud = WordCloud(width = 1000, height = 1000,background_color ='white',max_font_size=256).generate(word_cloud)

    wordcloudImage = wordcloud.to_image()
    img = io.BytesIO()
    wordcloudImage.save(img, format='PNG')
    imgword='data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())
    return imgword

    #plt.imshow(wordcloud)
    #plt.axis('off') # to off the axis of x and y
    #target= os.path.join('apps','static','assets','img','sentiment_news_analisis.png')
    #plt.savefig(target)

def sentiment_analysis(df,model,cat):
    from transformers import pipeline
    from tensorflow.python.keras.engine import data_adapter
    df2 = df.copy()
    
    #df2['date'] = pd.to_datetime(df2['date']).dt.date
    # Group by 'date' (only date part, time ignored) and merge the 'title' text
    df_time_title_merged = df2.groupby('date')['title'].agg(' '.join).reset_index()

    # Rename the columns as per your requirement --> pr pas gabung body tambah titik (belum dikerjakan ini dibawah)
    df_time_title_merged.columns = ['date', 'merged_title']

    # Display the new DataFrame
    #print(df_time_title_merged)

    # Initialize the zero-shot-classification pipeline
    classifier = pipeline("zero-shot-classification", model=model)

    # Candidate labels
    candidate_labels = cat#["Positif", "Negatif", "Netral", "Kecurangan", "kriminal", "hukum", "dana", "korupsi", "adil", "keterbukaan", "kebebasan"]

    analysis_results = []
    for index, row in df_time_title_merged.iterrows():
        sequence_to_classify = row['merged_title']
        output = classifier(sequence_to_classify, candidate_labels, multi_label=True)

        # Extract labels and scores
        label_scores = {label: 0 for label in candidate_labels}  # Initialize all scores to 0
        for label, score in zip(output['labels'], output['scores']):
            label_scores[label] = score

        # Add date and label scores to the results
        analysis_result = {'date': row['date']}
        analysis_result.update(label_scores)
        analysis_results.append(analysis_result)

    # Create a DataFrame from the analysis results
    df_analysis = pd.DataFrame(analysis_results)

    # Display the new DataFrame
    print(df_analysis)

    # Create a new DataFrame to store labels with scores greater than 0.5 ini user masukin
    filtered_labels = []

    for index, row in df_analysis.iterrows():
        labels_above_threshold = [label for label in candidate_labels if row[label] > 0.5]
        filtered_labels.append({
            'date': row['date'],
            'labels': ' '.join(labels_above_threshold)  # Join labels as a single string
        })

        # Convert the list to a DataFrame
    df_filtered = pd.DataFrame(filtered_labels)

    # Display the new DataFrame
    #print(df_filtered)
    
    return getWordCloud(df_filtered)

def getWordCloud(df_filtered):
    from wordcloud import WordCloud
    # Combine all labels into one large string
    all_labels = ' '.join(df_filtered['labels'])

    # Create a WordCloud object
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_labels)
    return wordcloud

def displayworldcloud(wordcoud):
    # Display the word cloud using matplotlib
    import matplotlib.pyplot as plt
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcoud, interpolation='bilinear')
    plt.axis('off')
    plt.show()

def save_to_db(df,db,table):
    import sqlite3
    df.pop('uuid')
    conn = sqlite3.connect('{}'.format(db)) # creates file
    df.to_sql(table, conn, if_exists='replace', index=False) # writes to file

def save_news_to_db(df):
    import sqlite3

    conn = sqlite3.connect('{}'.format(db_name)) # creates file
    df.to_sql(table_name, conn, if_exists='replace', index=False) # writes to file
    

def saveplot(wordcoud,path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcoud, interpolation='bilinear')
    plt.axis('off')
    plt.savefig(path)
    plt.close() 
    
def getnews(kwrds):
    if kwrds:
        keywords=kwrds
        
    with DDGS() as ddgs:
        # text search
        #results = [r for r in ddgs.text("Asuransi Jiwasraya", max_results=100)]
        #print(results)
        #map search
        #for r in ddgs.maps("school", place="Uganda", max_results=50):
        #    print(r)
        #results = [r for r in ddgs.news(keywords,region='id-id',safesearch='off', max_results=20000000)]
        #print(results)
        the_keywords=""
        for keyword in keywords:
            the_keywords+=keyword
        
        print(the_keywords)
        
        ddgs_news_gen =ddgs.news(
            the_keywords,
            region='id-id',
            safesearch='off',
            max_results=20000000
        )
        #make sure to clear results of news
        results.clear()
        for r in ddgs_news_gen:
            results.append({
                'date':r.get('date'),
                'title':r.get('title'),
                'body':r.get('body'),
                'url': r.get('url')
            })
    
    df =pd.DataFrame(results)
    if df.shape[0]!=0:
        df['date']=pd.to_datetime(df['date'])
        df=df.sort_values(by='date')
        save_news_to_db(df)

    return df

def get_news_from_db():
    import sqlite3
    con = sqlite3.connect(db_name)
    query='select * from {}'.format(table_name)
    df=pd.read_sql_query(query, con)
    df["date"] = pd.to_datetime(df["date"])
    #print(df)
    con.close()
    return df

def chart_visualize(df):
    # Dynamically size the figure width and height
    fig_width = max(10, len(df) * 0.8)
    fig_height = max(6, len(df) * 0.3)
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    # Create a scatter plot
    ax.scatter(df['date'], range(len(df)), marker='o')

    # Add labels for each point
    for i, (title, time) in enumerate(zip(df['title'], df['date'])):
        ax.text(time, i, ' '+title, va='center', ha='left', fontsize=8)

    # Set the x-axis major locator and formatter
    #ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    #ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

    # Improve layout to accommodate the labels
    plt.subplots_adjust(bottom=0.2, top=0.95, left=0.05, right=0.95)

    # Rotate date labels
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

    # Set title and y-axis labels
    ax.set_title('News Timeline')
    ax.set_yticks([])
    ax.set_yticklabels([])

    # Show grid for x-axis only
    ax.xaxis.grid(True)
    ax.yaxis.grid(False)

    # Display the plot
    plt.show()

def plotly_visualize(data):
    import json
    import plotly
    import plotly.express as px
    df = pd.DataFrame.from_dict(data)
    fig = px.scatter(df, x="date", y="title")
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def plotly_sentiment_visualize(data):
    import json
    import plotly
    import plotly.express as px
    df = pd.DataFrame.from_dict(data)
    fig = px.bar(df['sentiment'].value_counts().sort_index())
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

if __name__=="__main__":
    df = get_news_from_db()
    #plotly_visualize(df)
    #drawit(df)
    #my_model = {"MoritzLaurer/mDeBERTa-v3-base-mnli-xnli": "tab1", "lxyuan/distilbert-base-multilingual-cased-sentiments-student": "tab2", "bert-base-indonesian-1.5G-finetuned-sentiment-analysis-smsa": "tab3"}
    
    #model='MoritzLaurer/mDeBERTa-v3-base-mnli-xnli'
    #cat=["kecurangan", "kriminal", "hukum", "dana", "korupsi", "keterbukaan", "kebebasan","ketakutan","optimis","masalah","kasus"]
    #wordcloud=sentiment_analysis(df,model,cat)
    #print(wordcloud)
    #displayworldcloud(wordcloud)
    #sentimen_analisis_shopee()
    sentimen_analisis_NPN_Roberta(df)
