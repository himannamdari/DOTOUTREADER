import sys
import h5py
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, QComboBox, QVBoxLayout, QWidget, QLineEdit, QDoubleSpinBox, QCheckBox
from scipy.signal import find_peaks, butter, lfilter

class GPRMaxOutReader(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("GPRMAX .out Reader")
        self.setGeometry(100, 100, 400, 450)

        self.initUI()

    def initUI(self):
        self.file_paths = []  # Store multiple file paths
        self.current_file_index = 0  # Index of the currently displayed file
        self.data = None

        self.label = QLabel("Select a .out file:")
        self.file_label = QLabel("No file selected")
        self.component_label = QLabel("Select a component:")
        self.component_combo = QComboBox()
        self.component_combo.addItems(["Hx", "Hy", "Ez"])
        self.range_label = QLabel("Enable Range:")
        self.range_checkbox = QCheckBox()
        self.start_label = QLabel("Start Sample (optional):")
        self.start_input = QLineEdit()
        self.end_label = QLabel("End Sample (optional):")
        self.end_input = QLineEdit()
        self.threshold_label = QLabel("Enable Threshold:")
        self.threshold_checkbox = QCheckBox()
        self.threshold_label2 = QLabel("Peak Threshold:")
        self.threshold_input = QDoubleSpinBox()
        self.threshold_input.setDecimals(2)
        self.select_file_button = QPushButton("Select .out files")
        self.plot_button = QPushButton("Plot Data")
        self.next_file_button = QPushButton("Next File")
        self.prev_file_button = QPushButton("Previous File")
        self.file_info_label = QLabel("File 0 of 0")
        self.range_enabled = False
        self.threshold_enabled = False

        # Preprocessing filter buttons
        self.tga_button = QPushButton("Apply TGA")
        self.tzero_button = QPushButton("Apply T-Zero Correction")
        self.bandpass_button = QPushButton("Apply Bandpass Filter")
        self.apply_all_button = QPushButton("Apply All Filters")

        # Filter parameters
        self.tga_gain = 2.0  # TGA gain factor
        self.bandpass_lowcut = 10.0  # Bandpass filter lower cutoff frequency (Hz)
        self.bandpass_highcut = 1000.0  # Bandpass filter upper cutoff frequency (Hz)
        self.bandpass_order = 5  # Bandpass filter order

        # Add a class-level variable to track the selected filter type
        self.selected_filter = None

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.file_label)
        layout.addWidget(self.select_file_button)
        layout.addWidget(self.component_label)
        layout.addWidget(self.component_combo)
        layout.addWidget(self.range_label)
        layout.addWidget(self.range_checkbox)
        layout.addWidget(self.start_label)
        layout.addWidget(self.start_input)
        layout.addWidget(self.end_label)
        layout.addWidget(self.end_input)
        layout.addWidget(self.threshold_label)
        layout.addWidget(self.threshold_checkbox)
        layout.addWidget(self.threshold_label2)
        layout.addWidget(self.threshold_input)
        layout.addWidget(self.plot_button)
        layout.addWidget(self.file_info_label)
        layout.addWidget(self.prev_file_button)
        layout.addWidget(self.next_file_button)
        layout.addWidget(self.tga_button)
        layout.addWidget(self.tzero_button)
        layout.addWidget(self.bandpass_button)
        layout.addWidget(self.apply_all_button)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

        self.select_file_button.clicked.connect(self.browse_files)
        self.plot_button.clicked.connect(self.plot_data)
        self.next_file_button.clicked.connect(self.next_file)
        self.prev_file_button.clicked.connect(self.prev_file)
        self.range_checkbox.stateChanged.connect(self.toggle_range)
        self.threshold_checkbox.stateChanged.connect(self.toggle_threshold)
        self.tga_button.clicked.connect(self.apply_tga)
        self.tzero_button.clicked.connect(self.apply_tzero)
        self.bandpass_button.clicked.connect(self.apply_bandpass)
        self.apply_all_button.clicked.connect(self.apply_all_filters)

        self.update_ui()

    def update_ui(self):
        num_files = len(self.file_paths)
        self.file_info_label.setText(f"File {self.current_file_index + 1} of {num_files}")
        self.next_file_button.setEnabled(self.current_file_index < num_files - 1)
        self.prev_file_button.setEnabled(self.current_file_index > 0)

    def toggle_range(self, state):
        self.range_enabled = state == 2  # 2 corresponds to checked
        self.start_input.setEnabled(self.range_enabled)
        self.end_input.setEnabled(self.range_enabled)

    def toggle_threshold(self, state):
        self.threshold_enabled = state == 2  # 2 corresponds to checked
        self.threshold_input.setEnabled(self.threshold_enabled)

    def plot_data(self):
        if self.file_paths:
            component = self.component_combo.currentText()
            file_path = self.file_paths[self.current_file_index]
            file_name = file_path.split("/")[-1]  # Extract file name from path
            filter_name = self.selected_filter  # Use the selected filter name

            if self.data is not None:
                try:
                    if self.range_enabled:
                        start_sample = int(self.start_input.text()) if self.start_input.text() else 0
                        end_sample = int(self.end_input.text()) if self.end_input.text() else len(self.data)
                    else:
                        start_sample = 0
                        end_sample = len(self.data)

                    # Get the total length of the signal
                    signal_length = len(self.data)

                    # Check and set default values for start and end
                    if start_sample < 0:
                        start_sample = 0
                    if end_sample > signal_length:
                        end_sample = signal_length

                    if start_sample < end_sample:
                        data_to_plot = self.data[start_sample:end_sample]
                        time = np.arange(start_sample, end_sample, 1)

                        if self.threshold_enabled:
                            # Find peaks using a user-defined threshold
                            threshold = self.threshold_input.value()
                            peaks, _ = find_peaks(data_to_plot, height=threshold, distance=100)
                            filter_name += "Threshold Filter, "
                        else:
                            peaks = []

                        # Calculate statistics
                        min_value = np.min(data_to_plot)
                        max_value = np.max(data_to_plot)
                        mean_value = np.mean(data_to_plot)
                        std_value = np.std(data_to_plot)
                        q1 = np.percentile(data_to_plot, 25)
                        q2 = np.percentile(data_to_plot, 50)
                        q3 = np.percentile(data_to_plot, 75)

                        # Create the plot
                        plt.figure()
                        plt.plot(time, data_to_plot, label="GPR signal")
                        if peaks:
                            plt.scatter(time[peaks], data_to_plot[peaks], color='red', label="Peaks", marker='o')

                        # Add filter name to the plot
                        #plt.text(0.7, 0.9, f"Applied Filter: {filter_name}", transform=plt.gca().transAxes, bbox=dict(facecolor='white', edgecolor='gray', boxstyle='round'))

                        plt.xlabel("Time")
                        plt.ylabel(component)
                        plt.title(f"{component} Data - {file_name} ({filter_name})")  # Include filter name in the title

                        # Add legends
                        plt.legend()

                        # Add statistics to the plot
                        stats_text = f"Min: {min_value:.2f}\nMax: {max_value:.2f}\nMean: {mean_value:.2f}\nStd: {std_value:.2f}\nQ1: {q1:.2f}\nQ2: {q2:.2f}\nQ3: {q3:.2f}"
                        plt.text(0.7, 0.5, stats_text, transform=plt.gca().transAxes, bbox=dict(facecolor='white', edgecolor='gray', boxstyle='round'))

                        plt.show()
                    else:
                        print("Start sample should be less than end sample.")
                except ValueError:
                    print("Invalid input for start or end sample.")

    def read_gprmax_out_file(self, file_path, component):
        try:
            with h5py.File(file_path, 'r') as f:
                data = f['rxs']['rx1'][component][:]

            return data
        except Exception as e:
            print(f"Error reading .out file: {str(e)}")
            return None

    def browse_files(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_dialog = QFileDialog()
        file_dialog.setOptions(options)
        file_paths, _ = file_dialog.getOpenFileNames(self, "Select .out files", "", "GPRMAX .out files (*.out);;All Files (*)")

        if file_paths:
            self.file_paths = file_paths
            self.current_file_index = 0
            self.file_label.setText(file_paths[0])

            # Load the data from the selected file
            self.data = self.read_gprmax_out_file(file_paths[0], self.component_combo.currentText())
            self.update_ui()

    def next_file(self):
        if self.current_file_index < len(self.file_paths) - 1:
            self.current_file_index += 1
            self.file_label.setText(self.file_paths[self.current_file_index])
            self.data = self.read_gprmax_out_file(self.file_paths[self.current_file_index], self.component_combo.currentText())
            self.update_ui()

    def prev_file(self):
        if self.current_file_index > 0:
            self.current_file_index -= 1
            self.file_label.setText(self.file_paths[self.current_file_index])
            self.data = self.read_gprmax_out_file(self.file_paths[self.current_file_index], self.component_combo.currentText())
            self.update_ui()

    def apply_tga(self):
        if self.data is not None:
            # Apply Time Gain Adjustment (TGA)
            self.data = self.data * self.tga_gain  # Adjust the gain factor as needed
            self.selected_filter = "TGA"
            self.plot_data()

    def apply_tzero(self):
        if self.data is not None:
            # Apply T-Zero Correction
            self.data = self.data - np.mean(self.data)
            self.selected_filter = "T-Zero Correction"
            self.plot_data()

    def apply_bandpass(self):
        if self.data is not None:
            # Apply Bandpass Filter
            if self.bandpass_lowcut < self.bandpass_highcut:
                self.data = self.butter_bandpass_filter(self.data, self.bandpass_lowcut, self.bandpass_highcut, fs=1000.0, order=self.bandpass_order)
                self.selected_filter = f"Bandpass Filter ({self.bandpass_lowcut}-{self.bandpass_highcut} Hz)"
                self.plot_data()

    def apply_all_filters(self):
        # Apply all selected filters
        self.apply_tga()
        self.apply_tzero()
        self.apply_bandpass()

        # Replot the data with all filters applied
        self.plot_data()

    @staticmethod
    def butter_bandpass(lowcut, highcut, fs, order=5):
        nyquist = 0.5 * fs
        low = lowcut / nyquist
        high = highcut / nyquist
        b, a = butter(order, [low, high], btype='band')
        return b, a

    @staticmethod
    def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
        b, a = GPRMaxOutReader.butter_bandpass(lowcut, highcut, fs, order=order)
        y = lfilter(b, a, data)
        return y

def main():
    app = QApplication(sys.argv)
    window = GPRMaxOutReader()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
