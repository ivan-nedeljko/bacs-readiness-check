# -*- coding: utf-8 -*-
"""
Funktionskatalog BACS-Readiness-Check (TECHNE e.U.) - einzige Quelle fuer App, Excel und Katalog-MD.

Inhalt: sinngemaesse, eigene Beschreibung der GA-Funktionen fuer Nichtwohngebaeude mit Verweis auf die
Funktionsnummern der EN ISO 52120-1:2022 (Tabelle 6, Anhang B Tabelle B.1). Kein Normtext.
Die Klasse je Typ ist die hoechste Klasse, die der Typ in Nichtwohngebaeuden erreicht.
TECHNE-Regel (konservativ): Fuer Klasse C gilt der strengere Typ aus Tabelle 6 und Tabelle B.1.
Abweichungen sind je Funktion im Feld "n" vermerkt.

Aufruf:  py tools\\katalog_quelle.py   -> schreibt katalog.json und katalog.js ins Repo
"""
import json, os

VERSION = "1.2"  # 1.1: Hinweise nach Kontrolllauf 25.11.2026 · 1.2: NÖ § 44a am RIS, EU-Leitlinien Anhang 10 am Wortlaut (25.11.2026)
STAND = "2026-11-25"

GEWERKE = [
    {"k": "H", "name": "Heizung"},
    {"k": "W", "name": "Trinkwarmwasser"},
    {"k": "K", "name": "Kühlung"},
    {"k": "L", "name": "Lüftung und Klima"},
    {"k": "B", "name": "Beleuchtung"},
    {"k": "S", "name": "Sonnenschutz"},
    {"k": "T", "name": "Technisches Gebäudemanagement"},
]

ABGL_H = "Betrifft den Abgleich je Heizkörper oder je Gruppe mit mehr als 10 Heizkörpern."

F = []
def fn(id, g, t, z, p, typ, w, h=None, n=None):
    F.append({"id": id, "g": g, "t": t, "z": z, "p": p,
              "typ": [{"nr": a, "text": b, "k": c} for (a, b, c) in typ],
              "w": w, "h": h, "n": n})

# ---------------------------------------------------------------- 1 Heizung
RAUM_TYP_H = [
    ("0", "Keine Regelung im Raum (nur Handventil oder gar nichts)", "D"),
    ("1", "Nur zentrale Regelung, im Raum selbst keine", "D"),
    ("2", "Regelung je Raum, nicht vernetzt (z. B. Thermostatkopf, einfacher Raumthermostat)", "C"),
    ("3", "Regelung je Raum, stetig und mit der Gebäudeautomation vernetzt", "B"),
    ("3F", "Wie Typ 3, bei integrierter Flächenheizung (z. B. Fußboden, Wand)", "A"),
    ("4", "Wie Typ 3, zusätzlich mit Anwesenheitserkennung – nicht bei träger Flächenheizung", "A"),
]
fn("1.1", "H", "Raumtemperatur (Regelung im Raum)",
   "Wie die Temperatur am Heizkörper oder an der Heizfläche je Raum geregelt wird.",
   "In Zimmern und Büros nachsehen: Thermostatkopf, Raumthermostat oder Raumregler mit Busanschluss? "
   "Ist der Regler an die Gebäudeleittechnik angebunden (Sollwert zentral sichtbar und verstellbar)? "
   "Gibt es eine Anwesenheitserkennung im Raum (Präsenzmelder; Kartenschalter nur mit Begründung)?",
   RAUM_TYP_H, "TECHNE (Raumregler, GA) + HKLS (Ventile, Stellantriebe)",
   h="Hotelzimmer mit Thermostatkopf = Typ 2 (C). Absenkung über Kartenschalter: TECHNE-Auslegung als Anwesenheitserkennung im Bericht begründen, konservativ Typ 3. "
     "Absenkung nach Buchungsstatus der Hotelsoftware ist ein Belegungsplan, keine Erkennung – bei 1.5 (Betriebszeiten) werten.",
   n="Typ 3F: Bei integrierten Flächensystemen gilt Typ 3 bereits als Klasse A (Fußnote a zu Tab. 6).")

fn("1.2", "H", "Bauteilaktivierung (Heizen über Betondecken)",
   "Regelung von Heizflächen, die im Beton liegen (thermisch aktivierte Bauteile).",
   "Gibt es Betonkernaktivierung? Wenn nein: Anlage nicht vorhanden. Wenn ja: Regelung nur zentral, "
   "mit erweiterter Strategie, oder zusätzlich Taktbetrieb bzw. Rückführung der Raumtemperatur?",
   [("0", "Keine automatische Regelung", "D"),
    ("1", "Zentral automatisch geregelt", "C"),
    ("2", "Zentral, mit erweiterter Regelstrategie", "B"),
    ("3", "Zentral erweitert, zusätzlich Taktbetrieb und/oder Rückführung der Raumtemperatur", "A")],
   "HKLS + TECHNE (GA)")

fn("1.3", "H", "Vorlauftemperatur im Heizungsnetz",
   "Wie die Wassertemperatur im Heizungsnetz eingestellt wird.",
   "Am Heizungsregler: fester Wert, Heizkurve nach Außenfühler, oder Anpassung an den tatsächlichen Bedarf der Räume? "
   "Ist ein Außenfühler vorhanden und angeschlossen? Gilt sinngemäß auch für elektrische Direktheizung.",
   [("0", "Keine automatische Regelung (fester Wert)", "D"),
    ("1", "Nach Außentemperatur (Heizkurve)", "C"),
    ("2", "Nach dem Bedarf der Räume", "A")],
   "HKLS (Regler) – Anbindung TECHNE")

