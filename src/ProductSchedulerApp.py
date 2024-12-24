import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import time
from threading import Thread, Event
from scraper import fetch_products
from excel_helper import extract_kode_barang
from datetime import datetime

class ProductSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Price Tracker")
        self.root.geometry("800x700")
        
        # Configure color scheme
        self.bg_color = "#ffffff"  # Clean white background
        self.accent_color = "#2ecc71"  # Nice green color
        self.text_color = "#2c3e50"  # Dark blue-gray color
        
        # Configure root window
        self.root.configure(bg=self.bg_color)
        
        # Main container with padding
        self.main_container = tk.Frame(root, bg=self.bg_color, padx=40, pady=30)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Title Label
        self.title_label = tk.Label(
            self.main_container, 
            text="Price Tracker", 
            font=("Segoe UI", 24, "bold"), 
            bg=self.bg_color, 
            fg=self.text_color
        )
        self.title_label.pack(pady=(0, 30))
        
        # Input styles
        entry_style = {
            "font": ("Segoe UI", 12),
            "bg": "white",
            "fg": self.text_color,
            "relief": "solid",
            "bd": 1
        }
        
        label_style = {
            "font": ("Segoe UI", 12),
            "bg": self.bg_color,
            "fg": self.text_color
        }
        
        # Vendor Frame
        self.vendor_frame = tk.Frame(self.main_container, bg=self.bg_color)
        self.vendor_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.vendor_label = tk.Label(
            self.vendor_frame,
            text="Vendor Name",
            **label_style
        )
        self.vendor_label.pack(anchor="w")
        
        self.vendor_entry = tk.Entry(
            self.vendor_frame,
            width=50,
            **entry_style
        )
        self.vendor_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Time Interval Frame
        self.interval_frame = tk.Frame(self.main_container, bg=self.bg_color)
        self.interval_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.time_interval_label = tk.Label(
            self.interval_frame,
            text="Interval (minutes)",
            **label_style
        )
        self.time_interval_label.pack(anchor="w")
        
        self.time_interval_entry = tk.Entry(
            self.interval_frame,
            width=50,
            **entry_style
        )
        self.time_interval_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Button styles
        button_style = {
            "font": ("Segoe UI", 12),
            "fg": "white",
            "width": 20,
            "height": 2,
            "cursor": "hand2",
            "bd": 0
        }
        
        # Upload Button
        self.upload_button = tk.Button(
            self.main_container,
            text="Upload Excel File",
            bg=self.accent_color,
            activebackground="#27ae60",
            command=self.upload_file,
            **button_style
        )
        self.upload_button.pack(pady=20)
        
        # Start Button
        self.start_button = tk.Button(
            self.main_container,
            text="Start Tracking",
            bg="#3498db",
            activebackground="#2980b9",
            command=self.start_process,
            **button_style
        )
        self.start_button.pack(pady=10)
        
        # Stop Button
        self.stop_button = tk.Button(
            self.main_container,
            text="Stop Tracking",
            bg="#e74c3c",
            activebackground="#c0392b",
            command=self.confirm_stop,
            **button_style
        )
        self.stop_button.pack(pady=10)
        self.stop_button.pack_forget()  # Initially hidden
        
        # Progress Bar
        self.progress_bar = ttk.Progressbar(
            self.main_container,
            orient="horizontal",
            mode="determinate",
            style="Accent.Horizontal.TProgressbar"
        )
        
        # Progress Text
        self.progress_text = tk.Label(
            self.main_container,
            text="0/0",
            font=("Segoe UI", 10),
            bg=self.bg_color,
            fg=self.text_color
        )
        
        # Terminal Output
        self.terminal_frame = tk.Frame(
            self.main_container,
            bg=self.bg_color,
            pady=20
        )
        self.terminal_frame.pack(fill=tk.BOTH, expand=True)
        
        self.terminal_output = tk.Text(
            self.terminal_frame,
            height=10,
            width=50,
            font=("Consolas", 10),
            bg="#2c3e50",
            fg="#ecf0f1",
            state='disabled',
            wrap='word'
        )
        self.terminal_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar for Terminal
        self.scrollbar = ttk.Scrollbar(
            self.terminal_frame,
            orient=tk.VERTICAL,
            command=self.terminal_output.yview
        )
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.terminal_output.config(yscrollcommand=self.scrollbar.set)
        
        # Initialize tracking variables
        self.uploaded_file_path = None
        self.stop_event = Event()
        self.processing_thread = None
        self.changed_products = []

        # Result Label
        self.result_label = tk.Label(
            self.main_container,
            text="",
            font=("Segoe UI", 10),
            bg=self.bg_color,
            fg=self.text_color
        )
        self.result_label.pack(pady=5)
        
        # Center the window
        self.center_window()
        
        # Add hover effects for buttons
        for button in [self.upload_button, self.start_button, self.stop_button]:
            self.add_button_hover(button)

    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def add_button_hover(self, button):
        """Add hover effect to buttons"""
        orig_color = button.cget("background")
        darker_color = button.cget("activebackground")

        def on_enter(e):
            button.config(background=darker_color)

        def on_leave(e):
            button.config(background=orig_color)

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    def log_message(self, message):
        """Logs a message with a timestamp to the terminal-like widget."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        self.terminal_output.config(state='normal')
        self.terminal_output.insert(tk.END, formatted_message)
        self.terminal_output.config(state='disabled')
        self.terminal_output.see(tk.END)

    def upload_file(self):
        """Prompt user to upload an Excel file and store the path."""
        try:
            # Create a new Tk window for the file dialog
            file_dialog = tk.Toplevel(self.root)
            file_dialog.withdraw()  # Hide the extra window
            
            self.uploaded_file_path = filedialog.askopenfilename(
                parent=file_dialog,  # Set parent window
                title="Select an Excel file",
                filetypes=[("Excel files", "*.xlsx *.xls")],
                initialdir="~/Documents"  # Start in Documents folder
            )
            
            if not self.uploaded_file_path:
                self.result_label.config(text="No file selected!", fg="red")
                return False
                
            self.result_label.config(text=f"Selected: {self.uploaded_file_path}", fg="green")
            return True
            
        except Exception as e:
            self.result_label.config(text=f"Error selecting file: {str(e)}", fg="red")
            return False
        finally:
            if 'file_dialog' in locals():
                file_dialog.destroy()

    def process_data(self):
        """Run the data processing function, interruptible by stop event."""
        try:
            interval_minutes = int(self.time_interval_entry.get())
            if interval_minutes <= 0:
                raise ValueError("Time interval must be greater than zero.")
        except ValueError:
            self.result_label.config(text="Please enter a valid time interval (positive number)!", fg="red")
            return

        interval_seconds = interval_minutes * 60
        first_run = True
        self.changed_products = []  # Collect results for partial display

        while not self.stop_event.is_set():
            if first_run:
                if not self.upload_file():
                    return
                first_run = False

            try:
                kode_barang_list = extract_kode_barang(self.uploaded_file_path)
                total_kode_barang = len(kode_barang_list)

                if total_kode_barang == 0:
                    self.result_label.config(text="No kode barang found in the file!", fg="red")
                    return

                nama_vendor = self.vendor_entry.get().strip()
                if not nama_vendor:
                    self.result_label.config(text="Please enter a vendor name!", fg="red")
                    return

                self.progress_bar['maximum'] = total_kode_barang

                for index, kode_barang in enumerate(kode_barang_list):
                    if self.stop_event.is_set():  # Check stop event in the inner loop
                        self.log_message("Process stopped by user.")
                        return  # Graceful exit

                    self.progress_bar['value'] = index + 1
                    self.progress_text.config(text=f"{index + 1}/{total_kode_barang}")
                    self.result_label.config(text="Processing...")  # Update status to Processing
                    self.log_message(f"Processing kode barang: {kode_barang}")

                    self.root.update()  # Force UI update

                    try:
                        products = fetch_products(kode_barang, nama_vendor)
                        if self.stop_event.is_set():
                            self.log_message("Process stopped during fetching data.")
                            return  # Graceful exit
                        
                        for product in products:
                            if self.stop_event.is_set():
                                self.log_message("Process stopped during result collection.")
                                return  # Graceful exit

                            self.changed_products.append(
                                f"{kode_barang} | {product['nama_barang']} | {product['competitor_name']} | {product['competitor_price']} | {nama_vendor} | {product['nama_toko_price']}"
                            )
                    except Exception as e:
                        self.log_message(f"Error processing kode barang {kode_barang}: {e}")

                self.progress_bar['value'] = total_kode_barang
                self.show_results_window(self.changed_products)  # Display results after each iteration

                # Pause for the interval, allowing interruption
                for i in range(interval_seconds, 0, -1):
                    if self.stop_event.is_set():
                        self.log_message("Process stopped during interval.")
                        return
                    self.result_label.config(text=f"Rerunning in {i} seconds...")
                    self.root.update()
                    time.sleep(1)

            except Exception as e:
                self.result_label.config(text=f"An error occurred: {e}", fg="red")
                self.log_message(f"Error: {e}")
                return

    def show_results_window(self, changed_products):
        """Displays a new window with the results in a copyable format."""
        if not changed_products:
            return

        results_window = tk.Toplevel(self.root)
        results_window.title("Price Change Results")
        results_window.geometry("800x600")
        results_window.configure(bg="white")

        results_text = tk.Text(
            results_window, 
            wrap='word', 
            bg='white', 
            fg='black', 
            font=("Courier New", 10)
        )
        results_text.pack(fill='both', expand=True, padx=10, pady=10)

        for product in changed_products:
            kode_barang, nama_barang, competitor, competitor_price, vendor, vendor_price = product.split(" | ")
            results_text.insert(tk.END, f"{kode_barang} | {nama_barang} | {competitor} : {competitor_price} | {vendor}: {vendor_price}\n")

        scrollbar = ttk.Scrollbar(
            results_window, 
            orient="vertical", 
            command=results_text.yview
        )
        results_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        ok_button = tk.Button(
            results_window, 
            text="OK", 
            command=results_window.destroy, 
            bg="#4CAF50", 
            fg="white"
        )
        ok_button.pack(pady=10)

        results_window.transient(self.root)
        results_window.grab_set()

    def start_process(self):
        """Start the product processing in a separate thread."""
        if self.stop_event.is_set():
            self.log_message("Process already stopped. Resetting stop event.")
            return

        self.stop_event.clear()  # Reset stop event before starting the process
        self.start_button.pack_forget()  # Hide the Start button
        self.stop_button.pack(pady=10)  # Show the Stop button
        self.vendor_entry.config(state='disabled')  # Disable vendor input
        self.time_interval_entry.config(state='disabled')  # Disable time interval input
        self.result_label.config(text="")  # Clear any previous results

        # Ensure progress bar and text are visible
        self.progress_bar.pack(pady=5)  
        self.progress_text.pack(pady=5)
        
        self.log_message("Starting process...")
        self.processing_thread = Thread(target=self.process_data)
        self.processing_thread.start()

    def confirm_stop(self):
        """Prompt for confirmation to stop."""
        response = messagebox.askyesno("Confirmation", "Do you really want to stop?")
        if response:
            self.stop_event.set()  # Signal thread to stop
            self.log_message("Stopping process...")
            self.root.after(100, self.check_thread_status)  # Periodically check the thread status

    def check_thread_status(self):
        """Check the thread status and update UI when the thread stops."""
        if self.processing_thread.is_alive():
            self.root.after(100, self.check_thread_status)  # Check again after 100ms
        else:
            self.log_message("Thread stopped.")
            if self.changed_products:
                self.show_results_window(self.changed_products)
            self.reset_ui()

    def reset_ui(self):
        """Reset the UI to the initial landing page."""
        self.start_button.grid()  # Show the Start button
        self.stop_button.grid_remove()  # Hide the Stop button
        self.time_interval_entry.delete(0, tk.END)
        self.vendor_entry.delete(0, tk.END)
        self.vendor_entry.config(state='normal')  # Re-enable vendor input
        self.time_interval_entry.config(state='normal')  # Re-enable time interval input
        self.result_label.config(text="", fg=self.text_color)
        self.progress_bar.grid_remove()
        self.progress_text.grid_remove()
        self.progress_bar['value'] = 0
        self.uploaded_file_path = None
        self.stop_event.clear()
        self.changed_products = []


def main():
    root = tk.Tk()
    app = ProductSchedulerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
