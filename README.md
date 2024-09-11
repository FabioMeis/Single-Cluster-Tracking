Stelle sicher, dass du Python 3.x installiert hast. Außerdem müssen folgende Python-Bibliotheken installiert sein:

- `pandas`
- `numpy`
- `matplotlib`
- `scipy`
- `sklearn`
- `PyQt6`
- `tifffile`

Für die korrekte Funktion der Pipeline müssen alle Skripte im selben Ordner gespeichert werden. Die folgenden Dateien sollten sich im Projektverzeichnis befinden:

GUI.py: Startet die grafische Benutzeroberfläche.
CalculateDWithFlexibleAlphaGUI.py: Skript zur Berechnung der Diffusionskoeffizienten.
LowvsHighGUI.py: Skript zur Auswertung und Visualisierung der Diffusionskoeffizienten und Clustergrößen.
GetIntsGUI.py: Skript zur Extraktion von Intensitätsdaten aus TIF-Dateien.
PlotIntsGUI.py: Skript zur Analyse der Cluster- und Hintergrundkonzentrationen.

Verwendung

Skripte in einen Ordner legen und die Output-Pfade in PlotIntsGUI.py und LowvsHighGUI.py anpassen.
GUI starten: Um die grafische Benutzeroberfläche zu starten, führe das Skript GUI.py aus.

