import pandas as pd 
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import io
import random
import csv
from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline
import json
import os
import shutil

PROCESSED_FOLDER = r'files_folder\files_processed'
relations = ['father', 'mother', 'dad', 'mom', 'brother', 'sister', 'son', 'daughter', 'aunt',
             'parents', 'uncle', 'cousin', 'niece', 'stepfather', 'stepmother', 'stepson',
               'stepdaughter', 'half-brother', 'half-sister', 'foster father', 'foster mother',
                 'foster son', 'foster daughter', 'godfather', 'godmother', 'godson', 'goddaughter',
                   'father-in-law', 'mother-in-law', 'brother-in-law', 'sister-in-law', 'ex-husband',
                     'ex-wife', 'ex-boyfriend', 'ex-girlfriend', 'partner', 'partner\'s parents',
                       'partner\'s siblings', 'partner\'s children', 'adoptive father',
                         'adoptive mother', 'adopted son', 'adopted daughter', 'biological father',
                           'biological mother', 'biological son', 'biological daughter', 'guardian',
                             'ward', 'employer', 'employee', 'investor', 'debtor', 'creditor',
                               'customer', 'client', 'vendor', 'friend', 'best friend', 'close friend',
                                 'childhood friend', 'high school friend', 'college friend',
                                   'work friend', 'gym buddy', 'drinking buddy', 'travel companion',
                                     'adventure partner', 'wingman', 'wingwoman', 'bff', 'pal', 'buddy',
                                       'mate', 'amigo', 'comrade', 'chum', 'confidante', 'confidant',
                                         'ally', 'sidekick', 'acquaintance']

window_size = 8
min_score = 0.4


def store_characters_position(main_chars, relations):
  # store all positions of the first 10 character if their poss in relations list
  hits = []
  char_name = []
  poss = []
  for character in main_chars:
    for pos in character['poss']:
      if (len(character["mentions"]['proper']) > 0  ):
        if pos['w'] in relations:
          hits.append(pos['i'])
          char_name.append(character["mentions"]['proper'][0]['n'])
          poss.append(pos['w'])
  return hits, char_name, poss


def get_window(hits, tokens, window_size):
  windows = []
  tokens.sentence_ID = tokens.sentence_ID.astype('int') 
  for hit in hits:
    sentence_num = tokens.iloc[hit].sentence_ID
    if sentence_num - window_size < 0:
      start = 0
    else:
      start = sentence_num - window_size
      
    if sentence_num + window_size >= len(tokens):
      end = len(tokens)-1
    else:
      end = sentence_num + window_size

    df = tokens[tokens.sentence_ID >= start]
    df = df[df.sentence_ID <= end]
    window = (df.index[0],df.index[-1])
    windows.append(window)
  return windows

def get_sentences_of_window(windows, tokens):
  sentences = []
  
  for window in windows:
    words = tokens.iloc[window[0]:window[1],4]
    words = words.dropna()
    words = words.tolist()
    sentence = ' '.join(words)
    sentences.append(sentence)
  return sentences


def get_all_char(book_data):
  all_char = []
  for i in range(len(book_data['characters'])):
    for j in range(len(book_data["characters"][i]["mentions"]["proper"])):  
      all_char.append(book_data["characters"][i]["mentions"]["proper"][j]['n'])
  return all_char



def apply_model(sentences, all_char, char_name, poss, min_score):
  model_name = r"E:\GradProject\FLASK\code\models\qa"

  # a) Get predictions
  # b) Load model & tokenizer
  model = AutoModelForQuestionAnswering.from_pretrained(model_name,local_files_only=True)
  tokenizer = AutoTokenizer.from_pretrained(model_name,local_files_only=True)
  nlp = pipeline('question-answering', model=model_name, tokenizer=model_name)

  c = 0 
  temp = []
  for sentence in sentences:
    character = char_name[c]
    relationship = poss[c]
    QA_input = {
      'question': f"Who is {character}'s {relationship}",
      'context': sentence
    }
    res = nlp(QA_input)
    if res['score'] > min_score and res['answer'] in all_char: 
      my_dict = {'score' : res['score'] , "char_question" : character , "char_answer" : res['answer'], 'Relationship' : relationship}
      temp.append(my_dict)
    c+=1
  return temp
  



