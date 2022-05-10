import streamlit as st
from random import random

# set episode session state
def select_book(id):
    st.session_state['id'] = id
    
def tile_item(column, item):
    with column:
        st.button('cluster: ' + str(item['labels']) + ' | open item!', key=random(), on_click=select_book, args=(item['id'], ))
        st.image(item['image'])
        st.caption(item['title'])


def recommendations(df, label, num, bl):

  # check the number of items
    if bl:
        df = df.loc[df.labels == label, :]
    else:
        df = df.loc[df.labels != label, :]
    try:
        df = df.sample(num)
    except:
        pass
    nbr_items = df.shape[0]
    img_size = "288x162"
    df["image"] = [x.replace("{recipe}", img_size) for x in df["image"].values]
    if nbr_items != 0:    
        columns = st.columns(nbr_items)
        items = df.to_dict(orient='records')
        any(tile_item(x[0], x[1]) for x in zip(columns, items))
