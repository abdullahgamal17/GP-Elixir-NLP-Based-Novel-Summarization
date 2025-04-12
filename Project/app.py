from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os


# set working directory
os.chdir(r"E:\GradProject\FLASK")

UPLOAD_FOLDER = r'files_folder\files_received'
PROCESSING_FOLDER = r'files_folder\files_processed'
ALLOWED_EXTENSIONS = ('txt')
SECRET_KEY = 'secretkey'



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

db = SQLAlchemy(app)

class ServiceRequest(db.Model):
    id = db.Column(db.Integer(),primary_key=True)
    
    char_net_selected = db.Column(db.String(),nullable = False)
    emotion_selected = db.Column(db.String(),nullable = False)
    char_map_selected = db.Column(db.String(),nullable = False)
    summary_selected = db.Column(db.String(),nullable = False)
    review_analysis_selected = db.Column(db.String(),nullable = False)
    
    email = db.Column(db.String(),nullable = False)
    goodreads_link = db.Column(db.String())
    storygraph_link = db.Column(db.String())
    summary_range = db.Column(db.Integer(),nullable = False)
    emotions = db.Column(db.String(),nullable = True)


    filename = db.Column(db.String(),nullable = False)
    done_status = db.Column(db.String(),nullable = False)

#class Finished_Requested_Services(db.Model):
#    id = db.Column(db.Integer(),primary_key=True)
#    request_id = db.Column(db.Integer(),nullable = False)

#with app.app_context():
    #db.create_all()


@app.route('/')
def main_page():
    return render_template('index.html')

@app.route('/about')
def about_page():
    return render_template('about.html')

@app.route('/contact')
def contact_page():
    return render_template('contact.html')

@app.route('/submitted')
def submitted_page():
    return render_template('thanks.html')

@app.route('/Character_Network')
def character_network_page():
    return render_template('service1.html')

@app.route('/Emotion_Analysis')
def emotion_analysis_page():
    return render_template('service2.html')

@app.route('/Character_Map')
def character_map_page():
    return render_template('service3.html')

@app.route('/Novel_Summarization')
def novel_summarization_page():
    return render_template('service4.html')

@app.route('/Review_Analysis_Recommendation')
def review_analysis_page():
    return render_template('service5.html')

@app.route('/Form',methods=["GET","POST"])
def form_page():
    services_dict = {"char_net" : "0",
                     "emotion" : "0",
                     "char_map" : "0",
                     "novel_sum" : "0",
                     "review" : "0"}
    if request.method == 'POST':
        file = request.files['file']
        if file.filename == '':
            pass
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            #file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))

        services_dict["char_net"] = request.form.get("choose1")
        services_dict["emotion"] = request.form.get("choose2")
        services_dict["char_map"] = request.form.get("choose3")
        services_dict["novel_sum"] = request.form.get("choose4")
        services_dict["review"] = request.form.get("choose5")

        email = request.form.get("email")
        summ_range = request.form.get("sum_range")
        goodreads_link = request.form.get("goodreads")
        storygraph_link = request.form.get("storygraph")
        emotions = request.form.get("emotions")
        name_of_file = filename.split(".")[0]

        for key,value in services_dict.items():
            if value == None:
                services_dict[key] = "0"

        req_to_add = ServiceRequest(char_net_selected = services_dict["char_net"],
                                    emotion_selected = services_dict["emotion"],
                                    char_map_selected = services_dict["char_map"],
                                    review_analysis_selected = services_dict["review"],
                                    email = email,
                                    goodreads_link = goodreads_link,
                                    storygraph_link = storygraph_link,
                                    summary_range=summ_range,
                                    filename = name_of_file,
                                    emotions = emotions,
                                    done_status = "0"
                                    )
        db.session.add(req_to_add)
        db.session.commit()
        
        id = db.session.query(ServiceRequest).order_by(ServiceRequest.id.desc()).first().id
        
        file_folder_name = str(id) + "_" 
        for name in name_of_file.split():
            file_folder_name += name + "_"
        file_folder_name = file_folder_name[:-1]
        os.mkdir(os.path.join(UPLOAD_FOLDER,file_folder_name))
        os.mkdir(os.path.join(PROCESSING_FOLDER,file_folder_name))

        os.mkdir(os.path.join(PROCESSING_FOLDER,file_folder_name,"needed_files"))
        #os.mkdir(os.path.join(PROCESSING_FOLDER,file_folder_name,"chapterized_book"))
        os.mkdir(os.path.join(PROCESSING_FOLDER,file_folder_name,"services_output"))

        os.mkdir(os.path.join(PROCESSING_FOLDER,file_folder_name,"services_output","Dashboard"))
        #os.mkdir(os.path.join(PROCESSING_FOLDER,file_folder_name,'services_output',"summary"))
        
        file.save(os.path.join(UPLOAD_FOLDER,file_folder_name,filename))
        #do_request(id,db.session)
        
        return redirect(url_for('submitted_page'))
    
    return render_template('formpage.html')


app.run()