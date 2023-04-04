import glob
from io import StringIO
from pathlib import Path
from typing import Optional, Union
from PIL import Image
import tempfile
import io

import pythreejs as tjs
import pyvista as pv
import streamlit.components.v1 as components
from ipywidgets.embed import embed_minimal_html
import streamlit as st

pv.set_jupyter_backend('pythreejs')

icon = Image.open("favicon.ico")
st.set_page_config(
    page_title="CellAlyse",
    page_icon=icon,
    layout="centered",
    initial_sidebar_state="expanded",
)
hide_streamlit_style = """
                <style>
                div[data-testid="stToolbar"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stDecoration"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stStatusWidget"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                #MainMenu {
                visibility: hidden;
                height: 0%;
                }
                header {
                visibility: hidden;
               height: 0%;
                }
                footer {
                visibility: hidden;
                height: 0%;
                }
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

folder_list = glob.glob("*")
folder_list = [f for f in folder_list if Path(f).is_dir()]
folder = st.sidebar.selectbox("Wähle einen Ordner aus:", folder_list)
st.write(folder)
# if there are subfolders, select one. Exclude other files
subfolder_list = glob.glob(f"{folder}/*")
subfolder_list = [f for f in subfolder_list if Path(f).is_dir()]
if len(subfolder_list) > 0:
    subfolder = st.sidebar.selectbox("Wähle einen Unterordner aus:", subfolder_list)
    st.write(subfolder)
    folder = subfolder

stl_files = [f for f in Path(f"{folder}").glob("*.stl")]
stl_files = [f.name for f in stl_files]

model = st.sidebar.selectbox("Wähle ein Modell aus:", stl_files)


st.sidebar.markdown("---")

with tempfile.NamedTemporaryFile(suffix="_streamlit") as f:
    st.write(f"{folder}/{model}")
    col1, col2 = st.sidebar.columns(2)
    color_stl = col1.color_picker("Modell", "#848b90")
    color_bkg = col2.color_picker("Hintergrund", "#0e1117")

    ## Initialize pyvista reader and plotter
    plotter = pv.Plotter(border=False, window_size=[500, 400])
    plotter.background_color = color_bkg

    f.write(open(f"{folder}/{model}", "rb").read())
    reader = pv.STLReader(f.name)

    ## Read data and send to plotter
    mesh = reader.read()
    plotter.add_mesh(mesh, color=color_stl)

    ## Export to a pythreejs HTML
    model_html = io.StringIO()
    plotter.export_html(model_html, backend='pythreejs')

    ## Show in webpage
    st.components.v1.html(model_html.getvalue(), height=400)
