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

maxIter = 10000000 #Es muss mit maxIter gearbeit werden, da sonst immer wieder andere zufallszahlen kommen würden
resolutionChart = 1000 #in welchen Intervallen werden Relationen der Elemente (Jäger, Beute, Wiese) persistiert.
resolutionHeat = 200 #in welchen Intervallen werden Zustände der Matrix persistiert.

st.set_page_config(
    page_title="Zellularautomaten",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.linkedin.com/in/frank-mollard/',
        'Report a bug': "https://www.linkedin.com/in/frank-mollard/",
        'About': "Diese App dient der Simulation von Jäger Beute Schemen.\nby Frank Mollard"
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

st.markdown(
    '<h3 style="font-size: 20px; color: #004D92;"><i>Jäger Beute Simulation durch Zellularautomaten</i></h3>',
    unsafe_allow_html=True
)

#########SIDEBAR###########
with st.sidebar.form("simulation_form"):
    st.image("vawiaial.png", width = 120)
    """
    
    
    """
    submitted = st.form_submit_button("Simulieren", help="Simulation begint mit Druck auf den 'Simulieren'-Button")
    
    seedNo = st.number_input(
        "Insert a seed", min_value = 0, step=1, format="%d", 
        help="Der Seed steuert die Zufallszahlen. Gleicher Seed bedeutet gleiche Simulation."
    )
    matrixGroesse = st.select_slider(
       "Größe der Matrix",
       options=list(np.linspace(10, 50, 40).astype(np.int8)),
       value=30,
       help="Größer der symmetrischen Matrix wählen."
    )  
    iterationCount = st.number_input(
        "Anzahl der Simulationsschritte\n1000 bis\n{:,} in Tausenderschritten".format(maxIter).replace(",", "."), 
        min_value = 1000, step=1000, max_value=maxIter, format="%d", value = 100000,
        help="Wieviele Änderungen sollen auf dem Feld durchgeführt werden?"
    ) 
    prozentJaeger = st.select_slider(
       "Anteil Jäger zu Beginn in %",
       options=list(np.linspace(1, 100, 101).astype(np.int8)),
       value=15,
       help="Anteil der Jäger auf dem Feld zu Beginn der Simulation.\n100 - Jäger - Beute = Wiese"
    )  
    prozentBeute = st.select_slider(
       "Anteil Beute zu Beginn in %",
       options=list(np.linspace(1, 100, 101).astype(np.int8)),
       value=15,
       help="Anteil der Beutetiere auf dem Feld zu Beginn der Simulation.\n100 - Jäger - Beute = Wiese"
    )  
    geburtenBeute = st.select_slider(
       "Wieviele Beutetiere müssen für\neine Geburt im Umfels sein\nund keine Jäger",
       options=list(np.linspace(2, 9, 8).astype(np.int8)),
       value=3,
       help="Wenn keine Jäger in der Nähe sind und stören, und mindestens X Beutetiere da sind\nmindestens natürlich zwei, aber ggf. auch mehr, die Wache stehen, dann kann ein Beutetier geboren werden.\nWichtig: dies gilt nur, wenn der Zellkern Wiese ist.\nWenn 9 dann sind Geburten ausgeschaltet, da das Moore Umfeld nur 8 Elemente hat - Die Bedingung würde somit nie erfüllt."
    )
    geburtenJaeger = st.select_slider(
       "Wieviele Raubtiere müssen für\neine Geburt im Umfels sein\nund keine Beute",
       options=list(np.linspace(2, 9, 8).astype(np.int8)),
       value=3,
       help="Wenn keine Beutetiere in der Nähe sind und stören, und mindestens X Jäger da sind\nmindestens natürlich zwei, aber ggf. auch mehr, die Wache stehen, dann kann ein Jäger geboren werden.\nWichtig: dies gilt nur, wenn der Zellkern Wiese ist.\nWenn 9 dann sind Geburten ausgeschaltet, da das Moore Umfeld nur 8 Elemente hat - Die Bedingung würde somit nie erfüllt."
    )
    beuteProJaeger = st.select_slider(
       "Beute pro Jäger (für fressen und verteidigen)",
       options=list(np.linspace(0, 2, 21).astype(np.float16)),
       value=1.7,
       help="Bis zu welchem prozentualen Anteil Beute pro Jäger kann sich ein Jäger gegen Beute durchsetzen.\n Beispiel: Wenn der Anteil bei 1 liegt, also z.B. 2x Beute und 2xJäger im Umfeld dann gewinnt der Jäger und tötet die Beute.\n ansonsten ist es andersherum."
    )
    einzelGaenger = st.selectbox(
        "Sind Jäger auch Einzelgänger?",
        ("nein", "ja"),
        help="Wenn einem Jäger ein einzelnes Beutetier begegnet und keine weiteren Jäger im Moore Umfeld sind, dann frisst der Jäger die Beute.\ndefault=nein"
    )
    wieseWandern = st.select_slider(
       "Wieviel Wiese muss für Beutewanderung da sein?",
       options=list(np.linspace(1, 8, 8).astype(np.int8)),
       value=2,
       help="Wieviele Elemente im Umfeld müssen freie Wiese sein, um eine Wanderung der Beute in das Moor Umfeld zu ermöglichen?"
    )
    randomSprung = st.select_slider(
       "Wahrscheinlichkeit für zufälligen Sprung",
       options=list(np.linspace(0, 100, 11).astype(np.int8)),
       value=20,
       help="Wie hoch ist die Wahrscheinlichkeit, dass ein Tier, egal welches in das Moore Umfeld wandert?"
    )
    randomTot = st.select_slider(
       "Wahrscheinlichkeit für zufälliges Sterben",
       options=list(np.linspace(0, 100, 101).astype(np.int8)),
       value=20,
       help="Wahrscheinlichkeit für zufälligen Tod eines Tieres."
    )   
    verhungerungsFaktor = st.select_slider(
       "Wenn kein Futter, um welchen Faktor erhöht\nsich die Sterblichkeit (1=keine Erhöhung)",
       options=list(np.linspace(1, 10, 91).astype(np.float16)),
       value=2.5,
       help="Um welchen Faktor erhöht sich die Wahrscheinlichkeit zu sterben, wenn kein Futter mehr da ist?\n Bei Beutetieren, wenn Wiese fehlt bei Jägern wenn Beutetiere fehlen."
    )   
    codeSwitch = st.selectbox(
        "Verhungern oder Weggehen",
        ("Verhungern -> Weggehen", "Weggehen -> Verhungern"),
        help="Hierbei handelt es sich um die Reihenfolge der Bedingungen.\nEntweder wird erst gefragt, ob der zufällige Hungertod eintritt, wenn nicht, wird danach nochmal gefragt\nob zufällig gesprungen wird, oder umgekehrt.\nTheoretisch könnte ersteres dadurch begründet werden, dass der Tod ein Binäres Ereignis ist und darüber entscheided\nob überhaupt noch ein Sprung möglich ist. Andererseits könnte man argumentieren, dass die Bewegung das Tier noch etwas länger am leben hält."
    )
    MooreGross = st.selectbox(
        "Moore Umfeld",
        ("Normal", "Erweitert"),
        help="Soll das Moore Umfeld erweitert werden?"
    )
    beuteSchwelle = st.select_slider(
       "Jäger keine Geburten mehr ab Beute %",
       options=list(np.linspace(0, 100, 101).astype(np.int8)),
       value=0,
       help="Wieviel Prozent Beute müssen da sein, bevor die Jäger keine Kinder mehr bekommen, da Futter fehlt?\nDefault=0. Der Parameter führt zum Aussterben der Jäger und ist mit Vorsicht\nanzuwenden."
    )


def Moore_Umgebung_read(r,c, Zustand0, erweitert: bool=False):
    """
    r=row
    c=column
    Zustand0=aktueller Zustand der Matrix
    erweitert=Moore Umgebung Erweitert?
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

    if erweitert:
        leftLeft = Zustand0[r, c-2].tolist()
        upLeftLeft = Zustand0[r-1, c-2].tolist()
        upUpLeft = Zustand0[r-2, c-1].tolist()
        upUp = Zustand0[r-2, c].tolist()
        upUpRight = Zustand0[r-2, c+1].tolist()
        upRightRight = Zustand0[r-1, c+2].tolist()
        rightRight = Zustand0[r, c+2].tolist()
        rightRightLow = Zustand0[r+1, c+2].tolist()
        lowLowRight = Zustand0[r+2, c+1].tolist()
        lowLow = Zustand0[r+2, c].tolist()
        lowLowLeft = Zustand0[r+2, c-1].tolist()
        leftLeftLow = Zustand0[r+1, c-2].tolist()

        return [target, left, upLeft, up, upRight, right, lowRight, low, lowLeft, 
                leftLeft, upLeftLeft, upUpLeft, upUp, upUpRight, upRightRight, 
                rightRight, rightRightLow, lowLowRight, lowLow, lowLowLeft, leftLeftLow
               ]

    return [target, left, upLeft, up, upRight, right, lowRight, low, lowLeft,]


def bedingungen(
    seeds, test, Zustand0,
    gdB: int = 3, gdJ: int = 3, bpj: int = 1, ww: int = 3, 
    randSprung: float = 0.1, randTot: float = 0.01, verhungernFaktor: float = 2, 
    reihenfolge: str = "Sterben -> Rennen", eG: str = "nein", bS: int = 5
):
    """
    seeds: Zufalls Seed
    test: Zellen Vektor
    Zustand0: Matrix
    gdX: wieviele müssen für Geburt im Moore Umfeld sein
    bpj: beute pro jäger (für fressen und verteidigen)
    ww: wieviel Wiese muss für Wanderung da sein
    randSprung: Wahrscheinlichkeit für Zufallssprung
    randTot: Wahrscheinlichkeit für Zufallstod
    verhungernFaktor: Wenn kein Futter, um welchen Faktor erhöht sich die Sterblichkeit
    reihenfolge: Erst random Sterben, wenn nicht random wandern, vice versa
    eG: Ist der Jäger auch Einzelgänger? default nein.
    bS = Beuteschwelle
    """
    
    t = test.copy()
    
    BeutePerc = np.sum(Zustand0[1:-1, 1:-1]==1)/Zustand0[1:-1, 1:-1].shape[0]**2# Nur wenn noch mindestens prozentBeute Beute da ist, kann es zu Geburten von Jägern kommen.
    bSRand = 1
    if BeutePerc < bS/100:
        bSRand = np.random.rand(1,1)[0][0]#Damit der Abbau der Jäger nicht so schlagartig kommt.
        
    BeuteImUmfeld = np.where(np.array(t[1:]) == 1)[0]
    JägerImUmfeld = np.where(np.array(t[1:]) == -1)[0]
    WieseImUmfeld = np.where(np.array(t[1:]) == 0)[0]

    verhungern_tod = np.clip(randTot*verhungernFaktor, 0, 1).item()
    
    #random Tot
    np.random.seed(seed=seeds+1)
    rt = np.random.rand(1,1)[0][0]
    if rt <= randTot and t[0] != 0:
        t[0] = 0    
        return t

    if reihenfolge == "Sterben -> Rennen":
        reihenfolge = [0,1]
    else:
        reihenfolge = [1,0]
        
    for abschnitt in reihenfolge:
        if abschnitt == 0:
            #Verhungern
            if BeuteImUmfeld.shape[0] == 0 and rt <= verhungern_tod and t[0] == -1:
                t[0] = 0 
                return t
            if WieseImUmfeld.shape[0] == 0 and rt <= verhungern_tod and t[0] == 1:
                t[0] = 0 
                return t
    
        if abschnitt == 1:
            #random Sprung
            np.random.seed(seed=seeds)
            rs = np.random.rand(1,1)[0][0]
            if WieseImUmfeld.shape[0] != 0 and rs < randSprung and t[0] != 0:
                rnd = np.random.randint(0, WieseImUmfeld.shape[0])
                wandern = WieseImUmfeld[rnd]+1 #+1 weil erstes Element Zellkern ist und aus WieseImUmfeld rausgenommen wurde
                t[wandern] = t[0]
                t[0] = 0
                return t

    if JägerImUmfeld.shape[0] != 0 and BeuteImUmfeld.shape[0] / JägerImUmfeld.shape[0] <= bpj and t[0] == -1 \
    and BeuteImUmfeld.shape[0] != 0:#wandern
        rnd = np.random.randint(0, BeuteImUmfeld.shape[0])
        wandern = BeuteImUmfeld[rnd]+1 #+1 weil erstes Element Zellkern ist und aus BeuteImUmfeld rausgenommen wurde
        t[wandern] = -1
        t[0] = 0

    elif JägerImUmfeld.shape[0] == 0 and BeuteImUmfeld.shape[0] == 1 and t[0] == -1 and eG == "ja": #Einzelgänger?
        wandern = BeuteImUmfeld[0]+1 #+1 weil erstes Element Zellkern ist und aus BeuteImUmfeld rausgenommen wurde
        t[wandern] = -1
        t[0] = 0    
            
    elif JägerImUmfeld.shape[0] != 0 and BeuteImUmfeld.shape[0] / JägerImUmfeld.shape[0] > bpj and t[0] == -1: #Jäger stirbt
        t[0] = 0
              
    elif BeuteImUmfeld.shape[0] == 0 and JägerImUmfeld.shape[0] >= gdJ and t[0] == 0 and BeutePerc >= bS/100*bSRand: #Jäger geboren wenn noch prozentBeute % Beute vorhanden
        t[0] = -1
            
    elif JägerImUmfeld.shape[0] == 0 and BeuteImUmfeld.shape[0] >= gdB and t[0] == 0:#Beute geboren
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

    if len(UmgebungsVektor) > 9:
        Zn[r, c-2] = UmgebungsVektor[9]
        Zn[r-1, c-2] = UmgebungsVektor[10]
        Zn[r-2, c-1] = UmgebungsVektor[11]
        Zn[r-2, c] = UmgebungsVektor[12]
        Zn[r-2, c+1] = UmgebungsVektor[13]
        Zn[r-1, c+2] = UmgebungsVektor[14]
        Zn[r, c+2] = UmgebungsVektor[15]
        Zn[r+1, c+2] = UmgebungsVektor[16]
        Zn[r+2, c+1] = UmgebungsVektor[17]
        Zn[r+2, c] = UmgebungsVektor[18]
        Zn[r+2, c-1] = UmgebungsVektor[19]
        Zn[r+1, c-2] = UmgebungsVektor[20]

    return Zn



def trajektorie(mG, iC, percJaeger, percBeute, MooreUmfeld: str = "Normal", seedX: int = 0, **kwargs):
    
    width=int(mG+4) # Weil zwei ausgespart werden - pro Seite
    height=width
    percJaeger=percJaeger/100
    percBeute=percBeute/100
    percWiese=1-percJaeger-percBeute

    if MooreUmfeld == "Normal":#Soll Umfeld erweitert werden? Wenn Ja, dann True. Default = False
        MooreUmfeld = False
    else: 
        MooreUmfeld = True

    np.random.seed(seedX)
    
    z = np.random.choice([-1,0,1], size=(height, width), replace=True, p=[percJaeger, percWiese, percBeute])
    Z0 = z.copy()
    iterationen = iC
    randRow = np.random.randint(2, z.shape[0]-2, maxIter)[:iterationen]#-2 bis 2, weil die Ränder wegen erweiterter Moore Umgebung ausgespart werden.
    randCol = np.random.randint(2, z.shape[0]-2, maxIter)[:iterationen]

    #Damit keine Tier von außen reinkommen.
    Z0[:2, :] = 0      # obere 2 Zeilen
    Z0[-2:, :] = 0     # untere 2 Zeilen
    Z0[:, :2] = 0      # linke 2 Spalten
    Z0[:, -2:] = 0     # rechte 2 Spalten
    
    trajektorie = [Z0[2:-2, 2:-2]]
    animationFrame = np.zeros(Z0.shape[0])
    
    W, J, B=[], [], []
    
    for iterations, (r, c) in enumerate(zip(randRow, randCol)):
        Z0 = changeMoore(
            r, 
            c, 
            bedingungen(
                iterations + seedX, 
                Moore_Umgebung_read(r, c, Z0, erweitert=MooreUmfeld), 
                Z0,
                **kwargs
            ), 
            Z0
        )

        #Damit keine Tier von außen reinkommen.
        Z0[:2, :] = 0      # obere 2 Zeilen
        Z0[-2:, :] = 0     # untere 2 Zeilen
        Z0[:, :2] = 0      # linke 2 Spalten
        Z0[:, -2:] = 0     # rechte 2 Spalten

        persistIter = iterationen / resolutionChart
        if iterations % persistIter == 0: # genau resolutionChart mal wird W, J, B gespeichert
            W.append(np.where(np.reshape(Z0[2:-2, 2:-2], shape=(-1)) == 0)[0].shape[0]/(int(mG)**2))
            J.append(np.where(np.reshape(Z0[2:-2, 2:-2], shape=(-1)) == -1)[0].shape[0]/(int(mG)**2))
            B.append(np.where(np.reshape(Z0[2:-2, 2:-2], shape=(-1)) == 1)[0].shape[0]/(int(mG)**2))

        persistIter = iterationen / resolutionHeat
        if iterations % persistIter == 0: # genau resolutionHeat mal wird Z0 gespeichert
            trajektorie.append(Z0[2:-2, 2:-2].copy())

        if iterations % 100 == 0:
            progress = (iterations + 100) / iterationen
            progress_bar.progress(progress)
            status_text.write(f"Simulation: {iterations + 100} / {iterationen}")
    
    return {"Trajektorie": np.array(trajektorie), "Wiese": W, "Beute": B, "Jaeger": J}

@st.cache_data(show_spinner=False)
def attraktorPlot(wbj, iC):
    iterationen = iC
    persistIter = iterationen / 10
    xlabels = [ic for ic in range(iterationen + 1) if ic % persistIter == 0]
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.set_title("Entwicklung über {:,} Iterationen".format(iterationen).replace(",", "."))
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

    hover_tmpl = (
        "Feld info:<br>"
        "x: %{x}<br>"
        "y: %{y}<br>"
        "Spezies: %{customdata}<extra></extra>"  # <extra></extra> entfernt trace name
    )

    simTraject = (simTraject+1)/2 #damit aus -1,0,1 -> 0,0.51 wird
    
    hoverdata = np.where(
        simTraject == 0, "Jäger",
        np.where(
            simTraject == 0.5, "Wiese", "Beute"
        )
    ) #alle Layer und Matrizen werden angepasst und dann als customdata verwendet.
    
    fig = px.imshow(
        simTraject,
        animation_frame=0,  # first axis is the frame index
        binary_string=False,
        labels=dict(animation_frame="Frame"),
        color_continuous_scale=colorscale,
        origin="lower"
    )

    # Ändere Layout
    fig.update_layout(
        title="Trajektorie aufgeteilt auf %s Zyklen" % (resolutionHeat),
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
    
    # Tooltip für initiales Bild
    fig.data[0].customdata = hoverdata[0]
    fig.data[0].hovertemplate = hover_tmpl

    # Tooltip für alle Animations-Frames
    for i, frame in enumerate(fig.frames):
        frame.data[0].customdata = hoverdata[i]
        frame.data[0].hovertemplate = hover_tmpl
        
    return fig

##########START#################
if st.session_state["authentication_status"]:
    with st.sidebar:
        authenticator.logout() 
    if "runs" not in st.session_state:
        st.session_state["runs"] = 0
    st.session_state["runs"] += 1 
    if st.session_state["runs"] >= 2:
        st.session_state["Q"] = 1
        if submitted:
            if int(prozentJaeger) + int(prozentBeute) >= 100:
                st.error(f"Jäger + Beute müssen zusammen < 100 % ergeben.\nJäger liegt bei {int(prozentJaeger)} und Beute bei {int(prozentBeute)}, also beide zusammen bei {int(prozentJaeger)+int(prozentBeute)}")
                st.stop()
            gc.collect()
            with st.status("Simulation Läuft...", expanded=True) as state:

                progress_bar = st.progress(0)
                status_text = st.empty()
                try:
                    st.session_state["TRAJECTORIE"] = trajektorie(
                        mG=matrixGroesse, 
                        iC=iterationCount, 
                        percJaeger=prozentJaeger, 
                        percBeute=prozentBeute, 
                        seedX = seedNo,
                        gdB = geburtenBeute,
                        gdJ = geburtenJaeger,
                        bpj=beuteProJaeger, 
                        ww = wieseWandern,
                        randSprung=randomSprung/100, 
                        randTot=int(randomTot)/100, 
                        verhungernFaktor=verhungerungsFaktor,
                        reihenfolge = codeSwitch,
                        eG = einzelGaenger,
                        MooreUmfeld = MooreGross,
                        bS  = beuteSchwelle
                    )
                    state.update(label="Simulation vollendet!", state="complete", expanded=False)
                except Exception as e:
                    st.error("Die Simulation ist fehlgeschlagen.")
                    st.exception(e)
                    
        if "TRAJECTORIE" in st.session_state:
            # Display the plots in Streamlit
            st.pyplot(attraktorPlot(st.session_state["TRAJECTORIE"], iterationCount), width="content")
            st.plotly_chart(SimulationPlot(st.session_state["TRAJECTORIE"]["Trajektorie"]))

        if "matrixGroesse t-1" in st.session_state:
            letzteEingabe = pd.DataFrame(
                {
                    "Parameter t-1": [
                        st.session_state["matrixGroesse t-1"],
                        st.session_state["seedNo t-1"],
                        st.session_state["iterationCount t-1"], 
                        st.session_state["prozentJaeger t-1"],
                        st.session_state["prozentBeute t-1"],
                        st.session_state["geburtenBeute t-1"],
                        st.session_state["geburtenJaeger t-1"],
                        st.session_state["beuteProJaeger t-1"],
                        st.session_state["einzelGaenger t-1"],
                        st.session_state["wieseWandern t-1"],
                        st.session_state["randomSprung t-1"],
                        st.session_state["randomTot t-1"],
                        st.session_state["verhungerungsFaktor t-1"],
                        st.session_state["codeSwitch t-1"],
                        st.session_state["MooreGross t-1"],
                        st.session_state["beuteSchwelle t-1"],
                        st.session_state["VerhungernProba t-1"],
                    ],
                    "Parameter t": [
                        matrixGroesse,
                        seedNo,
                        iterationCount,
                        prozentJaeger,
                        prozentBeute,
                        geburtenBeute,
                        geburtenJaeger,
                        beuteProJaeger,
                        einzelGaenger,
                        wieseWandern,
                        randomSprung,
                        randomTot,
                        verhungerungsFaktor,
                        codeSwitch,
                        MooreGross,
                        beuteSchwelle,
                        np.clip(int(randomTot)/100 * verhungerungsFaktor, 0, 1) * 100,
                    ]
                },
                index=[
                    "Matrix Größe",
                    "Seed",
                    "Iterationen",
                    "Start % Jäger",
                    "Start % Beute",
                    "Geburten Beute",
                    "Geburten Jäger",
                    "Beute pro Jäger",
                    "Jäger Einzelgänger?",
                    "Beute wandert",
                    "Zufall Sprung",
                    "Zufall Tot",
                    "Verhungern Faktor",
                    "Sterben oder rennen",
                    "Erweitetes Moore Umfeld",
                    "Beute % keine Jäger mehr",
                    "Verhungern Risiko in %",
                ]
            )

            st.text("Letzte und aktuelle Eingabe")
            letzteEingabe = letzteEingabe.astype(str)
            st.table(letzteEingabe)

        st.session_state["matrixGroesse t-1"] = matrixGroesse
        st.session_state["iterationCount t-1"] = iterationCount
        st.session_state["prozentJaeger t-1"] = prozentJaeger
        st.session_state["prozentBeute t-1"] = prozentBeute
        st.session_state["seedNo t-1"] = seedNo
        st.session_state["geburtenBeute t-1"] = geburtenBeute
        st.session_state["geburtenJaeger t-1"] = geburtenJaeger
        st.session_state["beuteProJaeger t-1"] = beuteProJaeger
        st.session_state["einzelGaenger t-1"] = einzelGaenger
        st.session_state["wieseWandern t-1"] = wieseWandern
        st.session_state["randomSprung t-1"] = randomSprung
        st.session_state["randomTot t-1"] = randomTot
        st.session_state["verhungerungsFaktor t-1"] = verhungerungsFaktor
        st.session_state["codeSwitch t-1"] = codeSwitch
        st.session_state["MooreGross t-1"] = MooreGross 
        st.session_state["beuteSchwelle t-1"] = beuteSchwelle
        st.session_state["VerhungernProba t-1"] = np.clip(int(randomTot)/100 * verhungerungsFaktor, 0, 1) * 100
        
    else:
        st.error("rerun")
        st.rerun()
    
elif st.session_state["authentication_status"] is False:
    st.error("Falscher Username oder Passwort")
elif st.session_state["authentication_status"] is None:
    st.warning("Bitte Username und Passwort eingeben")
    st.session_state["runs"] = 0
    st.session_state["text"] = ""
    st.session_state["Q"] = 0
