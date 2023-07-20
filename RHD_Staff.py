##### `RHD_Staff.py`
##### RHD Staff Management
##### Open-Source, hosted on https://github.com/SeriousBenEntertainment/RHD_Staff
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
from calendar import month_abbr
from datetime import datetime, date, time, timedelta
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
        page_title = "RHD Staff Management",
        page_icon = st.secrets['custom']['rhd_image_thumbnail'],
        layout = "centered",
        initial_sidebar_state = "expanded",
        menu_items = {
            'About': '**RHD Staff Management**'
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




#### All functions used exclusively in RHD Staff Management
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
                                                          dest_path = './rhd_credentials.zip', unzip = True)
    client = pygsheets.authorize(service_file = st.secrets['google']['credentials_file'])
    if os.path.exists("rhd_credentials.zip"):
        os.remove("rhd_credentials.zip")
    if os.path.exists("rhd_credentials.json"):
        os.remove("rhd_credentials.json")
    if os.path.exists("__MACOSX"):
        shutil.rmtree("__MACOSX")

    # Return client
    return client



### Function read_sheet = Read data from Google Sheet
@st.cache_data
def read_sheet():
    try:
        data = wks.get_as_df()
    except Exception as e:
        print('Exception in read of Google Sheet', e)
    return data



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
    #record = MIMEBase('application', 'octet-stream')
    #record.set_payload(attachment)
    #encoders.encode_base64(record)
    #record.add_header('Content-Disposition', 'attachment', filename = '')
    #msg.attach(record)


    ## Sending the mail by specifying the from and to address and the message
    try:
        smtp_server.sendmail(st.secrets['mail']['user'], receiver, msg.as_string())

        # Printing a message on sending the mail
        print('Mail successfully sent to ' + receiver)
        #st.success(body = 'Email succesfully sent to ' + receiver, icon = "✅")

        # Terminating the server
        smtp_server.quit()
    except Exception as e:
        print("An exception occurred in function `send_mail` ", e)
        #st.error(body = 'No Mail sent!', icon = "🚨")




