
import os
import threading
import queue
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageOps

# =====================================================
# CONFIGURATION
# =====================================================

BG = "#0f172a"
CARD = "#1e293b"
INPUT_BG = "#0b1220"
BLUE = "#3b82f6"
GREEN = "#10b981"
RED = "#ef4444"
WHITE = "#f8fafc"
MUTED = "#94a3b8"
BORDER = "#334155"

SUPPORTED_FORMATS = (".jpg", ".jpeg", ".png", ".webp")


# =====================================================
# MAIN APPLICATION
# =====================================================

class BulkImageResizerApp:

    def __init__(self, root):

        self.root = root
        self.root.title("Bulk Image Resizer Pro")
        self.root.geometry("760x760")
        self.root.minsize(680, 680)
        self.root.configure(bg=BG)

        self.selected_files = []
        self.output_dir = ""
        self.ui_queue = queue.Queue()
        self.is_processing = False

        self.setup_styles()
        self.create_widgets()

        self.root.after(100, self.check_queue)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # =================================================
    # STYLES
    # =================================================

    def setup_styles(self):

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "TProgressbar",
            thickness=12,
            troughcolor=BORDER,
            background=BLUE,
            borderwidth=0
        )

        style.configure(
            "TCombobox",
            fieldbackground=INPUT_BG,
            background=CARD,
            foreground=WHITE,
            arrowcolor=WHITE
        )

    # =================================================
    # UI HELPERS
    # =================================================

    def create_label(self, parent, text, size=10, color=WHITE, bold=False):

        return tk.Label(
            parent,
            text=text,
            font=("Segoe UI", size, "bold" if bold else "normal"),
            bg=parent["bg"],
            fg=color
        )

    def create_button(self, parent, text, command, color=BLUE):

        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg=WHITE,
            activebackground=color,
            activeforeground=WHITE,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=7
        )

    def create_card(self, parent):

        return tk.Frame(
            parent,
            bg=CARD,
            highlightbackground=BORDER,
            highlightthickness=1,
            padx=15,
            pady=12
        )

    # =================================================
    # GUI
    # =================================================

    def create_widgets(self):

        main = tk.Frame(self.root, bg=BG, padx=22, pady=18)
        main.pack(fill="both", expand=True)

        # HEADER

        self.create_label(
            main, "Bulk Image Resizer Pro", 22, WHITE, True
        ).pack(anchor="w")

        self.create_label(
            main,
            "Resize multiple images quickly with professional quality.",
            9, MUTED
        ).pack(anchor="w", pady=(3, 15))

        # FILE SELECTION

        file_card = self.create_card(main)
        file_card.pack(fill="x", pady=(0, 12))

        header = tk.Frame(file_card, bg=CARD)
        header.pack(fill="x")

        self.create_label(
            header, "1. Select Images", 12, WHITE, True
        ).pack(side="left")

        self.create_button(
            header, "Browse Images", self.browse_files
        ).pack(side="right")

        self.files_label = self.create_label(
            file_card, "No images selected.", 9, MUTED
        )
        self.files_label.pack(anchor="w", pady=8)

        list_frame = tk.Frame(file_card, bg=CARD)
        list_frame.pack(fill="x")

        self.file_list = tk.Listbox(
            list_frame,
            height=4,
            bg=INPUT_BG,
            fg=WHITE,
            selectbackground=BLUE,
            selectforeground=WHITE,
            relief="flat",
            font=("Consolas", 9),
            bd=0
        )
        self.file_list.pack(side="left", fill="x", expand=True)

        scrollbar = ttk.Scrollbar(
            list_frame,
            orient="vertical",
            command=self.file_list.yview
        )
        scrollbar.pack(side="right", fill="y")
        self.file_list.config(yscrollcommand=scrollbar.set)

        buttons = tk.Frame(file_card, bg=CARD)
        buttons.pack(fill="x", pady=(8, 0))

        self.create_button(
            buttons, "Remove Selected", self.remove_selected, RED
        ).pack(side="left")

        self.create_button(
            buttons, "Clear All", self.clear_files, "#475569"
        ).pack(side="left", padx=8)

        # DIMENSIONS

        dim_card = self.create_card(main)
        dim_card.pack(fill="x", pady=(0, 12))

        self.create_label(
            dim_card, "2. Resize Settings", 12, WHITE, True
        ).pack(anchor="w", pady=(0, 12))

        dimensions = tk.Frame(dim_card, bg=CARD)
        dimensions.pack(fill="x")

        self.width_var = tk.StringVar()
        self.height_var = tk.StringVar()

        self.add_entry(dimensions, "Width (px)", self.width_var)
        self.add_entry(dimensions, "Height (px)", self.height_var)

        # RESIZE MODE

        settings = tk.Frame(dim_card, bg=CARD)
        settings.pack(fill="x", pady=(12, 0))

        self.create_label(
            settings, "Resize Mode:", 9
        ).pack(side="left")

        self.mode_var = tk.StringVar(value="Fit")

        mode_box = ttk.Combobox(
            settings,
            textvariable=self.mode_var,
            values=["Fit", "Fill", "Stretch"],
            state="readonly",
            width=12
        )
        mode_box.pack(side="left", padx=10)

        self.create_label(
            settings, "Output Format:", 9
        ).pack(side="left", padx=(15, 5))

        self.format_var = tk.StringVar(value="Original")

        format_box = ttk.Combobox(
            settings,
            textvariable=self.format_var,
            values=["Original", "JPEG", "PNG", "WEBP"],
            state="readonly",
            width=10
        )
        format_box.pack(side="left")

        # QUALITY

        quality_frame = tk.Frame(dim_card, bg=CARD)
        quality_frame.pack(fill="x", pady=(12, 0))

        self.create_label(
            quality_frame, "Image Quality:", 9
        ).pack(side="left")

        self.quality_var = tk.IntVar(value=90)

        self.quality_slider = tk.Scale(
            quality_frame,
            from_=10,
            to=100,
            orient="horizontal",
            variable=self.quality_var,
            bg=CARD,
            fg=WHITE,
            highlightthickness=0,
            troughcolor=BORDER,
            activebackground=BLUE,
            length=220
        )
        self.quality_slider.pack(side="left", padx=10)

        # OUTPUT DIRECTORY

        output_card = self.create_card(main)
        output_card.pack(fill="x", pady=(0, 12))

        self.create_label(
            output_card, "3. Output Location", 12, WHITE, True
        ).pack(anchor="w")

        output_row = tk.Frame(output_card, bg=CARD)
        output_row.pack(fill="x", pady=(10, 0))

        self.output_label = self.create_label(
            output_row, "Default: resized_images folder", 9, MUTED
        )
        self.output_label.pack(side="left", fill="x", expand=True)

        self.create_button(
            output_row, "Choose Folder", self.choose_output
        ).pack(side="right")

        # EXECUTION

        action_card = self.create_card(main)
        action_card.pack(fill="both", expand=True)

        action_header = tk.Frame(action_card, bg=CARD)
        action_header.pack(fill="x")

        self.create_label(
            action_header, "4. Processing", 12, WHITE, True
        ).pack(side="left")

        self.resize_btn = self.create_button(
            action_header,
            "Start Resizing",
            self.start_processing,
            GREEN
        )
        self.resize_btn.pack(side="right")

        self.progress = ttk.Progressbar(
            action_card,
            mode="determinate",
            maximum=100
        )
        self.progress.pack(fill="x", pady=(15, 5))

        self.status = self.create_label(
            action_card, "Ready to begin.", 9, MUTED
        )
        self.status.pack(anchor="w")

        # LOGS

        self.log_list = tk.Listbox(
            action_card,
            height=7,
            bg=INPUT_BG,
            fg=WHITE,
            relief="flat",
            font=("Consolas", 9),
            bd=0
        )
        self.log_list.pack(fill="both", expand=True, pady=(10, 0))

    # =================================================
    # ENTRY HELPER
    # =================================================

    def add_entry(self, parent, label, variable):

        frame = tk.Frame(parent, bg=CARD)
        frame.pack(side="left", padx=(0, 25))

        self.create_label(
            frame, label, 9
        ).pack(anchor="w")

        entry = tk.Entry(
            frame,
            textvariable=variable,
            width=13,
            bg=INPUT_BG,
            fg=WHITE,
            insertbackground=WHITE,
            relief="flat",
            font=("Segoe UI", 11),
            justify="center"
        )
        entry.pack(pady=5, ipady=5)

    # =================================================
    # FILE MANAGEMENT
    # =================================================

    def browse_files(self):

        files = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[
                ("Image Files", "*.jpg *.jpeg *.png *.webp"),
                ("All Files", "*.*")
            ]
        )

        if files:

            existing = set(self.selected_files)

            for path in files:

                if path not in existing:
                    self.selected_files.append(path)
                    existing.add(path)

            self.update_file_list()

    def update_file_list(self):

        self.file_list.delete(0, tk.END)

        for path in self.selected_files:
            self.file_list.insert(tk.END, os.path.basename(path))

        self.files_label.config(
            text=f"{len(self.selected_files)} image(s) selected."
        )

    def remove_selected(self):

        selected = self.file_list.curselection()

        for index in reversed(selected):
            del self.selected_files[index]

        self.update_file_list()

    def clear_files(self):

        self.selected_files.clear()
        self.update_file_list()

    def choose_output(self):

        folder = filedialog.askdirectory(
            title="Choose Output Folder"
        )

        if folder:

            self.output_dir = folder

            self.output_label.config(
                text=folder
            )

    # =================================================
    # VALIDATION
    # =================================================

    def validate_inputs(self):

        if not self.selected_files:

            messagebox.showwarning(
                "Missing Images",
                "Please select at least one image."
            )
            return None

        w = self.width_var.get().strip()
        h = self.height_var.get().strip()

        if not w and not h:

            messagebox.showwarning(
                "Missing Dimensions",
                "Enter at least width or height."
            )
            return None

        try:

            width = int(w) if w else None
            height = int(h) if h else None

            if width is not None and width <= 0:
                raise ValueError

            if height is not None and height <= 0:
                raise ValueError

            # Avoid accidentally requesting enormous images.
            if any(v is not None and v > 20000 for v in (width, height)):
                raise ValueError

        except ValueError:

            messagebox.showerror(
                "Invalid Dimensions",
                "Width and height must be positive integers, "
                "not exceeding 20000 pixels."
            )
            return None

        return width, height

    # =================================================
    # START PROCESSING
    # =================================================

    def start_processing(self):

        if self.is_processing:
            return

        dimensions = self.validate_inputs()

        if not dimensions:
            return

        width, height = dimensions

        self.is_processing = True
        self.resize_btn.config(state="disabled")

        self.progress["value"] = 0
        self.log_list.delete(0, tk.END)

        self.status.config(text="Starting...")

        files = self.selected_files.copy()

        mode = self.mode_var.get()
        output_format = self.format_var.get()
        quality = self.quality_var.get()
        output_dir = self.output_dir

        thread = threading.Thread(
            target=self.process_images,
            args=(
                files,
                width,
                height,
                mode,
                output_format,
                quality,
                output_dir
            ),
            daemon=True
        )

        thread.start()

    # =================================================
    # IMAGE RESIZING ENGINE
    # =================================================

    def process_images(
        self,
        files,
        width,
        height,
        mode,
        output_format,
        quality,
        output_dir
    ):

        total = len(files)
        success = 0
        errors = 0

        try:

            if not output_dir:

                output_dir = os.path.join(
                    os.path.dirname(files[0]),
                    "resized_images"
                )

            os.makedirs(output_dir, exist_ok=True)

            self.ui_queue.put(
                ("log", f"Output: {output_dir}", "info")
            )

        except Exception as e:

            self.ui_queue.put(
                ("complete", 0, total, output_dir, 0, str(e))
            )
            return

        for index, path in enumerate(files):

            filename = os.path.basename(path)

            try:

                with Image.open(path) as original:

                    img = ImageOps.exif_transpose(original)
                    img.load()

                    original_width, original_height = img.size

                    # Calculate missing dimension using aspect ratio.

                    if width and height:

                        target_w, target_h = width, height

                    elif width:

                        target_w = width
                        target_h = max(
                            1,
                            round(
                                original_height *
                                width / original_width
                            )
                        )

                    else:

                        target_h = height
                        target_w = max(
                            1,
                            round(
                                original_width *
                                height / original_height
                            )
                        )

                    # Resize according to selected mode.

                    if mode == "Fit":

                        img.thumbnail(
                            (target_w, target_h),
                            Image.Resampling.LANCZOS
                        )

                    elif mode == "Fill":

                        img = ImageOps.fit(
                            img,
                            (target_w, target_h),
                            method=Image.Resampling.LANCZOS
                        )

                    else:

                        img = img.resize(
                            (target_w, target_h),
                            Image.Resampling.LANCZOS
                        )

                    # Determine output format.

                    if output_format == "Original":

                        ext = os.path.splitext(filename)[1].lower()

                    else:

                        ext = {
                            "JPEG": ".jpg",
                            "PNG": ".png",
                            "WEBP": ".webp"
                        }[output_format]

                    # Prepare image for selected format.

                    if ext in (".jpg", ".jpeg"):

                        if img.mode in ("RGBA", "LA") or "transparency" in img.info:

                            img = img.convert("RGBA")

                            background = Image.new(
                                "RGB",
                                img.size,
                                (255, 255, 255)
                            )

                            background.paste(
                                img,
                                mask=img.getchannel("A")
                            )

                            img = background

                        else:

                            img = img.convert("RGB")

                    elif ext == ".png":

                        if img.mode not in ("RGB", "RGBA", "L", "LA", "P"):
                            img = img.convert("RGBA")

                    elif ext == ".webp":

                        if img.mode not in ("RGB", "RGBA"):
                            img = img.convert("RGBA")

                    # Generate a safe filename.

                    stem = os.path.splitext(filename)[0]

                    dest = os.path.join(
                        output_dir,
                        stem + "_resized" + ext
                    )

                    counter = 1

                    while os.path.exists(dest):

                        dest = os.path.join(
                            output_dir,
                            f"{stem}_resized_{counter}{ext}"
                        )

                        counter += 1

                    # Save image.

                    save_options = {}

                    if ext in (".jpg", ".jpeg", ".webp"):

                        save_options["quality"] = quality

                    if ext in (".jpg", ".jpeg"):

                        save_options["optimize"] = True

                    if ext == ".png":

                        save_options["optimize"] = True

                    img.save(
                        dest,
                        **save_options
                    )

                    success += 1

                    self.ui_queue.put(
                        (
                            "log",
                            f"[SUCCESS] {filename} -> {img.width}x{img.height}",
                            "success"
                        )
                    )

            except Exception as e:

                errors += 1

                self.ui_queue.put(
                    (
                        "log",
                        f"[ERROR] {filename}: {str(e)}",
                        "error"
                    )
                )

            progress = ((index + 1) / total) * 100

            self.ui_queue.put(
                (
                    "progress",
                    progress,
                    f"Processed {index + 1}/{total}: {filename}"
                )
            )

        self.ui_queue.put(
            (
                "complete",
                success,
                total,
                output_dir,
                errors,
                None
            )
        )

    # =================================================
    # UI QUEUE
    # =================================================

    def check_queue(self):

        try:

            while True:

                msg = self.ui_queue.get_nowait()
                msg_type = msg[0]

                if msg_type == "log":

                    _, text, log_type = msg

                    self.log_list.insert(tk.END, text)

                    color = {
                        "success": GREEN,
                        "error": RED,
                        "info": MUTED
                    }.get(log_type, WHITE)

                    self.log_list.itemconfig(
                        tk.END,
                        fg=color
                    )

                    self.log_list.see(tk.END)

                elif msg_type == "progress":

                    _, value, status = msg

                    self.progress["value"] = value
                    self.status.config(text=status)

                elif msg_type == "complete":

                    _, success, total, folder, errors, fatal_error = msg

                    self.is_processing = False
                    self.resize_btn.config(state="normal")

                    if fatal_error:

                        self.status.config(text="Processing failed.")

                        messagebox.showerror(
                            "Processing Failed",
                            fatal_error
                        )

                    else:

                        self.status.config(
                            text=f"Completed: {success}/{total} images."
                        )

                        messagebox.showinfo(
                            "Processing Completed",
                            f"Successfully resized: {success}\n"
                            f"Failed: {errors}\n"
                            f"Total: {total}\n\n"
                            f"Output folder:\n{folder}"
                        )

                self.ui_queue.task_done()

        except queue.Empty:
            pass

        if self.root.winfo_exists():
            self.root.after(100, self.check_queue)

    # =================================================
    # CLOSE APPLICATION
    # =================================================

    def on_close(self):

        if self.is_processing:

            messagebox.showwarning(
                "Processing",
                "Image processing is still running. "
                "Please wait until it finishes."
            )

            return

        self.root.destroy()


# =====================================================
# APPLICATION ENTRY POINT
# =====================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = BulkImageResizerApp(root)

    root.mainloop()
