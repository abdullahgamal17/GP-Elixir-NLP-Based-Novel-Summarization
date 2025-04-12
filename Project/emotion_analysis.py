import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import pipeline
import plotly
import plotly.graph_objs as go
import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd 
import csv
import json
import plotly.graph_objs as go
import os

PROCESSED_FOLDER = r'files_folder\files_processed'
UPLOAD_FOLDER = r'files_folder\files_received'

words_in_window = 16000
window_size = 4
minimum_quotes = 60
top_ids = 20


# This function split a huge corpus of text into small chunks or portions
def text_chunking(new_text, words_in_chunk):
    # Define the maximum number of words in a chunk
    max_chunk = words_in_chunk
    # Add end of sentence token after each punctuation mark
    new_text = new_text.replace('.', '.<eos>')
    new_text = new_text.replace('?', '?<eos>')
    new_text = new_text.replace('!', '!<eos>')

    # Split the text into sentences using the end of sentence token
    sentences = new_text.split('<eos>')
    # Initialize the current chunk and empty list to store chunks
    current_chunk = 0
    chunks = []

    # Loop through each sentence
    for sentence in sentences:
        # Check if the current sentence can be added to the current chunk
        if len(chunks) == current_chunk + 1:
            if len(chunks[current_chunk]) + len(sentence.split(' ')) <= max_chunk:
                chunks[current_chunk].extend(sentence.split(' '))
            else:
                # If the sentence can't fit in the current chunk, start a new chunk
                current_chunk += 1
                chunks.append(sentence.split(' '))
        else:
            # If there are no chunks or all chunks are full, start a new chunk
            chunks.append(sentence.split(' '))

    # Join the words in each chunk into a single string
    for chunk_id in range(len(chunks)):
        chunks[chunk_id] = ' '.join(chunks[chunk_id])
        
    return chunks



def novel_emotions_classify(emotions_list, chunks):
  model = AutoModelForSequenceClassification.from_pretrained(r'E:\GradProject\FLASK\code\models\zero_shot',local_files_only=True)
  tokenizer = AutoTokenizer.from_pretrained(r'E:\GradProject\FLASK\code\models\zero_shot',local_files_only=True)
  classifier = pipeline("zero-shot-classification", model=model,tokenizer=tokenizer,
                      multi_class=True, device=0 if torch.cuda.is_available() else -1)
  candidate_labels = emotions_list

  emotions_dict = {}  
  for emotion in emotions_list:
      emotions_dict[emotion] = 0
  scores_emo_list = []
  for chunk in chunks:
    result = classifier(chunk, candidate_labels)
    del classifier  # Clear GPU memory of transformers.pipeline
    torch.cuda.empty_cache()
    classifier = pipeline("zero-shot-classification", model=model,tokenizer=tokenizer,
                          multi_class=True, device=0 if torch.cuda.is_available() else -1)
    
    for label in range(len(result["labels"])):
      emotions_dict[result["labels"][label]] += result["scores"][label]

    print("one_chunk : " , result)
    print('All_chunks : ', emotions_dict)
  return emotions_dict



# def novel_emotions_ploting(labels, values, name_of_chart, output_path):
#     # create a pie chart
#   fig = go.Figure(data=[go.Pie(labels=labels, values=values)])

#   # set the chart title
#   fig.update_layout(title=name_of_chart)

#   # show the chart
#   #fig.show()

#   # save the chart as an HTML file
#   fig.write_html(output_path)

def novel_emotions_ploting(labels, values, name_of_chart, output_path):
    # Create a pie chart
    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])

    # Set the chart title
    fig.update_layout(title=name_of_chart)

    # Update the layout to set plot_bgcolor and paper_bgcolor
    fig.update_layout(
        plot_bgcolor='rgba(255, 99, 71, 0)',  # Set the background color of the plot area
        paper_bgcolor= 'rgba(255, 99, 71, 0)' , # Set the background color of the entire plot
        font=dict(family='Arial', size=14, color='white') # Set the font properties of the plot

    )

    # Show the chart
    fig.show()

    # Save the chart as an HTML file
    fig.write_html(output_path)

