import os
import shutil
import sqlite3
import re
from bs4 import BeautifulSoup

db_path = r"instance\app.db"
conn = sqlite3.connect(db_path)
PROCESSED_FOLDER = r"files_folder\files_processed"
PATH_IMAGES = r'needed_images_for_dashboard'

def query_row(row_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM service_request WHERE id = ?",(row_id,))
    row = cursor.fetchone()
    values_in_interest = {
    "char_net_selected" : row[1],
    "emotion_selected" : row[2],
    "char_map_selected" : row[3],
    "review_analysis_selected" : row[5],
    }
    return values_in_interest


def get_folder_in_work(req_id):
    for folder in os.listdir(PROCESSED_FOLDER):
        if folder.startswith(str(req_id)):
            return folder


# ----------- CHAR EMOTION DASH -------------      
def get_files_char_emotion_dash(req_id):
    main_folder = get_folder_in_work(str(req_id))
    char_emotion_analysis_html = os.path.join(PROCESSED_FOLDER,main_folder,"needed_files","characters_emotions.html")
    char_emotion_analysis_png = os.path.join(PROCESSED_FOLDER,main_folder,"needed_files","character_emotions_text.png")
    return char_emotion_analysis_html, char_emotion_analysis_png

def create_char_emotion_dash(req_id):
    main_folder = get_folder_in_work(req_id)
    dashboard_folder = os.path.join(PROCESSED_FOLDER,main_folder,"services_output","Dashboard")
    char_emotion_analysis_html, char_emotion_analysis_png = get_files_char_emotion_dash(req_id)
    char_emotion_read = None
    with open(char_emotion_analysis_html,"r",encoding='utf-8') as f:
        char_emotion_read = f.read()
    char_emotions_head = char_emotion_read.find("<head>")
    char_emotions_head_end = char_emotion_read.find("</head>")
    char_emotions_body = char_emotion_read.find("<body>")
    char_emotions_body_end = char_emotion_read.find("</body>")
    char_emotion_read_body = char_emotion_read[char_emotions_body+len("<body>"):char_emotions_body_end]
    in_head = char_emotion_read[char_emotions_head+len("<head>"):char_emotions_head_end]

    the_html = """
    <html>
        <head>
            {in_head}
        </head>
        
        <body style = "width: 50%;">
            <div style = "display: flex; margin-left: 100px;"
                <div>
                {char_emotion_read_body}
                <img src="character_emotions_text.png"/>
                </div>
                
            </div>
            
        
        </body>
        
        """.format(in_head = in_head, char_emotion_read_body = char_emotion_read_body)
    shutil.copy(char_emotion_analysis_png,os.path.join(dashboard_folder,"character_emotions_text.png"))
    with open(os.path.join(dashboard_folder,"char_emotion_dash.html"),"w",encoding='utf-8') as f:
        f.write(the_html)
    
    print("CHAR EMOTION DASH CREATED")

# ----------- CHAR EMOTION DASH -------------

# ----------- CHAR MAP DASH -------------

def get_files_char_map_dash(req_id):
    main_folder = get_folder_in_work(str(req_id))
    char_map_png = os.path.join(PROCESSED_FOLDER,main_folder,"needed_files","char_map.png")
    upper_char_map_text_png = os.path.join(PROCESSED_FOLDER,main_folder,"needed_files","char_map_text.png")
    return char_map_png, upper_char_map_text_png

def create_char_map_dash(req_id):
    the_html = """<html>\n
    <body>\n
    <img src="char_map_text.png" style="display: block; margin-left: auto; margin-right: auto; width: 90%;"/>\n
    <img src="char_map.png"/>\n
    </body>\n
    </html>\n
    """
    print("Creating char map dash")
    char_map_png,upper_char_map_text_png = get_files_char_map_dash(req_id)
    working_folder = get_folder_in_work(req_id)
    dashboard_folder = os.path.join(PROCESSED_FOLDER,working_folder,"services_output","Dashboard")
    with open(os.path.join(dashboard_folder,"char_map_dash.html"),"w") as f:
        f.write(the_html)
    
    print("Copying files")
    shutil.copy(char_map_png,dashboard_folder)
    shutil.copy(upper_char_map_text_png,os.path.join(dashboard_folder,"char_map_text.png"))
    print("Done")

# ----------- CHAR MAP DASH -------------

# ----------- CHAR NETWORK DASH -------------


def get_files_character_network_dash(req_id):
    main_folder = get_folder_in_work(str(req_id))
    working_folder = os.path.join(PROCESSED_FOLDER,main_folder,"needed_files")
    char_network_html = os.path.join(working_folder,"Character network.html")
    char_network_png = os.path.join(working_folder,"character network.png")
    return char_network_html , char_network_png

def create_character_network_dash(req_id):
    char_html , char_png = get_files_character_network_dash(req_id)
    working_folder = os.path.join(PROCESSED_FOLDER,get_folder_in_work(str(req_id)))
    shutil.copy(char_png,os.path.join(working_folder,"services_output",'Dashboard'))
    shutil.copy(char_html,os.path.join(working_folder,"services_output",'Dashboard'))
    characternetwork = ""
    with open(char_html,"r",encoding="utf-8") as f:
        characternetwork = f.read()
    body_start = characternetwork.find("<body")
    body_end = characternetwork.find("</body>")
    
    body = characternetwork[body_start:body_end]
    script_start = body.find("<script")
    script_end = body.find("</script>")
    len_script_end = len("</script>")
    script = body[script_start:script_end+len_script_end]
    the_html = """
    <html>\n
        <head>
            <meta charset="utf-8"/>
            <script src="lib/bindings/utils.js"></script>
            <link crossorigin="anonymous" href="https://cdnjs.cloudflare.com/ajax/libs/vis-network/9.1.2/dist/dist/vis-network.min.css" integrity="sha512-WgxfT5LWjfszlPHXRmBWHkV2eceiWTOBvrKCNbdgDYTHrT2AeLCGbF4sZlZw3UMN3WtL0tGUoIAKsu8mllg/XA==" referrerpolicy="no-referrer" rel="stylesheet"/>
            <script crossorigin="anonymous" integrity="sha512-LnvoEWDFrqGHlHmDD2101OrLcbsfkrzoSpvtSQtxK3RMnRV0eOkhhBN2dXHKRrUU8p2DGRTk35n4O8nWSVe1mQ==" referrerpolicy="no-referrer" src="https://cdnjs.cloudflare.com/ajax/libs/vis-network/9.1.2/dist/vis-network.min.js"></script>
            <center>
                <h1></h1>
            </center>
            <!-- <link rel="stylesheet" href="../node_modules/vis/dist/vis.min.css" type="text/css" />
            <script type="text/javascript" src="../node_modules/vis/dist/vis.js"> </script>-->
            <link crossorigin="anonymous" href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta3/dist/css/bootstrap.min.css" integrity="sha384-eOJMYsd53ii+scO/bJGFsiCZc+5NDVN2yr8+0RDqr0Ql0h+rP48ckxlpbzKgwra6" rel="stylesheet"/>
            <script crossorigin="anonymous" integrity="sha384-JEW9xMcG8R+pH31jmWH6WWP0WintQrMb4s7ZOdauHnUtxwoG2vI5DkLtS3qm9Ekf" src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta3/dist/js/bootstrap.bundle.min.js"></script>
            <center>
                <h1></h1>
            </center>
            <style type="text/css">

                \\#mynetwork {{
                    width: 1000px;
                    height: 600px;
                    background-color: rgba(255, 99, 71, 0);
                    border: 1px solid lightgray;
                    position: relative;
                    float: left;
                }}

            </style>

        </head>

        <body style="width: 90%;">
        <div style="display: flex; margin-left: 100px;">
            <img src="character network.png"/>
            <div class="card" style="width: 100%">    
                <div id="mynetwork" class="card-body">

                </div>
            </div>
        </div>
            {script}
        </body>
    </html>

    """.format(script=script)
    
    with open(os.path.join(working_folder,"services_output",'Dashboard',"character_network_dash.html"),"w",encoding="utf-8") as f:
        f.write(the_html)
    
    print("Hello")

# ----------- CHAR NETWORK DASH -------------

# ----------- NOVEL EMOTION DASH -------------

def get_files_novel_emotion_dash(req_id):
    main_folder = get_folder_in_work(str(req_id))
    emotion_analysis_html = os.path.join(PROCESSED_FOLDER,main_folder,"needed_files","entire_novel_emotions.html")
    emotion_analysis_png = os.path.join(PROCESSED_FOLDER,main_folder,"needed_files","entire_emotions_text.png")
    return emotion_analysis_html, emotion_analysis_png

def create_emotion_dash(req_id):
    emotion_analysis_html, emotion_analysis_png = get_files_novel_emotion_dash(req_id)
    dash_folder = os.path.join(PROCESSED_FOLDER,get_folder_in_work(req_id),"services_output","Dashboard")
    emotion_read = None
    with open(emotion_analysis_html,"r",encoding='utf-8') as f:
        emotion_read = f.read()
    emotions_body = emotion_read.find("<body>")
    emotions_head_end = emotion_read.find("</body>")
    emotion_read_body = emotion_read[emotions_body+len("<body>"):emotions_head_end]
    the_html = """
    <html>
        <body style = "width: 50%;">
            <div style = "display: flex; margin-left: 100px;"
                <div>
                <img src="entire_emotions_text.png"/>
                {emotion_read_body}
                </div>
            </div>
        </body>
        
        """.format(emotion_read_body = emotion_read_body)
    shutil.copy(emotion_analysis_png,os.path.join(dash_folder,"entire_emotions_text.png"))
    with open(os.path.join(dash_folder,"novel_emotion_dash.html"),"w",encoding='utf-8') as f:
        f.write(the_html)
    
    print("Done")

# ----------- NOVEL EMOTION DASH -------------

# ----------- REVIEWS DASH -------------

def get_files_reviews_dash(req_id):
    main_folder = get_folder_in_work(str(req_id))
    review_analysis_html = os.path.join(PROCESSED_FOLDER,main_folder,"needed_files","Reviews_emotions.html")
    review_analysis_png = os.path.join(PROCESSED_FOLDER,main_folder,"needed_files","Reviews_analysis.png")
    
    return review_analysis_html, review_analysis_png

def create_reviews_dash(req_id):
    review_analysis_html, review_analysis_png = get_files_reviews_dash(req_id)
    dash_folder = os.path.join(PROCESSED_FOLDER,get_folder_in_work(req_id),"services_output","Dashboard")
    review_read = None

    with open(review_analysis_html,"r",encoding='utf-8') as f:
        review_read = f.read()
    
    reviews_body = review_read.find("<body>")
    reviews_head_end = review_read.find("</body>")
    review_read_body = review_read[reviews_body+len("<body>"):reviews_head_end]

    the_html = """
    <html>
        <body style = "width: 50%;">
            <div style = "display: flex; margin-left: 100px;"
                <div>
                {review_read_body}
                <img src="Reviews_analysis.png"/>
                </div>
            </div>
        </body>
        
        """.format(review_read_body = review_read_body)
    
    shutil.copy(review_analysis_png,os.path.join(dash_folder,"Reviews_analysis.png"))
    with open(os.path.join(dash_folder,"review_dash.html"),"w",encoding='utf-8') as f:
        f.write(the_html)
    
# ----------- REVIEWS DASH -------------

def create_dashes(req_id):
    working_folder = get_folder_in_work(req_id)
    for img in os.listdir(PATH_IMAGES):
        shutil.copy(os.path.join(PATH_IMAGES,img),os.path.join(PROCESSED_FOLDER,working_folder,"needed_files"))
    services_selected = query_row(req_id)
    # WARNING: HARDCODED
    services = [0,0,0,0]
    for service,selected in services_selected.items():
        if service == "char_net_selected" and selected == "1":
            create_character_network_dash(req_id)
            services[0] = 1
        elif service == "emotion_selected" and selected == "1":
            create_emotion_dash(req_id)
            create_char_emotion_dash(req_id)
            services[1] = 1
        elif service == "review_analysis_selected" and selected == "1":
            create_reviews_dash(req_id)
            services[2] = 1
        elif service == "char_map_selected" and selected == "1":
            create_char_map_dash(req_id)
            services[3] = 1
    return services

def create_dashboard(req_id):
    services = create_dashes(req_id)
    dash_folder = os.path.join(PROCESSED_FOLDER,get_folder_in_work(req_id),"services_output","Dashboard")
    final_dashboard = os.path.join(PROCESSED_FOLDER,get_folder_in_work(req_id),"services_output","Dashboard","Elixir_Dashboard")
    if not os.path.exists(final_dashboard):
        os.mkdir(final_dashboard)
    for file in os.listdir(PATH_IMAGES):
        shutil.copy(os.path.join(PATH_IMAGES,file),final_dashboard)
    for file in os.listdir(dash_folder):
        if file.endswith(".html") or file == "Elixir_Dashboard":
            continue
        shutil.copy(os.path.join(dash_folder,file),final_dashboard)
    
    services_order = ["Reviews_Dash",
                      "Entire Novel Emotion",
                      "Character Emotion",
                      "Character Network",
                      "Character Map"]
    rest_of_head = ""

        
    review_dash_head = None
    entire_novel_emotion_dash_head = None
    character_emotion_dash_head = None
    character_network_dash_head= None
    character_map_dash_head = None

    review_dash_body = None
    entire_novel_emotion_dash_body = None
    character_emotion_dash_body = None
    character_network_dash_body = None
    character_map_dash_body = None    
    #print(type(char_soup.body.prettify()))

    #Review Dash
    if services[2] == 1:
        shutil.copy(os.path.join(dash_folder,"Reviews_analysis.png"),final_dashboard)
        review_soup = BeautifulSoup(open(os.path.join(dash_folder,"review_dash.html"),encoding='utf-8'),"html.parser")
        review_dash_head = review_soup.head
        review_dash_body = review_soup.body
        review_dash_body = "\n".join([str(x) for x in review_dash_body.contents]) + "<br><br><br>"
        if review_dash_head is not None:
            rest_of_head += review_dash_head.prettify() 
    # Entire Novel and Character Emotion
    if services[1] == 1:
        char_emotion_soup = BeautifulSoup(open(os.path.join(dash_folder,"char_emotion_dash.html"),encoding='utf-8'),"html.parser")
        emotion_soup = BeautifulSoup(open(os.path.join(dash_folder,"novel_emotion_dash.html"),encoding='utf-8'),"html.parser")
        entire_novel_emotion_dash_head = emotion_soup.head
        entire_novel_emotion_dash_body = "\n".join([str(x) for x in emotion_soup.body.contents]) + "<br><br><br>"
        character_emotion_dash_head = char_emotion_soup.head
        character_emotion_dash_body = "\n".join([str(x) for x in char_emotion_soup.body.contents]) + "<br><br><br>"
        if entire_novel_emotion_dash_head is not None:
            rest_of_head += '\n'.join([str(x) for x in entire_novel_emotion_dash_head.contents]) + '\n'  
        if character_emotion_dash_head is not None:
            rest_of_head += "\n".join([str(x) for x in character_emotion_dash_head.contents]) + '\n'
    # Character Network    
    if services[0] == 1:
        char_net_soup = BeautifulSoup(open(os.path.join(dash_folder,"character_network_dash.html"),encoding='utf-8'),"html.parser")
        character_network_dash_head = char_net_soup.head
        character_network_dash_body = '\n'.join([str(x) for x in char_net_soup.body.contents]) + "<br><br><br>"
        rest_of_head += '\n'.join([str(x) for x in character_network_dash_head.contents])
    # Character Map
    if services[3] == 1:
        char_map_soup = BeautifulSoup(open(os.path.join(dash_folder,"char_map_dash.html"),encoding='utf-8'),"html.parser")
        character_map_dash_head = char_map_soup.head
        character_map_dash_body = "\n".join([str(x) for x in char_map_soup.body.contents]) + "<br><br><br>"
        if character_map_dash_head is not None:
            rest_of_head += '\n'.join([str(x) for x in character_map_dash_head.contents])
    the_html = """
    <html>

        <head>
            <title>Elixir Dashboard</title>
            <style>
                body
                {{
                    background-image: url('background.jpg');
                    background-repeat: no-repeat;
                    background-size: cover;
                }}
            </style>
            {rest_of_head}
        </head>

        <body>
            <img id="head" src="head.png" style="margin-left: -10px; margin-top: -10px;"/>
            <br>
            <br>
            <br>
            <div>
            {reviews_dash}
            </div>

            <div>
            {entire_novel_emotion_dash}
            </div>
            {character_emotion_dash}
            <div>
            {character_network_dash}
            </div>

            <div>
            {character_map_dash}
            </div>
        </body>
    </html>""".format(rest_of_head=rest_of_head,
                      reviews_dash=review_dash_body,
                      entire_novel_emotion_dash=entire_novel_emotion_dash_body,
                      character_emotion_dash=character_emotion_dash_body,
                      character_network_dash=character_network_dash_body,
                      character_map_dash=character_map_dash_body)
    path_final = os.path.join(final_dashboard,"Elixir_Dashboard.html")
    with open(path_final,"w",encoding='utf-8') as f:
        f.write(the_html)