fn("1.4", "H", "Umwälzpumpen im Heizungsnetz",
   "Wie die Pumpen der Heizkreise betrieben werden.",
   "Typenschild bzw. Display der Pumpe: ungeregelt, Stufenschalter, Hocheffizienzpumpe mit eigener Regelung, "
   "oder Ansteuerung über ein externes Signal (0–10 V, Bus)?",
   [("0", "Keine automatische Regelung (läuft durch)", "D"),
    ("1", "Automatisch Ein/Aus", "C"),
    ("2", "Mehrstufig", "B"),
    ("3", "Drehzahlgeregelt, die Pumpe regelt selbst", "A"),
    ("4", "Drehzahlgeregelt nach einem externen Bedarfssignal", "A")],
   "HKLS")

fn("1.4a", "H", "Hydraulischer Abgleich Heizung",
   "Ob jeder Heizkörper bzw. jede Gruppe die richtige Wassermenge bekommt.",
   "Voreinstellbare Ventile? Strangregulierventile? Differenzdruckregler je Strang/Gruppe? "
   "Druckunabhängige (dynamische) Ventile je Heizkörper? Abgleichprotokoll vorhanden? " + ABGL_H,
   [("0", "Kein Abgleich", "D"),
    ("1", "Statisch je Heizkörper, ohne Gruppenabgleich", "D"),
    ("2", "Statisch je Heizkörper und statisch je Gruppe", "D"),
    ("3", "Statisch je Heizkörper, Gruppe dynamisch (z. B. Differenzdruckregler)", "C"),
    ("4", "Dynamisch je Heizkörper (druckunabhängige Ventile)", "A")],
   "HKLS",
   h="Häufiger Grund für Klasse D im Bestand: nur statischer Abgleich.")

fn("1.5", "H", "Betriebszeiten Heizung (Absenkbetrieb)",
   "Ob die Heizung Zeiten ohne Nutzung kennt und dann absenkt.",
   "Zeitprogramme am Regler oder in der Leittechnik: vorhanden, aktiv, zur Nutzung passend? "
   "Berechnet der Regler die Aufheizzeit selbst (optimierter Start/Stopp)? Oder richtet er sich nach der Belegung?",
   [("0", "Keine automatische Regelung (Dauerbetrieb)", "D"),
    ("1", "Fester Zeitplan", "C"),
    ("2", "Zeitplan mit optimiertem Start und Stopp", "B"),
    ("3", "Nach Bedarf bzw. Belegung", "A")],
   "TECHNE (GA) + HKLS",
   h="Zeitprogramme stehen oft seit Jahren unverändert oder auf Dauerbetrieb – am Regler nachsehen, nicht nur fragen. "
     "Absenkung nach Buchungsstatus der Hotelsoftware: Einordnung (Typ 1 oder Typ 3) im Bericht begründen.")

ERZ_TYP = [("0", "Konstante Temperatur", "D"),
           ("1", "Gleitend nach Außentemperatur", "C"),
           ("2", "Nach der Last", "A")]
fn("1.6", "H", "Wärmeerzeuger Kessel oder Fernwärme",
   "Wie Kessel bzw. Fernwärme-Übergabestation ihre Temperatur regeln.",
   "Kessel oder Übergabestation: konstante Temperatur, gleitend nach Außentemperatur, oder nach der Last (Rückmeldung aus dem Netz)?",
   ERZ_TYP, "HKLS")
fn("1.7", "H", "Wärmeerzeuger Wärmepumpe",
   "Wie die Wärmepumpe ihre Vorlauftemperatur regelt.",
   "Regler der Wärmepumpe: konstante Temperatur, Heizkurve nach Außentemperatur, oder lastabhängig?",
   ERZ_TYP, "HKLS",
   n="Tab. B.1 nennt hier abweichend einen Ein/Aus-Typ als Mindestniveau – TECHNE stuft nach Tab. 6 ein (strenger).")
fn("1.8", "H", "Leistungsstufung des Wärmeerzeugers",
   "Wie die Leistung des Erzeugers angepasst wird (z. B. Außeneinheit einer Wärmepumpe).",
   "Typenschild oder Datenblatt: nur Ein/Aus, mehrstufig, oder stufenlos (Inverter)?",
   [("0", "Nur Ein/Aus", "D"), ("1", "Mehrstufig", "B"), ("2", "Stufenlos (z. B. Inverter)", "A")],
   "HKLS")
fn("1.9", "H", "Reihenfolge mehrerer Wärmeerzeuger",
   "Wie bei mehreren Erzeugern entschieden wird, welcher läuft.",
   "Nur bei mehr als einem Erzeuger. Kaskade: Umschaltung nur nach Laufzeit, feste Rangfolge (auch reine Folge nach Last), wechselnde Rangfolge nach aktuellem Wirkungsgrad und Leistung der Erzeuger, oder mit Prognose?",
   [("0", "Nur nach Laufzeit", "D"),
    ("1", "Feste Rangfolge (auch reine Folge nach Last)", "C"),
    ("2", "Wechselnde Rangfolge nach aktuellem Wirkungsgrad und Leistung der Erzeuger", "B"),
    ("3", "Wechselnde Rangfolge mit Prognose", "A")],
   "HKLS")
fn("1.10", "H", "Ladung des Heizungs-Pufferspeichers",
   "Wie ein Pufferspeicher der Heizung geladen wird.",
   "Pufferspeicher vorhanden? Wenn nein: nicht vorhanden. Ladung dauernd, über zwei Fühler (oben/unten), oder nach Lastprognose?",
   [("0", "Dauernd geladen", "D"), ("1", "Ladung über zwei Fühler", "B"), ("2", "Nach Lastprognose", "A")],
   "HKLS")