def get_window(tokens,hits,window):
  windows = []
  for hit in hits:
    sentence_num = tokens.iloc[hit].sentence_ID
    if (sentence_num - window) < 0:
      start = 0
    else:
      start = sentence_num - window
    
    if (sentence_num + window) >= len(tokens):
      end = len(tokens)-1
    else:
      end = sentence_num + window
    df = tokens[tokens.sentence_ID >= start]
    df = df[df.sentence_ID <= end]
    window_tuple = (df.index[0],df.index[-1])
    windows.append(window_tuple)
  sentences = []
  for window in windows:
    words = tokens.iloc[window[0]:window[1],4]
    words = words.dropna()
    words = words.tolist()
    sentence = ' '.join(words)
    sentences.append(sentence)
  return sentences



# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------
# ------------------------------------ Quotes -------------------------------------
# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------



# get top frequent names, and return their IDs
def select_top_freq_char(top_number , quotes_df):
  return (quotes_df['char_id'].value_counts()[:top_number].index.tolist())



# return list of lists each one contains all quotes for specific char
def get_quoted_for_top(quotes_df,entities_df,book_data,tokens, IDs, atleast_quotes, window_size):
  main_chars = book_data['characters']
  list_quotes = []
  for i in IDs:
    if len(quotes_df[quotes_df['char_id'] == i]["quote"].tolist()) >=  atleast_quotes:
      for char in main_chars:
        char_id = entities_df[entities_df['COREF'] == quotes_df[quotes_df['char_id'] == i]["char_id"].tolist()[0]]["COREF"].tolist()[0]
        if(char["id"] == char_id):
          name_char = char["mentions"]['proper'][0]['n']
      all_quote_start = quotes_df[quotes_df['char_id'] == i]["quote_start"].tolist()
      sentences = get_window(tokens, all_quote_start, window_size)
      list_quotes.append({"character_name" : name_char ,'quotes' : sentences} )
  return list_quotes



# return list of lists each one contains all quotes for specific char
def get_quoted_for_top(quotes_df,entities_df,book_data,tokens, IDs, atleast_quotes, window_size):
  main_chars = book_data['characters']
  list_quotes = []
  for i in IDs:
    if len(quotes_df[quotes_df['char_id'] == i]["quote"].tolist()) >=  atleast_quotes:
      for char in main_chars:
        char_id = entities_df[entities_df['COREF'] == quotes_df[quotes_df['char_id'] == i]["char_id"].tolist()[0]]["COREF"].tolist()[0]
        if(char["id"] == char_id):
          if len(char["mentions"]['proper']) == 0:
            continue
          name_char = char["mentions"]['proper'][0]['n']
      all_quote_start = quotes_df[quotes_df['char_id'] == i]["quote_start"].tolist()
      sentences = get_window(tokens, all_quote_start, window_size)
      list_quotes.append({"character_name" : name_char ,'quotes' : sentences} )
  return list_quotes



def classify_characters(my_dict, emotions_list):
  model = AutoModelForSequenceClassification.from_pretrained(r'E:\GradProject\FLASK\code\models\zero_shot',local_files_only=True)
  tokenizer = AutoTokenizer.from_pretrained(r'E:\GradProject\FLASK\code\models\zero_shot',local_files_only=True)
  classifier = pipeline("zero-shot-classification", model=model,tokenizer= tokenizer,  multi_class=True, device= 0 if torch.cuda.is_available() else -1)
  emo_list = []
  for char in my_dict:
    temp_dict = {}
    temp_dict["character_name"] = char['character_name']
    all_scores = []
    for sentence in char['quotes']:
        sequence_to_classify = sentence
        res = classifier(sequence_to_classify, emotions_list)
        # Initialize an empty dictionary
        emotions_dict = {}

        # Loop through each emotion in the list and add it as a key to the dictionary with a value of 0
        for emotion in emotions_list:
          emotions_dict[emotion] = 0
        for label in range(len(res["labels"])):
          emotions_dict[res["labels"][label]] += res["scores"][label]
        all_scores.append(emotions_dict)
    del classifier # Clear GPU memory of transformers.pipeline
    torch.cuda.empty_cache()
    classifier = pipeline("zero-shot-classification", model=model,tokenizer=tokenizer,  multi_class=True, device= 0 if torch.cuda.is_available() else -1)
    temp_dict['scores'] = all_scores
    emo_list.append(temp_dict)
  return emo_list




