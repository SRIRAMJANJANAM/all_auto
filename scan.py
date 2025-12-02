import tkinter as tk
from tkinter import ttk, messagebox
import threading
import cv2
from pyzbar.pyzbar import decode
from datetime import datetime
import json
import os

# Sample product database
products = {
    "123456789012": {"name": "Example Product", "price": 29.99},
    "987654321098": {"name": "Another Product", "price": 19.99},
    "111111111111": {"name": "Special Product", "price": 49.99},
}

DATA_FILE = "scanned_products.jsonl"
RETURN_FILE = "return.txt"

class BarcodeScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Barcode Scanner")

        self.scanned = {}  # code -> details dict (normal scanned)
        self.load_scanned()

        self.returned_items = {}  # code -> details dict (return mode scanned)

        self.return_mode = False

        self.create_widgets()

        self.scanning = False
        self.capture = None
        self.thread = None

        # Populate listbox with loaded scanned items
        for code, info in self.scanned.items():
            self.listbox.insert(tk.END, self.format_list_item(code, info))
        self.update_total_price()

    def create_widgets(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=5)

        self.scan_btn = ttk.Button(btn_frame, text="Scan", command=self.start_scanning)
        self.scan_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(btn_frame, text="Stop", command=self.stop_scanning, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.delete_btn = ttk.Button(btn_frame, text="Delete Selected", command=self.delete_selected)
        self.delete_btn.pack(side=tk.LEFT, padx=5)

        self.return_btn = ttk.Button(btn_frame, text="Return Mode", command=self.toggle_return_mode)
        self.return_btn.pack(side=tk.RIGHT, padx=5)

        self.mode_label = ttk.Label(frame, text="Mode: Scanning", font=("Arial", 10, "italic"))
        self.mode_label.pack()

        list_frame = ttk.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.listbox = tk.Listbox(list_frame, height=15)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox.config(yscrollcommand=scrollbar.set)

        self.total_label = ttk.Label(frame, text="Total Price: $0.00", font=("Arial", 12, "bold"))
        self.total_label.pack()

    def format_list_item(self, code, info):
        return f"Code: {code} | Name: {info['name']} | Price: ${info['price']:.2f}"

    def load_scanned(self):
        self.scanned.clear()
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        self.scanned[record['code']] = {
                            "name": record.get("name", "Unknown Product"),
                            "price": float(record.get("price", 0.0))
                        }
                    except Exception as e:
                        print("Error loading line:", e)

    def save_scanned(self):
        with open(DATA_FILE, "w") as f:
            for code, info in self.scanned.items():
                record = {
                    "code": code,
                    "name": info["name"],
                    "price": info["price"],
                    "timestamp": datetime.now().isoformat()
                }
                f.write(json.dumps(record) + "\n")

    def save_returned_items(self):
        with open(RETURN_FILE, "a") as f:  # append mode
            for code, info in self.returned_items.items():
                timestamp = datetime.now().isoformat()
                line = f"{timestamp} | Code: {code} | Name: {info['name']} | Price: ${info['price']:.2f}\n"
                f.write(line)

    def start_scanning(self):
        if not self.scanning:
            self.scanning = True
            self.scan_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.thread = threading.Thread(target=self.scan_loop, daemon=True)
            self.thread.start()

    def stop_scanning(self):
        if self.scanning:
            self.scanning = False
            self.scan_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)

            if self.return_mode:
                total_return_price = sum(item['price'] for item in self.returned_items.values())
                self.total_label.config(text=f"Return Total Price: ${total_return_price:.2f}")
                messagebox.showinfo("Return Scanning Stopped",
                                    f"Return scanning stopped.\nTotal return price: ${total_return_price:.2f}")
                self.save_returned_items()
                self.returned_items.clear()
                self.listbox.delete(0, tk.END)
                self.update_total_price(0)
            else:
                total_price = sum(item['price'] for item in self.scanned.values())
                self.total_label.config(text=f"Total Price: ${total_price:.2f}")
                messagebox.showinfo("Scan Stopped", f"Scanning stopped.\nTotal price: ${total_price:.2f}")
                self.save_scanned()

            if self.capture is not None:
                self.capture.release()
                self.capture = None
            cv2.destroyAllWindows()

    def delete_selected(self):
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showwarning("Delete Selected", "Please select an item to delete.")
            return

        index = selected[0]
        item_text = self.listbox.get(index)
        try:
            code = item_text.split(" |")[0].replace("Code: ", "").strip()
        except Exception:
            messagebox.showerror("Delete Selected", "Failed to parse selected item.")
            return

        if messagebox.askyesno("Delete Selected", f"Are you sure you want to delete {code}?"):
            if self.return_mode:
                if code in self.returned_items:
                    del self.returned_items[code]
            else:
                if code in self.scanned:
                    del self.scanned[code]

            self.listbox.delete(index)
            self.update_total_price()
            if self.return_mode:
                pass
            else:
                self.save_scanned()
            messagebox.showinfo("Deleted", f"Deleted barcode {code} successfully.")

    def update_total_price(self, price=None):
        if price is not None:
            total_price = price
        else:
            total_price = sum(item['price'] for item in (self.returned_items if self.return_mode else self.scanned).values())
        self.total_label.config(text=f"Total Price: ${total_price:.2f}")

    def scan_loop(self):
        self.capture = cv2.VideoCapture(0)
        last_scanned_codes = set()

        while self.scanning:
            ret, frame = self.capture.read()
            if not ret:
                break

            barcodes = decode(frame)
            for barcode in barcodes:
                code = barcode.data.decode("utf-8")

                # Avoid processing same barcode multiple times quickly
                if code in last_scanned_codes:
                    continue

                if self.return_mode:
                    if code not in self.returned_items:
                        info = products.get(code, {"name": "Unknown Product", "price": 0.0})
                        self.returned_items[code] = info
                        self.root.after(0, self.add_to_listbox, code, info)
                        self.root.after(0, lambda c=code: messagebox.showinfo("Returned", f"Barcode {c} returned successfully!"))
                        last_scanned_codes.add(code)
                else:
                    if code not in self.scanned:
                        info = products.get(code, {"name": "Unknown Product", "price": 0.0})
                        self.scanned[code] = info
                        self.root.after(0, self.add_to_listbox, code, info)
                        last_scanned_codes.add(code)

            # Clear the scanned codes cache every 3 seconds to allow rescanning if needed
            if len(last_scanned_codes) > 50:
                last_scanned_codes.clear()

            cv2.imshow("Barcode Scanner - Press 'q' to quit webcam window", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.root.after(0, self.stop_scanning)
                break

        if self.capture:
            self.capture.release()
        cv2.destroyAllWindows()

    def add_to_listbox(self, code, info):
        self.listbox.insert(tk.END, self.format_list_item(code, info))
        self.update_total_price()

    def toggle_return_mode(self):
        if self.scanning:
            messagebox.showwarning("Mode Change", "Stop scanning before toggling return mode.")
            return

        if not self.return_mode:
            answer = messagebox.askyesno("Enter Return Mode",
                                         "Do you want to enter Return Mode and start scanning returned barcodes?")
            if not answer:
                return

            self.return_mode = True
            self.mode_label.config(text="Mode: Return")
            self.return_btn.config(text="Normal Scan Mode")
            self.returned_items.clear()
            self.listbox.delete(0, tk.END)
            self.update_total_price(0)
            self.start_scanning()  # START scanning immediately in return mode!

        else:
            # Stop scanning return mode first if active
            if self.scanning:
                self.stop_scanning()

            self.return_mode = False
            self.mode_label.config(text="Mode: Scanning")
            self.return_btn.config(text="Return Mode")
            self.listbox.delete(0, tk.END)
            for code, info in self.scanned.items():
                self.listbox.insert(tk.END, self.format_list_item(code, info))
            self.update_total_price()

if __name__ == "__main__":
    root = tk.Tk()
    app = BarcodeScannerApp(root)
    root.mainloop()
