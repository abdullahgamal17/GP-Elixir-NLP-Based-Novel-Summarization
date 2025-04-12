import os
import shutil

PROCESSED_FOLDER = r"files_folder\files_processed"

def get_folder_in_work(req_id):
    for folder in os.listdir(PROCESSED_FOLDER):
        if folder.startswith(str(req_id)):
            return folder

def get_files(req_id):
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
    char_map_png,upper_char_map_text_png = get_files(req_id)
    working_folder = get_folder_in_work(req_id)
    dashboard_folder = os.path.join(PROCESSED_FOLDER,working_folder,"services_output","Dashboard")
    with open(os.path.join(dashboard_folder,"char_map_dash.html"),"w") as f:
        f.write(the_html)
    
    print("Copying files")
    shutil.copy(char_map_png,os.path.join(dashboard_folder,"char_map.png"))
    shutil.copy(upper_char_map_text_png,os.path.join(dashboard_folder,"char_map_text.png"))
    print("Done")

create_char_map_dash(19)
    
    

    