def create_scores_dict(emo_list):
  final_list = []
  for dictionary in emo_list:
    final_dict = {}
    scores_list = dictionary['scores']
    # Initialize an empty dictionary to store the sums
    result_dict = {}
    # Loop through each dictionary in the list
    for d in scores_list:
        # Loop through each key-value pair in the dictionary
        for key, value in d.items():
            # If the key already exists in the result dictionary, add the value to the existing sum
            if key in result_dict:
                result_dict[key] += value
            # Otherwise, initialize a new key-value pair with the value
            else:
                result_dict[key] = value
    final_dict["character_name"] = dictionary['character_name']
    final_dict["scores"] = result_dict
    final_list.append(final_dict)
  return final_list
    


  
def characters_ploting(emotions_list, character_list, output_graph_path):

  # Get the unique character names from the list of character dictionaries
  unique_characters = list(set([character['character_name'] for character in character_list]))

  # Initialize a dictionary to hold the scores for each character
  character_scores = {}

  # Loop through each character dictionary
  for character in character_list:
      # Get the character name and scores
      character_name = character['character_name']
      scores = character['scores']

      # Add the scores to the character_scores dictionary
      character_scores[character_name] = [scores[emotion] for emotion in emotions_list]

  # Define the traces for the bar chart
  traces = []
  for character_name in unique_characters:
      trace = go.Bar(x=emotions_list, y=character_scores[character_name], name=character_name, visible='legendonly', marker=dict(color='purple'))
      trace.visible = (character_name == 'Harry')  # Set the trace for Harry to be visible by default
      traces.append(trace)

  # Define the layout for the bar chart
  layout = go.Layout(
      title='''Emotional Scores by Character
      Choose Character: ''',
      xaxis=dict(title='Emotion'),
      yaxis=dict(title='Score'),
      plot_bgcolor='rgba(255, 99, 71, 0)',  # Set the background color of the plot
      width=1000,  # Set the width of the plot
      height=500,  # Set the height of the plot
      margin=dict(l=50, r=50, t=50, b=50),  # Set the margins of the plot
      font=dict(family='Arial', size=14, color='white'),  # Set the font properties of the plot
      paper_bgcolor = 'rgba(255, 99, 71, 0)',  # Set the background color of the plot area
      # bargap=0.2  # Set the gap between bars
  )

  # Define the figure and add the traces and layout
  fig = go.Figure(data=traces, layout=layout)

  # Define the dropdown menu options
  dropdown_options = [{'label': character_name, 'method': 'update', 'args': [{'visible': [character_name == unique_character for unique_character in unique_characters]}, {'title': 'Emotional Scores for {}'.format(character_name)}]} for character_name in unique_characters]

  # Add the dropdown menu to the layout
  fig.update_layout(updatemenus=[{'buttons': dropdown_options, 'direction': 'down', 'showactive': True, 'x': 0.77, 'y': 1.13}])

  # Show the plot
  fig.show()

  # save the chart as an HTML file
  fig.write_html(output_graph_path)






def main(input_novel_path, words_in_chunk, emotions, novel_output_path, quotes_path, book_data_path, entities_path, token_path, top_ids, minimum_quotes, window_size, emotions_list, character_output_path ):

  # _____________________ novel emotions code ______________________________
  novel_path = input_novel_path
  with open(input_novel_path, 'r', encoding='utf-8', errors='ignore') as f:
      long_text = f.read()

  chunks = text_chunking(long_text, words_in_chunk)
  emotions_dict = novel_emotions_classify(emotions, chunks)
  
  total = sum(emotions_dict.values())
  percentage_dict = {}
  for key, value in emotions_dict.items():
    percentage_dict[key] = (value/total)*100
  # create a list of labels and values from the dictionary
  labels = list(percentage_dict.keys())
  values = list(percentage_dict.values())
  novel_emotions_ploting(labels, values, "Emotions Of Entire Novel", novel_output_path)

  # _______________________Character emotions code _________________________
  quotes = pd.read_csv(quotes_path,delimiter = '\t', on_bad_lines='skip', quoting=csv.QUOTE_NONE)
  with open (book_data_path, "r") as f:
    book_data = json.load(f)
  entities = pd.read_csv(entities_path ,delimiter = '\t')
  tokens = pd.read_csv(token_path ,delimiter = '\t' ,  on_bad_lines='skip', quoting=csv.QUOTE_NONE)
  
  # get the most 20 frequent characters, and return their IDs  
  ids = select_top_freq_char(top_ids , quotes)

  # get the quotes in window for only ids that has atleast minimum_quotes number 
  my_dict = get_quoted_for_top(quotes , entities,book_data,tokens, ids, minimum_quotes, window_size)

  
  # Apply Zero shot classification
  emo_dict = classify_characters(my_dict, emotions_list)

  scores_dict = create_scores_dict(emo_dict)
  characters_ploting(emotions_list,scores_dict , character_output_path)

