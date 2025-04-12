import os
import shutil

PROCESSED_FOLDER = r"files_folder\files_processed"

def get_folder_in_work(req_id):
    for folder in os.listdir(PROCESSED_FOLDER):
        if folder.startswith(str(req_id)):
            return folder

def get_files(req_id):
    main_folder = get_folder_in_work(str(req_id))
    working_folder = os.path.join(PROCESSED_FOLDER,main_folder,"needed_files")
    char_network_html = os.path.join(working_folder,"Character network.html")
    char_network_png = os.path.join(working_folder,"character network.png")
    return char_network_html , char_network_png

def create_character_network_dash(req_id):
    char_html , char_png = get_files(req_id)
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

create_character_network_dash(19)