# ---------------------------------------------------------------- 2 Trinkwarmwasser
fn("2.1", "W", "Warmwasserspeicher elektrisch",
   "Ladung eines Warmwasserspeichers mit Heizstab oder eingebauter Wärmepumpe.",
   "Elektro- oder Wärmepumpenboiler: lädt er jederzeit nach (nur Thermostat) oder nur zu freigegebenen Zeiten? Mehrere Fühler im Speicher?",
   [("0", "Automatisch Ein/Aus (Thermostat)", "D"),
    ("1", "Ein/Aus mit Ladefreigabe nach Zeitplan", "C"),
    ("2", "Zusätzlich Speichermanagement mit mehreren Fühlern", "A")],
   "HKLS / TECHNE (Freigabe)")
fn("2.2", "W", "Warmwasserspeicher über Wärmeerzeuger",
   "Ladung des Warmwasserspeichers über Kessel, Fernwärme oder Wärmepumpe.",
   "Speicherladung: nur Thermostat, mit Ladezeiten nach Zeitplan, oder zusätzlich bedarfsgeführte Ladetemperatur bzw. mehrere Speicherfühler?",
   [("0", "Automatisch Ein/Aus", "D"),
    ("1", "Ein/Aus mit Ladefreigabe nach Zeitplan", "C"),
    ("2", "Zusätzlich bedarfsgeführte Ladetemperatur oder Speichermanagement mit mehreren Fühlern", "A")],
   "HKLS",
   h="Im Hotel meist der größte Warmwasser-Posten. Trinkwasserhygiene geht vor – Ladezeiten und Temperaturen nur mit dem Installateur festlegen.")
fn("2.3", "W", "Warmwasser mit Solarthermie",
   "Speicherladung bei Solaranlage mit Nachheizung durch einen weiteren Erzeuger.",
   "Solaranlage vorhanden? Wenn nein: nicht vorhanden. Hat Solar automatisch Vorrang vor der Nachheizung?",
   [("0", "Händisch", "D"),
    ("1", "Automatisch: zuerst Solar, dann Nachheizung", "C"),
    ("2", "Wie Typ 1, zusätzlich bedarfsgeführte Temperatur oder Speichermanagement mit mehreren Fühlern", "A")],
   "HKLS")
fn("2.4", "W", "Zirkulationspumpe Warmwasser",
   "Ob die Zirkulationspumpe dauernd läuft.",
   "Zirkulationspumpe: Dauerbetrieb oder Zeitprogramm (Schaltuhr, Regler)?",
   [("0", "Dauerbetrieb, ungeregelt", "D"), ("1", "Mit Zeitprogramm", "A")],
   "HKLS",
   h="Im Hotel läuft die Zirkulation oft rund um die Uhr. Ein Zeitprogramm nur mit dem Hygienekonzept des Installateurs.")

# ---------------------------------------------------------------- 3 Kuehlung
RAUM_TYP_K = [
    ("0", "Keine Regelung im Raum", "D"),
    ("1", "Nur zentrale Regelung, im Raum selbst keine", "D"),
    ("2", "Regelung je Raum, nicht vernetzt (z. B. Split-Gerät mit eigener Fernbedienung)", "C"),
    ("3", "Regelung je Raum, stetig und mit der Gebäudeautomation vernetzt", "B"),
    ("3F", "Wie Typ 3, bei integrierter Flächenkühlung (z. B. Fußboden, Wand – nicht abgehängte Kühldecke)", "A"),
    ("4", "Wie Typ 3, zusätzlich mit Anwesenheitserkennung – nicht bei träger Flächenkühlung", "A"),
]
fn("3.1", "K", "Raumtemperatur Kühlung (Regelung im Raum)",
   "Wie die Kühlung je Raum geregelt wird (Kühlflächen, Gebläsekonvektoren, Innengeräte).",
   "Fan-Coils, Kühldecken, Split- oder VRF-Innengeräte: eigener Regler je Raum? Vernetzt mit der Gebäudeautomation "
   "(zentrale Sollwerte, Sperre bei offenem Fenster)? Kopplung an die Anwesenheit?",
   RAUM_TYP_K, "Kälte + TECHNE (GA)",
   h="Split-Geräte mit eigener Fernbedienung je Zimmer = Typ 2 (C).",
   n="Typ 3F: Bei integrierten Flächensystemen gilt Typ 3 bereits als Klasse A (Fußnote a zu Tab. 6).")
fn("3.2", "K", "Bauteilaktivierung (Kühlen über Betondecken)",
   "Regelung von Kühlflächen, die im Beton liegen.",
   "Gibt es Betonkernaktivierung für Kühlung? Wenn nein: nicht vorhanden.",
   [("0", "Keine automatische Regelung", "D"),
    ("1", "Zentral automatisch geregelt", "C"),
    ("2", "Zentral, mit erweiterter Regelstrategie", "B"),
    ("3", "Zentral erweitert, zusätzlich Taktbetrieb und/oder Rückführung der Raumtemperatur", "A")],
   "Kälte + TECHNE (GA)")
fn("3.3", "K", "Kaltwassertemperatur im Netz",
   "Wie die Kaltwassertemperatur eingestellt wird.",
   "Kaltwasser: fester Wert, nach Außentemperatur oder nach Bedarf? Bei Direktkühlung (Split, Kompaktgerät) sinngemäß am Gerät beurteilen.",
   [("0", "Konstante Temperatur", "D"), ("1", "Nach Außentemperatur", "C"), ("2", "Nach Bedarf", "A")],
   "Kälte – Anbindung TECHNE")
