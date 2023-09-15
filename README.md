# GPRMAX .out Reader

GPRMAX .out Reader is a Python-based graphical user interface (GUI) tool that facilitates reading, processing, and visualizing GPRMAX simulation output files (with `.out` extension). The application offers functionalities to apply various filters and visualize the resultant GPR signals.

## Features

- **File Selection**: Easily select one or multiple GPRMAX .out files and navigate between them.
- **Component Selection**: Choose the electromagnetic component (e.g., Hx, Hy, Ez) to display.
- **Data Plotting**: Visualize GPR signal data with capabilities to set a range and a threshold for peak detection.
- **Signal Processing**:
  - **Time Gain Adjustment (TGA)**: Adjust the amplitude of the GPR signal over time.
  - **T-Zero Correction**: Remove DC bias from the GPR signal.
  - **Bandpass Filter**: Focus on frequencies of interest by filtering out unwanted frequencies.
  - Option to apply all filters consecutively.
- **Interactive UI**: Toggle between different functionalities with ease, thanks to the PyQt5 framework.

## Dependencies

- Python
- h5py
- numpy
- matplotlib
- PyQt5
- scipy

## Usage

To run the application, execute the provided script. This will pop up the GUI, where you can load `.out` files, apply filters, and visualize the results.

```bash
python <script_name>.py
```

Ensure all dependencies are installed in your Python environment.

## How It Works

1. **Select .out files**: Start by choosing one or more GPRMAX `.out` files. Navigate between different files if multiple are loaded.
2. **Choose Component**: Select the electromagnetic component (e.g., Hx, Hy, Ez) to visualize.
3. **Set Range & Threshold (optional)**: Define a specific range for the data and set a threshold for peak detection.
4. **Apply Filters**: Use the provided buttons to apply various filters to the GPR signal data.
5. **Plot Data**: Visualize the processed GPR data, including detected peaks.

## Feedback & Contributions

If you have any suggestions, issues, or improvements, please open an issue on this GitHub repository. Contributions to the code are also welcome!

---

Note: Ensure to replace `<script_name>.py` with the actual name of your script when giving usage instructions. Also, you might want to provide a link to the GitHub repository in the "Feedback & Contributions" section.
