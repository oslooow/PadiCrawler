import os
import tkinter as tk
from tkinter import messagebox
import CompareBarangApp
import ProductSchedulerApp
from compare_scraper import init_browser as init_compare_browser, cleanup as cleanup_compare
from scraper import init_browser as init_scraper_browser, cleanup as cleanup_scraper
from PIL import Image, ImageTk

class MainMenu:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Robot Tender")
        self.root.geometry("500x600")
        self.root.configure(bg="#ffffff")
        
        # Add padding around the entire window
        self.main_frame = tk.Frame(self.root, bg="#ffffff", padx=40, pady=30)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Logo frame
        self.logo_frame = tk.Frame(self.main_frame, bg="#ffffff")
        self.logo_frame.pack(pady=(0, 30))
        
        # Load and display logo
        try:
            logo_img = Image.open("logo.png")  # Make sure to save the right logo as logo.png
            # Resize logo to desired dimensions (e.g., 150x150)
            logo_img = logo_img.resize((150, 150), Image.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(
                self.logo_frame, 
                image=self.logo_photo, 
                bg="#ffffff"
            )
            logo_label.pack()
        except Exception as e:
            print(f"Error loading logo: {e}")
        
        # Title label with custom font and styling
        title_label = tk.Label(
            self.main_frame,
            text="Robot Tender",
            font=("Segoe UI", 24, "bold"),
            bg="#ffffff",
            fg="#2c3e50"  # Dark blue-gray color
        )
        title_label.pack(pady=(0, 40))
        
        # Button style configuration
        button_style = {
            "font": ("Segoe UI", 12),
            "width": 20,
            "height": 2,
            "border": 0,
            "cursor": "hand2",  # Hand cursor on hover
            "borderwidth": 0,
        }
        
        # Compare Toko button with modern styling
        self.compare_button = tk.Button(
            self.main_frame,
            text="Compare Toko",
            command=self.launch_compare_app,
            bg="#3498db",  # Nice blue color
            fg="white",
            activebackground="#2980b9",  # Darker blue for hover
            **button_style
        )
        self.compare_button.pack(pady=10)
        
        # Price Tracker button with modern styling
        self.scheduler_button = tk.Button(
            self.main_frame,
            text="Price Tracker",
            command=self.launch_scheduler_app,
            bg="#2ecc71",  # Nice green color
            fg="white",
            activebackground="#27ae60",  # Darker green for hover
            **button_style
        )
        self.scheduler_button.pack(pady=10)
        
        # Exit button with modern styling
        self.exit_button = tk.Button(
            self.main_frame,
            text="Exit",
            command=self.on_exit,
            bg="#e74c3c",  # Nice red color
            fg="white",
            activebackground="#c0392b",  # Darker red for hover
            **button_style
        )
        self.exit_button.pack(pady=10)
        
        # Add hover effects
        for button in [self.compare_button, self.scheduler_button, self.exit_button]:
            self.add_button_hover(button)
        
        # Center the window on the screen
        self.center_window()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)

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

    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def launch_compare_app(self):
        """Launch the CompareBarangApp."""
        try:
            init_compare_browser()
            CompareBarangApp.main()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Compare Toko: {str(e)}")

    def launch_scheduler_app(self):
        """Launch the ProductSchedulerApp."""
        try:
            init_scraper_browser()
            ProductSchedulerApp.main()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Price Tracker: {str(e)}")

    def on_exit(self):
        """Handle application exit."""
        try:
            cleanup_compare()
            cleanup_scraper()
            self.root.destroy()
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")
            self.root.destroy()

    def run(self):
        """Start the main application."""
        self.root.mainloop()

def main():
    app = MainMenu()
    app.run()

if __name__ == "__main__":
    main()