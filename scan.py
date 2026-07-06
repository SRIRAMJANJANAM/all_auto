import tkinter as tk
from tkinter import ttk, messagebox
import threading
import cv2
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
        self.root.title("QR / Barcode Scanner")

        self.scanned = {}
        self.load_scanned()

        self.returned_items = {}
        self.return_mode = False

        self.create_widgets()

        self.scanning = False
        self.capture = None
        self.thread = None

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
                    except:
                        pass

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
        with open(RETURN_FILE, "a") as f:
            for code, info in self.returned_items.items():
                timestamp = datetime.now().isoformat()
                f.write(f"{timestamp} | Code: {code} | Name: {info['name']} | Price: ${info['price']:.2f}\n")

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
                total = sum(item['price'] for item in self.returned_items.values())
                messagebox.showinfo("Return Done", f"Total Return Price: ${total:.2f}")
                self.save_returned_items()
                self.returned_items.clear()
                self.listbox.delete(0, tk.END)
            else:
                total = sum(item['price'] for item in self.scanned.values())
                messagebox.showinfo("Scan Done", f"Total Price: ${total:.2f}")
                self.save_scanned()

            if self.capture:
                self.capture.release()
            cv2.destroyAllWindows()

    def delete_selected(self):
        selected = self.listbox.curselection()
        if not selected:
            return

        index = selected[0]
        item_text = self.listbox.get(index)
        code = item_text.split(" |")[0].replace("Code: ", "")

        if self.return_mode:
            self.returned_items.pop(code, None)
        else:
            self.scanned.pop(code, None)

        self.listbox.delete(index)
        self.update_total_price()

    def update_total_price(self):
        data = self.returned_items if self.return_mode else self.scanned
        total = sum(item['price'] for item in data.values())
        self.total_label.config(text=f"Total Price: ${total:.2f}")

    def scan_loop(self):
        self.capture = cv2.VideoCapture(0)
        detector = cv2.QRCodeDetector()
        last_scanned = set()

        while self.scanning:
            ret, frame = self.capture.read()
            if not ret:
                break

            data, bbox, _ = detector.detectAndDecode(frame)

            if data:
                code = data.strip()

                if code not in last_scanned:
                    info = products.get(code, {"name": "Unknown Product", "price": 0.0})

                    if self.return_mode:
                        self.returned_items[code] = info
                        self.root.after(0, self.add_to_listbox, code, info)
                    else:
                        self.scanned[code] = info
                        self.root.after(0, self.add_to_listbox, code, info)

                    last_scanned.add(code)

            if len(last_scanned) > 50:
                last_scanned.clear()

            cv2.imshow("Scanner (Press Q to quit)", frame)

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
            messagebox.showwarning("Stop First", "Stop scanning first!")
            return

        self.return_mode = not self.return_mode

        if self.return_mode:
            self.mode_label.config(text="Mode: Return")
            self.return_btn.config(text="Normal Mode")
            self.listbox.delete(0, tk.END)
        else:
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