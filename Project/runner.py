import sqlite3
from all_scraping_task import run_scraping_task
from booknlp_code import Run_BOOKNLP
from character_map import run_char_map
from emotion_analysis import run_emotion_analysis
from summarization import run_summarization
from character_network import run_char_network
from all_dashes import create_dashboard
from send_email import send_emails

DB = r'instance\app.db'

conn = sqlite3.connect(DB)

def query_row(row_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM service_request WHERE id = ?",(row_id,))
    row = cursor.fetchone()
    values_in_interest = {
    "char_net_selected" : row[1],
    "emotion_selected" : row[2],
    "summary_selected" : row[4],
    "char_map_selected" : row[3],
    "review_analysis_selected" : row[5],
    "email" : row[6],
    "goodreads_link" : row[7],
    "storygraph_link" : row[8],
    "summary_range" : row[9],
    "emotions" : row[10]
    }
    return values_in_interest

def do_request(req_id):
    value_in_interest = query_row(req_id)
    
    char_net_selected = value_in_interest["char_net_selected"]
    emotion_selected = value_in_interest["emotion_selected"]
    summary_selected = value_in_interest["summary_selected"]
    char_map_selected = value_in_interest["char_map_selected"]
    review_analysis_selected = value_in_interest["review_analysis_selected"]
    
    email = value_in_interest["email"]
    goodreads_link = value_in_interest["goodreads_link"]
    storygraph_link = value_in_interest["storygraph_link"]
    summary_range = value_in_interest["summary_range"]
    emotions = value_in_interest["emotions"]

    if review_analysis_selected == "1" :
        print("Starting Reviews Analysis")
        run_scraping_task(req_id,goodreads_link,storygraph_link)
        print("Reviews Analysis Done")
    if char_net_selected != "0" or emotion_selected != "0" or char_map_selected != "0" :
        Run_BOOKNLP(req_id)
    if char_net_selected == "1":
        print("Starting Creating Character Network")
        run_char_network(req_id)
        print("Character Network Done")
    if char_map_selected == "1":
        print("Starting Creating Character Map")
        run_char_map(req_id)
        print("Character Map Done")
    if emotion_selected == "1":
        print("Starting Emotion Analysis")
        run_emotion_analysis(req_id,emotions)
        print("Emotion Analysis Done")
    if summary_selected == "1":
        print("Starting Summarization")
        length_penalty = 1 / summary_range
        run_summarization(req_id,length_penalty)
        print("Summarization Done")
    
    
    create_dashboard(req_id)
    send_emails(req_id,email)
    
    #request_to_do.done_status = "1"

#do_request(8)

send_emails(8,"ahmed3ahmed27@gmail.com")
send_emails(8,"abdullahgamal74@gmail.com")

