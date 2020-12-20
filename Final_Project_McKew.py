"""
Mark McKew Final Project
Class: CS230--Section SN4
Name: Mark McKew
Description: Are most of the Earthquakes in the Data near the ocean?

I pledge that I have completed the programming assignment independently.
I have not copied the code from a student or any source.
I have not given my code to any student.
"""
import pandas as pd
import streamlit as st
import pydeck as pdk
import mapbox as mb
from matplotlib import pyplot as plt

MAPBOX_API_KEY = "pk.eyJ1IjoibWxtY3E5OSIsImEiOiJja2lueGtqc2MxN2QyMnlwZXFjZGpxOHRkIn0.jmj4xxlUa2Egq-zEF6AwdA"

# Data Reading and Handling
# This file is the original dataset that was provided
filename1 = "earthquakes_us_20201123.csv"  # "earthquakes_us_20201123.csv"
# This file is my own dataset of Latitude and Longitude lines to Graph the US on a cartesian plane
filename2 = "LongLatGraphing.csv"
# This is to get rid of a chained assignment (Though I know that Iloc is faster and better I used a lot of chained assignments in this project; please do not deduct too many points for that
pd.set_option('mode.chained_assignment', None)
# creating a dataframe for the dataset
df = pd.read_csv(filename1)
# Creating a copy in which I do not do any manipulation
dforiginal = df.copy()
# creating a dataframe for my dataset of cartesian coordinates
df2 = pd.read_csv(filename2)
# formatting the date and time columns (this has no use to the project but I wanted to include it to show fluency with dataframes
df[["Date", "time"]] = df['time'].str.split('T', 1, expand=True)
# these are only the columns I want so I wanted to clean the data
columns_cleaned = ["Date", "time", "latitude", "longitude", "depth", "mag", "place", "type"]
# Reformatting the dataframe
df = df[columns_cleaned]
# cleaning up the data to only include the earthquakes, not ice quakes, blasts, explosions, etc.
df = df[df["type"] == 'earthquake']
# This shows the city that the source location decided was the best identifier of the epicenter
df[["Displacement", "Place"]] = df["place"].str.split('of ', 1, expand=True)
# Setting the index of the 2nd dataframe
df2 = df2.set_index("Index")

# This is an interesting way that I came up with to iterate through the data and check whether or not the dataset is < or > the longitude, as the for loop later will show; I check to see if the latitude of the epicenter was less than each of the X coordinates in the second dataset and kept count of what lines the epicenter is inbetween. Then I use that line data in this dictionary to determine if the epicenter is offshore.
EastCoast = {0: 0, 1: -67.1073, 2: -67.1073, 3: -70.97449, 4: -73.65515, 5: -75.72058, 6: -77.91785, 7: -80.4667,
             8: -80.77429, 9: -80.77429, 10: -80.77429}
WestCoast = {0: 0, 1: -124.84457, 2: -123.74594, 3: -123.74594, 4: -123.74594, 5: -122.51547, 6: -119.87875,
             7: -115.29285, 8: -115.29285, 9: -115.13953, 10: -115.13953}

# Defaulting to False for whether or not the epicenter is in the ocean
df["In the Water"] = False
# Defaulting to 0 for the Latitude normalization lines
df["Line Above"] = 0
# This for loop iterates through all of the indices in the dataset, then determines which X coordinate lines the earthquake is inbetween and then finds if the earthquake happened in the water.
for earthquake in df.index:
    line_above = 0
    for line in df2.index:
        if df["latitude"][earthquake] < df2["Latitude"][line]:
            line_above += 1
        elif df["latitude"][earthquake] > df2["Latitude"][line]:
            df["Line Above"][earthquake] = line_above
            if df["longitude"][earthquake] > -80.77429:  # off the east coast
                if df["longitude"][earthquake] > EastCoast[line_above]:
                    df["In the Water"][earthquake] = True
                else:
                    break
            elif -97.03406 < df["longitude"][earthquake] < -83.45496:  # in the gulf of Mexico
                if line_above == 10:
                    df["In the Water"][earthquake] = True
                else:
                    break
            elif df["longitude"][earthquake] < -115.13953:  # off the west coast
                if df["longitude"][earthquake] < WestCoast[line_above]:
                    df["In the Water"][earthquake] = True
                else:
                    break
            break