fn("3.4", "K", "Umwälzpumpen im Kältenetz",
   "Wie die Pumpen der Kältekreise betrieben werden.",
   "Pumpen im Kaltwassernetz: ungeregelt, Ein/Aus, mehrstufig, drehzahlgeregelt?",
   [("0", "Keine automatische Regelung (läuft durch)", "D"),
    ("1", "Automatisch Ein/Aus", "C"),
    ("2", "Mehrstufig", "B"),
    ("3", "Drehzahlgeregelt, die Pumpe regelt selbst", "A"),
    ("4", "Drehzahlgeregelt nach einem externen Bedarfssignal", "A")],
   "Kälte")
fn("3.4a", "K", "Hydraulischer Abgleich Kühlung",
   "Ob jeder Kälteverbraucher bzw. jede Gruppe die richtige Wassermenge bekommt.",
   "Wie bei der Heizung: statisch, Gruppe dynamisch, oder dynamisch je Verbraucher? Gilt für Gruppen mit mehr als 10 Kälte-Übergabeeinrichtungen.",
   [("0", "Kein Abgleich", "D"),
    ("1", "Statisch je Verbraucher, ohne Gruppenabgleich", "D"),
    ("2", "Statisch je Verbraucher und statisch je Gruppe", "D"),
    ("3", "Statisch je Verbraucher, Gruppe dynamisch", "C"),
    ("4", "Dynamisch je Verbraucher", "A")],
   "Kälte",
   n="Tab. B.1 nennt hier den statischen Abgleich als Mindestniveau – TECHNE stuft nach Tab. 6 ein (strenger).")
fn("3.5", "K", "Betriebszeiten Kühlung",
   "Ob die Kühlung Zeiten ohne Nutzung kennt.",
   "Zeitprogramme für die Kühlung vorhanden und passend? Optimierter Start/Stopp? Nach Belegung?",
   [("0", "Keine automatische Regelung (Dauerbetrieb)", "D"),
    ("1", "Fester Zeitplan", "C"),
    ("2", "Zeitplan mit optimiertem Start und Stopp", "B"),
    ("3", "Nach Bedarf bzw. Belegung", "A")],
   "TECHNE (GA) + Kälte")
fn("3.6", "K", "Sperre gleichzeitiges Heizen und Kühlen",
   "Ob verhindert wird, dass im selben Raum gleichzeitig geheizt und gekühlt wird.",
   "Gibt es Räume mit Heizkörper und Kühlgerät? Ist gegenseitig verriegelt (Regler, GA)? Nur teilweise oder vollständig?",
   [("0", "Keine Verriegelung", "D"), ("1", "Teilweise (je nach System)", "B"), ("2", "Vollständig", "A")],
   "TECHNE (GA)",
   h="Häufiger Hotelfall: Heizkörper und Split-Gerät im selben Zimmer arbeiten gegeneinander.")
fn("3.7", "K", "Regelung der Kälteerzeuger",
   "Wie die Kältemaschine ihre Temperatur führt.",
   "Kältemaschine: konstante Kaltwassertemperatur, gleitend nach Außentemperatur, oder lastabhängig?",
   [("0", "Konstante Temperatur", "D"), ("1", "Gleitend nach Außentemperatur", "B"), ("2", "Nach der Last", "A")],
   "Kälte")
fn("3.8", "K", "Reihenfolge mehrerer Kälteerzeuger",
   "Wie bei mehreren Kälteerzeugern entschieden wird, welcher läuft.",
   "Nur bei mehr als einem Kälteerzeuger. Umschaltung nur nach Laufzeit, feste Reihenfolge nach Last, nach Wirkungsgrad, oder mit Prognose?",
   [("0", "Nur nach Laufzeit", "D"),
    ("1", "Feste Reihenfolge nach Last", "C"),
    ("2", "Nach Wirkungsgrad und Eigenschaften der Erzeuger", "B"),
    ("3", "Mit Lastprognose", "A")],
   "Kälte")
fn("3.9", "K", "Ladung von Kältespeichern",
   "Wie ein Kältespeicher (z. B. Eisspeicher) geladen wird.",
   "Kältespeicher vorhanden? Wenn nein: nicht vorhanden. Ladung dauernd, zeitgesteuert, oder nach Lastprognose?",
   [("0", "Dauernd geladen", "D"), ("1", "Zeitgesteuert", "C"), ("2", "Nach Lastprognose", "A")],
   "Kälte")

# ---------------------------------------------------------------- 4 Lueftung und Klima
fn("4.1", "L", "Luftmenge je Raum",
   "Ob die Luftmenge im Raum an die Nutzung angepasst wird.",
   "Volumenstromregler oder Klappen je Raum bzw. Zone (Seminar, Restaurant, Wellness)? Zeitgesteuert, über Präsenzmelder, oder nach Luftqualität (CO₂- oder Mischgasfühler)?",
   [("0", "Keine automatische Regelung", "D"),
    ("1", "Nach Zeitplan", "B"),
    ("2", "Nach Anwesenheit", "B"),
    ("3", "Nach Bedarf (z. B. CO₂)", "A")],
   "Lüftung + TECHNE (Präsenz, GA)")
fn("4.2", "L", "Raumtemperatur über die Lüftungsanlage",
   "Wie die Raumlufttemperatur über die Zuluft der Lüftungsanlage geregelt wird.",
   "Bei Lüftungsanlagen, die die Raumtemperatur führen – auch wenn zusätzlich Heizkörper oder Kühlflächen im Raum sind (dann zusätzlich 4.3 prüfen): Ein/Aus, stetige Regelung, oder optimierte Regelung?",
   [("0", "Ein/Aus", "D"), ("1", "Stetige Regelung", "C"), ("2", "Optimierte Regelung", "A")],
   "Lüftung + TECHNE (GA)")
