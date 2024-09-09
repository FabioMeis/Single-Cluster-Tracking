import tifffile
import numpy as np
import pandas as pd
import os
import sys

def extract_intensities(tif_file, output_folder):
    # Bild öffnen
    with tifffile.TiffFile(tif_file) as tif:
        image = tif.asarray()

    # Zugriff auf den 0. Frame
    frame_0 = image[0]

    # Koordinaten und Intensitäten sammeln
    height, width = frame_0.shape
    data = []

    for y in range(height):
        for x in range(width):
            intensity = frame_0[y, x]
            data.append({'x': x, 'y': y, 'Intensity': intensity})

    # In ein DataFrame umwandeln
    df = pd.DataFrame(data)

    # Ausgabeordner sicherstellen
    os.makedirs(output_folder, exist_ok=True)

    # In einer CSV-Datei speichern
    output_csv_path = os.path.join(output_folder, 'Int.csv')
    df.to_csv(output_csv_path, index=False)

    print("CSV-Datei wurde erfolgreich erstellt:", output_csv_path)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python GetInts.py <tif_file> <output_folder>")
        sys.exit(1)

    tif_file = sys.argv[1]
    output_folder = sys.argv[2]

    extract_intensities(tif_file, output_folder)
