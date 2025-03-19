import pandas as pd
british_Airways_df = pd.DataFrame.from_dict(d)
british_Airways_df
# Load the new dataset
new_file_path = "/content/Frontier Airlines.csv"
df_new = pd.read_csv(new_file_path, encoding = 'latin1')
df_new["Reviews"] = df_new["Reviews"].replace("Frontier Airlines customer review"," ")
df_new.to_csv("Frontier Airlines.csv", index=False)

df_new = pd.read_csv('/content/Frontier Airlines.csv', encoding='latin1')
df_new.info(), df_new.head()

import re
# Remove quotes from reviews and strip extra spaces
df_new['Reviews'] = df_new['Reviews'].apply(lambdax: re.sub(r'^"|"$','',str(x)).strip())

# Standardize text columns to lowercase for consistency
text_columns = ["Type of Traveller","Seat Type","Route","Recommended","Reviews"]
df_new[text_columns] = df_new[text_columns].apply(lambdax: x.str.lower())

# Fill missing values in categorical columns with"unknown"
df_new.fillna({"Date Flown":"unknown","Type Of Traveller":"unknown",
               "Seat Type":"unknown","Route":"unknown","Rating": df_new["Rating"].median()}, inplace=True)

# Convert Rating to integer
df_new["Rating"] = df_new["Rating"].astype(int)
# Display sample cleaned data
df_new.head()

from textblob import TextBlob

def get_sentiment(text):
  analysis = TextBlob(text)
  if analysis.sentiment.polarity > 0:
    return "positive"
  elif analysis.sentiment.polarity < 0:
    return "negative"
  else:
    return "neutral"

# Apply sentiment analysis
df_new["Sentiment"] = df_new["Reviews"].apply(get_sentiment)
# Display sentiment distribution
df_new["Sentiment"].value_counts() 

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF # Import NMF

# Re-run TF-IDF with adjusted preprocessing
vectorizer_new = TfidfVectorizer(stop_words="english", max_features=500) # Reduce feature size
tfidf_matrix_new = vectorizer_new.fit_transform(df_new["Reviews"])

# Apply NMF for topic modeling (choosing 3 topics)
nmf_model_new = NMF(n_components=3, random_state=42)
W_new = nmf_model_new.fit_transform(tfidf_matrix_new)
H_new = nmf_model_new.components_

# Extract top words for each topic
words_new = vectorizer_new.get_feature_names_out()
topics_new = {}
for topic_idx, topic in enumerate(H_new):
  top_words = [words_new[i] for i in topic.argsort()[:-6:-1]]  # Top 5 words per topic
  topics_new[f"Topic{topic_idx+1}"] = top_words

# !pip install wordcloud
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# Generate word cloud
wordcloud_new = WordCloud(width=800, height=400, background_color="white", colormap="viridis").generate(" ".join(df_new["Reviews"]))

# Display word cloud
plt.figure(figsize=(10,5))
plt.imshow(wordcloud_new, interpolation="bilinear")
plt.axis("off")
plt.title("Word Cloud of Customer Reviews", fontsize=14)
plt.show()

import pandas as pd
from collections import Counter

# Apply TF-IDF vectorization with custom stop words
vectorizer = TfidfVectorizer(stop_words="english") # Default English stop words
vectorizer.stop_words_ = vectorizer.get_stop_words() # Add custom words

# Transform the reviews
tfidf_matrix = vectorizer.fit_transform(df_new["Reviews"])

# Get feature names (words) and their frequencies
words = vectorizer.get_feature_names_out()
word_freq = tfidf_matrix.sum(axis=0).A1 # Sum of TF-IDF scores across all documents

# Create a DataFrame of words and their frequencies
word_freq_df = pd.DataFrame({"Word": words,"Frequency": word_freq})

# Get the top 20 most frequent words
top_words = word_freq_df.nlargest(30,"Frequency")

# Plot the frequency chart
plt.figure(figsize=(12,6))
plt.barh(top_words["Word"], top_words["Frequency"], color="skyblue")
plt.xlabel("Frequency")
plt.ylabel("Words")
plt.title("Top 30 Most Frequent Words in Reviews")
plt.gca().invert_yaxis() # Invert y-axis to show highest frequency on top
plt.show()
