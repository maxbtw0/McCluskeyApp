# McCluskeyApp

Desktop Tool zur Minimierung boolescher Funktionen nach dem **Verfahren von Quine und McCluskey**. Die App zeigt jeden Schritt einzeln an, von der Gruppierung der Minterme bis zur fertigen disjunktiven Minimalform.

## Download

Die fertige **`McCluskeyApp.exe`** gibt es unter [Releases](../../releases). Einfach herunterladen und starten, keine Installation nötig (Windows).

## Funktionen

* 1 bis 6 Variablen (A, B, C, ...)
* Minterme per Checkbox auswählen oder zufällig generieren lassen
* Schrittweise Zusammenfassung über alle Ordnungen mit Markierung der verwendeten Terme
* Primimplikantentabelle mit farbiger Hervorhebung
* Ausgabe aller gleichwertigen Minimallösungen im Log
* Einstellbares Design (Dark/Light, Farbthema)

## Bedienung

1. Anzahl Bits wählen
2. Gewünschte Dezimalwerte anhaken (oder im Modus `random` auf **Generate Random** klicken)
3. **Run** startet mit der Tabelle 0. Ordnung
4. **Next** berechnet jeweils die nächste Ordnung
5. **Calculate Answer** erstellt die Primimplikantentabelle und gibt die Lösung im Log aus
6. **Reset** setzt alles zurück

### Farben in der Primimplikantentabelle

Aktivierbar in den Einstellungen über *toggle color in table 2*.

| Farbe | Bedeutung |
|---|---|
| Dunkelrot | Wesentlicher Primimplikant und der Minterm, der ihn wesentlich macht |
| Orange | Von wesentlichen Primimplikanten abgedeckte Minterme |
| Grün | In allen Lösungen enthalten, aber nicht wesentlich |
| Blau | Austauschbar, unterscheidet sich zwischen den Lösungen |

## Aus dem Quellcode starten

Benötigt Python 3.12+ und CustomTkinter:

```bash
pip install customtkinter
python McCluskeyApp.py
```

## Einstellungen

Werden gespeichert unter:

```
%APPDATA%\maxbtw0\McCluskeyApp\settings.json
```
