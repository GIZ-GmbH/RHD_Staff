##### `Car_Pool.py`
##### Car Pool
##### Open-Source, hosted on https://github.com/DrBenjamin/Car_Pool
##### Please reach out to ben@benbox.org for any questions
#### Loading needed Python libraries
import streamlit as st
import platform
import pandas as pd
import numpy as np
import os
from google_drive_downloader import GoogleDriveDownloader
import pygsheets
import shutil
from datetime import datetime
from datetime import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import sys
sys.path.insert(1, "module/")
import extra as stx




#### Streamlit initial setup
try:
    st.set_page_config(
        page_title = "GIZ MW Car Pool",
        page_icon = st.secrets['custom']['car_pool_image_thumbnail'],
        layout = "centered",
        initial_sidebar_state = "expanded",
        menu_items = {
            'About': '**Car Pool**'
        }
    )
except Exception as e:
    print(e)




#### Initialization of session states
## Session states
if ('admin' not in st.session_state):
    st.session_state['admin'] = False
if ('logout' not in st.session_state):
    st.session_state['logout'] = False
if ('header' not in st.session_state):
    st.session_state['header'] = True
if ('index' not in st.session_state):
    st.session_state['index'] = 1




#### All functions used exclusively in Car Fleet Management
### Function: check_password = Password / user checking
def check_password():
    # Session states
    if ("username" not in st.session_state):
        st.session_state["username"] = ''
    if ("password" not in st.session_state):
        st.session_state["password"] = ''
    if ("admin" not in st.session_state):
        st.session_state["admin"] = False
    if ("password_correct" not in st.session_state):
        st.session_state["password_correct"] = False
    if ('logout' not in st.session_state):
        st.session_state['logout'] = False
    
    # Checks whether a password entered by the user is correct
    def password_entered():
        try:
            if st.session_state["username"] in st.secrets["passwords"] and st.session_state["password"] == st.secrets["passwords"][
                st.session_state["username"]]:
                st.session_state["password_correct"] = True
                st.session_state["admin"] = False
                
                # Delete username + password
                del st.session_state["password"]
                del st.session_state["username"]
            
            # Checks whether a password entered by the user is correct for admins
            elif st.session_state["username"] in st.secrets["admins"] and st.session_state["password"] == st.secrets["admins"][
                st.session_state["username"]]:
                st.session_state["password_correct"] = True
                st.session_state["admin"] = True
                
                # Delete username + password
                del st.session_state["password"]
                del st.session_state["username"]
            
            # No combination fits
            else:
                st.session_state["password_correct"] = False
        except Exception as e:
            print('Exception in `password_entered` function. Error: ', e)
            st.session_state["password_correct"] = False
    
    ## Sidebar
    # Show Sidebar Header Image
    st.sidebar.image(st.secrets['custom']['sidebar_image'])
    
    # Header switch
    if st.session_state['header'] == True:
        index = 0
    elif st.session_state['header'] == False:
        index = 1
    else:
        index = 0
    header = st.sidebar.radio(label = 'Switch headers on or off', options = ('on', 'off'), index = index, horizontal = True)
    if header == 'on':
        st.session_state['header'] = True
    elif header == 'off':
        st.session_state['header'] = False
    else:
        st.session_state['header'] = True
    
    # First run, show inputs for username + password
    if "password_correct" not in st.session_state:
        st.sidebar.subheader('Please enter username and password')
        st.sidebar.text_input(label = "Username", on_change = password_entered, key = "username")
        st.sidebar.text_input(label = "Password", type = "password", on_change = password_entered, key = "password")
        return False
    
    # Password not correct, show input + error
    elif not st.session_state["password_correct"]:
        st.sidebar.text_input(label = "Username", on_change = password_entered, key = "username")
        st.sidebar.text_input(label = "Password", type = "password", on_change = password_entered, key = "password")
        if (st.session_state['logout']):
            st.sidebar.success('Logout successful!', icon = "✅")
        else:
            st.sidebar.error(body = "User not known or password incorrect!", icon = "🚨")
        return False
    
    else:
        # Password correct
        st.sidebar.success(body = 'You are logged in.', icon = "✅")
        st.sidebar.info(body = 'You can close this menu')
        st.sidebar.button(label = 'Logout', on_click = logout)
        return True



