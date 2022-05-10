import streamlit as st
import pandas as pd
import template as t
from datetime import datetime
from random import random
import process as p 
import numpy as np

def erase():
    bbc = st.session_state['old']
    bbc = bbc.loc[bbc.id != st.session_state["id"], :]
    st.session_state['old'] = bbc
    
    options = st.session_state.opts
    if len(options) > 0:
        bbc = bbc.loc[bbc.category.isin(options), :]
    
    rng = st.session_state.sld
    bbc = bbc.loc[(bbc["release_date"].astype(float).astype(int) >= rng[0].year) & (bbc["release_date"].astype(float).astype(int) <= rng[1].year), :]
    
    st.session_state["df"] = bbc
    st.session_state["id"] = bbc.sample(1)["id"].item()


    
st.set_page_config(layout="wide")


bbc = pd.read_csv("bbc_data.csv")
if 'id' not in st.session_state:
    #img_size = "240x135"
    #bbc["image"] = [x.replace("{recipe}", img_size) for x in bbc["image"].values]
    bbc["release_date"] = bbc["release_date"].astype(str)
    bbc["release_date"] = [x.split()[-1] for x in bbc["release_date"]]
    bbc = bbc.loc[bbc.release_date != "nan",:]
    bbc = bbc.loc[bbc.synops_long != "", :]
    
    bbc = bbc.loc[~pd.isna(bbc.synops_long), :]
    bbc = bbc.loc[~pd.isna(bbc.category), :]

    #print(bbc.loc[bbc.synops_long == np.])
    data = p.get_tfidf(bbc.synops_long.values)
    bbc["labels"] = p.get_labels(data, 10).labels_
    st.session_state['df'] = bbc
    st.session_state['old'] = bbc
    st.session_state['id'] = 156
    st.session_state["groups"] = []
    st.session_state["range"] = []
    min_date = bbc.loc[ bbc.release_date != "nan", "release_date"].min()
    max_date = bbc.loc[ bbc.release_date != "nan", "release_date"].max()
    st.session_state["min"] = int(float(min_date))
    st.session_state["max"] = int(float(max_date))
    st.session_state["min_f"] = int(float(min_date))
    st.session_state["max_f"] = int(float(max_date))
    st.session_state["slider"] = []
    st.session_state["cmin"] = 5
    st.num = 10
else:
    bbc = st.session_state['df'] 

film = bbc[bbc['id'] == st.session_state['id']]


buttons, cover, info = st.columns([1,1,1])

def trigger_slider(): 
    rng = st.session_state.sld
    bbc = st.session_state['old']
    bbc = bbc.loc[(bbc["release_date"].astype(float).astype(int) >= rng[0].year) & (bbc["release_date"].astype(float).astype(int) <= rng[1].year), :]
    st.session_state["min"] = rng[0].year
    st.session_state["max"] = rng[1].year

    options = st.session_state.opts
    if len(options) > 0:
        bbc = bbc.loc[bbc.category.isin(options), :]

    st.session_state['df'] = bbc
    st.session_state["id"] = bbc.sample(1)["id"].item()
    
def trigger_butts():
    options = st.session_state.opts
    bbc = st.session_state['old'] 
    if len(options) > 0:
        bbc = bbc.loc[bbc.category.isin(options), :]
        
    rng = st.session_state.sld
    bbc = bbc.loc[(bbc["release_date"].astype(float).astype(int) >= rng[0].year) & (bbc["release_date"].astype(float).astype(int) <= rng[1].year), :]
    
    st.session_state['df'] = bbc
    st.session_state["id"] = bbc.sample(1)["id"].item()
    st.session_state["groups"] = options
    
with buttons:
    st.subheader('Customize your parameters!')
    rng = st.slider("When do you start?",
        value=(datetime(st.session_state["min"], 1, 1), datetime(st.session_state["max"], 1, 1)), min_value =datetime(st.session_state["min_f"], 1, 1), max_value = datetime(st.session_state["max_f"], 1, 1), on_change = trigger_slider, key = "sld")
    
    options = st.multiselect(
     'Choose category', options = st.session_state["old"].category.unique(), default = st.session_state["groups"], key = "opts", on_change = trigger_butts)
    st.button('👎 Delete me', key=random(), on_click=erase)

with cover:
    st.image(film['image'].iloc[0].replace("{recipe}", "352x198"))
    st.markdown(str(film['title'].item()))
    st.caption(str(film['description'].item()))
    

def change_clusters():
    num_min = st.session_state.num_cls
    st.session_state["cmin"] = num_min
    bbc = st.session_state['df'] 
    data = p.get_tfidf(bbc.synops_long.values)
    bbc["labels"] = p.get_labels(data, num_min).labels_

def shuffle():
    st.session_state['df'] = bbc
    st.session_state["id"] = bbc.sample(1)["id"].item()

with info:
    # display the book information
    #st.title(film['title'].iloc[0])
    #st.markdown(film['Book-Author'].iloc[0])
    st.button('Shuffle me!', key=random(), on_click=shuffle)
    st.slider("Choose number of clusters",
        value=(st.session_state["cmin"]), min_value = 2, max_value = 10, on_change = change_clusters, key = "num_cls")
    st.caption("Why it was chosen?")
    st.markdown("The inner working of this algorithm is based on adding similar descriptions of movies to common groups/clusters. Each cluster can be seen next to every movie ")

st.subheader('Something which matches the main content:')

t.recommendations(st.session_state['df'], film["labels"].item(), 7, True)

st.subheader('Something which does not match this content:')

t.recommendations(st.session_state['df'], film["labels"].item(), 7, False)