fn("4.3", "L", "Abstimmung Luft und Wasser (kombinierte Anlagen)",
   "Ob bei Luft-Wasser-Anlagen Luftseite und Wasserseite zusammenarbeiten.",
   "Nur bei kombinierten Anlagen (z. B. Lüftung plus Fan-Coil/Kühldecke): arbeiten beide Regelungen abgestimmt?",
   [("0", "Nicht abgestimmt", "D"), ("1", "Aufeinander abgestimmt", "A")],
   "Lüftung + Kälte + TECHNE (GA)",
   n="Tab. B.1 nennt für Nichtwohngebäude den nicht abgestimmten Typ als Mindestniveau – TECHNE stuft nach Tab. 6 ein (strenger).")
fn("4.4", "L", "Außenluftmenge",
   "Wie viel Außenluft das Lüftungsgerät ansaugt.",
   "Fester Außenluftanteil, zweistufig nach Zeitplan oder nach Anwesenheit, oder stufenlos variabel?",
   [("0", "Fester Außenluftanteil", "D"),
    ("1", "Zweistufig nach Zeitplan", "B"),
    ("2", "Zweistufig nach Anwesenheit", "B"),
    ("3", "Stufenlos variabel", "A")],
   "Lüftung",
   n="Tab. 6 würde Typ 0 als C werten; Tab. B.1 verlangt für C mindestens Typ 1 – TECHNE stuft konservativ als D ein.")
fn("4.5", "L", "Luftmenge bzw. Druck am Lüftungsgerät",
   "Wie das Lüftungsgerät seine Luftmenge regelt.",
   "Lüftungsgerät: Schaltuhr, Stufenschalter, Frequenzumrichter mit Druck- oder Volumenstromregelung? Wird der Sollwert nachgeführt?",
   [("0", "Keine automatische Regelung", "D"),
    ("1", "Ein/Aus nach Zeit", "C"),
    ("2", "Mehrstufig", "B"),
    ("3", "Automatische Volumenstrom- oder Druckregelung", "A"),
    ("4", "Wie Typ 3, mit Nachführung des Sollwerts", "A")],
   "Lüftung")
fn("4.6", "L", "Wärmerückgewinnung: Vereisungsschutz",
   "Ob die Wärmerückgewinnung gegen Vereisen geschützt ist.",
   "Wärmerückgewinnung vorhanden? Wenn nein: nicht vorhanden. Vereisungsschutz geregelt?",
   [("0", "Ohne Vereisungsschutz", "D"), ("1", "Mit Vereisungsschutz", "A")],
   "Lüftung")
fn("4.7", "L", "Wärmerückgewinnung: Überhitzungsschutz",
   "Ob die Wärmerückgewinnung im Sommer umgangen wird, wenn sie nur Wärme ins Haus bringt.",
   "Bypass oder Drehzahlregelung der WRG im Sommer vorhanden?",
   [("0", "Ohne Überhitzungsschutz", "D"), ("1", "Mit Überhitzungsschutz (z. B. Bypass)", "A")],
   "Lüftung")
fn("4.8", "L", "Freie Kühlung über die Lüftung",
   "Ob kühle Außenluft zum Kühlen genutzt wird.",
   "Nachtlüftung, freie Kühlung, oder Regelung nach Temperatur und Feuchte der Außenluft (Enthalpie)?",
   [("0", "Keine automatische Regelung", "D"),
    ("1", "Nachtlüftung bzw. Nachtkühlung", "C"),
    ("2", "Freie Kühlung", "B"),
    ("3", "Nach Enthalpie (Temperatur und Feuchte)", "A")],
   "Lüftung + TECHNE (GA)")
fn("4.9", "L", "Zulufttemperatur",
   "Wie die Temperatur der eingeblasenen Luft geführt wird.",
   "Fester Sollwert, nach Außentemperatur, oder nach der Last?",
   [("0", "Keine automatische Regelung", "D"),
    ("1", "Fester Sollwert", "C"),
    ("2", "Sollwert nach Außentemperatur", "B"),
    ("3", "Sollwert nach der Last", "A")],
   "Lüftung")
fn("4.10", "L", "Luftfeuchte",
   "Wie befeuchtet oder entfeuchtet wird.",
   "Nur wenn befeuchtet oder entfeuchtet wird, sonst nicht vorhanden. Regelung über Taupunkt oder direkt nach Raum-/Abluftfeuchte?",
   [("0", "Keine automatische Regelung", "D"), ("1", "Über den Taupunkt", "C"), ("2", "Direkte Feuchteregelung", "A")],
   "Lüftung")

# ---------------------------------------------------------------- 5 Beleuchtung
fn("5.1", "B", "Licht nach Anwesenheit",
   "Ob das Licht von selbst ausgeht, wenn niemand da ist.",
   "Je Zone ansehen: Gänge, Stiegenhäuser, Nebenräume, WC, Lager, Tiefgarage, Büro, Rezeption. "
   "Präsenz- oder Bewegungsmelder? Zeitschalter bzw. automatisches Ausschalten? Nur Taster?",
   [("0", "Nur Schalter oder Taster", "D"),
    ("1", "Schalter plus automatisches Ausschalten (mind. einmal täglich, z. B. abends; Zeitschalter, Kartenschalter)", "D"),
    ("2", "Melder schaltet ein und aus", "A"),
    ("3", "Von Hand ein, Melder schaltet aus", "A")],
   "TECHNE",
   h="Kartenschalter im Zimmer: Einordnung (Typ 1 oder 3) im Bericht begründen – konservativ Typ 1. Gänge mit Bewegungsmelder = Typ 2.",
   n="Tab. 6 würde Typ 1 als C werten; Tab. B.1 verlangt für C die automatische Erkennung – TECHNE stuft konservativ als D ein. "
     "Die gesetzliche Beleuchtungssteuerung (zoniert, mit Belegungserkennung) wird über diese Funktion beurteilt.")
