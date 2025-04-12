import os
import shutil

PROCESSED_FOLDER = r"files_folder\files_processed"

def get_folder_in_work(req_id):
    for folder in os.listdir(PROCESSED_FOLDER):
        if folder.startswith(str(req_id)):
            return folder

def get_files(req_id):
    main_folder = get_folder_in_work(str(req_id))
    emotion_analysis_html = os.path.join(PROCESSED_FOLDER,main_folder,"needed_files","entire_novel_emotions.html")
    emotion_analysis_png = os.path.join(PROCESSED_FOLDER,main_folder,"needed_files","entire_emotions_text.png")



    return emotion_analysis_html, emotion_analysis_png


def create_emotion_dash(req_id):
    emotion_analysis_html, emotion_analysis_png = get_files(req_id)
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

create_emotion_dash(19)