### Funtion: logout = Logout button
def logout():
    # Set `logout` to get logout-message
    st.session_state['logout'] = True
    
    # Set password to `false`
    st.session_state["password_correct"] = False



### Function header = Shows header information
def header(title, data_desc, expanded = True):
    with st.expander("Header", expanded = expanded):
        ## Header information
        st.title(title)
        st.image(st.secrets['custom']['facility_image'])
        st.header(st.secrets['custom']['facility'] + ' (' + st.secrets['custom']['facility_abbreviation'] + ')')
        st.subheader(st.secrets['custom']['facility_abbreviation'] + ' ' + data_desc)
        st.write('All data is stored in a secret Google Sheet for ' + st.secrets['custom'][
            'facility_abbreviation'] + '.')
        st.write(
            'The ' + title + ' is developed with Python (v' + platform.python_version() + ') and Streamlit (v' + st.__version__ + ').')



### Function: landing_page = Shows landing page
def landing_page(page):
    ## Title and information
    header = 'Welcome to the' + page
    st.title(header)
    st.header(st.secrets['custom']['facility'] + ' (' + st.secrets['custom']['facility_abbreviation'] + ')')
    st.subheader('User Login')
    st.info(body = 'Please login (sidebar on the left) to access the ' + page, icon = "ℹ️")
    
    

### google_sheet_credentials = Get google credentials file
@st.cache_resource
def google_sheet_credentials():
    ## Google Sheet API authorization
    output = st.secrets['google']['credentials_file']
    GoogleDriveDownloader.download_file_from_google_drive(file_id = st.secrets['google']['credentials_file_id'],
                                                          dest_path = './credentials.zip', unzip = True)
    client = pygsheets.authorize(service_file = st.secrets['google']['credentials_file'])
    if os.path.exists("credentials.zip"):
        os.remove("credentials.zip")
    if os.path.exists("google_credentials.json"):
        os.remove("google_credentials.json")
    if os.path.exists("__MACOSX"):
        shutil.rmtree("__MACOSX")

    # Return client
    return client



### Function: send_mail = Email sending
def send_mail(subject, body, receiver, attachment = None):
    ## Creating the SMTP server object by giving SMPT server address and port number
    smtp_server = smtplib.SMTP(st.secrets['mail']['smtp_server'], st.secrets['mail']['smtp_server_port'])

    # setting the ESMTP protocol
    smtp_server.ehlo()

    # Setting up to TLS connection
    smtp_server.starttls()

    # Calling the ehlo() again as encryption happens on calling startttls()
    smtp_server.ehlo()

    # Logging into out email id
    smtp_server.login(st.secrets['mail']['user'], st.secrets['mail']['password'])


    ## Message to be send
    msg = MIMEMultipart()  # create a message

    # Setup the parameters of the message
    msg['From'] = st.secrets['mail']['user']
    msg['To'] = receiver
    msg['Cc'] = ''
    msg['Subject'] = subject

    # Setup text
    msg.attach(MIMEText(body))

    # Setup attachment
    record = MIMEBase('application', 'octet-stream')
    record.set_payload(attachment)
    encoders.encode_base64(record)
    record.add_header('Content-Disposition', 'attachment', filename = '')
    msg.attach(record)


    ## Sending the mail by specifying the from and to address and the message
    try:
        smtp_server.sendmail(st.secrets['mail']['user'], receiver, msg.as_string())

        # Printing a message on sending the mail
        print('Mail successfully sent to ' + receiver)
        st.success(body = 'Email succesfully sent to ' + receiver, icon = "✅")

        # Terminating the server
        smtp_server.quit()
    except Exception as e:
        print("An exception occurred in function `send_mail` ", e)
        st.error(body = 'No Mail sent!', icon = "🚨")