fn("5.2", "B", "Licht nach Tageslicht",
   "Ob das Kunstlicht an das Tageslicht angepasst wird.",
   "Nur Räume mit nennenswertem Tageslicht (Büro, Rezeption, Restaurant, Seminar). Lichtsensor vorhanden? Leuchten dimmbar (DALI, 1–10 V)?",
   [("0", "Von Hand, zentral", "C"),
    ("1", "Von Hand, je Raum oder Zone", "C"),
    ("2", "Automatisch schalten nach Tageslicht", "B"),
    ("3", "Automatisch dimmen nach Tageslicht", "A")],
   "TECHNE")

# ---------------------------------------------------------------- 6 Sonnenschutz
fn("6", "S", "Sonnenschutz",
   "Wie Jalousien, Markisen oder Rollläden gesteuert werden.",
   "Kurbel, Taster, Wetterstation? Fährt der Sonnenschutz automatisch nach der Sonne, um Überhitzung bzw. Kühllast zu senken? Gibt es eine Verknüpfung mit Heizung/Kühlung und Licht?",
   [("0", "Händisch", "D"),
    ("1", "Motor, von Hand bedient (auch mit reiner Wind- oder Zeitautomatik)", "D"),
    ("2", "Motor, automatisch zur Senkung von Überhitzung bzw. Kühllast (z. B. nach Sonne)", "C"),
    ("3", "Automatisch und abgestimmt mit Licht und Heizung/Kühlung", "A")],
   "Sonnenschutz + TECHNE (Steuerung)",
   h="Ohne Sonnenschutzeinrichtung: als nicht vorhanden markieren. Motor mit Taster, Windwächter oder Zeitfahrt allein = D.")

# ---------------------------------------------------------------- 7 TGM
fn("7.1", "T", "Sollwerte verstellen",
   "Wo die Raumsollwerte eingestellt werden.",
   "Wo werden Raumtemperaturen verstellt? Nur im Raum, in Technikräumen, zentral am Bildschirm (Leittechnik, Rezeption)? Werden Nutzereinstellungen regelmäßig zurückgesetzt (z. B. beim Check-out)?",
   [("0", "Händisch in jedem Raum", "D"),
    ("1", "Nur in Technikräumen vor Ort", "C"),
    ("2", "Von zentraler Stelle", "B"),
    ("3", "Zentral, mit regelmäßigem Zurücksetzen der Nutzereingaben", "A")],
   "TECHNE",
   h="Zurücksetzen der Nutzereingaben (z. B. beim Check-out) zählt nur zusammen mit zentraler Verstellung als Typ 3; Raumbediengeräte allein zählen nicht.")
fn("7.2", "T", "Betriebszeiten verwalten",
   "Wie die Betriebszeiten der Anlagen festgelegt werden.",
   "Werden Anlagen von Hand eingeschaltet, je Anlage mit eigenem Zeitplan, oder zentral mit anpassender Vorlaufzeit?",
   [("0", "Anlagen werden von Hand eingeschaltet", "D"),
    ("1", "Je Anlage fester Zeitplan, feste Vorlaufzeiten", "C"),
    ("2", "Zentral verwaltet, Vorlaufzeiten passen sich an", "A")],
   "TECHNE")
fn("7.3", "T", "Störmeldungen",
   "Ob Störungen der Haustechnik an einer zentralen Stelle sichtbar werden.",
   "Wo sieht der Haustechniker eine Störung von Kessel, Pumpe, Lüftung oder Kälte? Nur am Gerät vor Ort = keine zentrale Anzeige. Sammelstörung per SMS/Mail? Hilft das System bei der Ursachensuche?",
   [("0", "Keine zentrale Anzeige", "D"),
    ("1", "Störungen und Warnungen zentral angezeigt", "C"),
    ("2", "Zentral angezeigt, mit Unterstützung bei der Diagnose", "A")],
   "TECHNE",
   h="Fehlende zentrale Störanzeige ist ein häufiger Grund für Klasse D.")
fn("7.4", "T", "Energie- und Raumklima-Information",
   "Was das System über Verbrauch und Raumklima anzeigt und auswertet.",
   "Werden nur aktuelle Werte gezeigt, gibt es Verläufe und Verbrauchsermittlung, oder eine Auswertung mit Bewertung von Energie und Raumklima?",
   [("-", "Gar keine Anzeige von Werten", "D"),
    ("0", "Nur aktuelle Werte (z. B. Temperaturen, Zählerstände)", "C"),
    ("1", "Verläufe (Trends) und Verbrauchsermittlung", "B"),
    ("2", "Auswertung und Bewertung von Energie und Raumklima", "A")],
   "TECHNE",
   n="Typ „–“ ist kein Normtyp: ohne jede Anzeige liegt die Funktion unter dem Mindestniveau – TECHNE wertet D.")
fn("7.5", "T", "Eigene Erzeugung (PV, BHKW)",
   "Ob eigene Erzeugung auf den Verbrauch im Haus abgestimmt wird.",
   "PV oder BHKW vorhanden? Wenn nein: nicht vorhanden. Wenn ja: steuert ein Energiemanagement Verbraucher bzw. Speicher nach der Erzeugung?",
   [("0", "Läuft unabgestimmt, Überschuss geht ins Netz", "C"),
    ("1", "Auf den Verbrauch abgestimmt, mit Speicher bzw. Eigenverbrauchsoptimierung", "A")],
   "TECHNE")