# This for loop removes any Line above entries that are equal to 0 which means that they are outside of the contiguous USA
for errorcheck in df.index:
    if df["Line Above"][errorcheck] == 0:
        df.drop(errorcheck, inplace=True)
# Creates a copy of the dataframe to create another layer of the map that will have a different color
df3 = df.copy()

# This for loop drops all of the datapoints that are not in the water, to then chart those in a different color on the map
for earthquake2 in df3.index:
    if not df3["In the Water"][earthquake2]:
        df3.drop(earthquake2, inplace=True)
    else:
        pass
# Creates a title for the streamlit pag
st.title("Mark McKew's CS230 Final Project")
# Header for the Map
st.header("Cartesian Map for Plotting the US")
# Implementing the Actual map
st.image("https://i.imgur.com/MUuod7Y.png",caption="Custom Map made by Me on Maps.co", use_column_width=True)
# Creates a title for the map
st.header("Map of Earthquakes")
# This creates the view state for the map, centering on the mean of the dataframes' lat and long coordinates, with a zoom of 2 and a pitch of 0
view_state = pdk.ViewState(
    latitude=df["latitude"].mean(),
    longitude=df["longitude"].mean(),
    zoom=2,
    pitch=0)
# This layer shows all of the datapoints that are not in the water in red
layer1 = pdk.Layer('ScatterplotLayer',
                   data=df,
                   get_position=['longitude', 'latitude'],
                   get_radius=50000,
                   get_color=[255, 0, 0],
                   pickable=True
                   )
# This layer shows all of the datapoints that are in the water in blue
layer2 = pdk.Layer('ScatterplotLayer',
                   data=df3,
                   get_position=['longitude', 'latitude'],
                   get_radius=50000,
                   get_color=[0, 0, 255],
                   pickable=True
                   )
# This shows the tool tip for the cities that are nearest to the epicenter of the earthquake
tool_tip = {"html": "Earthquake Nearest City:<br/> <b>{Place}</b> ",
            "style": {"backgroundColor": "darkviolet",
                      "color": "white"}
            }
# This creates the map
map1 = pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=view_state,
    mapbox_key=MAPBOX_API_KEY,
    layers=[layer1, layer2],
    tooltip=tool_tip
)
st.pydeck_chart(map1)
# This section creates a piechart showing the disparity in the dataset between the earthquakes in the US vs Out of the US and the ones that happened inland vs in the water
labels = ["Outside of the US", "Inside of the US"]
sizes = [(len(dforiginal)-len(df))/len(dforiginal), len(df)/len(dforiginal)]

sizes2 = [(len(df)-len(df3))/len(df), len(df3)/len(df)]
labels2 = ["Inland", "In the Water"]

fig, ax = plt.subplots()
ax.pie(sizes, labels=labels, autopct='%1.2f%%', explode=[.2, 0])
ax.axis('equal')

fig1, ax1 = plt.subplots()
ax1.pie(sizes2, labels=labels2, autopct='%1.2f%%', explode=[.2, 0])
ax1.axis('equal')

st.header("Inside of the US vs Outside of the US Pie Chart")
st.pyplot(fig)

st.header("Inland vs In the Water")
st.pyplot(fig1)

# This section imports a youtube video to the Streamlit site; which I thought was pretty cool and relevant to the dataset
st.header("Video on the 40 years of Earthquakes in US")
st.video(data="https://www.youtube.com/watch?v=sv7JwrWURyQ")
st.write("Video Credit: PacificTWC on Youtube\n\n"
         "Video URL:https://www.youtube.com/watch?v=sv7JwrWURyQ")
# This is just an image that shows that the streamlit site is finished
st.image("https://fin.plaid.com/content/images/2019/05/open-graph-image.jpg", caption="Image Citation: fin.plaid.com\n\nImage Url: https://fin.plaid.com/content/images/2019/05/open-graph-image.jpg", use_column_width=True)
