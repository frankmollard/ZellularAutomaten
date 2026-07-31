# Zellularautomaten – Jäger-Beute-Simulation

Dieses Repository enthält eine interaktive **Jäger-Beute-Simulation auf Grundlage zellulärer Automaten**. Auf einem zweidimensionalen Gitter wird untersucht, wie sich Jäger, Beutetiere und freie Wiesenflächen unter verschiedenen lokalen Regeln und Zufallseinflüssen entwickeln.

Die Anwendung wurde mit [Streamlit](https://streamlit.io/)](https://zellularautomaten.streamlit.app) umgesetzt. Sämtliche Modellparameter können über eine grafische Benutzeroberfläche verändert werden. Die Ergebnisse werden als zeitliche Populationsentwicklung und als animierte räumliche Verteilung dargestellt.

## Inhalt

- [Modellidee](#modellidee)
- [Zellzustände](#zellzustände)
- [Nachbarschaften](#nachbarschaften)
- [Simulationsregeln](#simulationsregeln)
- [Anwendung verwenden](#anwendung-verwenden)
- [Parameter der Simulation](#parameter-der-simulation)
- [Ergebnisse auswerten](#ergebnisse-auswerten)
- [Installation und lokaler Start](#installation-und-lokaler-start)
- [Anmeldung](#anmeldung)
- [Aufbau des Repositories](#aufbau-des-repositories)
- [Technische Umsetzung](#technische-umsetzung)
- [Hinweise und Grenzen](#hinweise-und-grenzen)

## Modellidee

Zelluläre Automaten bilden komplexe dynamische Systeme mithilfe einfacher lokaler Regeln ab. Das Modell besteht aus einem quadratischen Gitter. Jede Zelle repräsentiert entweder einen Jäger, ein Beutetier oder eine freie Wiesenfläche.

In jedem Simulationsschritt wird zufällig eine Zelle ausgewählt. Ihr Zustand und gegebenenfalls die Zustände benachbarter Zellen werden anhand der eingestellten Regeln aktualisiert. Die Aktualisierung erfolgt **asynchron**: Pro Schritt wird eine lokale Umgebung betrachtet und verändert, nicht das gesamte Gitter gleichzeitig.

Das Modell enthält stochastische Elemente. Zufallsereignisse beeinflussen unter anderem Bewegung und Sterblichkeit. Über einen festen Seed lassen sich Simulationsläufe reproduzieren und miteinander vergleichen.

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

Die Summe aus Jäger- und Beuteanteil muss deshalb kleiner als 100 % sein.

## Nachbarschaften

Für die Zustandsänderungen wird die Moore-Nachbarschaft verwendet. Die Anwendung unterstützt zwei Varianten:

- **Normal:** die acht direkt und diagonal angrenzenden Zellen
- **Erweitert:** zusätzlich zwölf weiter außen liegende Zellen; insgesamt werden 20 Nachbarzellen betrachtet

Am Rand des Gitters werden zwei zusätzliche Zellreihen und -spalten als Puffer geführt. Diese bleiben Wiese und verhindern, dass Tiere von außerhalb des eigentlichen Simulationsfeldes einwandern.

## Simulationsregeln

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

## Anwendung verwenden

### 1. Anmelden

Beim Öffnen der Anwendung erscheint zunächst die Anmeldemaske. Benutzername und Passwort werden eingegeben und über die Schaltfläche zum Anmelden bestätigt.

Die Anmeldung dient als einfache Zugangsschranke vor der Streamlit-Anwendung. Sie schützt keine vertraulichen Daten. Ein gemeinsamer Demo- oder Gastzugang ist daher für diesen Anwendungsfall ausreichend.

Nach erfolgreicher Anmeldung werden die Bedienelemente in der linken Seitenleiste und der Ergebnisbereich im Hauptfenster angezeigt. Über **Logout** kann die Sitzung wieder beendet werden.

### 2. Nachbarschaft wählen

Im Auswahlfeld **Moore Umfeld** wird festgelegt, wie viele Nachbarzellen bei der Anwendung der Regeln berücksichtigt werden:

- **Normal** untersucht acht Nachbarzellen.
- **Erweitert** untersucht 20 Nachbarzellen.

Die gewählte Nachbarschaft beeinflusst insbesondere Geburten, Jagd, Bewegung und Nahrungsverfügbarkeit. Ergebnisse unterschiedlicher Nachbarschaften sollten daher nur unter Berücksichtigung dieser Modelländerung verglichen werden.

### 3. Grundeinstellungen festlegen

Vor der Simulation werden folgende Grundeinstellungen gewählt:

- **Seed:** steuert die verwendeten Zufallszahlen.
- **Größe der Matrix:** legt Breite und Höhe des quadratischen Gitters fest.
- **Anzahl der Simulationsschritte:** bestimmt, wie viele lokale Aktualisierungen ausgeführt werden.
- **Anteil Jäger und Anteil Beute:** bestimmen die anfängliche Zusammensetzung des Gitters.

Für einen reproduzierbaren Vergleich zweier Szenarien sollten Seed, Matrixgröße und Simulationsdauer gleich bleiben. Anschließend wird nur der gezielt zu untersuchende Parameter verändert.

Die Summe aus dem anfänglichen Jäger- und Beuteanteil muss unter 100 % liegen. Der verbleibende Anteil wird automatisch als Wiese initialisiert.

### 4. Verhaltensregeln einstellen

Danach werden Geburts-, Jagd-, Bewegungs- und Sterberegeln festgelegt. Die Hilfetexte der Bedienelemente erläutern die jeweilige Wirkung.

Einige Schwellenwerte lassen sich so hoch einstellen, dass die zugehörige Bedingung nicht mehr erreicht werden kann. Dadurch kann eine Regel gezielt deaktiviert werden. Die jeweils maximal sinnvolle Ausprägung hängt davon ab, ob das normale oder das erweiterte Moore-Umfeld gewählt wurde.

### 5. Simulation starten

Die Simulation wird über **Simulieren** gestartet. Während der Berechnung zeigt die Anwendung einen Fortschrittsbalken und die bereits ausgeführte Anzahl von Simulationsschritten an.

Je größer die Matrix und je höher die Zahl der Simulationsschritte, desto länger dauert die Berechnung. Für erste Versuche empfiehlt sich daher eine kleinere Matrix mit einer moderaten Zahl von Iterationen.

Die Anwendung prüft vor dem Start insbesondere:

- ob die Summe aus Jäger- und Beuteanteil kleiner als 100 % ist;
- ob die Zahl der Iterationen in einem unterstützten Intervall liegt.

Bei ungültigen Eingaben erscheint eine Fehlermeldung und die Simulation wird nicht ausgeführt.

### 6. Ergebnisse betrachten

Nach Abschluss werden zwei Darstellungen erzeugt:

1. Ein Liniendiagramm zeigt die Entwicklung der prozentualen Anteile von Wiese, Beute und Jägern.
2. Eine animierte Heatmap zeigt die räumliche Entwicklung des Gitters.

Unterhalb der Darstellungen werden außerdem die aktuellen Parameter den Einstellungen des vorherigen Simulationslaufs gegenübergestellt. Dadurch lassen sich Änderungen zwischen zwei Szenarien nachvollziehen.

## Parameter der Simulation

| Parameter | Bedeutung |
|---|---|
| Moore-Umfeld | Auswahl zwischen normaler und erweiterter Nachbarschaft |
| Seed | Startwert des Zufallszahlengenerators für reproduzierbare Läufe |
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

## Ergebnisse auswerten

### Populationsentwicklung

Das Liniendiagramm stellt den Anteil jedes Zustands in Prozent dar:

- **Grün:** Wiese
- **Orange:** Beute
- **Rot:** Jäger

Die Darstellung ermöglicht unter anderem die Untersuchung folgender Fragen:

- Stabilisieren sich die Populationen?
- Entstehen wiederkehrende Schwankungen?
- Stirbt eine Population aus?
- Wie verändert eine einzelne Parameteränderung das langfristige Verhalten?

Wenn eine Beuteschwelle verwendet wird, erscheint diese zusätzlich als Orientierungslinie.

### Räumliche Entwicklung

Die animierte Heatmap zeigt ausgewählte Zwischenstände der Simulation. Der Schieberegler kann verwendet werden, um einzelne Frames direkt anzusteuern. Über die Wiedergabeschaltfläche lässt sich die Entwicklung als Animation abspielen.

Beim Bewegen des Mauszeigers über eine Zelle zeigt ein Tooltip:

- die x-Position,
- die y-Position,
- den Zustand der Zelle.

Damit können neben der Gesamtentwicklung auch räumliche Muster, lokale Gruppenbildungen und Ausbreitungsprozesse untersucht werden.

### Szenarien sinnvoll vergleichen

Für einen kontrollierten Vergleich sollte jeweils nur ein Parameter verändert werden. Ein typisches Vorgehen ist:

1. Basisszenario mit festem Seed simulieren.
2. Ergebnis und Parameter dokumentieren.
3. Einen ausgewählten Parameter ändern.
4. Simulation erneut ausführen.
5. Populationsverlauf und räumliche Entwicklung vergleichen.

Der feste Seed sorgt dabei für identische anfängliche Zufallsbedingungen. Unterschiede lassen sich dadurch besser auf die gezielte Parameteränderung zurückführen.

## Installation und lokaler Start

Vorausgesetzt wird eine aktuelle Python-Installation:

```bash
git clone https://github.com/frankmollard/ZellularAutomaten.git
cd ZellularAutomaten

python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Unter Windows wird die virtuelle Umgebung so aktiviert:

```powershell
.venv\Scripts\activate
```

Anschließend wird die Anwendung gestartet:

```bash
streamlit run ZA_Simulator.py
```

Streamlit zeigt danach die lokale Adresse an, üblicherweise:

```text
http://localhost:8501
```

## Anmeldung

Die Anwendung verwendet `streamlit-authenticator`. Die Datei `config.yaml` enthält die Benutzerkonten und die Cookie-Konfiguration.

Da die Anmeldung hier lediglich verhindern soll, dass die App ohne vorgeschaltete Login-Seite vollständig offen ist, kann ein gemeinsamer Gastzugang verwendet werden. Es werden keine vertraulichen Daten geschützt.

Ein vereinfachtes Konfigurationsbeispiel:

```yaml
credentials:
  usernames:
    gast:
      email: gast@example.org
      name: Gast
      password: "$2b$12$..."

cookie:
  expiry_days: 1
  key: "COOKIE_SCHLUESSEL"
  name: "zellularautomaten_cookie"
```

Das Passwort wird als von `streamlit-authenticator` erzeugter Hash gespeichert. Wenn die Anwendung über Streamlit Community Cloud direkt aus GitHub bereitgestellt wird, muss `config.yaml` im Repository vorhanden sein oder alternativ über Streamlit Secrets bereitgestellt werden. Wird die Datei durch `.gitignore` ausgeschlossen, steht sie bei einem neuen Cloud-Deployment nicht automatisch zur Verfügung.

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
| `config.yaml` | Konfiguration der einfachen Anmeldemaske |
| `.streamlit/config.toml` | Streamlit-Konfiguration |
| `vawiaial.png` | In der Seitenleiste angezeigte Grafik |

## Technische Umsetzung

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
- Die Ergebnisse hängen stark von Regeln, Wahrscheinlichkeiten und Anfangsbedingungen ab.
- Größere Gitter und sehr viele Iterationen erhöhen Laufzeit und Speicherbedarf.
- Ein identischer Seed ermöglicht nur dann einen sinnvollen Vergleich, wenn auch die übrigen Parameter und die Programmversion unverändert bleiben.
- Die Randzellen sind dauerhaft als Wiese definiert; das Modell verwendet keine periodischen Randbedingungen.
- Die Simulation aktualisiert zufällig ausgewählte lokale Umgebungen nacheinander und nicht alle Zellen gleichzeitig.

## Autor

Frank Mollard  
[LinkedIn](https://www.linkedin.com/in/frank-mollard/)
