# BACS-Readiness-Check

Arbeitswerkzeug der **TECHNE e.U.** für die Bestandsaufnahme der Gebäudeautomation in Nichtwohngebäuden (Hotels, Büro, Handel, Gastronomie, Schulen).

- **Betroffenheit:** Leistung Heizung/Kühlung gegen 70 / 290 kW, Landesrecht Wien, Niederösterreich, Burgenland
- **Funktionen:** 45 GA-Funktionen in 7 Gewerken, Ist-Zustand je Funktion, Klasse D–A, Gesamtklasse nach der schwächsten Funktion
- **Fähigkeiten a–d:** Prüfpunkte zur Rechtspflicht (EPBD Art. 13 Abs. 10), getrennt von der Klasse
- **Auswertung:** Lücken zu Klasse B mit Zuständigkeit, Druck/PDF, CSV, JSON-Export/-Import

Live: https://ivan-nedeljko.github.io/bacs-readiness-check/

## Wichtig

- Alle Eingaben bleiben im Browser des Geräts (localStorage). Nach jeder Begehung exportieren und in der Projektablage speichern.
- Beschreibungen sinngemäß mit Verweis auf die Funktionsnummern der ÖNORM EN ISO 52120-1:2022 (Tabelle 6, Tabelle B.1) – **kein Normtext**. Maßgeblich ist die Norm.
- Klasse je Typ = höchste in Nichtwohngebäuden erreichte Klasse. TECHNE-Regel: Für Klasse C gilt der strengere Typ aus Tabelle 6 und B.1.
- Mit „TECHNE-Prüfmaßstab“ markierte Werte sind Praxiswerte, kein Gesetzeswortlaut.

## Pflege

Der Katalog wird nur in `tools/katalog_quelle.py` geändert und mit `py tools\katalog_quelle.py` nach `katalog.json` und `katalog.js` geschrieben. Bei Änderungen an App-Dateien die Cache-Version in `sw.js` erhöhen.

© TECHNE e.U. · Franz Josef-Straße 43-45/1/3 · 2344 Maria Enzersdorf · techne.co.at
