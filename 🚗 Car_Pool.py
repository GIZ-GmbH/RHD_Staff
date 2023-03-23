##### `🚗 Car_Pool.py`
##### Car Pool
##### Open-Source, hosted on https://github.com/DrBenjamin/Car_Pool
##### Please reach out to ben@benbox.org for any questions
#### Loading needed Python libraries
import streamlit as st
import extra_streamlit_components as stx
import streamlit_scrollable_textbox as sty
import platform
import pandas as pd
import numpy as np
import cv2
import mysql.connector
import os
from google_drive_downloader import GoogleDriveDownloader
import pygsheets
import shutil
from datetime import datetime



#### Streamlit initial setup
try:
    st.set_page_config(
        page_title = "GIZ MW Car Pool",
        page_icon = st.secrets['custom']['car_pool_image_thumbnail'],
        layout = "centered",
        initial_sidebar_state = "expanded",
        menu_items = {
            'Get Help': st.secrets['custom']['menu_items_help'],
            'Report a bug': st.secrets['custom']['menu_items_bug'],
            'About': '**Car Pool**'
        }
    )
except Exception as e:
    print(e)




#### OS Check
### Check for 3 different platforms
## Check which OS
plt = platform.system()
if plt == "Windows":
    print("Your system is Windows")
elif plt == "Linux":
    print("Your system is Linux")
elif plt == "Darwin":
    print("Your system is MacOS")




#### Query parameters
## Get param `EMPLOYE_NO`
eno = st.experimental_get_query_params()


## Get params for trainings / workshops
# [code]




#### Initialization of session states
## Session states
if ('admin' not in st.session_state):
    st.session_state['admin'] = False
if ('logout' not in st.session_state):
    st.session_state['logout'] = False
if ('header' not in st.session_state):
    st.session_state['header'] = True




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
    header = st.sidebar.radio(label = 'Switch headers on or off', options = ('on', 'off'), index = index,
                              horizontal = True)
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



### Function: init_connection = Initial SQL connection
def init_connection():
    try:
        ## Initialize connection
        return mysql.connector.connect(**st.secrets["mysql_car"])
    except:
        print("An exception occurred in function `init_connection`")
        st.error(body = 'Databank connection timeout!', icon = "🚨")
        st.stop()



### Function: run_query = SQL query
def run_query(query):
    with conn.cursor() as cur:
        # Perform query
        try:
            cur.execute(query)
            return cur.fetchall()

        except:
            print('An exception occurred in function `run_query` with query \"' + query + '\"')



### Function: lastID = checks for last ID number in Table (to add data after)
def lastID(url):
    query = "SELECT MAX(ID) FROM %s;" % (url)
    rows = run_query(query)

    # Check for ID
    for row in rows:
        if (row[0] != None):
            id = int(row[0]) + 1
        else:
            id = 1
            break

    # Return ID
    return id



### Function: check_vehicles = checking for unique Vehicles IDs
def check_vehicles(column, data):
    vehicle = []
    i = 0
    while i < len(data):
        if i > 0:
            x = 0
            double = False
            for x in range(len(vehicle)):
                if (vehicle[x] == data[column][i + 1]):
                    double = True
            if (double != True):
                vehicle.append(data[column][i + 1])
        else:
            vehicle.append(data[column][i + 1])
        i += 1
    return vehicle



### Function: pictureUploaderDrivers = uploads driver images
def pictureUploaderDrivers(image, index):
    # Initialize connection
    connection = mysql.connector.connect(**st.secrets["mysql_car"])
    cursor = connection.cursor()

    # SQL statement
    sql_insert_blob_query = """ UPDATE DRIVERS SET DRIVER_IMAGE = %s WHERE ID = %s;"""

    # Convert data into tuple format
    insert_blob_tuple = (image, index)
    result = cursor.execute(sql_insert_blob_query, insert_blob_tuple)
    connection.commit()



### Function: pictureUploaderVehicles = Uploads vehicle images
def pictureUploaderVehicles(image, index):
    # Initialize connection
    connection = mysql.connector.connect(**st.secrets["mysql_car"])
    cursor = connection.cursor()

    # SQL statement
    sql_insert_blob_query = """ UPDATE VEHICLES SET VEHICLE_IMAGE = %s WHERE ID = %s;"""

    # Convert data into tuple format
    insert_blob_tuple = (image, index)
    result = cursor.execute(sql_insert_blob_query, insert_blob_tuple)
    connection.commit()




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



    ### Custom Tab with IDs
    chosen_id = stx.tab_bar(data = [
        stx.TabBarItemData(id = 1, title = "Trips", description = "can see open Trips"),
        stx.TabBarItemData(id = 2, title = "Driver", description = "can enter Trips"),
    ], default = 1)
    with st.form("Car Pool", clear_on_submit = True):
        ## tab `Trips`
        if (f"{chosen_id}" == '1'):
            st.title('Hitchhiker')
            st.subheader('Look for a trip')
            
            # Read worksheet first to add data
            try:
                data = wks.get_as_df()
            except Exception as e:
                print('Exception in read of Google Sheet', e)
            
            # Convert numpy in pandas dataframe
            actual_data = []
            data["ID"] = data.index + 1
            data = pd.DataFrame(data = data, columns = ["ID", "Driver", "Phone", "Departure", "Destination", "Date", "Time", "Seats"])
            data = data.set_index('ID')
            print(data)
            for idx, row in data.iterrows():
                print(idx, row)
                print(datetime.strptime(row['Date'], '%d/%m/%Y'))
                print(datetime.now())
                if datetime.strptime(row['Date'], '%d/%m/%Y') >= datetime.now():
                    actual_data.append(row)

            st.dataframe(actual_data)
            


        ## tab `Driver`
        elif (f"{chosen_id}" == '2'):
            st.title('Drivers')
            st.subheader('Enter a Trip')
            name = st.text_input('Name')
            phone = st.text_input('Phone')
            dep = st.text_input('Departure')
            des = st.text_input('Destination')
            date = st.date_input('Date')
            time = st.time_input('Time')
            seats = st.number_input('Seats', min_value = 1, max_value = 6, value = 1)

            # Read worksheet first to add data
            try:
                data = wks.get_as_df()
            except Exception as e:
                print('Exception in read of Google Sheet', e)

                
        ## Submit button
        submitted = st.form_submit_button('Submit')
        if submitted:
            # Creating numpy array
            data = np.array(data)
    
            # Add data to existing
            newrow = np.array([name, phone, dep, des, str(date), str(time), seats])
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


            
    #### Outside the form
    
### Not Logged in state (Landing page)
else:
    landing_page('the Car Pool.')


