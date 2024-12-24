import pandas as pd
import tkinter as tk
from tkinter import filedialog

# Function to select file using file dialog
def select_file():
    root = tk.Tk()
    root.withdraw()  # Hide the main Tkinter window
    file_path = filedialog.askopenfilename(
        title="Select Excel File",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )
    return file_path

# Function to extract "kode barang" from the selected Excel file
def extract_kode_barang(file_path):
    if file_path:
        # Read the Excel file
        excel_data = pd.read_excel(file_path)

        # Extract relevant rows from column B (Unnamed: 1 in your case)
        product_data = excel_data.iloc[2:, 1]  # Skip first two rows, and select column B

        # Convert entries to strings and extract numeric part at the start of each entry
        kode_barang = product_data.astype(str).str.extract(r'^(\d+)')[0]  # Convert to string, extract numeric sequence

        # Remove any null values and return as a list
        kode_barang = kode_barang.dropna().tolist()

        return kode_barang
    return []
