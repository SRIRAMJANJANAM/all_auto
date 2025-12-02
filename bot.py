import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import time

class ProfessionalAgenticChatbot:
    def __init__(self, root):
        self.root = root
        self.root.title("Agentic Task Manager")
        self.root.geometry("900x700")
        self.root.configure(bg="#f8f9fa")
        self.root.minsize(800, 600)
        
        # Initialize variables
        self.goal = None
        self.tasks = []  # Each task is a dict: {'text': '', 'status': 'not_started'/'in_progress'/'completed'}
        
        # Configure styles
        self.setup_styles()
        
        # Create main layout
        self.create_main_layout()
        
        # Initial message
        self.update_chat("🤖 Welcome to your Agentic Task Manager!\nClick 'Set Goal' to begin a new project.", "bot")
        
    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Colors
        self.primary_color = "#4f46e5"
        self.secondary_color = "#10b981"
        self.accent_color = "#f59e0b"
        self.danger_color = "#ef4444"
        self.light_bg = "#f8fafc"
        self.dark_bg = "#1e293b"
        self.text_color = "#334155"
        self.light_text = "#64748b"
        
        # Status colors
        self.status_colors = {
            'not_started': '#ef4444',    # Red
            'in_progress': '#f59e0b',    # Yellow/Orange
            'completed': '#10b981'       # Green
        }
        
        # Configure styles
        self.style.configure("Primary.TButton", background=self.primary_color, foreground="white", 
                           font=("Segoe UI", 10, "bold"), borderwidth=0)
        self.style.map("Primary.TButton", 
                      background=[('active', '#4338ca'), ('pressed', '#3730a3')])
        
        self.style.configure("Secondary.TButton", background=self.secondary_color, foreground="white", 
                           font=("Segoe UI", 10, "bold"), borderwidth=0)
        self.style.map("Secondary.TButton", 
                      background=[('active', '#0da271'), ('pressed', '#047857')])
        
        self.style.configure("Accent.TButton", background=self.accent_color, foreground="white", 
                           font=("Segoe UI", 10, "bold"), borderwidth=0)
        self.style.map("Accent.TButton", 
                      background=[('active', '#e99a0c'), ('pressed', '#d97706')])
        
        self.style.configure("Danger.TButton", background=self.danger_color, foreground="white", 
                           font=("Segoe UI", 10, "bold"), borderwidth=0)
        self.style.map("Danger.TButton", 
                      background=[('active', '#dc2626'), ('pressed', '#b91c1c')])
        
    def create_main_layout(self):
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title = tk.Label(header_frame, text="Agentic Task Manager", 
                         font=("Segoe UI", 20, "bold"), foreground=self.primary_color, bg="#f8f9fa")
        title.pack(side=tk.LEFT)
        
        # Status indicator
        status_frame = ttk.Frame(header_frame)
        status_frame.pack(side=tk.RIGHT)
        
        status_dot = tk.Label(status_frame, text="●", foreground=self.secondary_color, 
                              font=("Arial", 14), bg="#f8f9fa")
        status_dot.pack(side=tk.LEFT, padx=(0, 5))
        
        status_text = tk.Label(status_frame, text="Ready", foreground=self.light_text, bg="#f8f9fa")
        status_text.pack(side=tk.LEFT)
        
        # Content area (split into two columns)
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left column - Chat area
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        chat_label = tk.Label(left_frame, text="Conversation", font=("Segoe UI", 12, "bold"),
                              foreground=self.text_color, bg="#f8f9fa")
        chat_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Chat container with border
        chat_container = tk.Frame(left_frame, bg="white", relief="raised", bd=1)
        chat_container.pack(fill=tk.BOTH, expand=True)
        
        # Chat area
        self.chat_frame = tk.Canvas(chat_container, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(chat_container, orient="vertical", command=self.chat_frame.yview)
        self.scrollable_chat = tk.Frame(self.chat_frame, bg="white")
        
        self.scrollable_chat.bind(
            "<Configure>",
            lambda e: self.chat_frame.configure(scrollregion=self.chat_frame.bbox("all"))
        )
        
        self.chat_frame.create_window((0, 0), window=self.scrollable_chat, anchor="nw")
        self.chat_frame.configure(yscrollcommand=scrollbar.set)
        
        self.chat_frame.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Right column - Progress panel
        right_frame = ttk.Frame(content_frame, width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(15, 0))
        right_frame.pack_propagate(False)
        
        progress_label = tk.Label(right_frame, text="Progress", font=("Segoe UI", 12, "bold"),
                                  foreground=self.text_color, bg="#f8f9fa")
        progress_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Progress container with border
        progress_container = tk.Frame(right_frame, bg="white", relief="raised", bd=1)
        progress_container.pack(fill=tk.BOTH, expand=True)
        
        # Goal section
        goal_header = tk.Label(progress_container, text="CURRENT GOAL", 
                               font=("Segoe UI", 10, "bold"), foreground=self.primary_color, bg="white")
        goal_header.pack(anchor=tk.W, padx=15, pady=(15, 5))
        
        self.goal_text = tk.StringVar(value="No goal set")
        goal_value = tk.Label(progress_container, textvariable=self.goal_text, 
                              font=("Segoe UI", 11), wraplength=250, 
                              foreground=self.text_color, bg="white", justify=tk.LEFT)
        goal_value.pack(anchor=tk.W, padx=15, pady=(0, 15))
        
        # Separator
        separator = ttk.Separator(progress_container, orient="horizontal")
        separator.pack(fill=tk.X, padx=10, pady=5)
        
        # Tasks section
        tasks_header = tk.Label(progress_container, text="TASKS", 
                                font=("Segoe UI", 10, "bold"), foreground=self.primary_color, bg="white")
        tasks_header.pack(anchor=tk.W, padx=15, pady=(5, 10))
        
        # Tasks list container
        tasks_container = tk.Frame(progress_container, bg="white")
        tasks_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.tasks_canvas = tk.Canvas(tasks_container, bg="white", highlightthickness=0, height=200)
        tasks_scrollbar = ttk.Scrollbar(tasks_container, orient="vertical", command=self.tasks_canvas.yview)
        self.tasks_frame = tk.Frame(self.tasks_canvas, bg="white")
        
        self.tasks_frame.bind(
            "<Configure>",
            lambda e: self.tasks_canvas.configure(scrollregion=self.tasks_canvas.bbox("all"))
        )
        
        self.tasks_canvas.create_window((0, 0), window=self.tasks_frame, anchor="nw")
        self.tasks_canvas.configure(yscrollcommand=tasks_scrollbar.set)
        
        self.tasks_canvas.pack(side="left", fill="both", expand=True)
        tasks_scrollbar.pack(side="right", fill="y")
        
        # Progress bar
        separator = ttk.Separator(progress_container, orient="horizontal")
        separator.pack(fill=tk.X, padx=10, pady=10)
        
        progress_text = tk.Label(progress_container, text="OVERALL PROGRESS", 
                                 font=("Segoe UI", 10, "bold"), foreground=self.primary_color, bg="white")
        progress_text.pack(anchor=tk.W, padx=15, pady=(5, 5))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_container, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Status indicator
        status_indicator_frame = tk.Frame(progress_container, bg="white")
        status_indicator_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        tk.Label(status_indicator_frame, text="Status: ", font=("Segoe UI", 9), 
                bg="white", fg=self.text_color).pack(side=tk.LEFT)
        
        self.status_text = tk.StringVar(value="No tasks")
        status_label = tk.Label(status_indicator_frame, textvariable=self.status_text, 
                               font=("Segoe UI", 9, "bold"), bg="white")
        status_label.pack(side=tk.LEFT)
        
        # Button panel
        button_frame = ttk.Frame(main_container)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Button grid
        self.btn_set_goal = ttk.Button(button_frame, text="Set Goal", 
                                      style="Primary.TButton", command=self.set_goal)
        self.btn_set_goal.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        self.btn_add_task = ttk.Button(button_frame, text="Add Task", 
                                      style="Secondary.TButton", command=self.add_task)
        self.btn_add_task.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        self.btn_view_progress = ttk.Button(button_frame, text="View Progress", 
                                           style="Secondary.TButton", command=self.view_progress)
        self.btn_view_progress.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        
        self.btn_restart = ttk.Button(button_frame, text="Restart", 
                                     style="Danger.TButton", command=self.restart)
        self.btn_restart.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        
        # Configure grid weights
        for i in range(3):
            button_frame.columnconfigure(i, weight=1)
        
    def update_chat(self, message, sender="bot"):
        # Create message frame
        msg_frame = tk.Frame(self.scrollable_chat, bg="white")
        msg_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Avatar
        avatar_text = "👤" if sender == "user" else "🤖"
        avatar = tk.Label(msg_frame, text=avatar_text, font=("Arial", 14), bg="white")
        avatar.pack(side=tk.LEFT, padx=(0, 10))
        
        # Message bubble with appropriate background
        bubble_bg = "#eef2ff" if sender == "bot" else "#dbeafe"
        bubble_frame = tk.Frame(msg_frame, bg=bubble_bg, relief="raised", bd=1)
        bubble_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Message text
        msg_label = tk.Label(bubble_frame, text=message, wraplength=400, 
                             font=("Segoe UI", 10), bg=bubble_bg, justify=tk.LEFT)
        msg_label.pack(anchor=tk.W, padx=10, pady=8)
        
        # Timestamp
        timestamp = tk.Label(msg_frame, text=time.strftime("%H:%M"), 
                             font=("Segoe UI", 8), foreground=self.light_text, bg="white")
        timestamp.pack(side=tk.RIGHT)
        
        # Scroll to bottom
        self.chat_frame.update_idletasks()
        self.chat_frame.yview_moveto(1.0)
        
    def update_progress_panel(self):
        # Update goal text
        if self.goal:
            self.goal_text.set(self.goal)
        else:
            self.goal_text.set("No goal set")
            
        # Clear tasks frame
        for widget in self.tasks_frame.winfo_children():
            widget.destroy()
            
        # Add tasks to list
        if not self.tasks:
            empty_label = tk.Label(self.tasks_frame, text="No tasks yet", 
                                   foreground=self.light_text, font=("Segoe UI", 10), bg="white")
            empty_label.pack(pady=10)
            self.status_text.set("No tasks")
        else:
            for i, task in enumerate(self.tasks, 1):
                task_frame = tk.Frame(self.tasks_frame, bg="white")
                task_frame.pack(fill=tk.X, pady=2)
                
                # Task number
                num_label = tk.Label(task_frame, text=f"{i}.", 
                                     font=("Segoe UI", 10, "bold"), 
                                     foreground=self.primary_color, width=3, bg="white")
                num_label.pack(side=tk.LEFT)
                
                # Task text with status color
                status_color = self.status_colors[task['status']]
                task_text = f"{task['text']} [{task['status'].replace('_', ' ').title()}]"
                task_label = tk.Label(task_frame, text=task_text, 
                                      font=("Segoe UI", 10), fg=status_color,
                                      wraplength=220, bg="white", justify=tk.LEFT,
                                      cursor="hand2")
                task_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                # Bind click event to change status
                task_label.bind("<Button-1>", lambda e, idx=i-1: self.change_task_status(idx))
                
        # Update progress bar and status
        self.update_progress_bar()
            
    def update_progress_bar(self):
        if not self.tasks:
            self.progress_var.set(0)
            self.progress_bar.configure(style="TProgressbar")
            self.status_text.set("No tasks")
            return
            
        # Calculate progress
        completed_count = sum(1 for task in self.tasks if task['status'] == 'completed')
        progress = (completed_count / len(self.tasks)) * 100
        self.progress_var.set(progress)
        
        # Determine overall status and color
        if all(task['status'] == 'completed' for task in self.tasks):
            status = "All tasks completed"
            color = self.status_colors['completed']
        elif any(task['status'] == 'in_progress' for task in self.tasks):
            status = "In progress"
            color = self.status_colors['in_progress']
        else:
            status = "Not started"
            color = self.status_colors['not_started']
            
        # Update progress bar color and status text
        self.progress_bar.configure(style=f"{color}.Horizontal.TProgressbar")
        self.status_text.set(status)
        
        # Create custom style for progress bar if it doesn't exist
        for status_name, color in self.status_colors.items():
            self.style.configure(f"{color}.Horizontal.TProgressbar", 
                                background=color, troughcolor="#e5e7eb")
        
    def change_task_status(self, task_index):
        if not (0 <= task_index < len(self.tasks)):
            return
            
        task = self.tasks[task_index]
        current_status = task['status']
        
        # Create a menu for status selection
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Not Started", 
                         command=lambda: self.set_task_status(task_index, 'not_started'),
                         foreground=self.status_colors['not_started'])
        menu.add_command(label="In Progress", 
                         command=lambda: self.set_task_status(task_index, 'in_progress'),
                         foreground=self.status_colors['in_progress'])
        menu.add_command(label="Completed", 
                         command=lambda: self.set_task_status(task_index, 'completed'),
                         foreground=self.status_colors['completed'])
        
        # Show the menu at cursor position
        try:
            menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())
        finally:
            menu.grab_release()
            
    def set_task_status(self, task_index, status):
        if 0 <= task_index < len(self.tasks):
            self.tasks[task_index]['status'] = status
            self.update_progress_panel()
            
            status_text = status.replace('_', ' ').title()
            self.update_chat(f"Task status updated: '{self.tasks[task_index]['text']}' is now {status_text}", "user")
            
    def set_goal(self):
        goal = simpledialog.askstring("Set Goal", "🎯 What goal do you want to achieve?")
        if goal:
            self.goal = goal
            self.tasks = []
            self.update_chat(f"New goal set: '{goal}'", "bot")
            self.update_progress_panel()
            messagebox.showinfo("Goal Set", "Now start adding tasks using the 'Add Task' button.")
            
    def add_task(self):
        if self.goal is None:
            messagebox.showwarning("No Goal", "Please set a goal first.")
            return
        if len(self.tasks) >= 5:
            messagebox.showinfo("Task Limit", "You can only add up to 5 tasks.")
            return
            
        task_text = simpledialog.askstring("Add Task", "📝 Enter a task to achieve your goal:")
        if task_text:
            self.tasks.append({
                'text': task_text,
                'status': 'not_started'  # Default status
            })
            self.update_chat(f"Task added: {task_text}", "user")
            self.update_progress_panel()
            
    def view_progress(self):
        if self.goal is None:
            messagebox.showwarning("No Goal", "Please set a goal first.")
            return
            
        if not self.tasks:
            self.update_chat("You have no tasks right now.", "bot")
        else:
            self.update_chat("Your current tasks:", "bot")
            for i, task in enumerate(self.tasks, 1):
                status_text = task['status'].replace('_', ' ').title()
                self.update_chat(f"{i}. {task['text']} [{status_text}]", "bot")
                
    def restart(self):
        self.goal = None
        self.tasks = []
        
        # Clear chat area
        for widget in self.scrollable_chat.winfo_children():
            widget.destroy()
            
        self.update_progress_panel()
        self.update_chat("Session restarted. Click 'Set Goal' to begin a new session.", "bot")

# Create and run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = ProfessionalAgenticChatbot(root)
    root.mainloop()