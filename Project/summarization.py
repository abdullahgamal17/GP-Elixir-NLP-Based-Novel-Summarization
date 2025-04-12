# !pip install transformers accelerate -q
# !pip install PyPDF2
# !pip install pdfminer.six
# !pip install fpdf


# Importing Dependencies
from transformers import pipeline
import PyPDF2
#from pdfminer.high_level import extract_text
#import resource
#import re
import textwrap
from fpdf import FPDF
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import pprint as pp
import os
words_in_chunk = 5000
min_length = 50
max_length = 1024
#length_penalty = 0.5

PROCESSED_FOLDER = r'files_folder\files_processed'
UPLOAD_FOLDER = r'files_folder\files_received'
#@markdown add auto-Colab formatting with `IPython.display`
from IPython.display import HTML, display
# colab formatting
def set_css():
    display(
        HTML(
            """
  <style>
    pre {
        white-space: pre-wrap;
    }
  </style>
  """
        )
    )

#get_ipython().events.register("pre_run_cell", set_css)



def load_model_and_tokenizer(hugging_face_model):
  model_name = hugging_face_model #@param {type:"string"}

  tokenizer = AutoTokenizer.from_pretrained(model_name,local_files_only=True)
  model = AutoModelForSeq2SeqLM.from_pretrained(model_name,local_files_only=True)
  return model_name, tokenizer


# This function convert the text into the pdf and save it at the specified location
def text_to_pdf(text, filename):
    # Define the width of the A4 sheet in millimeters
    a4_width_mm = 200
    # Define the conversion factor from points to millimeters
    pt_to_mm = 0.35
    # Define the font size in points
    fontsize_pt = 11
    # Convert the font size to millimeters
    fontsize_mm = fontsize_pt * pt_to_mm
    # Define the bottom margin in millimeters
    margin_bottom_mm = 10
    # Define the width of a single character in millimeters
    character_width_mm = 7 * pt_to_mm
    # Calculate the maximum number of characters that can fit on a line
    width_text = a4_width_mm / character_width_mm

    # Create a new PDF document with A4 size
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    # Enable automatic page breaks and set the bottom margin
    pdf.set_auto_page_break(True, margin=margin_bottom_mm)
    # Add a new page to the document
    pdf.add_page()
    # Set the font to Courier with the specified size
    pdf.set_font(family='Courier', size=fontsize_pt)
    # Split the text into lines based on newline characters
    splitted = text.split('\n')

    # Loop through each line of text
    for line in splitted:
        # Wrap the line into multiple lines if it exceeds the maximum width
        lines = textwrap.wrap(line, width_text)

        # If the line is empty, insert a blank line
        if len(lines) == 0:
            pdf.ln()

        # Loop through each wrapped line and add it to the PDF
        for wrap in lines:
            pdf.cell(0, fontsize_mm, wrap, ln=1)

    # Save the PDF to the specified filename
    pdf.output(filename, 'F')
    # Print a message indicating that the PDF has been saved
    print("PDF of summary Saved!!")




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

    # Print the total number of chunks and return the list of chunks
    print("Total chunks of text are: ", len(chunks))
    return chunks





# This function takes in all the chunks, find the summary of each chunk and return all the summaries of chunks in list form. 

