import os
import shutil

PROCESSED_FOLDER = r"files_folder\files_processed"

def get_folder_in_work(req_id):
    for folder in os.listdir(PROCESSED_FOLDER):
        if folder.startswith(str(req_id)):
            return folder

def get_files(req_id):
    main_folder = get_folder_in_work(str(req_id))
    char_emotion_analysis_html = os.path.join(PROCESSED_FOLDER,main_folder,"needed_files","characters_emotions.html")
    char_emotion_analysis_png = os.path.join(PROCESSED_FOLDER,main_folder,"needed_files","character_emotions_text.png")

    return char_emotion_analysis_html, char_emotion_analysis_png

def create_char_emotion_dash(req_id):
    main_folder = get_folder_in_work(req_id)
    dashboard_folder = os.path.join(PROCESSED_FOLDER,main_folder,"services_output","Dashboard")
    char_emotion_analysis_html, char_emotion_analysis_png = get_files(req_id)
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
    

create_char_emotion_dash(19)

