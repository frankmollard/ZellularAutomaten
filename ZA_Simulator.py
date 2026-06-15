import streamlit as st
import streamlit_authenticator as stauth
import numpy as np
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
from matplotlib import pyplot as plt
import gc

import yaml
from yaml.loader import SafeLoader

import warnings 
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Zellularautomaten",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.linkedin.com/in/frank-mollard/',
        'Report a bug': "https://www.linkedin.com/in/frank-mollard/",
        'About': "# Diese App dient der Simulation von Jäger Beute Schemen"
    }
)

with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)
    
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    #config['preauthorized']
)

try:
    authenticator.login()
except Exception as e:
    st.error(e)

st.title("Jäger Beute Simulation durch Zellularautomaten")

#########SIDEBAR###########
with st.sidebar.form("simulation_form"):
    st.image("vawiaial.png", width = 120)
    """
    
    
    """
    submitted = st.form_submit_button("Simulieren")
    
    matrixGroesse = st.select_slider(
       "Größe der Matrix",
       options=list(np.linspace(10, 50, 40).astype(np.int8)),
       value=30
    )  
    iterationCount = st.select_slider(
       "Anzahl der Simulationsschritte",
       options=list(np.linspace(1000, 200000, 200).astype(np.int32)),
       value=1000
    )  
    prozentJaeger = st.select_slider(
       "Anteil Jäger zu Beginn in %",
       options=list(np.linspace(1, 100, 101).astype(np.int8)),
       value=15
    )  
    prozentBeute = st.select_slider(
       "Anteil Beute zu Beginn in %",
       options=list(np.linspace(1, 100, 101).astype(np.int8)),
       value=15
    )  
    geburtenBeute = st.select_slider(
       "Wieviele Beutetiere müssen für\neine Geburt im Umfels sein\nund keine Jäger",
       options=list(np.linspace(1, 8, 8).astype(np.int8)),
       value=3
    )
    geburtenJaeger = st.select_slider(
       "Wieviele Raubtiere müssen für\neine Geburt im Umfels sein\nund keine Beute",
       options=list(np.linspace(1, 8, 8).astype(np.int8)),
       value=3
    )
    beuteProJaeger = st.select_slider(
       "Beute pro Jäger (für fressen und verteidigen)",
       options=list(np.linspace(0, 2, 21).astype(np.float16)),
       value=1
    )
    wieseWandern = st.select_slider(
       "Wieviel Wiese muss für Wanderung da sein?",
       options=list(np.linspace(1, 8, 8).astype(np.int8)),
       value=3
    )
    randomSprung = st.select_slider(
       "Wahrscheinlichkeit für zufälligen Sprung",
       options=list(np.linspace(0, 100, 11).astype(np.int8)),
       value=20
    )
    randomTot = st.select_slider(
       "Wahrscheinlichkeit für zufälliges Sterben",
       options=list(np.linspace(0, 100, 101).astype(np.int8)),
       value=20
    )   
    verhungerungsFaktor = st.select_slider(
       "Wenn kein Futter, um welchen Faktor erhöht\nsich die Sterblichkeit (1=keine Erhöhung)",
       options=list(np.linspace(1, 10, 91).astype(np.float16)),
       value=3
    )   

def clear_Q():
    st.session_state["Q"] = 0

@st.cache_data(show_spinner=False)
def Moore_Umgebung_read(r,c, Zustand0):
    """
    r=row
    c=column
    Zustand0=aktueller Zustand der Matrix
    """

    Zustand0 = Zustand0.copy()
    
    target = Zustand0[r,c].tolist()
    
    left = Zustand0[r, c-1].tolist()
    upLeft = Zustand0[r-1, c-1].tolist()
    up = Zustand0[r-1, c].tolist()
    upRight = Zustand0[r-1, c+1].tolist()
    right = Zustand0[r, c+1].tolist()
    lowRight = Zustand0[r+1, c+1].tolist()
    low = Zustand0[r+1, c].tolist()
    lowLeft = Zustand0[r+1, c-1].tolist()
    
    return [target, left, upLeft, up, upRight, right, lowRight, low, lowLeft]

