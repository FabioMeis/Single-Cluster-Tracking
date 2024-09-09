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
    QFormLayout,
    QHBoxLayout,
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Fluoreszenzmikroskopie Analyse")
        self.setGeometry(100, 100, 800, 900)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()

        # Diffusionsanalyse Einstellungen
        diffusion_group_box = QFormLayout()

        self.diffusion_checkbox = QCheckBox("Diffusionsanalyse durchführen")
        diffusion_group_box.addRow(self.diffusion_checkbox)

        self.input_calculate_label = QLabel("MosaicResults auswählen:")
        self.input_calculate_input = QLineEdit()
        self.input_calculate_button = QPushButton("Datei auswählen")
        self.input_calculate_button.clicked.connect(self.select_calculate_input_file)

        diffusion_group_box.addRow(self.input_calculate_label, self.input_calculate_input)
        diffusion_group_box.addWidget(self.input_calculate_button)

        self.r_squared_label = QLabel("R² Schwellenwert:")
        self.r_squared_input = QLineEdit("0.9")
        diffusion_group_box.addRow(self.r_squared_label, self.r_squared_input)

        self.min_duration_label = QLabel("Minimale Zeit, die ein Cluster existieren muss (Sekunden):")
        self.min_duration_input = QLineEdit("30")
        diffusion_group_box.addRow(self.min_duration_label, self.min_duration_input)

        self.frame_interval_label = QLabel("Frame-Intervall (Sekunden):")
        self.frame_interval_input = QLineEdit("10")
        diffusion_group_box.addRow(self.frame_interval_label, self.frame_interval_input)

        # Plots erstellen Checkbox
        self.plot_checkbox = QCheckBox("Plots erstellen")
        diffusion_group_box.addRow(self.plot_checkbox)

        layout.addLayout(diffusion_group_box)

        # Start Button
        self.start_button = QPushButton("Analyse starten")
        self.start_button.clicked.connect(self.run_analysis)
        layout.addWidget(self.start_button)

        self.central_widget.setLayout(layout)

    def select_calculate_input_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "MosaicResults auswählen:")
        if file_path:
            self.input_calculate_input.setText(file_path)

    def run_analysis(self):
        calculate_input_file = self.input_calculate_input.text()
        r_squared_threshold = self.r_squared_input.text()
        min_duration = self.min_duration_input.text()
        frame_interval = self.frame_interval_input.text()

        script_dir = os.path.dirname(os.path.realpath(__file__))

        # Prüfe, ob Diffusionsanalyse durchgeführt werden soll
        if self.diffusion_checkbox.isChecked():
            if not os.path.isfile(calculate_input_file):
                QMessageBox.warning(self, "Fehler", "Bitte wählen Sie eine gültige Eingabedatei für die Diffusionsanalyse aus.")
                return
            try:
                output_folder = os.path.join(os.path.dirname(calculate_input_file), "Graphen")
                os.makedirs(output_folder, exist_ok=True)

                # Skript CalculateDWithFlexibleAlphaGUI.py ausführen
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

        # Optional: Plots erstellen
        if self.plot_checkbox.isChecked():
            try:
                result_lowhigh = subprocess.run(
                    ["python", os.path.join(script_dir, "LowvsHighGUI.py"),
                     output_folder, output_folder],
                    check=True, capture_output=True, text=True
                )
                print("LowvsHigh Output:", result_lowhigh.stdout)
            except subprocess.CalledProcessError as e:
                QMessageBox.critical(self, "Fehler", f"Ein Fehler ist aufgetreten: {e.stderr}")
                print("Fehler:", e.stderr)
                return

        QMessageBox.information(self, "Erfolg", "Die Analyse wurde erfolgreich abgeschlossen.")


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