#### Two versions of the page -> Landing page vs. Car Pool
### Logged in state (Car Fleet Management System)
if check_password():
    ## Header
    header(title = 'Car Pool', data_desc = 'available trips', expanded = st.session_state['header'])
    st.title('Car Pool')


    ## Open the spreadsheet and the first sheet
    # Getting credentials
    client = google_sheet_credentials()

    # Opening sheet
    sh = client.open_by_key(st.secrets['google']['spreadsheet_id'])
    wks = sh.sheet1
    
    
    ## Check for Requests
    # Read worksheet first to add data
    try:
        all_data = wks.get_as_df()
    except Exception as e:
        print('Exception in read of Google Sheet', e)

    # Set index
    all_data["ID"] = all_data.index + 1
    all_data = all_data.set_index('ID')



    ### Custom Tab with IDs
    chosen_id = stx.tab_bar(data = [
        stx.TabBarItemData(id = 1, title = "Hitchhiker", description = "can see open Trips"),
        stx.TabBarItemData(id = 2, title = "Driver", description = "can enter Trips"),
        stx.TabBarItemData(id = 3, title = "Requester", description = "can ask for a Trip"),
    ], default = st.session_state['index'])
    with st.form("Car Pool", clear_on_submit = True):
        ## tab `Hitchhiker`
        if (f"{chosen_id}" == '1'):
            st.title('Hitchhiker')
            st.subheader('Look for a trip')
            
            # Search for trips in the future
            actual_data = []
            for idx, row in all_data.iterrows():
                if datetime.strptime(row['Date'], '%d/%m/%Y') >= datetime.now() and row['Request'] == 'FALSE':
                    actual_data.append(row)
            request = ''
            button = 'Request'
            st.dataframe(actual_data)


        ## tab `Driver`
        elif (f"{chosen_id}" == '2'):
            st.title('Drivers')
            st.subheader('Enter a Trip')
            name = st.text_input('Name')
            phone = st.text_input('Phone')
            mail = st.text_input('Mail')
            dep = st.text_input('Departure')
            des = st.text_input('Destination')
            date = st.date_input('Date')
            time_start = st.time_input('Start Time', value = time(11, 30))
            time_end = st.time_input('Approx. Arrival', value = time(12, 45))
            seats = st.number_input('Seats', min_value = 1, max_value = 6, value = 1)
            request = 'FALSE'
            button = 'Enter'


        ## tab `Requester`
        elif (f"{chosen_id}" == '3'):
            st.title('Request')
            st.subheader('Ask for a Trip')
            name = st.text_input('Name')
            phone = st.text_input('Phone')
            mail = st.text_input('Mail')
            dep = st.text_input('Departure')
            des = st.text_input('Destination')
            date = st.date_input('Date')
            time = st.slider('Arrival time (range)', value = (time(11, 30), time(12, 45)))
            time_start = time[0]
            time_end = time[1]
            seats = st.number_input('Seats', min_value = 1, max_value = 6, value = 1)
            request = 'TRUE'
            button = 'Ask'

        
        ## Submit button
        submitted = st.form_submit_button(button)
        if submitted:
            if request != '':
                # Read worksheet first to add data
                try:
                    data = wks.get_as_df()
                except Exception as e:
                    print('Exception in read of Google Sheet', e)
                    
                # Creating numpy array
                data = np.array(data)
        
                # Add data to existing
                newrow = np.array([name, phone, mail, dep, des, str(date), str(time_start), str(time_end), seats, request])
                data = np.vstack((data, newrow))
        
                # Converting numby array to list
                data = data.tolist()
        
                # Writing to worksheet
                try:
                    wks.update_values(crange = 'A2', values = data)
                    st.session_state['google'] = True
                    print('Updated Google Sheet')
                except Exception as e:
                    print('No Update to Google Sheet', e)
            else:
                st.session_state['index'] = 3
                st.experimental_rerun()
            
            
            
            
    #### Outside the form
    
### Not Logged in state (Landing page)
else:
    landing_page(' GIZ MW Car Pool')