@st.cache_data(show_spinner=False)
def bedingungen(seeds, test, gdB: int = 3, gdJ: int = 3, bpj: int = 1, ww: int = 3, randSprung: float = 0.1, randTot: float = 0.01, verhungernFaktor: float = 2):
    """
    gd=wieviele müssen für Geburt im Moore Umfeld sein
    bpj=beute pro jäger (für fressen und verteidigen)
    ww=wieviel Wiese muss für Wanderung da sein
    randSprung=Wahrscheinlichkeit für Zufallssprung
    randTot=Wahrscheinlichkeit für Zufallstod
    verhungernFaktor=Wenn kein Futter, um welchen Faktor erhöht sich die Sterblichkeit
    """

    t = test.copy()
    BeuteImUmfeld = np.where(np.array(t[1:]) == 1)[0]
    JägerImUmfeld = np.where(np.array(t[1:]) == -1)[0]
    WieseImUmfeld = np.where(np.array(t[1:]) == 0)[0]

    verhungern_tod = np.clip(randTot*verhungernFaktor, 0, 1).item()
    
    #random Tot
    np.random.seed(seed=seeds+1)
    rt = np.random.rand(1,1)[0][0]
    if rt < randTot and t[0] != 0:
        t[0] = 0    
        return t

    #random Sprung
    np.random.seed(seed=seeds)
    rs = np.random.rand(1,1)[0][0]
    if WieseImUmfeld.shape[0] != 0 and rs < randSprung and t[0] != 0:
        rnd = np.random.randint(0, WieseImUmfeld.shape[0])
        wandern = WieseImUmfeld[rnd]+1#+1 weil erstes Element die Mitte ist
        t[wandern] = t[0]
        t[0] = 0
        return t

    #Verhungern
    if BeuteImUmfeld.shape[0] == 0 and rt < verhungern_tod and t[0] == -1:
        t[0] = 0 
        return t
    if WieseImUmfeld.shape[0] == 0 and rt < verhungern_tod and t[0] == 1:
        t[0] = 0 
        return t

    else:
        if JägerImUmfeld.shape[0] != 0 and BeuteImUmfeld.shape[0] / JägerImUmfeld.shape[0] <= bpj and t[0] == -1 \
        and BeuteImUmfeld.shape[0] != 0:#wandern
            rnd = np.random.randint(0, BeuteImUmfeld.shape[0])
            wandern = BeuteImUmfeld[rnd]+1#+1 weil erstes Element die Mitte ist
            t[wandern] = -1
            t[0] = 0
                
        elif JägerImUmfeld.shape[0] != 0 and BeuteImUmfeld.shape[0] / JägerImUmfeld.shape[0] > bpj and t[0] == -1:#sterben
            t[0] = 0
                  
        elif BeuteImUmfeld.shape[0] == 0 and JägerImUmfeld.shape[0] >= gd and t[0] == 0:#Jäger geboren
            t[0] = -1
                
        elif JägerImUmfeld.shape[0] == 0 and BeuteImUmfeld.shape[0] >= gd and t[0] == 0:#Beute geboren
            t[0] = 1

    ##########################################################################################################NEU
        elif JägerImUmfeld.shape[0] != 0 and WieseImUmfeld.shape[0] >= ww and t[0] == 1:#Beute wandert
            rnd = np.random.randint(0, WieseImUmfeld.shape[0])
            wandern = WieseImUmfeld[rnd]+1#+1 weil erstes Element die Mitte ist
            t[wandern] = 1
            t[0] = 0

    ##########################################################################################################Neu ENDE
        else:
            t = t
        
    return t

@st.cache_data(show_spinner=False)
def changeMoore(r, c, UmgebungsVektor, Zustand0):

    """
    r=row
    c=column
    UmgebungsVektor=Moore_Umgebung_read result
    Zustand0=aktueller Zustand der Matrix
    """
    
    Zn = Zustand0.copy()
    
    Zn[r, c] = UmgebungsVektor[0]
    Zn[r, c-1] = UmgebungsVektor[1]
    Zn[r-1, c-1] = UmgebungsVektor[2]
    Zn[r-1, c] = UmgebungsVektor[3]
    Zn[r-1, c+1] = UmgebungsVektor[4]
    Zn[r, c+1] = UmgebungsVektor[5]
    Zn[r+1, c+1] = UmgebungsVektor[6]
    Zn[r+1, c] = UmgebungsVektor[7]
    Zn[r+1, c-1] = UmgebungsVektor[8]
    
    return Zn


def trajektorie(mG, iC, percJaeger, percBeute, **kwargs):
    
    width=int(mG)
    height=width
    percJaeger=percJaeger/100
    percBeute=percBeute/100
    percWiese=1-percJaeger-percBeute
    
    z = np.random.choice([-1,0,1], size=(height, width), replace=True, p=[percJaeger, percWiese, percBeute])
    Z0 = z.copy()
    iterationen = iC
    randRow = np.random.randint(1, z.shape[0]-1, iterationen)#-1 bis 1, weil die Ränder wegen Moore Umgebung ausgespart werden.
    randCol = np.random.randint(1, z.shape[0]-1, iterationen)
    
    trajektorie = [Z0]
    animationFrame = np.zeros(Z0.shape[0])
    
    W, J, B=[], [], []
    
    for iterations, (r, c) in enumerate(zip(randRow, randCol)):
        Z0 = changeMoore(
            r, 
            c, 
            bedingungen(
                iterations, 
                Moore_Umgebung_read(r, c, Z0), 
                **kwargs
            ), 
            Z0
        )

        persistIter = iterationen / 1000
        if iterations % persistIter == 0: # genau 1000 mal wird W, J, B gespeichert
            W.append(np.where(np.reshape(Z0, shape=(-1)) == 0)[0].shape[0]/(height*width))
            J.append(np.where(np.reshape(Z0, shape=(-1)) == -1)[0].shape[0]/(height*width))
            B.append(np.where(np.reshape(Z0, shape=(-1)) == 1)[0].shape[0]/(height*width))

        persistIter = iterationen / 100
        if iterations % persistIter == 0: # genau 100 mal wird Z0 gespeichert
            trajektorie.append(Z0)

        if iterations % 100 == 0:
            progress = (iterations + 100) / iterationen
            progress_bar.progress(progress)
            status_text.write(f"Simulation: {iterations + 100} / {iterationen}")
    
    return {"Trajektorie": np.array(trajektorie), "Wiese": W, "Beute": B, "Jaeger": J}


