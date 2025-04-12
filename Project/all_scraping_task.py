import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objs as go
import plotly.express as px
import plotly.figure_factory as ff
from nltk.corpus import stopwords
from wordcloud import WordCloud
import numpy as np 
import pandas as pd 
import random as rn
import re
import nltk
import os
import emoji
from transformers import pipeline,AutoTokenizer, AutoModelForSequenceClassification
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import pandas as pd
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.chrome.options import Options
from langdetect import detect, LangDetectException

PROCESSED_FOLDER = r'files_folder\files_processed'
driver_path = r'chromedriver_win32\chromedriver.exe'
num_pages_goodreads = 2
num_scroll_down_storygraph = 3
model = AutoModelForSequenceClassification.from_pretrained(r'E:\GradProject\FLASK\code\models\text_classification',local_files_only = True)
tokenizer = AutoTokenizer.from_pretrained(r'E:\GradProject\FLASK\code\models\text_classification',local_files_only = True)

# _________________________________________scraping _____________________________
def is_english(text, default='unknown'):
    try:
        lang = detect(text)
    except LangDetectException:
        lang = default
    return lang

# def init_driver(web, path):
#     chrome_options = Options()
#     chrome_options.add_experimental_option("detach", True)
#     driver = webdriver.Chrome(chrome_options)  # add the "options" argument to make sure the changes are applied
#     driver.get(web)
#     time.sleep(2)
#     driver.get(web)
#     return driver 
def init_driver(web):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # تمت إضافة هذا السطر لتشغيل Chrome في وضع Headless
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)  # تمت إضافة خيارات Chrome هنا
    driver.get(web)
    time.sleep(2)
    driver.get(web)
    return driver


def click_more_reviews_and_ratings_button(xpath, driver):
    # locate and click on a button
    all_reviews_button = driver.find_element(By.XPATH, xpath)
    href_link = all_reviews_button.get_attribute("href")
    # Open the URL in the webdriver
    driver.get(href_link)
    time.sleep(2)
    driver.get(href_link)
    return driver

def click_show_more_reviews_button(xpath, num_pages, driver):
    # locate and click on a button
    for i in range (0,num_pages):
        element = driver.find_element(By.XPATH , xpath)
        # all_matches_button = element.find_element(By.XPATH, xpath)
        time.sleep(2)
        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.execute_script("arguments[0].click();", element)
        time.sleep(2)
        # all_matches_button.click()
        time.sleep(2)

def extract_reviews(xpath, driver):
    reviews = driver.find_elements(By.XPATH, xpath)
    return reviews


def check_reviews(reviews):
    reviews_list = []
    for review in reviews: 
        print(review.text)
        english_review = is_english(review.text)
        if (len(review.text) <= 512) and (english_review): 
            reviews_list.append(review.text)
    return reviews_list

def all_reviews_button_SG(xpath, driver):
    all_reviews_button = driver.find_element(By.XPATH, xpath)
    # get href link from the button
    return(all_reviews_button.get_attribute("href")) 

def show_reviews_with_explanation(driver):
    # Find the checkbox input tag by its name attribute
    checkbox = driver.find_element(By.NAME, "explanation_reviews_only")
    # Click on the checkbox
    time.sleep(5)
    checkbox.click()
    time.sleep(5)

def scroll_down(num_times, driver):
    # Scroll down the page multiple times to load more reviews
    for i in range(num_times): # Adjust the number of times to scroll down
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        time.sleep(2) # Add a wait time to allow the page to load
        # driver.implicitly_wait(10)








# _________________________________________cleeaning text and applying the model _____________________________


#  Function to remove emoji
def deEmojify(text):
    """Remove all emoji characters from the given text"""
    return emoji.demojize(text, delimiters=("", ""))

# Clean some basic characters
def clean(raw):
    """ Remove hyperlinks and markup """
    result = re.sub("<[a][^>]*>(.+?)</[a]>", 'Link.', raw)
    # matches the HTML entity for the greater than symbol > and replaces it with an empty string.
    result = re.sub('&gt;', "", result)
    # matches the HTML entity for the single quote character ' and replaces it with a regular single quote character.
    result = re.sub('&#x27;', "'", result)
    # matches the HTML entity for the double quote character " and replaces it with a regular double quote character.
    result = re.sub('&quot;', '"', result)
    # matches the HTML entity for the forward slash character / and replaces it with a space.
    result = re.sub('&#x2F;', ' ', result)
    # This regular expression matches the HTML paragraph tag <p> and replaces it with a space.
    result = re.sub('<p>', ' ', result)
    # matches the closing italic tag </i> and replaces it with an empty string.
    result = re.sub('</i>', '', result)
    # matches the HTML entity for the greater than symbol > and replaces it with an empty string.
    result = re.sub('&#62;', '', result)
    # matches the italic tag <i> and replaces it with a space.
    result = re.sub('<i>', ' ', result)
    # matches any newline characters and replaces them with a space.
    result = re.sub("\n", ' ', result)
    # Remove non-alphanumeric characters
    result = re.sub(r'[^\w\s]', ' ', result)   
    # Remove digits
    result = re.sub(r'\d+', ' ', result)
    # Remove non-ASCII characters
    result = re.sub(r'[^\x00-\x7F]+', ' ', result)
    # Remove non-alphanumeric characters except for sentence-ending punctuation marks
    review = re.sub(r'[^\w\s\.\?\!]', '', result)
    # Remove duplicate words
    result = re.sub(r'(\b\w+\b)(?=.*\b\1\b)', r'\1', result)
        
    # Replace consecutive whitespace characters with a single space
    result = re.sub(r'\s+', ' ', result)
    return result


