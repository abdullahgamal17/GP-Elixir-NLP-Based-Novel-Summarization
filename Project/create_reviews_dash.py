import os
import shutil

PROCESSED_FOLDER = r"files_folder\files_processed"

def get_folder_in_work(req_id):
    for folder in os.listdir(PROCESSED_FOLDER):
        if folder.startswith(str(req_id)):
            return folder

def get_files(req_id):
    main_folder = get_folder_in_work(str(req_id))
    review_analysis_html = os.path.join(PROCESSED_FOLDER,main_folder,"needed_files","Reviews_emotions.html")
    review_analysis_png = os.path.join(PROCESSED_FOLDER,main_folder,"needed_files","Reviews_analysis.png")
    
    return review_analysis_html, review_analysis_png

def create_reviews_dash(req_id):
    review_analysis_html, review_analysis_png = get_files(req_id)
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
create_reviews_dash(19)
    