def attraktorPlot(wbj, iC):
    iterationen = iC
    persistIter = iterationen / 10
    xlabels = [ic for ic in range(iterationen + 1) if ic % persistIter == 0]
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.set_title("Attraktor")
    ax.plot(wbj["Wiese"], c="green", label= "Wiese")
    ax.plot(wbj["Beute"], c="orange", label= "Beute")
    ax.plot(wbj["Jaeger"], c="red", label= "Jäger")
    ax.set_xticks([i*100 for i in list(range(len(xlabels)))])
    ax.set_xticklabels(xlabels)
    ax.tick_params(axis='x', labelrotation=45)
    ax.spines["top"].set_visible(False); ax.spines['right'].set_visible(False)
    ax.legend()
    return fig

@st.cache_data(show_spinner=False)
def SimulationPlot(simTraject):

    colorscale = [
        (0, "red"),     
        (0.5, "green"),  
        (1, "orange")     
    ]

    fig = px.imshow(
        (simTraject+1)/2,#damit aus -1,0,1 -> 0,0.51 wird
        animation_frame=0,  # first axis is the frame index
        binary_string=False,
        labels=dict(animation_frame="Frame"),
        color_continuous_scale=colorscale,
        origin="lower"
    )

    # Improve layout
    fig.update_layout(
        title="Trajektorie aufgeteilt auf 100 Zyklen",
        coloraxis_showscale=True,
        coloraxis=dict(
            cmin=0,
            cmax=1,
            colorbar=dict(
                tickvals=[0,0.5,1],
                ticktext=[f"{i}" for i in ["Jäger", "Wiese", "Beute"]]
            )
        ),
        width=900,   # Fixed width in pixels
        height=600,  # Fixed height in pixels
        sliders=[{
            "currentvalue": {"prefix": "Frame: "}
        }]
    )
    #fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 50
    #fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 50
    return fig

##########START#################
if st.session_state['authentication_status']:
    st.session_state["runs"] += 1 
    if st.session_state["runs"] >= 2:
        st.session_state["Q"] = 1
        if submitted:
            gc.collect()
            with st.status("Simulation Läuft...", expanded=True):

                progress_bar = st.progress(0)
                status_text = st.empty()
                try:
                    st.session_state["TRAJECTORIE"] = trajektorie(
                        mG=matrixGroesse, 
                        iC=iterationCount, 
                        percJaeger=prozentJaeger, 
                        percBeute=prozentBeute, 
                        gdB = geburtenBeute,
                        gdJ = geburtenJaeger,
                        bpj=beuteProJaeger, 
                        randSprung=randomSprung/100, 
                        randTot=int(randomTot)/100, 
                        verhungernFaktor=verhungerungsFaktor
                    )
                except Exception as e:
                    st.error("Die Simulation ist fehlgeschlagen.")
                    st.exception(e)
                    
        if "TRAJECTORIE" in st.session_state:
            # Display the plots in Streamlit
            st.pyplot(attraktorPlot(st.session_state["TRAJECTORIE"], iterationCount), use_container_width=False)
            st.plotly_chart(SimulationPlot(st.session_state["TRAJECTORIE"]["Trajektorie"]))
            
        
        with st.sidebar:
            authenticator.logout()
    
    else:
        st.error("rerun")
        st.rerun()
    
elif st.session_state['authentication_status'] is False:
    st.error('Falscher Username oder Passwort')
elif st.session_state['authentication_status'] is None:
    st.warning('Bitte Username und Passwort eingeben')
    if 'runs' not in st.session_state:
        st.session_state["runs"] = 0
        st.session_state["text"] = ""
    else:
        st.session_state["runs"] = 0
        st.session_state["text"] = ""
    if 'Q' not in st.session_state:
        st.session_state["Q"] = 0
    else:
        st.session_state["Q"] = 0
