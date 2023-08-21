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
def read_sheet(sheet = 0):
    wks = sh[sheet]
    try:
        data = wks.get_as_df()
    except Exception as e:
        print('Exception in read of Google Sheet', e)
    return data




#### Two versions of the page -> Landing page vs. Car Pool
### Logged in state (RHD Staff Management)
if check_password():
    ## Header
    header(title = 'RHD Staff Managment', data_desc = 'officers location', expanded = st.session_state['header'])
    st.title('RHD Staff Managment')


    ## Open the spreadsheet and the first sheet
    # Getting credentials
    client = google_sheet_credentials()

    # Opening sheet
    sh = client.open_by_key(st.secrets['google']['spreadsheet_id'])
    print('Opened Google Sheet: ', sh)
    


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
            officers = read_sheet(sheet = 1)
            name = st.selectbox('Officer', options = officers['Officer'].unique())
            phone = st.text_input('Phone', value = officers.loc[officers['Officer'] == name]['Phone'].values[0])
            phone = phone.replace("+", "'+")
            mail = st.text_input('Mail', value = officers.loc[officers['Officer'] == name]['Mail'].values[0])
            duty_loc = st.selectbox('Location of duty', options = ['RHD office Area 4', 'MoH office Capital Hill', 'home office', 'in the field', 'out of country', 'on leave', 'sick leave', 'other'])
            duty_place = ''
            if duty_loc == 'in the field':
                places_r = read_sheet(sheet = 2)
                duty_place = st.selectbox('Place of duty', options = places_r['District'].unique())
            
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
                for d in data:
                    if d[1][0:1] != "'+":
                        d[1] = d[1].replace("+", "'+")

                # Add data to existing
                newrow = np.array([name, phone, mail, duty_loc, duty_place, duty_comment, str(date_start), str(date_end)])
                data = np.vstack((data, newrow))
            
                # Converting numby array to list
                data = data.tolist()
            
                # Writing to worksheet
                try:
                    wks = sh[0]
                    wks.update_values(crange = 'A2', values = data)
                    st.session_state['google'] = True
                    read_sheet.clear()
                    print('Updated Google Sheet')
                    st.info(body = 'Data successfully submitted!', icon = "✅")
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
            range_date = [date.today() - timedelta(days = 4), date.today() + timedelta(days = 14)]
            for idx, row in all_data.iterrows():
                if (datetime.date(datetime.strptime(row['Date from'], '%d/%m/%Y')) >= range_date[0] and datetime.date(datetime.strptime(row['Date from'], '%d/%m/%Y')) <= range_date[1]):
                    actual_data.append(row)
            actual_data = pd.DataFrame(actual_data)
                     
            # Show data
            try:
                st.dataframe(actual_data[['Officer', 'Phone', 'Mail', 'Location', 'Place', 'Comment', 'Date from', 'Date to']])
            except:
                st.info('No current data', icon = "ℹ️")


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
            range_date = [date.today() - timedelta(days = 4), date.today() + timedelta(days = 14)]
            for idx, row in all_data.iterrows():
                if (datetime.date(datetime.strptime(row['Date from'], '%d/%m/%Y')) >= range_date[0] and datetime.date(datetime.strptime(row['Date from'], '%d/%m/%Y')) <= range_date[1]):
                    actual_data.append(row)
            actual_data = pd.DataFrame(actual_data)
            places = all_data['Place'].unique()
            df = pd.DataFrame([[-13.9550205, 33.7101647]], columns = ['lat', 'lon'])
            places_cordinates = read_sheet(sheet = 2)
            for place in places:
                for cordinate in places_cordinates['District']:
                    if place == cordinate:
                        lat = str(places_cordinates.loc[places_cordinates['District'] == cordinate]['lat.'].values)[1:-1]
                        lon = str(places_cordinates.loc[places_cordinates['District'] == cordinate]['lon.'].values)[1:-1]
                        df.loc[len(df.index)] = [float(lat), float(lon)]
            try:
                # Map
                st.map(df)
            except:
                st.info('No current data', icon = "ℹ️")


                
            
            
            
    #### Outside the form
    
### Not Logged in state (Landing page)
else:
    landing_page(' RHD Staff Management')