#### Two versions of the page -> Landing page vs. Car Pool
### Logged in state (Car Fleet Management System)
if check_password():
    ## Header
    header(title = 'RHD Staff Managment', data_desc = 'officers location', expanded = st.session_state['header'])
    st.title('RHD Staff Managment')


    ## Open the spreadsheet and the first sheet
    # Getting credentials
    client = google_sheet_credentials()

    # Opening sheet
    sh = client.open_by_key(st.secrets['google']['spreadsheet_id'])
    wks = sh.sheet1
    
    
    ## Send mail to Requester
    try:
        read_sheet.clear()
    except:
        print('No clearance of the cache')
    
    data_requester = read_sheet()

    data_check = []
    for idx, row in data_requester.iterrows():
        data_check.append(row)
    data_check = pd.DataFrame(data_check)
    
    data_trips = []
    for  idx, row in data_requester.iterrows():
        data_trips.append(row)
    data_trips = pd.DataFrame(data_trips)

    #for idx, row in data_trips.iterrows():
    #    for idy, row_check in data_check.iterrows():
    #        if row['Date'] == row_check['Date']:
    #            if datetime.date(datetime.strptime(row['Date'], '%d/%m/%Y')) >= date.today():
    #                info = row[['Mail', 'Departure', 'Start', 'Destination', 'Arrival', 'Seats']].to_string()
    #                send_mail(subject = 'Trip available', body = 'Dear ' + row_check['Driver'] + ',\n\na trip is available on ' + row['Date'] + ' from ' + row['Driver'] + ' - call on ' + row['Phone'] + '.\n\nInformation:\n' + info + '\n\nBest regards\n\nGIZ Car Pooling Service', receiver = row_check['Mail'], attachment = None)



    ### Custom Tab with IDs
    chosen_id = stx.tab_bar(data = [
        stx.TabBarItemData(id = 1, title = "Officers", description = "enter location of duty"),
        stx.TabBarItemData(id = 2, title = "Calendar", description = "view officers in a calendar view"),
        stx.TabBarItemData(id = 3, title = "Map", description = "view officers on a map"),
    ], default = st.session_state['index'])
    
    
    ## tab `Officers`
    if (f"{chosen_id}" == '1'):
        with st.expander('Officers', expanded = True):
            st.title('Location of duty')
            st.subheader('Enter your location data')
            name = st.selectbox('Officer', options = ['Benjamin', 'Chikondi', 'Chimwemwe', 'Chisomo', 'Davie', 'Dorothy', 'Esnart', 'Felix', 'Fiskani', 'Gloria', 'Grace', 'Humphrey', 'Ishmael', 'James', 'John', 'Joseph', 'Kondwani', 'Linda', 'Lloyd', 'Loveness', 'Maggie', 'Makina', 'Makweti', 'Mavuto', 'Moses', 'Mphatso', 'Nancy', 'Nelson', 'Nester', 'Nora', 'Paul', 'Peter', 'Rabecca', 'Raphael', 'Ruth', 'Samuel', 'Sangwani', 'Saulos', 'Shadreck', 'Sharon', 'Stella', 'Steven', 'Tapiwa', 'Thokozani', 'Tionge', 'Tiyamike', 'Trevor', 'Victor', 'Winston', 'Yamikani', 'Yohane', 'Zione'])
            phone = st.text_input('Phone')
            mail = st.text_input('Mail')
            duty_loc = st.selectbox('Location of duty', options = ['RHD office Area 4', 'MoH office Capital Hill', 'home office', 'in the field', 'out of country', 'on leave', 'sick leave', 'other'])
            
            duty_place = ''
            if duty_loc == 'in the field':
                duty_place = st.selectbox('Place of duty', options = ['Salima', 'Blantyre', 'Lilongwe', 'Mzuzu', 'Zomba'])
            
            duty_comment = ''
            if duty_loc == 'other':
                duty_comment = st.text_input('Comment')
            range_date = []
            date_start = st.date_input('Starting day')
            range_date.append(date_start)
            date_end = st.date_input('Ending day')
            range_date.append(date_end)

            # Submit button
            submitted = st.button('Submit')
            if submitted:
                # Read worksheet first to add data
                data = read_sheet()
                    
                # Creating numpy array
                data = np.array(data)
            
                # Add data to existing
                newrow = np.array([name, phone, mail, duty_loc, duty_place, duty_comment, str(date_start), str(date_end)])
                data = np.vstack((data, newrow))
            
                # Converting numby array to list
                data = data.tolist()
            
                # Writing to worksheet
                try:
                    wks.update_values(crange = 'A2', values = data)
                    st.session_state['google'] = True
                    print('Updated Google Sheet')
                    read_sheet.clear()
                except Exception as e:
                    print('No Update to Google Sheet', e)


    ## tab `Calendar`
    elif (f"{chosen_id}" == '2'):
        with st.expander("Calendar", expanded = True):
            st.title('Calendar')
            st.subheader('Officers location by date')
            
            # Read worksheet
            all_data = read_sheet()

            # Set index
            all_data["ID"] = all_data.index + 1
            all_data = all_data.set_index('ID')
            
            # Search for trips in the future
            actual_data = []

            # datetime date of today
            range_date = [date.today(), date.today() + timedelta(days = 7)]
            for idx, row in all_data.iterrows():
                if (datetime.date(datetime.strptime(row['Date from'], '%d/%m/%Y')) >= range_date[0] and datetime.date(datetime.strptime(row['Date from'], '%d/%m/%Y')) <= range_date[1]):
                    actual_data.append(row)
            actual_data = pd.DataFrame(actual_data)
            try:
                st.dataframe(actual_data[['Officer', 'Phone', 'Mail', 'Location', 'Place', 'Comment', 'Date from', 'Date to']].head(10))
            except:
                st.warning(body = 'No Trips in this range!', icon = "🚨")


    ## tab `Map`
    elif (f"{chosen_id}" == '3'):
        with st.expander("Map", expanded = True):
            st.title('Map')
            st.subheader('Officers location on the map')

            # Read worksheet
            all_data = read_sheet()

            # Set index
            all_data["ID"] = all_data.index + 1
            all_data = all_data.set_index('ID')
            
            # Search for trips in the future
            actual_data = []
            
            # datetime date of today
            range_date = [date.today(), date.today() + timedelta(days = 7)]
            for idx, row in all_data.iterrows():
                if (datetime.date(datetime.strptime(row['Date from'], '%d/%m/%Y')) >= range_date[0] and datetime.date(datetime.strptime(row['Date from'], '%d/%m/%Y')) <= range_date[1]):
                    actual_data.append(row)
            actual_data = pd.DataFrame(actual_data)
            places = all_data['Place'].unique()
            df = pd.DataFrame([[-13.9550205, 33.7101647]], columns = ['lat', 'lon'])
            for place in places:
                print(place)
                if place == 'Blantyre':
                    loc = [-15.7760278, 34.9483648]
                    df.loc[len(df.index)] = loc
                elif place == 'Salima':
                    loc = [-13.7790881, 34.4442415]
                    df.loc[len(df.index)] = loc
                elif place == 'Mzuzu':
                    loc = [-11.4313957, 33.9744892]
                    df.loc[len(df.index)] = loc
                elif place == 'Zomba':
                    loc = [-15.3927981, 35.3023974]
                    df.loc[len(df.index)] = loc
            try:
                # Map
                st.map(df)
            except:
                st.warning(body = 'No Officer in this range!', icon = "🚨")


                
            
            
            
    #### Outside the form
    
### Not Logged in state (Landing page)
else:
    landing_page(' RHD Staff Management')