def model_summary(chunks,model_name, tokenizer, max_length, min_length, length_penalty ):
  print("Summarizing the text. Please wait .......")
  all_summaries = []
  count = 0
  for chunk in chunks:
    print("Summarizing Chunk NO: ", count + 1)
    count +=1
    #@markdown define generation parameters
    #@markdown - for even better performance increase `num_beams`
    params = {
        "max_length": max_length, #@markdown - Max length is a parameter that specifies the maximum number of tokens that the summary can have. This parameter is usually used to ensure that the summary does not become too long and loses its essence. If the summary exceeds the maximum length, it is truncated to meet the length constraint. For example, if max length is set to 100, the summary will have a maximum of 100 tokens.
        "min_length": min_length,
        
        "no_repeat_ngram_size": 3, #@markdown - "no_repeat_ngram_size": 3: This parameter is used to avoid repetition of n-grams (sequences of words) in the generated text. Setting the value to 3, for example, would ensure that no three-word sequence is repeated in the generated text. This helps to improve the diversity of the generated text and make it sound more natural.

        "early_stopping": True, #@markdown - "early_stopping": True: This parameter is used to stop generation early if certain conditions are met. In the case of text generation, it usually means stopping the generation if the model predicts an end-of-sequence token (such as a period or question mark) for all generated outputs. This helps to avoid generating unnecessary text beyond the point where the model has already predicted an end to the sentence or paragraph.
        
        "repetition_penalty": 3.5, #@markdown - "repetition_penalty": 3.5: This parameter is used to penalize the model for generating repeated tokens. The higher the value of the repetition penalty, the more the model is discouraged from repeating tokens in the generated text.
        
        "length_penalty": length_penalty, #@markdown - penalty length is a parameter used to encourage the model to generate shorter summaries. It works by imposing a penalty on the score of the generated summary based on its length. The longer the summary, the higher the penalty, and the lower the overall score. This encourages the model to generate more concise summaries. Penalty length is often used in conjunction with other methods for controlling summary length, such as max length.
        
        "encoder_no_repeat_ngram_size": 3, #@markdown - "encoder_no_repeat_ngram_size": 3: This parameter is similar to "no_repeat_ngram_size", but it applies specifically to the encoder part of the model. It is used to avoid encoding repeated n-grams in the input text, which could lead to the model producing repetitive or redundant output.
        
        "num_beams": 4, #@markdown - "num_beams": 8: This parameter is used in beam search decoding, a method for generating multiple possible outputs and selecting the one with the highest probability. Setting "num_beams" to 8, for example, means that the model generates 8 possible outputs and selects the one with the highest probability. This helps to improve the quality of the generated text by considering multiple possibilities for each sequence.
    }
    summarizer = pipeline("summarization", model= model_name , tokenizer=tokenizer,
                      device='cpu',)
    res = summarizer(chunk,**params , do_sample=False)
    del summarizer # Clear GPU memory of transformers.pipeline
    torch.cuda.empty_cache()
    res[0]['summary_text'] = f'\n\n\nChunk {count}:\n\n' + res[0]['summary_text']
    all_summaries += res
  return all_summaries




# Combining all the individual parts into a single function
# Input to this function is path to the pdf
# This function do all the pre-processing, get the summary and save it in the pdf
# Parameter to this function is only the path to the pdf

def find_summary(raw_text, pdf_path, model_name, tokenizer ,words_in_chunk, max_length, min_length, length_penalty):
  chunks = text_chunking(raw_text, words_in_chunk)   # chunk the large text into small parts so it can be supplied to the model
  all_summaries = model_summary(chunks, model_name, tokenizer, max_length, min_length, length_penalty) # passing the chunks to the model for the summarization
  joined_summary = ' '.join([summ['summary_text'] for summ in all_summaries])  # combine all chunks of summaries to single
  txt_to_save = (joined_summary.encode('latin1','ignore')).decode("latin1")  # This ignore the "aphostrope" which is little problematic
  spl = pdf_path.split('/') # Splitting the path based on "/" to get the name of the book or pdf
  file_name = spl[-1][:-4]+"_summary.pdf" # Summary is added at the end i.e book name is the_alchemist so it becomes -> the_alchemist_summary.pdf etc.
  text_to_pdf(txt_to_save, file_name)





# load model and tokenizer 
hugging_face_model =  r'E:\GradProject\FLASK\code\models\summarization_model'
model_name, tokenizer = load_model_and_tokenizer(hugging_face_model)

# load text file 
#input_filepath = r'files_folder\files_received\19_Oliver_Twist_by_Charles_Dickens\Oliver_Twist_by_Charles_Dickens.txt'

#@markdown read textfile into the `long_text` var
#with open(input_filepath, 'r', encoding='utf-8', errors='ignore') as f:
#    long_text = f.read()

# count number of words in text
#word_count = len(long_text.split())
#print("Number of words in the file:", word_count)
#print(f"First 1500 chars of input file:\n\n{long_text[:1500]} ...")


# output path pdf file 
#pdf_path = "Summary.pdf"

def create_input_and_output(req_id):
    input_file_path = None
    long_text = None
    output_path = None
    output_folder = None
    long_text = None
    for folder in os.listdir(UPLOAD_FOLDER):
        if folder.startswith(str(req_id)):
            input_file_path = os.path.join(os.path.join(UPLOAD_FOLDER, folder),os.listdir(os.path.join(UPLOAD_FOLDER, folder))[0])
            break
    for folder in os.listdir(PROCESSED_FOLDER):
        if folder.startswith(str(req_id)):
            output_folder = os.path.join(PROCESSED_FOLDER, folder)
            break
    output_path = os.path.join(output_folder,"services_output","Summary.pdf")
    with open(input_file_path, 'r', encoding='utf-8', errors='ignore') as f:
        long_text = f.read()
    return long_text, output_path

def run_summarization(req_id,length_penalty):   
    long_text, pdf_path = create_input_and_output(req_id)
    find_summary(long_text, pdf_path, model_name, tokenizer, words_in_chunk, max_length, min_length, length_penalty)

#run_summarization(19,50)