def create_pathes(req_id):
  target_folder = None
  input_file_path = None
  books_path = None
  quotes_path = None
  entities_path = None
  tokens_path = None
  novel_output_path = None
  for folder in os.listdir(PROCESSED_FOLDER):
    if folder.startswith(str(req_id)):
      target_folder = folder
      break
  novel_output_path = os.path.join(PROCESSED_FOLDER, target_folder,"needed_files", 'entire_novel_emotions.html')
  character_output_path = os.path.join(PROCESSED_FOLDER, target_folder,"needed_files", 'characters_emotions.html')
  for file in os.listdir(os.path.join(PROCESSED_FOLDER, target_folder,"needed_files")):
    if file.endswith(".book"):
        books_path = os.path.join(PROCESSED_FOLDER, target_folder,"needed_files", file)
    elif file.endswith(".quotes"):
        quotes_path = os.path.join(PROCESSED_FOLDER, target_folder,"needed_files", file)
    elif file.endswith(".entities"):
        entities_path = os.path.join(PROCESSED_FOLDER, target_folder,"needed_files", file)
    elif file.endswith(".tokens"):
        tokens_path = os.path.join(PROCESSED_FOLDER, target_folder,"needed_files", file)
    
  for file in os.listdir(os.path.join(UPLOAD_FOLDER, target_folder)):
    if file.endswith(".txt"):
        input_file_path = os.path.join(UPLOAD_FOLDER, target_folder, file)

  return input_file_path,books_path, quotes_path, entities_path, tokens_path, novel_output_path,character_output_path


def run_emotion_analysis(req_id,emotions):
  novel_emotions = emotions.split(",")
  novel_emotions = [word.strip() for word in novel_emotions]
  emotions_list = novel_emotions
  input_file_path,book_path, quotes_path, entities_path, tokens_path, novel_output_path,character_output_path = create_pathes(req_id)
  main (input_file_path , words_in_window, novel_emotions, novel_output_path, quotes_path, book_path, entities_path, tokens_path, top_ids, minimum_quotes, window_size, emotions_list, character_output_path)



# ________novel_parameters____________
#novel_emotions = ['guilt', 'anguish','love','hate' ,'fear', 'joy']
#input_file_path = '/content/Harry Potter 1.txt'
#novel_output_path = 'entire novel emotions.html'

# ________characters_parameters____________
# emotions_list = ['Love', 'Joy', 'Sadness', 'Anger', 'Fear', 'Disgust', 'Surprise', 'Anticipation', 'Confidence', 'Envy', 'Frustration', 'Guilt', 'Hope', 'Jealousy', 'Loneliness', 'Regret', 'Sympathy', 'Empathy', 'Disappointment', 'Insecurity', 'Excitement', 'Curiosity', 'Awe', 'Gratitude', 'Happiness', 'Boredom', 'Anxiety', 'Despair', 'Nostalgia', 'Pity', 'Resentment', 'Shame', 'wonder', 'determination', 'courage']
#emotions_list = ['guilt', 'anguish','love','hate' ,'fear', 'joy']
#book_data_path = "/content/Harry Potter.book"
#quotes_path = '/content/Harry Potter.quotes'
#entities_path = '/content/Harry Potter.entities'
#token_path = '/content/Harry Potter.tokens'
#character_output_path = 'characters_emotions.html'

