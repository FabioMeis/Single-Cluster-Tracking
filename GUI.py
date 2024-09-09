import sys
import os
import subprocess
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QCheckBox,
    QGroupBox,
    QFormLayout,
    QHBoxLayout,
)
from PyQt6.QtGui import QPalette, QColor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Fluoreszenzmikroskopie Analyse")
        self.setGeometry(100, 100, 800, 900)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()

        # Diffusionsanalyse Einstellungen
        diffusion_group_box = QGroupBox("Diffusionsanalyse Einstellungen")
        diffusion_layout = QFormLayout()

        self.diffusion_checkbox = QCheckBox("Diffusionsanalyse durchführen")
        diffusion_layout.addRow(self.diffusion_checkbox)

        self.input_calculate_label = QLabel("MosaicResults auswählen:")
        self.input_calculate_input = QLineEdit()
        self.input_calculate_button = QPushButton("Datei auswählen")
        self.input_calculate_button.clicked.connect(self.select_calculate_input_file)

        diffusion_layout.addRow(self.input_calculate_label, self.input_calculate_input)
        diffusion_layout.addWidget(self.input_calculate_button)

        self.r_squared_label = QLabel("R² Schwellenwert:")
        self.r_squared_input = QLineEdit("0.9")
        diffusion_layout.addRow(self.r_squared_label, self.r_squared_input)

        self.min_duration_label = QLabel("Minimale Zeit, die ein Cluster existieren muss (Sekunden):")
        self.min_duration_input = QLineEdit("30")
        diffusion_layout.addRow(self.min_duration_label, self.min_duration_input)

        self.frame_interval_label = QLabel("Frame-Intervall (Sekunden):")
        self.frame_interval_input = QLineEdit("10")
        diffusion_layout.addRow(self.frame_interval_label, self.frame_interval_input)

        # Plot Einstellungen innerhalb der Diffusionsanalyse
        self.plot_checkbox = QCheckBox("Plots erstellen")
        diffusion_layout.addRow(self.plot_checkbox)

        self.advanced_settings_widget = QWidget()
        advanced_layout = QVBoxLayout()
        self.advanced_settings_widget.setLayout(advanced_layout)

        # Diffusion Coefficient Plot Settings
        self.diffusion_bins_label = QLabel("Anzahl der Bins (Diffusionskoeffizient):")
        self.diffusion_bins_input = QLineEdit("30")
        advanced_layout.addWidget(self.diffusion_bins_label)
        advanced_layout.addWidget(self.diffusion_bins_input)

        self.diffusion_range_label = QLabel("Diffusionsbereich (min, max):")
        self.diffusion_range_min_input = QLineEdit("0.0")
        self.diffusion_range_max_input = QLineEdit("0.07")
        diffusion_range_layout = QHBoxLayout()
        diffusion_range_layout.addWidget(self.diffusion_range_min_input)
        diffusion_range_layout.addWidget(self.diffusion_range_max_input)
        advanced_layout.addWidget(self.diffusion_range_label)
        advanced_layout.addLayout(diffusion_range_layout)

        # Average Cluster Size Plot Settings
        self.size_bins_label = QLabel("Anzahl der Bins (Clustergröße):")
        self.size_bins_input = QLineEdit("30")
        advanced_layout.addWidget(self.size_bins_label)
        advanced_layout.addWidget(self.size_bins_input)

        self.size_range_label = QLabel("Größenbereich (min, max):")
        self.size_range_min_input = QLineEdit("0.0")
        self.size_range_max_input = QLineEdit("3.5")
        size_range_layout = QHBoxLayout()
        size_range_layout.addWidget(self.size_range_min_input)
        size_range_layout.addWidget(self.size_range_max_input)
        advanced_layout.addWidget(self.size_range_label)
        advanced_layout.addLayout(size_range_layout)

        self.advanced_settings_widget.setVisible(False)

        self.advanced_options_button = QPushButton("Erweiterte Einstellungen")
        self.advanced_options_button.clicked.connect(self.toggle_advanced_settings)
        diffusion_layout.addWidget(self.advanced_options_button)
        diffusion_layout.addWidget(self.advanced_settings_widget)

        diffusion_group_box.setLayout(diffusion_layout)
        layout.addWidget(diffusion_group_box)

        # Intensitätsanalyse Einstellungen
        intensity_group_box = QGroupBox("Intensitätsbasierte Bleichschrittanalyse Einstellungen")
        intensity_layout = QFormLayout()

        self.intensity_checkbox = QCheckBox("Bleichschrittanalyse durchführen")
        intensity_layout.addRow(self.intensity_checkbox)

        self.tif_file_label = QLabel("TIF-Datei für Bleichschrittanalyse:")
        self.tif_file_input = QLineEdit()
        self.tif_file_button = QPushButton("Datei auswählen")
        self.tif_file_button.clicked.connect(self.select_tif_file)

        intensity_layout.addRow(self.tif_file_label, self.tif_file_input)
        intensity_layout.addWidget(self.tif_file_button)

        self.classified_image_label = QLabel("Classified Image TIF-Datei:")
        self.classified_image_input = QLineEdit()
        self.classified_image_button = QPushButton("Datei auswählen")
        self.classified_image_button.clicked.connect(self.select_classified_image_file)

        intensity_layout.addRow(self.classified_image_label, self.classified_image_input)
        intensity_layout.addWidget(self.classified_image_button)

        self.laser_power_label = QLabel("Laser Power:")
        self.laser_power_input = QLineEdit("2")
        intensity_layout.addRow(self.laser_power_label, self.laser_power_input)

        self.gain_label = QLabel("Gain:")
        self.gain_input = QLineEdit("300")
        intensity_layout.addRow(self.gain_label, self.gain_input)

        self.bleaching_step_height_label = QLabel("Bleichschritthöhe:")
        self.bleaching_step_height_input = QLineEdit("4572")
        intensity_layout.addRow(self.bleaching_step_height_label, self.bleaching_step_height_input)

        intensity_group_box.setLayout(intensity_layout)
        layout.addWidget(intensity_group_box)

        # Start Button
        self.start_button = QPushButton("Analyse starten")
        self.start_button.clicked.connect(self.run_analysis)
        layout.addWidget(self.start_button)

        self.central_widget.setLayout(layout)

        # Set styles for group boxes
        self.set_styles()

    def set_styles(self):
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#f0f0f0"))
        self.setPalette(palette)

        # Custom styles for group boxes
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #666666;
                border-radius: 5px;
                margin-top: 10px;
                background-color: #e6f2ff;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 5px;
                color: #333333;
            }
            QLabel {
                margin-left: 5px;
                color: #333333; /* Dunklere Schriftfarbe */
            }
            QPushButton {
                margin: 5px 0;
                padding: 5px 10px;
            }
            QLineEdit {
                color: #000000; /* Dunklere Schriftfarbe für Eingabefelder */
            }
            QWidget#AdvancedSettingsWidget {
                border: 1px solid #999999;
                margin-top: 5px;
                padding: 5px;
                background-color: #f9f9f9;
            }
        """)

    def select_calculate_input_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "MosaicResults auswählen:")
        if file_path:
            self.input_calculate_input.setText(file_path)

    def select_tif_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Wählen Sie die TIF-Datei für die Bleichschrittanalyse aus", filter="TIF Files (*.tif *.tiff)")
        if file_path:
            self.tif_file_input.setText(file_path)

    def select_classified_image_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Wählen Sie die Classified Image TIF-Datei aus", filter="TIF Files (*.tif *.tiff)")
        if file_path:
            self.classified_image_input.setText(file_path)

    def toggle_advanced_settings(self):
        self.advanced_settings_widget.setVisible(not self.advanced_settings_widget.isVisible())

    def run_analysis(self):
        calculate_input_file = self.input_calculate_input.text()
        r_squared_threshold = self.r_squared_input.text()
        min_duration = self.min_duration_input.text()
        frame_interval = self.frame_interval_input.text()
        diffusion_bins = int(self.diffusion_bins_input.text())
        size_bins = int(self.size_bins_input.text())
        diffusion_range_min = float(self.diffusion_range_min_input.text())
        diffusion_range_max = float(self.diffusion_range_max_input.text())
        size_range_min = float(self.size_range_min_input.text())
        size_range_max = float(self.size_range_max_input.text())

        tif_file = self.tif_file_input.text()
        classified_image_file = self.classified_image_input.text()
        laser_power = self.laser_power_input.text()
        gain = self.gain_input.text()
        bleaching_step_height = self.bleaching_step_height_input.text()

        script_dir = os.path.dirname(os.path.realpath(__file__))

        if self.diffusion_checkbox.isChecked():
            if not os.path.isfile(calculate_input_file):
                QMessageBox.warning(self, "Fehler", "Bitte wählen Sie eine gültige Eingabedatei für CalculateDWithFlexibleAlpha aus.")
                return
            try:
                # Ausgabeordner "Graphen" im selben Pfad wie die Eingabedatei erstellen
                base_folder = os.path.dirname(calculate_input_file)
                output_folder = os.path.join(base_folder, "Graphen")
                os.makedirs(output_folder, exist_ok=True)

                # Ausführen von CalculateDWithFlexibleAlphaGUI.py im selben Ordner wie dieses Skript
                result_calculate = subprocess.run(
                    ["python", os.path.join(script_dir, "CalculateDWithFlexibleAlphaGUI.py"), 
                    calculate_input_file, r_squared_threshold, min_duration, frame_interval, output_folder],
                    check=True, capture_output=True, text=True
                )
                print("CalculateDWithFlexibleAlpha Output:", result_calculate.stdout)
            except subprocess.CalledProcessError as e:
                QMessageBox.critical(self, "Fehler", f"Ein Fehler ist aufgetreten: {e.stderr}")
                print("Fehler:", e.stderr)
                return

        if self.plot_checkbox.isChecked():
            if not os.path.isdir(os.path.join(os.path.dirname(calculate_input_file), "Graphen")):
                QMessageBox.warning(self, "Fehler", "Es gibt keinen Ausgabeordner 'Graphen', um die Plots zu erstellen.")
                return
            try:
                # Verwenden des Ausgabeordners von CalculateD als Eingabeordner für LowvsHigh
                output_folder = os.path.join(os.path.dirname(calculate_input_file), "Graphen")
                result_lowhigh = subprocess.run(
                    ["python", os.path.join(script_dir, "LowvsHighGUI.py"), 
                    output_folder, output_folder, str(diffusion_bins), str(diffusion_range_min), str(diffusion_range_max),
                    str(size_bins), str(size_range_min), str(size_range_max)],
                    check=True, capture_output=True, text=True
                )
                print("LowvsHigh Output:", result_lowhigh.stdout)
            except subprocess.CalledProcessError as e:
                QMessageBox.critical(self, "Fehler", f"Ein Fehler ist aufgetreten: {e.stderr}")
                print("Fehler:", e.stderr)
                return

        if self.intensity_checkbox.isChecked():
            if not os.path.isfile(tif_file):
                QMessageBox.warning(self, "Fehler", "Bitte wählen Sie eine gültige TIF-Datei für die Intensitätsanalyse aus.")
                return
            if not os.path.isfile(classified_image_file):
                QMessageBox.warning(self, "Fehler", "Bitte wählen Sie eine gültige Classified Image TIF-Datei aus.")
                return
            try:
                output_folder = os.path.join(os.path.dirname(calculate_input_file), "Graphen")
                # Analyse der Intensitäten mit GetInts.py im selben Ordner wie dieses Skript
                result_getints = subprocess.run(
                    ["python", os.path.join(script_dir, "GetIntsGUI.py"),
                    tif_file, output_folder],
                    check=True, capture_output=True, text=True
                )
                print("GetInts Output:", result_getints.stdout)

                # Umwandlung der Intensitäten in Konzentrationen mit PlotInts.py im selben Ordner wie dieses Skript
                result_plotints = subprocess.run(
                    ["python", os.path.join(script_dir, "PlotIntsGUI.py"),
                    output_folder, classified_image_file, laser_power, gain, bleaching_step_height],
                    check=True, capture_output=True, text=True
                )
                print("PlotInts Output:", result_plotints.stdout)

            except subprocess.CalledProcessError as e:
                QMessageBox.critical(self, "Fehler", f"Ein Fehler ist aufgetreten: {e.stderr}")
                print("Fehler:", e.stderr)
                return

        QMessageBox.information(self, "Erfolg", "Die Analyse wurde erfolgreich abgeschlossen.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