# Remove numeric
def remove_num(texts):
    output = re.sub(r'\d+', ' ', texts )
    return output


# function to unify whitespaces
def unify_whitespaces(text):
    cleaned_string = re.sub(' +', ' ', text )
    return cleaned_string

# function to remove punctuation
def remove_punctuation(text):
    result = "".join(u for u in text if u not in ("?", ".", ";", ":",  "!",'"',',') )
    return result


# Aplying all the cleaning util methods
def cleaning(df, review):
    df_processed = df.copy()
    df_processed[review] = df_processed['reviews']
    df_processed[review] = df_processed[review].apply(clean)
    df_processed[review] = df_processed[review].apply(deEmojify)
    df_processed[review] = df_processed[review].apply(remove_num)
    df_processed[review] = df_processed[review].apply(remove_punctuation)
    return df_processed

def ploting(labels, values, output_graph_path):
    # create a pie chart
    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
        # Update the layout to set plot_bgcolor and paper_bgcolor
    fig.update_layout(
        plot_bgcolor='rgba(255, 99, 71, 0)',  # Set the background color of the plot area
        paper_bgcolor= 'rgba(255, 99, 71, 0)' , # Set the background color of the entire plot
        font=dict(family='Arial', size=14, color='white') # Set the font properties of the plot

    )

    # set the chart title
    fig.update_layout(title='Reviews Emotions Distribution')

    # show the chart
    fig.show()

    # save the chart as an HTML file
    fig.write_html(output_graph_path)

def main(storygraph_web_path, goodreads_web_path, goodreads_output_path, storygraph_output_path, storygraph_CSV_path, goodreads_CSV_path,output_graph_path ):   
  # ______________________________Start Of Scraping____________________________________
        ## --------------------------- GoodReads ------------------------------
    driver = init_driver(goodreads_web_path)
    time.sleep(3)
    # driver.implicitly_wait(10)
    xpath_of_more_reviews_button = "//div [@class = 'BookPage__reviewsSection']//div [@id ='ReviewsSection'] //div[@class = 'ReviewsList']//a [@class = 'Button Button--transparent Button--small']"
    driver = click_more_reviews_and_ratings_button(xpath_of_more_reviews_button , driver)
    # wait for the page to load completely
    time.sleep(3)

    xpath_of_show_more_reviews_button = "//div [@class ='BookReviewsPage__rightColumn']//div[@class = 'ReviewsList']//div[@class = 'Divider Divider--contents Divider--largeMargin']//div[@class = 'Button__container']//button[@type = 'button']"
    click_show_more_reviews_button(xpath_of_show_more_reviews_button,num_pages_goodreads , driver)

    xpath_of_reviews_text = "//div[@class = 'ReviewsList']//article[@class='ReviewCard']//section[@class = 'ReviewCard__content']//section[@class ='ReviewText']//span[@class = 'Formatted']"
    # Extract the reviews
    reviews = extract_reviews(xpath_of_reviews_text, driver)
    valid_reviews = check_reviews(reviews)
    # Create Dataframe in Pandas and export to CSV (Excel)
    df_goodreads = pd.DataFrame({'reviews': valid_reviews})
    df_goodreads.to_csv(goodreads_output_path, index=False)
    driver.quit()
    ## --------------------------- GoodReads ------------------------------


    ## --------------------------- the story graph ------------------------------
    driver = init_driver(storygraph_web_path)
    xpath = "//div [@class = 'hidden md:block container mx-auto max-w-6xl my-6']//h3//span//a[@class = 'standard-link font-medium uppercase border-b' ]"
    href_link = all_reviews_button_SG(xpath, driver)
    # Open the URL in the webdriver
    driver.get(href_link)
    show_reviews_with_explanation(driver)
    # Scroll down the page multiple times to load more reviews
    scroll_down(num_scroll_down_storygraph, driver)
    xpath = "//span[@class='review-panes']//div[@class='trix-content review-explanation']"
    reviews = extract_reviews(xpath, driver)
    valid_reviews = check_reviews(reviews)
    # Create Dataframe in Pandas and export to CSV (Excel)
    df_storygraph = pd.DataFrame({'reviews': valid_reviews})
    df_storygraph.to_csv(storygraph_output_path, index=False)
    driver.quit()
    ## --------------------------- the story graph ------------------------------

  # ______________________________End Of Scraping____________________________________








  # ______________________________Start Of Cleaning and apply model____________________________________

    df_storygraph = pd.read_csv(storygraph_CSV_path)
    df_goodreads = pd.read_csv(goodreads_CSV_path)
    
    # merge two dataframes 
    frames = [df_goodreads, df_storygraph]
    df_reviews = pd.concat(frames)
    df_reviews['reviews'] = df_reviews['reviews'].astype(str)
        
    # drop NaN values
    df_reviews.dropna(inplace=True)

    # data cleaning 
    df_processed = cleaning(df_reviews, 'review_text_clean' )

    # delete all nan values 
    df_processed  = df_processed[~df_processed.review_text_clean.isin(['nan'])]


    # initiate the pipeline of the model 
    classifier = pipeline("text-classification", model=model,tokenizer=tokenizer, return_all_scores=True, device = "cpu")

    # apply model 
    emotions_list = classifier(df_processed.review_text_clean.to_list())

    # get the summation score of each emotion throughout all reviews   
    sum_values = {"anger" : 0, "disgust" : 0, "joy" : 0, "neutral" : 0, "fear" : 0, "surprise" : 0, "sadness" : 0}

    print(emotions_list)
    for i in range(len(emotions_list)):
        for j in range(7):
            sum_values[list(emotions_list[i][j].values())[0]] += list(emotions_list[i][j].values())[1]

    # calculate the percentage
    for key, value in sum_values.items():
      sum_values[key] = ( value/len(emotions_list) ) * 100


    # create a list of labels and values from the dictionary
    labels = list(sum_values.keys())
    values = list(sum_values.values())
    ploting(labels, values, output_graph_path)


  # ______________________________End Of Cleaning and apply model____________________________________

