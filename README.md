# Zellularautomaten – Jäger-Beute-Simulation

Dieses Repository enthält eine interaktive Simulation eines **Jäger-Beute-Systems mit zellulären Automaten**. Auf einem zweidimensionalen Gitter werden die zeitliche Entwicklung von Jägern, Beutetieren und freien Wiesenflächen sowie deren räumliche Verteilung untersucht.

Die Anwendung wurde mit [Streamlit](https://streamlit.io/) umgesetzt. Sämtliche Modellparameter können über eine grafische Benutzeroberfläche verändert werden. Die Ergebnisse werden als Zeitreihe und als animierte Heatmap dargestellt.

## Inhalt

- [Modellidee](#modellidee)
- [Zellzustände](#zellzustände)
- [Nachbarschaften](#nachbarschaften)
- [Simulationsregeln](#simulationsregeln)
- [Installation](#installation)
- [Konfiguration der Anmeldung](#konfiguration-der-anmeldung)
- [Anwendung starten](#anwendung-starten)
- [Bedienung und Parameter](#bedienung-und-parameter)
- [Ergebnisse](#ergebnisse)
- [Aufbau des Repositories](#aufbau-des-repositories)
- [Technische Umsetzung](#technische-umsetzung)
- [Hinweise und Grenzen](#hinweise-und-grenzen)

## Modellidee

Zelluläre Automaten bilden komplexe dynamische Systeme mithilfe einfacher lokaler Regeln ab. Das Modell besteht aus einem quadratischen Gitter. Jede Zelle repräsentiert entweder einen Jäger, ein Beutetier oder eine freie Wiesenfläche.

In jedem Simulationsschritt wird zufällig eine Zelle ausgewählt. Ihr Zustand und gegebenenfalls die Zustände benachbarter Zellen werden anhand der gewählten Regeln aktualisiert. Die Aktualisierung erfolgt somit **asynchron**: Pro Schritt wird nur eine lokale Umgebung betrachtet und verändert.

Das Modell ist stochastisch. Zufallsereignisse beeinflussen unter anderem Bewegung und Sterblichkeit. Über einen Seed lassen sich Simulationen dennoch reproduzieren.

## Zellzustände

Intern werden die drei möglichen Zustände numerisch codiert:

| Wert | Zustand | Darstellung |
|---:|---|---|
| `-1` | Jäger | Rot |
| `0` | Wiese | Grün |
| `1` | Beute | Orange |

Der anfängliche Wiesenanteil ergibt sich aus:

```text
Wiesenanteil = 100 % − Jägeranteil − Beuteanteil
```

Daher muss die Summe aus Jäger- und Beuteanteil kleiner als 100 % sein.

## Nachbarschaften

Für die Zustandsänderungen wird die Moore-Nachbarschaft verwendet. Die Anwendung unterstützt zwei Varianten:

- **Normal:** die acht direkt und diagonal angrenzenden Zellen
- **Erweitert:** zusätzlich zwölf weiter außen liegende Zellen; insgesamt werden 20 Nachbarzellen betrachtet

Am Rand des Gitters werden zwei zusätzliche Zellreihen und -spalten als Puffer geführt. Diese bleiben Wiese und verhindern, dass Tiere von außerhalb des eigentlichen Simulationsfeldes einwandern.

## Simulationsregeln

Die Regeln lassen sich über die Benutzeroberfläche parametrisieren. In vereinfachter Form umfasst das Modell folgende Prozesse:

### Geburt

- Beutetiere können auf einer Wiesenfläche entstehen, wenn sich genügend Beutetiere und keine Jäger in der Nachbarschaft befinden.
- Jäger können auf einer Wiesenfläche entstehen, wenn sich genügend Jäger und keine Beutetiere in der Nachbarschaft befinden.
- Optional kann die Geburt von Jägern bei einem zu geringen globalen Beuteanteil eingeschränkt werden.

### Jagd und Konkurrenz

- Ein Jäger kann ein Beutetier erbeuten und dessen Zelle übernehmen.
- Ob sich Jäger oder Beute durchsetzen, hängt vom Verhältnis zwischen Beutetieren und Jägern in der betrachteten Nachbarschaft ab.
- Optional können Jäger auch allein ein einzelnes Beutetier erlegen.

### Bewegung

- Tiere können mit einer einstellbaren Wahrscheinlichkeit zufällig auf eine freie Nachbarzelle springen.
- Beutetiere können ausweichen, wenn sich Jäger und ausreichend freie Wiesenflächen in ihrer Umgebung befinden.

### Sterblichkeit und Nahrungsmangel

- Jäger und Beutetiere können mit einer einstellbaren Grundwahrscheinlichkeit zufällig sterben.
- Fehlt Nahrung, wird die Sterbewahrscheinlichkeit mit einem Verhungerungsfaktor erhöht:

```text
P(Verhungern) = min(P(Zufallstod) × Verhungerungsfaktor, 1)
```

- Für Jäger bedeutet Nahrungsmangel, dass keine Beute in der Umgebung vorhanden ist.
- Für Beutetiere liegt Nahrungsmangel vor, wenn keine Wiese in der Umgebung vorhanden ist.
- Die Reihenfolge von Bewegung und Verhungern kann als Modellannahme verändert werden.

## Installation

Vorausgesetzt wird eine aktuelle Python-Installation. Das Repository kann anschließend geklont und die benötigten Pakete können installiert werden:

```bash
git clone https://github.com/frankmollard/ZellularAutomaten.git
cd ZellularAutomaten

python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Unter Windows wird die virtuelle Umgebung wie folgt aktiviert:

```powershell
.venv\Scripts\activate
```

Zu den wichtigsten Abhängigkeiten gehören:

- Streamlit
- Streamlit Authenticator
- NumPy
- pandas
- Plotly
- Matplotlib
- PyYAML

## Konfiguration der Anmeldung

Die Anwendung verwendet `streamlit-authenticator`. Vor dem Start muss deshalb im Hauptverzeichnis eine Datei `config.yaml` vorhanden sein. Ein vereinfachtes Schema sieht so aus:

```yaml
credentials:
  usernames:
    beispiel:
      email: beispiel@example.org
      name: Beispiel Benutzer
      password: "$2b$12$..."

cookie:
  expiry_days: 1
  key: "LANGER_ZUFAELLIGER_GEHEIMER_SCHLUESSEL"
  name: "zellularautomaten_cookie"
```

Passwörter dürfen nicht im Klartext gespeichert werden. Verwenden Sie ausschließlich sichere Passwort-Hashes und einen zufällig erzeugten Cookie-Schlüssel.

> **Sicherheit:** Eine produktive `config.yaml` mit Benutzerkonten, Passwort-Hashes oder Cookie-Schlüsseln sollte nicht in ein öffentliches Repository eingecheckt werden. Es empfiehlt sich, sie über `.gitignore` auszuschließen und stattdessen eine anonymisierte `config.example.yaml` bereitzustellen. Falls echte Zugangsdaten bereits veröffentlicht wurden, sollten diese unverzüglich ausgetauscht werden.

## Anwendung starten

Nach Installation und Konfiguration wird die Anwendung im Repository-Verzeichnis gestartet:

```bash
streamlit run ZA_Simulator.py
```

Streamlit zeigt anschließend die lokale Adresse der Anwendung an, üblicherweise:

```text
http://localhost:8501
```

Nach erfolgreicher Anmeldung können die Parameter in der Seitenleiste festgelegt und über **Simulieren** ausgeführt werden.

## Bedienung und Parameter

| Parameter | Bedeutung |
|---|---|
| Moore-Umfeld | Auswahl zwischen normaler und erweiterter Nachbarschaft |
| Seed | Startwert des Zufallszahlengenerators; identische Werte ermöglichen reproduzierbare Läufe |
| Größe der Matrix | Breite und Höhe des quadratischen Simulationsgitters |
| Simulationsschritte | Anzahl der lokal ausgeführten Zustandsänderungen |
| Anteil Jäger | Prozentualer Jägeranteil zu Beginn |
| Anteil Beute | Prozentualer Beuteanteil zu Beginn |
| Geburten Beute | Mindestzahl benachbarter Beutetiere für eine Geburt |
| Geburten Jäger | Mindestzahl benachbarter Jäger für eine Geburt |
| Beute pro Jäger | Schwellenwert für das lokale Kräfteverhältnis zwischen Beute und Jägern |
| Jäger als Einzelgänger | Legt fest, ob ein einzelner Jäger ein einzelnes Beutetier erlegen kann |
| Wiese für Beutewanderung | Mindestzahl freier Nachbarzellen für eine Ausweichbewegung |
| Zufälliger Sprung | Wahrscheinlichkeit einer zufälligen Bewegung |
| Zufälliges Sterben | Grundwahrscheinlichkeit für den zufälligen Tod eines Tieres |
| Verhungerungsfaktor | Multiplikator der Sterbewahrscheinlichkeit bei fehlender Nahrung |
| Verhungern oder Weggehen | Reihenfolge, in der Nahrungsmangel und Bewegung geprüft werden |
| Beuteschwelle | Beuteanteil, unterhalb dessen Jägergeburten eingeschränkt werden |

Einige Schwellenwerte können auf einen Wert gesetzt werden, der größer als die Zahl der betrachteten Nachbarzellen ist. Die entsprechende Regel kann dadurch faktisch deaktiviert werden.

## Ergebnisse

Nach Abschluss einer Simulation erzeugt die Anwendung zwei Visualisierungen:

### Entwicklung der Populationen

Ein Liniendiagramm zeigt die prozentualen Anteile von:

- Wiese
- Beute
- Jägern

über den Verlauf der Simulation. Falls eine Beuteschwelle festgelegt wurde, wird sie zusätzlich eingezeichnet.

### Räumliche Entwicklung

Eine animierte Plotly-Heatmap zeigt die Verteilung der drei Zellzustände auf dem Gitter. Über den Schieberegler kann die räumliche Entwicklung schrittweise betrachtet werden. Tooltips zeigen Position und Zustand einer Zelle.

Zusätzlich vergleicht die Anwendung die aktuellen Eingaben mit den Parametern des vorherigen Simulationslaufs.

## Aufbau des Repositories

```text
ZellularAutomaten/
├── .streamlit/
│   └── config.toml
├── ZA_Simulator.py
├── config.yaml
├── requirements.txt
├── vawiaial.png
└── README.md
```

| Datei | Aufgabe |
|---|---|
| `ZA_Simulator.py` | Streamlit-Oberfläche, Modellregeln, Simulation und Visualisierung |
| `requirements.txt` | Python-Abhängigkeiten |
| `config.yaml` | Konfiguration der Anmeldung |
| `.streamlit/config.toml` | Streamlit-Konfiguration |
| `vawiaial.png` | In der Seitenleiste angezeigte Grafik |

## Technische Umsetzung

Die zentralen Funktionen sind:

| Funktion | Aufgabe |
|---|---|
| `Moore_Umgebung_read()` | Liest den Zellkern und seine normale oder erweiterte Moore-Nachbarschaft aus |
| `bedingungen()` | Wendet Geburts-, Jagd-, Bewegungs- und Sterberegeln auf die lokale Umgebung an |
| `changeMoore()` | Schreibt die veränderte lokale Umgebung in die Gesamtmatrix zurück |
| `trajektorie()` | Initialisiert das Gitter und führt die stochastische Simulation aus |
| `attraktorPlot()` | Erstellt das Liniendiagramm der Populationsanteile |
| `SimulationPlot()` | Erstellt die animierte Heatmap der räumlichen Entwicklung |

Zur Begrenzung des Speicherbedarfs werden nicht sämtliche Zwischenzustände gespeichert:

- Populationsanteile werden über bis zu 1.000 Zeitpunkte erfasst.
- Gitterzustände werden über bis zu 200 Animationsframes gespeichert.
- Die maximale Zahl der Simulationsschritte ist im Quellcode auf 10.000.000 begrenzt.

## Hinweise und Grenzen

- Das Modell ist eine abstrahierte Simulation und keine empirisch kalibrierte Vorhersage realer Ökosysteme.
- Die Ergebnisse hängen stark von den gewählten Regeln, Wahrscheinlichkeiten und Anfangsbedingungen ab.
- Größere Gitter und sehr viele Iterationen erhöhen Laufzeit und Speicherbedarf.
- Ein identischer Seed ermöglicht nur dann einen sinnvollen Vergleich, wenn auch die übrigen Parameter und die Programmversion unverändert bleiben.
- Die Randzellen sind dauerhaft als Wiese definiert; das Modell verwendet daher keine periodischen Randbedingungen.
- Die Simulation aktualisiert zufällig ausgewählte lokale Umgebungen nacheinander und nicht alle Zellen gleichzeitig.

## Autor

Frank Mollard  
[LinkedIn](https://www.linkedin.com/in/frank-mollard/)

