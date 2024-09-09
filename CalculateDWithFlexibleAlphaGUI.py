import os
import csv
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score

def process_tracking_data(input_file_path):
    print(f"Processing file: {input_file_path}")
    data = pd.read_csv(input_file_path)
    tracks_data = {}

    for index, row in data.iterrows():
        track_id = int(row[1])
        frame_id = int(row[2])
        x_coord = float(row[3])
        y_coord = float(row[4])
        size_pixel = float(row[6]) 

        if track_id not in tracks_data:
            tracks_data[track_id] = []
        tracks_data[track_id].append([frame_id, x_coord, y_coord, size_pixel])

    return tracks_data

def export_to_csv(tracks_data, output_folder, output_file_name):
    os.makedirs(output_folder, exist_ok=True)
    
    csv_file_path = os.path.join(output_folder, output_file_name)
    with open(csv_file_path, 'w', newline='') as f:
        writer = csv.writer(f)

        header_row = ['FrameID', 'Time [s]'] + [f'TrackID: {track_id} {param}' for track_id in tracks_data.keys() for param in ['X', 'Y', 'Size']]
        writer.writerow(header_row)

        max_frames = max(len(data) for data in tracks_data.values())
        frame_rate = 10

        for i in range(max_frames):
            time_seconds = i * frame_rate
            row = [i, time_seconds]
            for track_data in tracks_data.values():
                if i < len(track_data):
                    row.extend([track_data[i][1] * 0.16, track_data[i][2] * 0.16, track_data[i][3] * 0.0256]) # Convert pixels to µm and µm²
                else:
                    row.extend(['', '', ''])
            writer.writerow(row)

    print(f"Exported to {csv_file_path}")

def plot_tracks(tracks_data, output_folder, plot_file_name):
    os.makedirs(output_folder, exist_ok=True)

    plt.figure(figsize=(10, 6))
    for track_id, track_data in tracks_data.items():
        track_data = np.array(track_data)
        plt.plot(track_data[:, 1] * 0.16, track_data[:, 2] * 0.16, label=f'TrackID {track_id}')
    
    plt.xlabel('X Position (µm)')
    plt.ylabel('Y Position (µm)')
    plt.title('Particle Tracks')
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(output_folder, plot_file_name))
    plt.close()

def compute_diffusion_coefficients(data, plot_folder, r_squared_threshold, min_duration, frame_interval):
    os.makedirs(plot_folder, exist_ok=True)

    track_columns = [col for col in data.columns if col.startswith("TrackID")]

    diffusion_coefficients = []
    avg_cluster_sizes = []
    msd_data = []
    valid_clusters = []
    alphas = []
    r_squared_values = []

    for i in range(0, len(track_columns), 3):
        track_x_col = track_columns[i]
        track_y_col = track_columns[i+1]
        track_size_col = track_columns[i+2]
        track_data = data[["Time [s]", track_x_col, track_y_col, track_size_col]].dropna()
        times = track_data["Time [s]"].values

        if len(times) <= 1 or (times[-1] - times[0]) < min_duration:
            print(f"Track {track_x_col} hat nicht genügend Datenpunkte oder Dauer.")
            continue

        x_positions = track_data[track_x_col].values
        y_positions = track_data[track_y_col].values
        sizes_um2 = track_data[track_size_col].values

        lags = np.arange(1, int(len(times) / 4))
        if len(lags) == 0:
            print(f"Nicht genügend Datenpunkte für Track {track_x_col}")
            continue

        msd = np.zeros(len(lags))
        for j, lag in enumerate(lags):
            if len(x_positions) <= lag:
                print(f"Nicht genügend Datenpunkte für Lag {lag} bei Track {track_x_col}")
                continue
            dx = x_positions[lag:] - x_positions[:-lag]
            dy = y_positions[lag:] - y_positions[:-lag]
            msd[j] = np.mean(dx**2 + dy**2)

        if len(msd) == 0 or np.isnan(msd).all():
            print(f"Keine gültigen MSD-Daten für Track {track_x_col}")
            continue

        fit_range = min(int(len(lags) * 0.8), len(lags))
        if fit_range < 4:
            print(f"Nicht genügend Datenpunkte für linearen Fit bei Track {track_x_col}")
            continue

        xdata = np.log10(lags[:fit_range] * frame_interval)
        ydata = np.log10(msd[:fit_range])

        def log_fit_func(x, alpha, lg4D):
            return alpha * x + lg4D

        try:
            popt, _ = curve_fit(log_fit_func, xdata, ydata, p0=[1, 0.1])
            y_fit = log_fit_func(xdata, *popt)
            r_squared = r2_score(ydata, y_fit)

            if r_squared >= r_squared_threshold:
                alpha, lg4D = popt
                D_log = (10 ** lg4D) / 4

                diffusion_coefficients.append(D_log)
                avg_cluster_sizes.append(np.mean(sizes_um2))
                valid_clusters.append(track_x_col.split(":")[1].strip().split()[0])
                msd_data.append((lags * frame_interval, msd))
                alphas.append(alpha)
                r_squared_values.append(r_squared)
            else:
                print(f"R²-Wert zu niedrig für Track {track_x_col}: {r_squared:.2f}")
        except Exception as e:
            print(f"Fehler beim Fitten von log(MSD) vs. log(LagTime) für Track {track_x_col}: {e}")

    output_df = pd.DataFrame({
        "Cluster": valid_clusters,
        "Average Cluster Size": avg_cluster_sizes,
        "Diffusion Coefficient": diffusion_coefficients,
        "Alpha": alphas,
        "R_squared": r_squared_values
    })

    print(f"Output DataFrame: {output_df}")
    return output_df, msd_data, valid_clusters