fn("7.6", "T", "Abwärmenutzung",
   "Ob vorhandene Abwärme gesteuert genutzt wird.",
   "Nur wenn Abwärme genutzt wird (z. B. Kälteanlage, Küche, Wäscherei). Sonst: nicht vorhanden. Direkt und ungesteuert, oder gesteuert mit Speicher?",
   [("0", "Direkt und ungesteuert genutzt", "D"),
    ("1", "Gesteuert genutzt, auch mit Laden/Entladen von Speichern", "A")],
   "HKLS",
   n="Tab. B.1 nennt Typ 0 als Mindestniveau – TECHNE stuft nach Tab. 6 ein (strenger).")
fn("7.7", "T", "Zusammenspiel mit dem Stromnetz",
   "Ob das Gebäude auf Signale des Stromnetzes reagiert.",
   "Gibt es Lastverschiebung oder Steuerung nach Netz- bzw. Preissignal (z. B. Wärmepumpe, Ladestationen, Speicher)?",
   [("0", "Läuft unabhängig von der Netzsituation", "C"),
    ("1", "Reagiert auf Anforderungen des Netzes (Lastverschiebung)", "A")],
   "TECHNE",
   n="Für Klasse B gibt es keinen eigenen Typ: entweder netzdienlicher Betrieb (A) oder begründet weglassen.")

# ---------------------------------------------------------------- Faehigkeiten (EPBD Art. 13 Abs. 10, sinngemaess)
MASSSTAB = "TECHNE-Prüfmaßstab, kein Gesetzeswortlaut"
FAEH = [
    {"k": "v", "t": "Vorfrage: Abdeckung",
     "z": "Die Gebäudeautomation erfasst die wesentlichen Anlagen für Heizung, Kühlung und Lüftung – sonst ist die Prüfung a–d nicht aussagekräftig.",
     "punkte": [{"id": "v1", "t": "Die wesentlichen Anlagen für Heizung, Kühlung und Lüftung sind an ein Automationssystem angebunden."}]},
    {"k": "a", "t": "a) Energieverbrauch erfassen, aufzeichnen, auswerten, anpassen",
     "z": "Laufende Erfassung, Aufzeichnung und Auswertung des Energieverbrauchs; Eingriff muss möglich sein.",
     "punkte": [
        {"id": "a1", "t": "Zähler für die Hauptverbraucher (Heizung, Warmwasser, Kühlung, Lüftung, Licht) werden automatisch ausgelesen."},
        {"id": "a2", "t": "Die Werte werden gespeichert.", "m": MASSSTAB + ": Intervall höchstens 15 Minuten, mindestens 12 Monate gespeichert."},
        {"id": "a3", "t": "Der Verbrauch lässt sich auswerten (Verläufe, Vergleich von Zeiträumen, Kennzahlen)."},
        {"id": "a4", "t": "Zeitprogramme und Sollwerte lassen sich über das System anpassen."}]},
    {"k": "b", "t": "b) Vergleichen und Verluste erkennen",
     "z": "Vergleich der Energieeffizienz mit Kennwerten, Erkennen von Effizienzverlusten und Information der Verantwortlichen.",
     "punkte": [
        {"id": "b1", "t": "Vergleich mit Kennwerten oder der eigenen Vorgeschichte ist möglich."},
        {"id": "b2", "t": "Effizienzverluste (z. B. steigender Verbrauch, Anlage läuft außerhalb der Zeit) werden erkannt."},
        {"id": "b3", "t": "Die verantwortliche Person wird informiert (Meldung, Bericht) – und es ist geklärt, wer reagiert."}]},
    {"k": "c", "t": "c) Zusammenarbeit der Anlagen",
     "z": "Die technischen Anlagen kommunizieren miteinander und lassen sich auch herstellerübergreifend gemeinsam betreiben.",
     "punkte": [
        {"id": "c1", "t": "Anlagen verschiedener Gewerke tauschen über das System Daten aus."},
        {"id": "c2", "t": "Die Schnittstellen sind offen bzw. dokumentiert (z. B. BACnet, KNX, Modbus, DALI) – auch beim Tausch einzelner Teile."},
        {"id": "c3", "t": "Daten lassen sich exportieren (Datei oder Schnittstelle)."}]},
    {"k": "d", "t": "d) Raumklima überwachen",
     "z": "Laufende Messung des Raumklimas in Aufenthaltsräumen.",
     "punkte": [
        {"id": "d1", "t": "In den genutzten Räumen bzw. Bereichen (in der Regel je Raum nach Nutzung, z. B. Büro, Seminar, Restaurant, Rezeption) werden Temperatur, relative Feuchte und CO₂ laufend gemessen, wo nötig auch Feinstaub.",
         "m": "Empfehlung EU-Leitlinien C/2025/6438, Anhang 10 Pkt. 3.2"},
        {"id": "d2", "t": "Die Messwerte werden aufgezeichnet."},
        {"id": "d3", "t": "Grenzwerte werden angezeigt bzw. gemeldet.", "m": MASSSTAB + ": Grenzwerte im Bericht festlegen und begründen (Orientierung: Anhang 10 Pkt. 3.3, CO₂ als Abstand zur Außenluft)."}]},
]
FAEH_STATUS = ["erfüllt", "teilweise", "nicht erfüllt", "nicht geprüft"]