def get_output_path(req_id):
    target_folder = None
    output_graph_path = None
    for folder in os.listdir(PROCESSED_FOLDER):
        if folder.startswith(str(req_id)):
            target_folder = os.path.join(PROCESSED_FOLDER, folder)
            break

    folder_for_csv = os.path.join(target_folder, 'needed_files')
    output_graph_path = os.path.join(target_folder,"needed_files")
    return folder_for_csv, output_graph_path


#folder_csv, output_graph_path = get_output_path(19)
#goodreads_web_path = "https://www.goodreads.com/book/show/6969.Emma"
#storygraph_web_path = "https://app.thestorygraph.com/books/db5bad36-6dc5-4404-a8f9-1cdbe388ec39"
#goodreads_output_path = os.path.join(folder_csv, 'goodreads_reviews.csv')
#storygraph_output_path = os.path.join(folder_csv, 'storygraph_reviews.csv')
#storygraph_CSV_path = os.path.join(folder_csv, 'storygraph_reviews.csv')
#goodreads_CSV_path = os.path.join(folder_csv, 'goodreads_reviews.csv')
#output_graph_path = os.path.join(output_graph_path, 'Reviews_emotions.html')
#main(storygraph_web_path, goodreads_web_path, driver_path, goodreads_output_path, storygraph_output_path, storygraph_CSV_path, goodreads_CSV_path, output_graph_path)

good_reads = "https://www.goodreads.com/book/show/8127.Anne_of_Green_Gables?ac=1&from_search=true&qid=RuWs29asMe&rank=1"
story_graph = "https://app.thestorygraph.com/books/e7ea7691-7137-4af6-b36a-301ada49e5b3"

def run_scraping_task(req_id,goodreads_web_path = None,storygraph_web_path = None):
    folder_csv, output_graph_path = get_output_path(str(req_id))
    goodreads_output_path = os.path.join(folder_csv, 'goodreads_reviews.csv')
    storygraph_output_path = os.path.join(folder_csv, 'storygraph_reviews.csv')
    storygraph_CSV_path = os.path.join(folder_csv, 'storygraph_reviews.csv')
    goodreads_CSV_path = os.path.join(folder_csv, 'goodreads_reviews.csv')
    output_graph_path = os.path.join(output_graph_path, 'Reviews_emotions.html')
    main(storygraph_web_path, goodreads_web_path, goodreads_output_path, storygraph_output_path, storygraph_CSV_path, goodreads_CSV_path, output_graph_path)




