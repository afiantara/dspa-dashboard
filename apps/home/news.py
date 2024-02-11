from duckduckgo_search import DDGS
import pandas as pd
import matplotlib.pyplot as plt

#initialize to store the result of searching
results=[]
keywords =['"warnaartha life"','"asuransi"']
    #,'"Pertumbuhan premi"','"Tingkat penetrasi"','"Kinerja perusahaan"','"Regulasi"','"Inovasi produk"']

def drawit(df):
    import plotly.express as px
    # Use directly Columns as argument. You can use tab completion for this!
    fig = px.scatter(x=df.date, y=df.title, labels={'x':'News Timeline', 'y':'Title'}) # override keyword names with labels
    fig.show()

def sentiment_analysis(df,model,cat):
    from transformers import pipeline
    from tensorflow.python.keras.engine import data_adapter
    df2 = df.copy()
    df2['date'] = pd.to_datetime(df2['date']).dt.date
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
    #print(df_analysis)

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
    df['date']=pd.to_datetime(df['date'])
    df=df.sort_values(by='date')
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

def plotly_visualize(df):
    import plotly.express as px
    fig = px.scatter(df, x="date", y="title")
    fig.show()

if __name__=="__main__":
    df = getnews()
    plotly_visualize(df)

    #drawit(df)
    #sentiment_analysis(df)
    


    
    

