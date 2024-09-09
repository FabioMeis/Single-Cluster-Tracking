import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import sys
import tifffile as tiff

def analyze_concentration_per_cluster_and_background(base_path, classified_image_file, laser_power, gain, bleaching_step_height):
    # Dateinamen
    csv_filename = 'Int.csv'

    # Parameter für die Konzentrationsberechnung
    pixellength = 0.16  # µm
    cell_height = 1  # µm
    factor = 10 / laser_power * 50 / gain  # Umrechnungsfaktor
    avogadro_number = 6.022e23

    # Dateien laden
    csv_file_path = os.path.join(base_path, csv_filename)

    # Lesen der CSV-Datei
    data = pd.read_csv(csv_file_path)

    # Lesen des Classified Image
    classified_image_stack = tiff.imread(classified_image_file)

    # Initialisieren von Listen für die Durchschnittskonzentrationen
    average_cluster_concentrations = []
    average_cellular_background_concentrations = []

    # Anzahl der Frames und Abmessungen der Bilder
    num_frames = classified_image_stack.shape[0]

    # Iteration über alle Frames im Bildstapel
    for frame_index, frame in enumerate(classified_image_stack):
        # Definieren der Klassifizierung der Pixel:
        # 0 für Cluster, 1 für zellulären Hintergrund, 2 für nicht zellulären Hintergrund
        cluster_mask = (frame == 0)
        cellular_background_mask = (frame == 1)
        non_cellular_background_mask = (frame == 2)

        # Sicherstellen, dass x und y innerhalb der Grenzen liegen
        height, width = frame.shape
        valid_data = data[(data['x'] < width) & (data['y'] < height)]

        # Verwenden der `x` und `y` Koordinaten, um die relevanten Pixel zu extrahieren
        cluster_pixels = cluster_mask[valid_data['y'], valid_data['x']]
        cellular_background_pixels = cellular_background_mask[valid_data['y'], valid_data['x']]
        non_cellular_background_pixels = non_cellular_background_mask[valid_data['y'], valid_data['x']]

        cluster_intensities = valid_data.loc[cluster_pixels, 'Intensity']
        cellular_background_intensities = valid_data.loc[cellular_background_pixels, 'Intensity']
        non_cellular_background_intensities = valid_data.loc[non_cellular_background_pixels, 'Intensity']

        # Überprüfen, ob es Clusterintensitäten gibt
        if len(cluster_intensities) == 0:
            continue  # Überspringen, wenn keine Cluster vorhanden sind

        # Berechnung der Teilchenzahl pro Pixel
        cluster_particles_per_pixel = cluster_intensities / bleaching_step_height
        cellular_background_particles_per_pixel = cellular_background_intensities / bleaching_step_height
        non_cellular_background_particles_per_pixel = non_cellular_background_intensities / bleaching_step_height

        # Volumen eines Pixels in µm^3
        pixel_volume = (pixellength ** 2) * cell_height

        # Berechnung der Teilchen pro µm^3
        cluster_particles_per_um3 = cluster_particles_per_pixel / pixel_volume * factor
        cellular_background_particles_per_um3 = cellular_background_particles_per_pixel / pixel_volume * factor
        non_cellular_background_particles_per_um3 = non_cellular_background_particles_per_pixel / pixel_volume * factor

        # Konzentration in Mol pro Liter
        cluster_concentration_m_per_l = cluster_particles_per_um3 / avogadro_number * 1e15
        cellular_background_concentration_m_per_l = cellular_background_particles_per_um3 / avogadro_number * 1e15
        non_cellular_background_concentration_m_per_l = non_cellular_background_particles_per_um3 / avogadro_number * 1e15

        # Berechnung der Konzentration in Nanomolar (nM) mit Umrechnungsfaktor
        cluster_concentration_nM = cluster_concentration_m_per_l * 1e9
        cellular_background_concentration_nM = cellular_background_concentration_m_per_l * 1e9
        non_cellular_background_concentration_nM = non_cellular_background_concentration_m_per_l * 1e9

        # Korrektur durch nichtzellulären Hintergrund
        corrected_cluster_concentration_nM = cluster_concentration_nM - np.mean(non_cellular_background_concentration_nM)
        corrected_cellular_background_concentration_nM = cellular_background_concentration_nM - np.mean(non_cellular_background_concentration_nM)

        # Durchschnittliche Konzentrationen berechnen
        average_corrected_cluster_concentration = np.mean(corrected_cluster_concentration_nM)
        average_corrected_cellular_background_concentration = np.mean(corrected_cellular_background_concentration_nM)

        # Speichern der Durchschnittskonzentrationen für diesen Frame
        average_cluster_concentrations.append(average_corrected_cluster_concentration)
        average_cellular_background_concentrations.append(average_corrected_cellular_background_concentration)

        print(f"Frame {frame_index}: Avg Corrected Cluster Concentration = {average_corrected_cluster_concentration:.2f} nM, Avg Corrected Background Concentration = {average_corrected_cellular_background_concentration:.2f} nM")

    # Plotten der Durchschnittskonzentrationen gegen die Frame-Nummer
    plt.figure(figsize=(12, 6))
    plt.plot(range(len(average_cluster_concentrations)), average_cluster_concentrations, marker='o', linestyle='-', label='Average Corrected Cluster Concentration', color='b')
    plt.plot(range(len(average_cellular_background_concentrations)), average_cellular_background_concentrations, marker='x', linestyle='--', label='Average Corrected Cellular Background Concentration', color='g')
    plt.title('Corrected Average Concentrations Over Time')
    plt.xlabel('Frame Index')
    plt.ylabel('Concentration (nM)')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    # Speichern des Plots
    output_folder = os.path.join(base_path, 'Plots')
    os.makedirs(output_folder, exist_ok=True)
    plt.savefig(os.path.join(output_folder, 'corrected_average_concentrations_over_time.png'))
    plt.show()

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python PlotInts.py <base_path> <classified_image_file> <laser_power> <gain> <bleaching_step_height>")
        sys.exit(1)

    base_path = sys.argv[1]
    classified_image_file = sys.argv[2]
    laser_power = float(sys.argv[3])
    gain = float(sys.argv[4])
    bleaching_step_height = float(sys.argv[5])

    analyze_concentration_per_cluster_and_background(base_path, classified_image_file, laser_power, gain, bleaching_step_height)
