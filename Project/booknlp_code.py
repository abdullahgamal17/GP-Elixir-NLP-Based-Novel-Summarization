from booknlp.booknlp import BookNLP
import os

UPLOAD_FOLDER = r'files_folder\files_received'
PROCESSING_FOLDER = r'files_folder\files_processed'

def create_inputs_for_BOOKNLP(req_id):
    folders_list = os.listdir(UPLOAD_FOLDER)
    target_folder_for_input = None
    target_folder_for_output = None
    book_id = None
    for folder in folders_list:
        if folder.startswith(str(req_id)):
            target_folder = folder
            break
    target_folder_for_input = os.path.join(UPLOAD_FOLDER,target_folder)
    target_folder_for_output = os.path.join(PROCESSING_FOLDER,target_folder,"needed_files")
    input_file_path = os.listdir(target_folder_for_input)[0]
    book_id = input_file_path.split(".")[0]
    input_file_path = os.path.join(target_folder_for_input,input_file_path)
    return input_file_path, target_folder_for_output, book_id


def Run_BOOKNLP(req_id):
    file_path, output_dir,book_id = create_inputs_for_BOOKNLP(req_id)
    model_params={
                "pipeline":"entity,quote,supersense,event,coref", 
                "model":"big"
                }
    NLP = BookNLP("en", model_params)
    NLP.process(file_path, output_dir, book_id)

#Run_BOOKNLP(21)
    
           
    


