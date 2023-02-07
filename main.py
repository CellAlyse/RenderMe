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

folder = st.sidebar.selectbox(
    "Wähle einen Typ aus:",
    ("Komplett","Elektronik", "Objektiv", "komplexe Körper", "Tubus", "XYZ"),
)

# get all stl files in the folder 
stl_files = [f for f in Path(f"stl/{folder}").glob("*.stl")]
stl_files = [f.name for f in stl_files]

# let the user select a stl file
model = st.sidebar.selectbox("Wähle ein Modell aus:", stl_files)


st.sidebar.markdown("---")

col1,col2 = st.sidebar.columns(2)
color_stl = col1.color_picker("Element","#848b90")
color_bkg = col2.color_picker("Background","#0e1117")


plotter = pv.Plotter(border=False, window_size=[800,900]) 
plotter.background_color = color_bkg
with tempfile.NamedTemporaryFile(suffix=".stl") as stl_file:
    stl_file.write(open(f"stl/{folder}/{model}", "rb").read())
    reader = pv.STLReader(stl_file.name)


    mesh = reader.read()
    mesh = mesh.decimate(0.5)
    plotter.add_mesh(
        mesh,
        color=color_stl,
        specular=0.8,
        specular_power=20,

    )

    plotter.enable_eye_dome_lighting()
    plotter.enable_anti_aliasing()

    # increase quality of the mesh even more
    plotter.enable_depth_peeling()

    # add a better light source
    plotter.add_light(
        pv.Light(position=[0, 10, 10], intensity=0.8)
    )
    model_html = io.StringIO()
    plotter.export_html(model_html, backend="pythreejs")

    st.components.v1.html(model_html.getvalue(),height=900)