def plot_and_fit_alphas(output_df, plot_folder):
    os.makedirs(plot_folder, exist_ok=True)

    # Split data by expression level
    expression_levels = {
        "HighEx": output_df[output_df['Cluster'].str.contains('HighEx')],
        "LowEx": output_df[output_df['Cluster'].str.contains('LowEx')]
    }

    for level, df in expression_levels.items():
        if df.empty:
            print(f'Keine Daten für {level}')
            continue

        plt.figure(figsize=(10, 6))
        plt.scatter(df["Average Cluster Size"], df["Alpha"], label=f'{level} Alpha')
        
        # Fit a line to the data
        def linear_fit(x, m, c):
            return m * x + c

        try:
            popt, _ = curve_fit(linear_fit, df["Average Cluster Size"], df["Alpha"])
            plt.plot(df["Average Cluster Size"], linear_fit(df["Average Cluster Size"], *popt), color='red', label=f'{level} Fit')
            plt.xlabel('Average Cluster Size (µm²)')
            plt.ylabel('Alpha')
            plt.title(f'Alpha vs. Average Cluster Size for {level}')
            plt.legend()
            plt.grid(True)
            plt.savefig(os.path.join(plot_folder, f'{level}_alpha_fit.png'))
            plt.close()
            print(f'Fit parameters for {level}: Slope = {popt[0]}, Intercept = {popt[1]}')
        except Exception as e:
            print(f'Fehler beim Fitten der Alpha-Werte für {level}: {e}')

def main():
    if len(sys.argv) != 6:
        print("Usage: python CalculateDWithFlexibleAlphaGUI.py <input_file> <r_squared_threshold> <min_duration> <frame_interval> <output_folder>")
        return

    input_file = sys.argv[1]
    r_squared_threshold = float(sys.argv[2])
    min_duration = int(sys.argv[3])
    frame_interval = int(sys.argv[4])
    output_folder = sys.argv[5]

    output_file_name = "calculated_output.csv"

    tracks_data = process_tracking_data(input_file)
    export_to_csv(tracks_data, output_folder, output_file_name)
    plot_tracks(tracks_data, output_folder, f'{output_file_name}_tracks_plot.png')
    
    combined_csv_file = os.path.join(output_folder, output_file_name)
    data = pd.read_csv(combined_csv_file, encoding='latin-1')
    
    plot_folder = os.path.join(output_folder, 'Log(MSD)vsLog(LagTime)')
    diffusion_output_file = os.path.join(output_folder, 'diffusion_coefficients.csv')

    output_df, msd_data, valid_clusters = compute_diffusion_coefficients(data, plot_folder, r_squared_threshold, min_duration, frame_interval)

    for i, (lags, msd) in enumerate(msd_data):
        plt.figure(figsize=(10, 6))
        plt.scatter(np.log10(lags), np.log10(msd), label=f'Cluster {valid_clusters[i]}')
        plt.xlabel('Log10(Time Lag (s))')
        plt.ylabel('Log10(MSD (Mean Squared Displacement))')
        plt.title(f'MSD vs. Time Lag for Cluster {valid_clusters[i]}')
        plt.legend()
        plt.grid(True)
        plot_path = os.path.join(plot_folder, f'MSD_Cluster_{valid_clusters[i]}.png')
        plt.savefig(plot_path)
        plt.close()

    output_df.to_csv(diffusion_output_file, index=False)
    print(f"Diffusion coefficients saved to {diffusion_output_file}")

    plot_and_fit_alphas(output_df, plot_folder)

if __name__ == "__main__":
    main()