def draw_fig(target, data):
    all_figures = []
    temp = ''
    for dict_1 in data:
        if dict_1['char_question'] == temp:
            continue
        temp = dict_1['char_question']
        specific_char = []
        relation_dict = {}
        for dict_2 in data:
            if dict_1['char_question'] == dict_2['char_question']:
                specific_char.append((dict_1['char_question'], dict_2['char_answer']))
                relation_dict[(dict_1['char_question'], dict_2['char_answer'])] = dict_2['Relationship']
        all_figures.append([specific_char, relation_dict])

    networks = []
    for figure in all_figures:
        networks.append((nx.Graph(figure[0]), figure[1]))

    n_networks = len(networks)
    n_rows = (n_networks + 1) // 2
    n_cols = 2
    colors = [
        "#FF0000", "#FFA500", "#FFFF00", "#00FF00", "#00FFFF",
        "#0000FF", "#FF00FF", "#C71585", "#FF1493", "#B22222",
        "#8B008B", "#FF69B4", "#FFD700", "#32CD32", "#00CED1",
        "#4169E1", "#FF7F50", "#FF6347", "#9ACD32", "#DC143C"
    ]

        # Draw the networks in a grid
    fig = plt.figure(figsize=(15, 4*n_rows), facecolor='red')
    axs = fig.subplots(nrows=n_rows, ncols=n_cols)

    for i, (G, edge_labels) in enumerate(networks):
        row = i // n_cols
        col = i % n_cols

        pos = nx.spring_layout(G)
        node_color = random.choice(colors)
        
        nx.draw(G, pos, with_labels=True, font_weight='bold', ax=axs[row, col], font_color ='white',
                node_shape='p', node_size=2500, node_color=node_color, width=3, edge_color='lightgray', margins=0.15)
        if edge_labels:
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red', font_size=12, ax=axs[row, col])


    # Change the background color of the entire plot
    fig.patch.set_facecolor((1.0, 0.39, 0.28, 0.0))

    # Save the graph as a PNG file
    plt.tight_layout()
    canvas = FigureCanvas(fig)
    buf = io.BytesIO()
    canvas.print_png(buf)
    with open('char_map.png', 'wb') as f:
        f.write(buf.getbuffer())
    shutil.move("char_map.png",target)

    # Create an HTML file to display the graph
    html_content = f'<html><body><img src="char_map.png" /></body></html>'
    with open('char_map.html', 'w') as f:
        f.write(html_content)
    shutil.move("char_map.html",target)


def create_needed_paths(req_id):
  target_folder = None
  tokens_path = None
  entities_path = None
  book_data_path = None
  for folder in os.listdir(PROCESSED_FOLDER):
    if folder.startswith(str(req_id)):
      target_folder = folder
      break
  for file in os.listdir(os.path.join(PROCESSED_FOLDER, target_folder,"needed_files")):
    if file.endswith(".tokens"):
      tokens_path = os.path.join(PROCESSED_FOLDER, target_folder,"needed_files", file)
    elif file.endswith(".entities"):
      entities_path = os.path.join(PROCESSED_FOLDER, target_folder,"needed_files", file)
    elif file.endswith(".book"):
      book_data_path = os.path.join(PROCESSED_FOLDER, target_folder,"needed_files", file)
  return tokens_path, entities_path, book_data_path


def main(req_id,relations = relations, window_size = window_size,min_score = min_score):
  tokens_path, entities_path, book_data_path = create_needed_paths(req_id)
  main_path = tokens_path.split("\\")[:-2]
  print('hi')
  output_path = os.path.join(*main_path, 'needed_files')
  tokens = pd.read_csv(tokens_path, on_bad_lines='skip',delimiter = '\t', quoting=csv.QUOTE_NONE)
  entities = pd.read_csv(entities_path, delimiter = '\t')
  with open (book_data_path, "r") as f:
      book_data = json.load(f)
  main_chars = book_data['characters']
  hits , char_name, poss = store_characters_position(main_chars, relations)
  windows = get_window(hits, tokens, window_size)
  sentences = get_sentences_of_window(windows, tokens)
  all_char = get_all_char(book_data)
  data = apply_model(sentences, all_char, char_name, poss, min_score)
  draw_fig(output_path,data)

def run_char_map(req_id):
   main(req_id)
  





#tokens_path = '/content/drive/MyDrive/crime_and_punishment/crime_and_punishment/crime_and_punishment.tokens'
#entities_path = '/content/drive/MyDrive/crime_and_punishment/crime_and_punishment/crime_and_punishment.entities'
#book_data_path = "/content/drive/MyDrive/crime_and_punishment/crime_and_punishment/crime_and_punishment.book"

#run_char_map(20)