# ---------------------------------------------------------------- Landesrecht (Stand 25.11.2026, Faktenregister Infoblatt F1-F17)
LAND = {
    "W": {"name": "Wien", "gesetz": "§ 14b WHLKG 2015 idF LGBl. 25/2026",
          "b290": "Abs. 1 – Pflicht besteht", "b70": "Abs. 1a – bis 31.12.2029",
          "licht": "über 290 kW bis 31.12.2027, über 70 kW bis 31.12.2029 (Abs. 1, 1a, 2a)",
          "faeh": "Abs. 2 Z 1–4 (vier Fähigkeiten)", "vorbehalt": "sofern technisch und wirtschaftlich realisierbar (BACS)",
          "adressat": "Eigentümer des Gebäudes",
          "inspektion": "§ 23a: Summe der Erzeuger über 70 kW alle 5 Jahre, über 290 kW alle 3 Jahre; entfällt bei Erfüllung von § 14b Abs. 2 (Abs. 8)",
          "pruef": "am Wortlaut geprüft (24.11.2026)"},
    "N": {"name": "Niederösterreich", "gesetz": "§ 44a NÖ BO 2014 idF LGBl. 1/2026",
          "b290": "Abs. 3 – Pflicht besteht", "b70": "Abs. 4 – bis 31.12.2029",
          "licht": "über 290 kW bis 31.12.2027, über 70 kW bis 31.12.2029 (Abs. 3–5)",
          "faeh": "Abs. 5 Z 1–4 (vier Fähigkeiten; Beleuchtung zoniert, mit Belegungserkennung)", "vorbehalt": "sofern technisch und wirtschaftlich realisierbar (BACS und Beleuchtung)",
          "adressat": "Eigentümer (über Strafbestimmung § 37)",
          "inspektion": "nicht im Katalog – einzeln prüfen; Abs. 1: beim Austausch des Wärme- oder Kälteerzeugers (sofern technisch und wirtschaftlich realisierbar) Temperaturregelung je Raum und, sofern zweckmäßig, hydraulischer Abgleich – unabhängig von 70 kW",
          "pruef": "am Wortlaut geprüft (RIS, Fassung vom 25.11.2026)"},
    "B": {"name": "Burgenland", "gesetz": "§ 34g Bgld. BauVO 2008 idF LGBl. 75/2026",
          "b290": "Abs. 6 Z 1 – Pflicht besteht", "b70": "Abs. 6 Z 2 – ab 31.12.2029",
          "licht": "über 290 kW ab 31.12.2027, über 70 kW ab 31.12.2029 (Abs. 8, ohne Vorbehalt)",
          "faeh": "Abs. 7 Z 1–4 (inkl. Raumklima)", "vorbehalt": "sofern technisch und wirtschaftlich realisierbar (BACS, nicht Beleuchtung)",
          "adressat": "im Text nicht genannt",
          "inspektion": "Bgld. HKG § 36a: über 70 kW alle 12 Jahre, Befreiung über 290 kW mit BACS – Stand nach LGBl. 83/2024 prüfen",
          "pruef": "am Wortlaut geprüft (RIS 15.11.2026)"},
    "X": {"name": "anderes Bundesland", "gesetz": "nicht im Katalog",
          "b290": "Landesrecht prüfen", "b70": "Landesrecht prüfen", "licht": "Landesrecht prüfen",
          "faeh": "Landesrecht prüfen", "vorbehalt": "–", "adressat": "–", "inspektion": "–",
          "pruef": "nicht geprüft"},
}
SCHWELLE_HINWEISE = [
    "Heizung und Kühlung werden je für sich gegen die Schwelle geprüft – maßgeblich ist die Leistung des Wärme- oder des Kälteerzeugers „für sich“ (EU-Leitlinien C/2025/6438, Anhang 10 Pkt. 2.5).",
    "Der Vorbehalt „technisch und wirtschaftlich realisierbar“ ist eine eng auszulegende Ausnahme, keine Wahlmöglichkeit; wirtschaftlich heißt: Nutzen über der Lebensdauer höher als die Kosten (Anhang 10 Pkt. 5).",
    "Mehrere Erzeuger derselben Anlage zählen in der Regel zusammen.",
    "Gesucht ist die abgegebene Wärme- bzw. Kälteleistung, nicht die elektrische Leistungsaufnahme.",
    "Fernwärme: rechtlich offen – konservativ die Leistung der Übergabestation (sekundär) bzw. die Anschlussleistung laut Vertrag ansetzen.",
    "Heizung und Kühlung nur zusammen über der Schwelle, gemischte Nutzung: einzeln klären.",
]

# ---------------------------------------------------------------- Ausgabe
KW = {"D": 1, "C": 2, "B": 3, "A": 4}
def check():
    ids = set()
    for f in F:
        assert f["id"] not in ids, f["id"]; ids.add(f["id"])
        assert f["g"] in [g["k"] for g in GEWERKE]
        nrs = [t["nr"] for t in f["typ"]]
        assert len(nrs) == len(set(nrs)), f["id"]
        for t in f["typ"]:
            assert t["k"] in KW, (f["id"], t)
    return len(F)

def ausgabe():
    n = check()
    daten = {"version": VERSION, "stand": STAND, "norm": "ÖNORM EN ISO 52120-1:2022 (Tab. 6, Tab. B.1) – Verweise, kein Normtext",
             "regel": "Klasse je Typ = höchste in Nichtwohngebäuden erreichte Klasse; für C gilt der strengere Typ aus Tab. 6 und Tab. B.1.",
             "gewerke": GEWERKE, "funktionen": F, "faehigkeiten": FAEH, "faeh_status": FAEH_STATUS,
             "land": LAND, "schwelle_hinweise": SCHWELLE_HINWEISE}
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(root, "katalog.json"), "w", encoding="utf-8") as fh:
        json.dump(daten, fh, ensure_ascii=False, indent=1)
    with open(os.path.join(root, "katalog.js"), "w", encoding="utf-8") as fh:
        fh.write("// erzeugt aus tools/katalog_quelle.py – nicht von Hand ändern\nwindow.KATALOG = ")
        json.dump(daten, fh, ensure_ascii=False)
        fh.write(";\n")
    print("Funktionen:", n, "| Typen:", sum(len(f["typ"]) for f in F))

if __name__ == "__main__":
    ausgabe()
