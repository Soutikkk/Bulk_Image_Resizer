import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import queue
from PIL import Image

# ==========================================
# Theme and Colors (Modern Slate Palette)
# ==========================================
BG_DARK = "#0f172a"          # Dark slate background
CARD_BG = "#1e293b"          # Card background
ACCENT_BLUE = "#3b82f6"      # Primary button (blue)
ACCENT_BLUE_HOVER = "#2563eb"
ACCENT_GREEN = "#10b981"     # Success/Process button (green)
ACCENT_GREEN_HOVER = "#059669"
ACCENT_RED = "#ef4444"       # Danger/Cancel/Error color
TEXT_WHITE = "#f8fafc"       # White text
TEXT_MUTED = "#94a3b8"       # Secondary/Muted text
TEXT_DARK = "#0f172a"        # Text color for entry widgets
BORDER_COLOR = "#334155"     # Border for custom inputs

class BulkImageResizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bulk Image Resizer")
        self.root.geometry("680x620")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_DARK)

        # App state
        self.selected_files = []
        self.ui_queue = queue.Queue()
        self.is_processing = False

        # Set up styles for ttk widgets
        self.setup_styles()
        
        # Build UI layout
        self.create_widgets()

        # Start background check queue
        self.root.after(100, self.check_queue)

    def setup_styles(self):
        """Configure styles for standard ttk widgets to match our custom dark theme."""
        style = ttk.Style()
        style.theme_use("clam")
        
        # Style the Progressbar
        style.configure(
            "TProgressbar",
            thickness=12,
            troughcolor=BORDER_COLOR,
            background=ACCENT_BLUE,
            borderwidth=0
        )

    def create_widgets(self):
        """Create and arrange UI widgets."""
        # Main Outer Container (with margin padding)
        main_container = tk.Frame(self.root, bg=BG_DARK, padx=20, pady=20)
        main_container.pack(fill="both", expand=True)

        # -------------------------------------------------------------
        # 1. HEADER SECTION
        # -------------------------------------------------------------
        header_frame = tk.Frame(main_container, bg=BG_DARK)
        header_frame.pack(fill="x", pady=(0, 15))

        title_label = tk.Label(
            header_frame,
            text="Bulk Image Resizer",
            font=("Segoe UI", 20, "bold"),
            fg=TEXT_WHITE,
            bg=BG_DARK
        )
        title_label.pack(anchor="w")

        subtitle_label = tk.Label(
            header_frame,
            text="Resize multiple images (JPG, PNG, WEBP) in a single run. Keep originals safe.",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=BG_DARK
        )
        subtitle_label.pack(anchor="w")

        # -------------------------------------------------------------
        # 2. FILE SELECTION CARD
        # -------------------------------------------------------------
        self.file_card = tk.Frame(
            main_container,
            bg=CARD_BG,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1,
            padx=15,
            pady=15
        )
        self.file_card.pack(fill="x", pady=(0, 15))

        file_header = tk.Frame(self.file_card, bg=CARD_BG)
        file_header.pack(fill="x")

        file_title = tk.Label(
            file_header,
            text="1. Select Files",
            font=("Segoe UI", 12, "bold"),
            fg=TEXT_WHITE,
            bg=CARD_BG
        )
        file_title.pack(side="left")

        # Select Files button
        self.btn_select = self.create_custom_button(
            file_header,
            text="Browse Images",
            command=self.browse_files,
            bg_color=ACCENT_BLUE,
            hover_color=ACCENT_BLUE_HOVER,
            width=14
        )
        self.btn_select.pack(side="right")

        # File stats / details
        self.files_label = tk.Label(
            self.file_card,
            text="No files selected yet.",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=CARD_BG,
            justify="left"
        )
        self.files_label.pack(anchor="w", pady=(10, 5))

        # Files Preview Box
        preview_frame = tk.Frame(self.file_card, bg=CARD_BG)
        preview_frame.pack(fill="x")

        self.preview_listbox = tk.Listbox(
            preview_frame,
            height=3,
            bg=BG_DARK,
            fg=TEXT_MUTED,
            selectbackground=CARD_BG,
            selectforeground=TEXT_WHITE,
            relief="flat",
            bd=0,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1,
            font=("Consolas", 9)
        )
        self.preview_listbox.pack(side="left", fill="x", expand=True)

        list_scrollbar = tk.Scrollbar(preview_frame, orient="vertical", command=self.preview_listbox.yview)
        list_scrollbar.pack(side="right", fill="y")
        self.preview_listbox.config(yscrollcommand=list_scrollbar.set)

        # -------------------------------------------------------------
        # 3. DIMENSIONS CARD
        # -------------------------------------------------------------
        dim_card = tk.Frame(
            main_container,
            bg=CARD_BG,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1,
            padx=15,
            pady=15
        )
        dim_card.pack(fill="x", pady=(0, 15))

        dim_title = tk.Label(
            dim_card,
            text="2. Target Dimensions",
            font=("Segoe UI", 12, "bold"),
            fg=TEXT_WHITE,
            bg=CARD_BG
        )
        dim_title.pack(anchor="w", pady=(0, 10))

        inputs_frame = tk.Frame(dim_card, bg=CARD_BG)
        inputs_frame.pack(fill="x")

        # Width Input
        width_label = tk.Label(inputs_frame, text="Width (px):", font=("Segoe UI", 10), fg=TEXT_WHITE, bg=CARD_BG)
        width_label.pack(side="left", padx=(0, 5))

        self.width_border, self.width_entry = self.create_custom_entry(inputs_frame, width=8)
        self.width_border.pack(side="left", padx=(0, 20))

        # Height Input
        height_label = tk.Label(inputs_frame, text="Height (px):", font=("Segoe UI", 10), fg=TEXT_WHITE, bg=CARD_BG)
        height_label.pack(side="left", padx=(0, 5))

        self.height_border, self.height_entry = self.create_custom_entry(inputs_frame, width=8)
        self.height_border.pack(side="left", padx=(0, 10))

        # Aspect ratio helper note
        aspect_note = tk.Label(
            dim_card,
            text="💡 Tip: Provide only one value to resize dynamically keeping original aspect ratio.",
            font=("Segoe UI", 8, "italic"),
            fg=TEXT_MUTED,
            bg=CARD_BG
        )
        aspect_note.pack(anchor="w", pady=(8, 0))

        # -------------------------------------------------------------
        # 4. ACTION & LOGS CARD
        # -------------------------------------------------------------
        action_card = tk.Frame(
            main_container,
            bg=CARD_BG,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1,
            padx=15,
            pady=15
        )
        action_card.pack(fill="both", expand=True)

        action_header = tk.Frame(action_card, bg=CARD_BG)
        action_header.pack(fill="x")

        action_title = tk.Label(
            action_header,
            text="3. Execution & Logs",
            font=("Segoe UI", 12, "bold"),
            fg=TEXT_WHITE,
            bg=CARD_BG
        )
        action_title.pack(side="left")

        # Resize Button
        self.btn_resize = self.create_custom_button(
            action_header,
            text="Start Resizing",
            command=self.start_processing,
            bg_color=ACCENT_GREEN,
            hover_color=ACCENT_GREEN_HOVER,
            width=14
        )
        self.btn_resize.pack(side="right")

        # Progress bar
        self.progress_bar = ttk.Progressbar(action_card, mode="determinate", style="TProgressbar")
        self.progress_bar.pack(fill="x", pady=(15, 5))

        # Status text
        self.status_label = tk.Label(
            action_card,
            text="Ready to begin.",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=CARD_BG
        )
        self.status_label.pack(anchor="w", pady=(0, 10))

        # Log details Listbox (for detailed run feedback)
        log_frame = tk.Frame(action_card, bg=CARD_BG)
        log_frame.pack(fill="both", expand=True)

        self.log_listbox = tk.Listbox(
            log_frame,
            bg=BG_DARK,
            fg=TEXT_WHITE,
            relief="flat",
            bd=0,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1,
            font=("Consolas", 9),
            selectbackground=CARD_BG,
            selectforeground=TEXT_WHITE
        )
        self.log_listbox.pack(side="left", fill="both", expand=True)

        log_scrollbar = tk.Scrollbar(log_frame, orient="vertical", command=self.log_listbox.yview)
        log_scrollbar.pack(side="right", fill="y")
        self.log_listbox.config(yscrollcommand=log_scrollbar.set)

    # -------------------------------------------------------------
    # Helper widgets
    # -------------------------------------------------------------
    def create_custom_button(self, parent, text, command, bg_color, hover_color, fg_color=TEXT_WHITE, width=15):
        """Creates a flat button with pointer hover cursor and colors."""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg_color,
            fg=fg_color,
            font=("Segoe UI", 9, "bold"),
            activebackground=hover_color,
            activeforeground=fg_color,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=12,
            pady=6
        )
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_color) if not self.is_processing else None)
        btn.bind("<Leave>", lambda e: btn.config(bg=bg_color) if not self.is_processing else None)
        return btn

    def create_custom_entry(self, parent, width=10):
        """Creates a styled text entry with a custom border wrapper."""
        border_frame = tk.Frame(parent, bg=BORDER_COLOR, bd=1)
        entry = tk.Entry(
            border_frame,
            bg="#0f172a",
            fg=TEXT_WHITE,
            insertbackground=TEXT_WHITE,
            relief="flat",
            bd=0,
            font=("Segoe UI", 10),
            width=width,
            justify="center"
        )
        entry.pack(padx=2, pady=2, fill="both", expand=True)
        return border_frame, entry

    # -------------------------------------------------------------
    # UI Actions & Core Logic
    # -------------------------------------------------------------
    def browse_files(self):
        """Open open-file dialog to select multiple image files."""
        file_types = [
            ("Image files", "*.jpg;*.jpeg;*.png;*.webp"),
            ("JPEG files", "*.jpg;*.jpeg"),
            ("PNG files", "*.png"),
            ("WEBP files", "*.webp"),
            ("All files", "*.*")
        ]
        files = filedialog.askopenfilenames(
            title="Select Images to Resize",
            filetypes=file_types
        )
        if files:
            self.selected_files = list(files)
            # Update GUI fields
            self.files_label.config(text=f"{len(self.selected_files)} files selected.")
            
            # Clear and populate preview listbox
            self.preview_listbox.delete(0, tk.END)
            for f in self.selected_files:
                self.preview_listbox.insert(tk.END, os.path.basename(f))
        
    def log_message(self, message, log_type="info"):
        """Add a formatted entry to the logs log listbox."""
        self.log_listbox.insert(tk.END, message)
        self.log_listbox.see(tk.END)  # Scroll to end
        
        # Color-code line based on success/error/info
        idx = self.log_listbox.size() - 1
        if log_type == "success":
            self.log_listbox.itemconfig(idx, fg=ACCENT_GREEN)
        elif log_type == "error":
            self.log_listbox.itemconfig(idx, fg=ACCENT_RED)
        else:
            self.log_listbox.itemconfig(idx, fg=TEXT_MUTED)

    def validate_inputs(self):
        """Validates entry fields for width/height and file list."""
        if not self.selected_files:
            messagebox.showwarning("Warning", "Please select at least one image file first.")
            return None

        w_str = self.width_entry.get().strip()
        h_str = self.height_entry.get().strip()

        if not w_str and not h_str:
            messagebox.showwarning("Warning", "Please enter at least one target dimension (Width or Height).")
            return None

        target_width = None
        target_height = None

        if w_str:
            try:
                target_width = int(w_str)
                if target_width <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Width must be a positive integer.")
                return None

        if h_str:
            try:
                target_height = int(h_str)
                if target_height <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Height must be a positive integer.")
                return None

        return target_width, target_height

    def start_processing(self):
        """Initiate background thread processing to prevent GUI freeze."""
        if self.is_processing:
            return

        dims = self.validate_inputs()
        if not dims:
            return

        width, height = dims

        # Update state and lock inputs
        self.is_processing = True
        self.toggle_ui_state(tk.DISABLED)
        
        self.log_listbox.delete(0, tk.END)
        self.progress_bar["value"] = 0
        self.status_label.config(text="Initializing resizing operations...")

        # Spawn background processing thread
        thread = threading.Thread(
            target=self.process_resizing,
            args=(width, height),
            daemon=True
        )
        thread.start()

    def toggle_ui_state(self, state):
        """Enables/Disables interactive fields while processing runs."""
        # Toggle inputs
        self.width_entry.config(state=state)
        self.height_entry.config(state=state)
        self.preview_listbox.config(state=state)
        
        # To maintain visually disabled borders
        border_col = BORDER_COLOR if state == tk.NORMAL else CARD_BG
        self.width_border.config(bg=border_col)
        self.height_border.config(bg=border_col)

        # Toggle buttons
        if state == tk.DISABLED:
            self.btn_select.config(state=tk.DISABLED, bg=BORDER_COLOR, cursor="arrow")
            self.btn_resize.config(state=tk.DISABLED, bg=BORDER_COLOR, cursor="arrow")
        else:
            self.btn_select.config(state=tk.NORMAL, bg=ACCENT_BLUE, cursor="hand2")
            self.btn_resize.config(state=tk.NORMAL, bg=ACCENT_GREEN, cursor="hand2")

    def process_resizing(self, target_w, target_h):
        """Executed on background thread: opens, resizes, and saves photos."""
        total = len(self.selected_files)
        success_count = 0

        # Define destination directory (within first file's folder)
        first_file_dir = os.path.dirname(self.selected_files[0])
        output_dir = os.path.join(first_file_dir, "resized_images")

        try:
            os.makedirs(output_dir, exist_ok=True)
            self.ui_queue.put({
                "type": "log",
                "log_type": "info",
                "message": f"Saving resized files in: {output_dir}"
            })
        except Exception as e:
            self.ui_queue.put({
                "type": "log",
                "log_type": "error",
                "message": f"Error: Failed to create folder. {str(e)}"
            })
            self.ui_queue.put({
                "type": "complete",
                "success_count": 0,
                "total_count": total,
                "output_dir": ""
            })
            return

        for idx, file_path in enumerate(self.selected_files):
            filename = os.path.basename(file_path)
            try:
                with Image.open(file_path) as img:
                    orig_w, orig_h = img.size

                    # Calculate target dimensions dynamically based on aspect ratio
                    if target_w and target_h:
                        new_w, new_h = target_w, target_h
                    elif target_w:
                        new_w = target_w
                        new_h = int(orig_h * (target_w / orig_w))
                    elif target_h:
                        new_h = target_h
                        new_w = int(orig_w * (target_h / orig_h))
                    else:
                        raise ValueError("Dimension error")

                    # High-quality Resampling Filter fallback for version safety
                    try:
                        resample_filter = Image.Resampling.LANCZOS
                    except AttributeError:
                        resample_filter = Image.LANCZOS

                    resized_img = img.resize((new_w, new_h), resample_filter)

                    # Safe handling for transparency profiles before writing JPG format
                    ext = os.path.splitext(filename)[1].lower()
                    if ext in ['.jpg', '.jpeg']:
                        if resized_img.mode in ('RGBA', 'LA'):
                            background = Image.new('RGB', resized_img.size, (255, 255, 255))
                            background.paste(resized_img, mask=resized_img.split()[3] if resized_img.mode == 'RGBA' else resized_img.split()[1])
                            resized_img = background
                        elif resized_img.mode != 'RGB':
                            resized_img = resized_img.convert('RGB')

                    dest_path = os.path.join(output_dir, filename)
                    resized_img.save(dest_path)
                    success_count += 1

                    self.ui_queue.put({
                        "type": "log",
                        "log_type": "success",
                        "message": f"[Success] {filename} -> {new_w}x{new_h}"
                    })
            except Exception as e:
                self.ui_queue.put({
                    "type": "log",
                    "log_type": "error",
                    "message": f"[Error] {filename} -> {str(e)}"
                })

            # Update progress bar
            progress = int(((idx + 1) / total) * 100)
            self.ui_queue.put({
                "type": "progress",
                "value": progress,
                "status": f"Resized {idx + 1} of {total} images..."
            })

        self.ui_queue.put({
            "type": "complete",
            "success_count": success_count,
            "total_count": total,
            "output_dir": output_dir
        })

    def check_queue(self):
        """Runs periodically in Tkinter event loop to receive updates from background threads."""
        try:
            while True:
                msg = self.ui_queue.get_nowait()
                if msg["type"] == "log":
                    self.log_message(msg["message"], msg.get("log_type", "info"))
                elif msg["type"] == "progress":
                    self.progress_bar["value"] = msg["value"]
                    self.status_label.config(text=msg["status"])
                elif msg["type"] == "complete":
                    self.is_processing = False
                    self.toggle_ui_state(tk.NORMAL)
                    self.status_label.config(text="Processing cycle finished.")
                    self.show_summary(msg["success_count"], msg["total_count"], msg["output_dir"])
                self.ui_queue.task_done()
        except queue.Empty:
            pass

        # Trigger self-check again after 100 milliseconds
        self.root.after(100, self.check_queue)

    def show_summary(self, success, total, out_path):
        """Displays completion notification popup to the user."""
        if success == total:
            messagebox.showinfo(
                "Resizing Completed",
                f"Successfully resized all {total} images!\n\nSaved in:\n{out_path}"
            )
        elif success > 0:
            messagebox.showwarning(
                "Resizing Finished with Warnings",
                f"Resized {success} of {total} images.\nCheck the log box for details on failed files.\n\nSaved in:\n{out_path}"
            )
        else:
            messagebox.showerror(
                "Resizing Failed",
                "Failed to resize any images. Please check the formats and dimension values."
            )

# Start Tkinter App
if __name__ == "__main__":
    root = tk.Tk()
    app = BulkImageResizerApp(root)
    root.mainloop()
