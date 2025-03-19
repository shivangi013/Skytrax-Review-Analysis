import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import numpy as np

url = 'https://www.airlinequality.com/'

page = requests.get(url)

soup = BeautifulSoup(page.text, 'html')
reviews = soup.find_all('div', class_='body')[0:3]
links =[]

for review in reviews:
links.append(review.find('a').get('href'))

# Function to extract Customer Name
def get_name(soup):
  try:
    # Outer Tag Object
    name = soup.find("span", attrs={"itemprop":'name'}).text.strip()
  except AttributeError:
    name = ""
  return name
  
def get_date(soup):
  trs = soup.find_all("tr")
  for tr in trs:
  try:
    redate = tr.find("td", class_="review-rating-header date_flown")
    if redate.text == "Date Flown":
    date = tr.find("td", class_="review-value").text
  else :
    continue
  except AttributeError:
    continue
  try:
    return date
  except:
    return ""
    
# Function to extract Customer Rating
def get_rating(soup):
  try:
    rating = soup.find("span", attrs={'itemprop':'ratingValue'}).text.strip()
    
  except AttributeError:
    rating = ""
  return rating
  
# Function to extract seat type
def get_seat_type(soup):
  trs = soup.find_all("tr")
  for tr in trs:
    try:
      redate = tr.find("td", class_="review-rating-header cabin_flown")
      if redate.text == "Seat Type":
        seat_type = tr.find("td", class_="review-value").text
      else :
        continue
    except AttributeError:
      continue
  try:
    return seat_type
  except:
    return ""

# Function to extract Customer Reviews
def get_reviews(soup):
  try:
    review_count = soup.find("h2", attrs={'class':'text_header'}).string.strip()
  except AttributeError:
    review_count = ""
  return review_count

# Function to extract recomendation
def get_recommended(soup):
  try:
    available = soup.find_all("tr")[-1].find("td", class_="review-value rating-no").text
  except AttributeError:
    try:
      available = soup.find_all("tr")[-1].find("td", class_="review-value rating-yes").text
    except AttributeError:
      available = "Not Available"
  return available

# Function to extract type of traveller
def get_type_of_traveller(soup):
  trs = soup.find_all("tr")
  for tr in trs:
    try:
      redate = tr.find("td", class_="review-rating-header type_of_traveller")
      if redate.text == "Type Of Traveller":
        type_of_traveller = tr.find("td", attrs={'class':"review-value"}).text
      else :
        continue
    except AttributeError:
      continue
  try:
    return type_of_traveller
  except:
    return ""

# Function to extract Route
def get_route(soup):
  trs = soup.find_all("tr")
  for tr in trs:
    try:
      redate = tr.find("td", class_="review-rating-header route")
      if redate.text == "Route":
        route = tr.find("td", class_="review-value").text
      else :
        continue
    except AttributeError:
      continue
  try:
    return route
  except:
    return ""


d = {"Name":[], "Date Flown":[], "Rating":[], "Type Of Traveller":[], "Seat Type":[], "Route":[], "Recommended":[], "Reviews":[]}
# Loop for extracting product details from each link
for link in links:
  new_webpage = requests.get( "https://www.airlinequality.com" + link +"/?sortby=post_date%3ADesc&pagesize=100")
  new_soup = BeautifulSoup(new_webpage.content, "html.parser")
  new_articles = new_soup.find("article", attrs={'class':"comp comp_reviews-pagination querylist-paginationposition-"})
  
  review_count =int(new_soup.find('div', attrs={'class':"review-count"}).find('span', attrs={'itemprop':"reviewCount"}).text)
  
  if(int(review_count/100) !=0):
    new_links = new_articles.find_all('a')[0:6]
  for new_link in new_links:
    next_webpage = requests.get("https://www.airlinequality.com"+ new_link.get('href'))
    next_soup = BeautifulSoup(next_webpage.content,"html.parser")
    next_articles = next_soup.find_all("article", attrs={'itemprop':"review"})
    
    for article in next_articles:
      rating = article.find("div", attrs={'itemprop':"reviewRating"})
      review = article.find("div", class_='body')
      
      d['Name'].append(get_name(review))
      d['Date Flown'].append(get_date(review))
      d['Seat Type'].append(get_seat_type(review))
      d['Reviews'].append(get_reviews(review))
      d['Recommended'].append(get_recommended(review))
      d['Rating'].append(get_rating(rating))
      d['Type Of Traveller'].append(get_type_of_traveller(review))
      d['Route'].append(get_route(review))

british_Airways_df = pd.DataFrame.from_dict(d)
british_Airways_df['Name'].replace('', np.nan, inplace=True)
british_Airways_df = british_Airways_df.dropna(subset=['Name'])
british_Airways_df.to_csv("british_Airways_data.csv", index=False)
