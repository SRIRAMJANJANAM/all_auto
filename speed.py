import tkinter as tk
from tkinter import ttk, messagebox
import threading
import speedtest
import math
import time
import random

class SpeedTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Internet Speed Test")
        self.root.geometry("650x700")
        self.root.resizable(False, False)
        self.root.configure(bg="#f5f7fa")
        
        # Apply a modern theme
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Customize styles
        self.style.configure('TButton', font=('Arial', 10), padding=6)
        self.style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background="#f5f7fa")
        self.style.configure('Result.TLabel', font=('Arial', 12), background="#f5f7fa")
        self.style.configure('Status.TLabel', font=('Arial', 11), background="#f5f7fa")
        
        self.running = False
        self.current_speed = 0
        self.max_speed = 100  # Default max speed for speedometer
        self.test_results = {"download": 0, "upload": 0, "ping": 0}

        # Header
        header_frame = tk.Frame(root, bg="#3498db", height=70)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="INTERNET SPEED TEST", 
                              font=("Arial", 20, "bold"), fg="white", bg="#3498db")
        title_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Status label
        self.status_label = ttk.Label(root, text="Ready to test your internet speed", 
                                     style='Status.TLabel')
        self.status_label.pack(pady=15)

        # Speedometer Canvas
        canvas_frame = tk.Frame(root, bg="#f5f7fa")
        canvas_frame.pack(pady=10)
        
        self.canvas = tk.Canvas(canvas_frame, width=400, height=250, bg="#f5f7fa", 
                               highlightthickness=0)
        self.canvas.pack()
        self.draw_speedometer()

        # Results frame
        results_frame = tk.Frame(root, bg="#f5f7fa", relief=tk.GROOVE, bd=1)
        results_frame.pack(pady=20, fill=tk.X, padx=40)
        
        # Results title
        results_title = tk.Label(results_frame, text="Test Results", 
                                font=("Arial", 14, "bold"), bg="#f5f7fa", fg="#101ee6")
        results_title.pack(pady=10)
        
        # Download speed
        download_frame = tk.Frame(results_frame, bg="#f5f7fa")
        download_frame.pack(fill=tk.X, pady=8, padx=20)
        tk.Label(download_frame, text="Download:", font=("Arial", 12, "bold"), 
                bg="#f5f7fa", fg="#101ee6", width=12, anchor=tk.W).pack(side=tk.LEFT)
        self.download_label = tk.Label(download_frame, text="-- Mbps", 
                                      font=("Arial", 12), bg="#f5f7fa", fg="#2980b9")
        self.download_label.pack(side=tk.LEFT)
        
        # Upload speed
        upload_frame = tk.Frame(results_frame, bg="#f5f7fa")
        upload_frame.pack(fill=tk.X, pady=8, padx=20)
        tk.Label(upload_frame, text="Upload:", font=("Arial", 12, "bold"), 
                bg="#f5f7fa", fg="#101ee6", width=12, anchor=tk.W).pack(side=tk.LEFT)
        self.upload_label = tk.Label(upload_frame, text="-- Mbps", 
                                    font=("Arial", 12), bg="#f5f7fa", fg="#2980b9")
        self.upload_label.pack(side=tk.LEFT)
        
        # Ping
        ping_frame = tk.Frame(results_frame, bg="#f5f7fa")
        ping_frame.pack(fill=tk.X, pady=8, padx=20)
        tk.Label(ping_frame, text="Ping:", font=("Arial", 12, "bold"), 
                bg="#f5f7fa", fg="#101ee6", width=12, anchor=tk.W).pack(side=tk.LEFT)
        self.ping_label = tk.Label(ping_frame, text="-- ms", 
                                  font=("Arial", 12), bg="#f5f7fa", fg="#2980b9")
        self.ping_label.pack(side=tk.LEFT)

        # Buttons
        button_frame = tk.Frame(root, bg="#f5f7fa")
        button_frame.pack(pady=20)
        
        self.start_button = ttk.Button(button_frame, text="Start Test", 
                                      command=self.start_test, width=15)
        self.start_button.grid(row=0, column=0, padx=10)

        self.retry_button = ttk.Button(button_frame, text="Retry", 
                                      command=self.retry_test, width=15, state=tk.DISABLED)
        self.retry_button.grid(row=0, column=1, padx=10)

        self.stop_button = ttk.Button(button_frame, text="Stop", 
                                     command=self.stop_test, width=15, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=2, padx=10)

        # Progress bar
        self.progress = ttk.Progressbar(root, mode='indeterminate', length=500)
        self.progress.pack(pady=10)
        
        # Footer
        footer_frame = tk.Frame(root, bg="#ecf0f1", height=40)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        footer_frame.pack_propagate(False)
        
        footer_label = tk.Label(footer_frame, text="© 2023 Internet Speed Test", 
                               font=("Arial", 9), fg="#7f8c8d", bg="#ecf0f1")
        footer_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def draw_speedometer(self):
        # Draw semicircle
        self.canvas.create_arc(30, 30, 370, 370, start=0, extent=180, 
                              style=tk.ARC, width=4, outline="#34495e")
        
        # Draw colored zones
        self.canvas.create_arc(30, 30, 370, 370, start=0, extent=60, 
                              style=tk.ARC, width=20, outline="#e61057")
        self.canvas.create_arc(30, 30, 370, 370, start=60, extent=60, 
                              style=tk.ARC, width=20, outline="#e61057")
        self.canvas.create_arc(30, 30, 370, 370, start=120, extent=60, 
                              style=tk.ARC, width=20, outline="#e61057")
        
        # Draw tick marks and labels
        for i in range(0, 181, 30):
            angle = math.radians(180 - i)
            x1 = 200 + 110 * math.cos(angle)
            y1 = 200 - 110 * math.sin(angle)
            x2 = 200 + 120 * math.cos(angle)
            y2 = 200 - 120 * math.sin(angle)
            self.canvas.create_line(x1, y1, x2, y2, width=3, fill="#101ee6")
            
            # Add labels
            label_value = int(i / 180 * self.max_speed)
            label_x = 200 + 130 * math.cos(angle)
            label_y = 200 - 130 * math.sin(angle)
            self.canvas.create_text(label_x, label_y, text=f"{label_value}", 
                                   font=("Arial", 10, "bold"), fill="#101ee6")

        # Center circle
        self.canvas.create_oval(195, 195, 205, 205, fill="#e74c3c", outline="")
        
        # Create needle
        self.needle = self.canvas.create_line(200, 200, 200, 50, width=4, fill='#e74c3c', arrow=tk.LAST)
        
        # Add speed label
        self.speed_text = self.canvas.create_text(200, 230, text="0 Mbps", 
                                                font=("Arial", 12, "bold"), fill="#101ee6")

    def update_needle(self, speed):
        # Calculate angle based on current speed and max speed
        angle = 180 - (speed / self.max_speed * 180)
        angle = max(0, min(180, angle))  # clamp between 0 and 180

        x = 200 + 150 * math.cos(math.radians(angle))
        y = 200 - 150 * math.sin(math.radians(angle))

        self.canvas.coords(self.needle, 200, 200, x, y)
        self.canvas.itemconfig(self.speed_text, text=f"{speed:.1f} Mbps")

    def simulate_speed_animation(self, target_speed, test_type):
        """Simulate realistic speedometer movement"""
        current = 0
        increment = target_speed / 20  # Divide into 20 steps
        
        while current < target_speed and self.running:
            current += increment
            if current > target_speed:
                current = target_speed
                
            self.root.after(0, lambda s=current: self.update_needle(s))
            time.sleep(0.05)
        
        # Update the final result
        if test_type == "download":
            self.test_results["download"] = target_speed
            self.root.after(0, lambda: self.download_label.config(text=f"{target_speed:.2f} Mbps"))
        elif test_type == "upload":
            self.test_results["upload"] = target_speed
            self.root.after(0, lambda: self.upload_label.config(text=f"{target_speed:.2f} Mbps"))

    def reset_needle(self):
        self.update_needle(0)

    def start_test(self):
        if not self.running:
            self.running = True
            self.status_label.config(text="Testing your internet speed...")
            self.start_button.config(state=tk.DISABLED)
            self.retry_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.reset_needle()
            self.progress.start()

            # Reset results
            self.download_label.config(text="-- Mbps")
            self.upload_label.config(text="-- Mbps")
            self.ping_label.config(text="-- ms")
            self.test_results = {"download": 0, "upload": 0, "ping": 0}

            # Start the speed test in a separate thread
            self.test_thread = threading.Thread(target=self.run_speed_test)
            self.test_thread.daemon = True
            self.test_thread.start()

    def stop_test(self):
        self.running = False
        self.status_label.config(text="Test stopped.")
        self.start_button.config(state=tk.NORMAL)
        self.retry_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress.stop()

    def retry_test(self):
        self.start_test()

    def run_speed_test(self):
        try:
            st = speedtest.Speedtest()
            
            # Get best server with progress updates
            self.root.after(0, lambda: self.status_label.config(text="Finding best server..."))
            st.get_best_server()
            
            if not self.running: 
                return
                
            # Test ping
            ping = st.results.ping
            self.test_results["ping"] = ping
            self.root.after(0, lambda: self.ping_label.config(text=f"{ping:.2f} ms"))
                
            # Test download speed with progress updates
            self.root.after(0, lambda: self.status_label.config(text="Testing download speed..."))
            
            # Simulate download test with realistic animation
            download_thread = threading.Thread(target=self.simulate_download_test, args=(st,))
            download_thread.start()
            download_thread.join()
            
            if not self.running: 
                return
                
            # Test upload speed with progress updates
            self.root.after(0, lambda: self.status_label.config(text="Testing upload speed..."))
            
            # Simulate upload test with realistic animation
            upload_thread = threading.Thread(target=self.simulate_upload_test, args=(st,))
            upload_thread.start()
            upload_thread.join()
            
            if not self.running: 
                return

            # Update UI with final results
            self.root.after(0, lambda: self.status_label.config(text="Test completed!"))
            
            # Adjust max speed if needed for better visualization
            if self.test_results["download"] > self.max_speed * 0.8:
                self.max_speed = math.ceil(self.test_results["download"] / 50) * 50  # Round up to nearest 50
                self.root.after(0, self.redraw_speedometer)
                self.root.after(0, lambda: self.update_needle(self.test_results["download"]))

        except Exception as e:
            self.root.after(0, lambda: self.status_label.config(text="Error during test."))
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.running = False
            self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.retry_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))
            self.root.after(0, self.progress.stop)
    
    def simulate_download_test(self, st):
        """Simulate download test with realistic speed fluctuations"""
        # Get actual download speed
        download = st.download()
        download_mbps = download / 1_000_000
        
        # Simulate the test with realistic fluctuations
        current_speed = 0
        target_speed = download_mbps
        
        # Start with a rapid increase
        while current_speed < target_speed * 0.7 and self.running:
            current_speed += random.uniform(2, 5)
            if current_speed > target_speed * 0.7:
                current_speed = target_speed * 0.7
            self.root.after(0, lambda s=current_speed: self.update_needle(s))
            time.sleep(0.05)
        
        # Simulate some fluctuations around the actual speed
        for _ in range(10):
            if not self.running:
                break
            fluctuation = random.uniform(-3, 3)
            current_speed = max(0, min(target_speed, current_speed + fluctuation))
            self.root.after(0, lambda s=current_speed: self.update_needle(s))
            time.sleep(0.1)
        
        # Gradually reach the actual speed
        while current_speed < target_speed and self.running:
            current_speed += random.uniform(0.5, 1.5)
            if current_speed > target_speed:
                current_speed = target_speed
            self.root.after(0, lambda s=current_speed: self.update_needle(s))
            time.sleep(0.05)
        
        # Update the final result
        self.test_results["download"] = target_speed
        self.root.after(0, lambda: self.download_label.config(text=f"{target_speed:.2f} Mbps"))
    
    def simulate_upload_test(self, st):
        """Simulate upload test with realistic speed fluctuations"""
        # Get actual upload speed
        upload = st.upload()
        upload_mbps = upload / 1_000_000
        
        # Simulate the test with realistic fluctuations
        current_speed = 0
        target_speed = upload_mbps
        
        # Start with a rapid increase
        while current_speed < target_speed * 0.7 and self.running:
            current_speed += random.uniform(1, 3)
            if current_speed > target_speed * 0.7:
                current_speed = target_speed * 0.7
            self.root.after(0, lambda s=current_speed: self.update_needle(s))
            time.sleep(0.05)
        
        # Simulate some fluctuations around the actual speed
        for _ in range(8):
            if not self.running:
                break
            fluctuation = random.uniform(-2, 2)
            current_speed = max(0, min(target_speed, current_speed + fluctuation))
            self.root.after(0, lambda s=current_speed: self.update_needle(s))
            time.sleep(0.1)
        
        # Gradually reach the actual speed
        while current_speed < target_speed and self.running:
            current_speed += random.uniform(0.3, 1.0)
            if current_speed > target_speed:
                current_speed = target_speed
            self.root.after(0, lambda s=current_speed: self.update_needle(s))
            time.sleep(0.05)
        
        # Update the final result
        self.test_results["upload"] = target_speed
        self.root.after(0, lambda: self.upload_label.config(text=f"{target_speed:.2f} Mbps"))
    
    def redraw_speedometer(self):
        self.canvas.delete("all")
        self.draw_speedometer()

if __name__ == "__main__":
    root = tk.Tk()
    app = SpeedTestApp(root)
    root.mainloop()