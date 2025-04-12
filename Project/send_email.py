"""
######################################################################
Email With Attachments Python Script
Coded By "The Intrigued Engineer" over a coffee
Thanks For Watching!!!
######################################################################
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import shutil

# Setup port number and server name

smtp_port = 587                 # Standard secure SMTP port
smtp_server = "smtp.gmail.com"  # Google SMTP Server
#smtp_server = "aspmx.l.google.com"
PROCESSED_FOLDER = r"files_folder\files_processed"
# Set up the email lists
email_from = "graduation.project.elixir@gmail.com"
email_list = ["abdullahgamal74@gmail.com","ahmed3ahmed27@gmail.com"]

# Define the password (better to reference externally)
pswd = "fllnojcqjlebyklm" # As shown in the video this password is now dead, left in as example only


# name the email subject
subject = "Your Novel Analysis Dashboard is Ready!"



# Define the email function (dont call it email!)
def send_emails(req_id,email):
    folder_name = None
    for folder in os.listdir(PROCESSED_FOLDER):
        if folder.startswith(str(req_id)):
            folder_name = folder
            break
    folder = os.path.join(PROCESSED_FOLDER,folder_name,"services_output")
    for file in os.listdir(folder):
        if file.endswith(".pdf"):
            summary = os.path.join(folder,file)
            shutil.copy(summary,os.path.join(folder,"Dashboard","Elixir_Dashboard"))
            break 
    # zip the folder os.path.join(folder,"Dashboard","Elixir_Dashboard")
    shutil.make_archive(os.path.join(folder,"Dashboard","Elixir_Dashboard"), 'zip', os.path.join(folder,"Dashboard","Elixir_Dashboard"))
    filename_path = os.path.join(folder,"Dashboard","Elixir_Dashboard.zip")
    filename = 'Elixir_Dashboard.zip'
        # Make the body of the email
    body = f"""
🌟 Greetings! 🌟

I hope this email finds you well. I'm thrilled to inform you that your personalized Novel Analysis Dashboard is ready for your exploration! 📚✨ Our team has worked diligently to analyze the novel you provided and extract valuable insights to enhance your reading experience.

Before diving into the details, let me provide you with a brief overview of the services and features included in your dashboard:

    1️⃣ Character Networking: 🕸
        - We have detected and mapped all the characters in the novel, including the primary and secondary characters. Through our character networking analysis, you can explore the relationships between characters and gain insights into their interactions within the story.

    2️⃣ Emotions Analysis: 😂😍😭😡😳
        - Our sentiment analysis algorithm has identified the emotions and themes present throughout the narrative. This analysis will give you a deeper understanding of the storyline and the overall sensations conveyed within the novel.

    3️⃣ Character Map: 👨‍👩‍👧‍👦 👩‍❤️‍👨
        - Understanding the family & friendships relationships between characters is crucial for comprehending the story's dynamics. Our character map provides a visual representation of how characters interact and relate to each other, enabling you to gain a meaningful understanding of the narrative.

    4️⃣ Goodreads Review Sentiment Analysis: ⭐⭐⭐★★
        - We have incorporated sentiment analysis on Goodreads user reviews to provide you with additional insights and opinions from fellow readers. This feature allows you to compare our results with the viewpoints of other readers, further enriching your reading experience.

📂 The Dashboard will be attached to this email. You will find a user-friendly interface that enables seamless navigation through the various sections and features. Feel free to explore and interact with the analytical results to better understand the novel.


                                    ------------------------------------------------------------------------------------------------------------


To ensure a seamless experience, I would like to provide you with step-by-step instructions on how to set it up and access its features. Please follow these instructions carefully:

    1️⃣ Download the attached folder: "Result.zip"
            - Locate the email attachment named "Result.zip" and download it to your computer.

    2️⃣ Unzip the folder:
            - Extract the contents of the "Result.zip" folder. This action will create a new folder with the extracted files.

    3️⃣ Place the files in the same directory:
            - Ensure that all the files from the extracted folder are placed in the same directory or folder on your computer.

    4️⃣ Open the Novel Analysis Dashboard:
            - Locate the file named "Dashboard.html" among the extracted files. Double-click on the "Dashboard.html" file.

    5️⃣ Accessing the Dashboard on Google Chrome:
            - By double-clicking on the "Dashboard.html" file, it should automatically open in your default web browser.

Once you have completed these steps, you should be able to access and interact with your Novel Analysis Dashboard seamlessly ✅. It will provide you with a user-friendly interface to explore the various analytical results we have generated based on the novel you provided.

If you encounter any difficulties during the setup process or while operating the dashboard, please don't hesitate to reach out to us for assistance. We are here to ensure your experience is as smooth as possible.

Happy analyzing and enjoy your reading journey with the Novel Analysis Dashboard! 😊📊📖

Happy reading! 🌟

Best regards,

Ahmed Mohamed
ELIXIR

        """

        # make a MIME object to define parts of the email
    msg = MIMEMultipart()
    msg['From'] = email_from
    msg['To'] = email
    msg['Subject'] = subject

        # Attach the body of the message
    msg.attach(MIMEText(body, 'plain'))

        # Define the file to attach

        # Open the file in python as a binary
    attachment= open(filename_path, 'rb')  # r for read and b for binary

        # Encode as base 64
    attachment_package = MIMEBase('application', 'octet-stream')
    attachment_package.set_payload((attachment).read())
    encoders.encode_base64(attachment_package)
    attachment_package.add_header('Content-Disposition', "attachment; filename= " + filename)
    msg.attach(attachment_package)

        # Cast as string
    text = msg.as_string()

        # Connect with the server
    print("Connecting to server...")
    TIE_server = smtplib.SMTP(smtp_server, smtp_port)
    TIE_server.starttls()
    TIE_server.login(email_from, pswd)
    print("Succesfully connected to server")
    print()


        # Send emails to "person" as list is iterated
    print(f"Sending email to: {email}...")
    TIE_server.sendmail(email_from, email, text)
    print(f"Email sent to: {email}")
    print()

    # Close the port
    TIE_server.quit()


# Run the function
send_emails(8,"abdullahgamal74@gmail.com")
