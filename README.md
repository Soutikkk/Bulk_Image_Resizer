# 🖼️ Bulk Image Resizer

A modern, minimal, and user-friendly desktop application built with Python and Tkinter for batch-resizing images. It supports modern formats like JPG, PNG, and WEBP, utilizes multi-threaded processing to keep the interface smooth and responsive, and protects your original photos by saving resized output in a separate folder.

---

## ✨ Features

- **Intuitive GUI**: A sleek dark mode palette designed with simple, beginner-friendly instructions.
- **Bulk Processing**: Select multiple images from various folders and process them all in a single click.
- **Aspect Ratio Maintenance**: 
  - Provide both width and height to crop/scale to exact size.
  - Leave one field (either width or height) empty to automatically scale the image while **preserving its original aspect ratio**.
- **Real-time Color Coded Logs**: View success and error messages for each file in real-time as processing occurs.
- **Safe Execution**: Resized photos are saved into a new directory named `resized_images` created inside your files' parent folder. Original images are kept intact and unmodified.
- **Multi-threaded Logic**: The GUI remains completely responsive and functional (no freezes) even when processing hundreds of files.

---

## 🛠️ Prerequisites

Make sure you have **Python 3.x** installed on your computer. You can download it from [python.org](https://www.python.org/downloads/).

---

## 🚀 Installation & Running the App

### 1. Clone or Download the repository
If you have Git installed, clone this repository:
```bash
git clone https://github.com/Soutikkk/Bulk_Image_Resizer.git
cd Bulk_Image_Resizer
```
Or simply download the `resizer.py` file to your folder.

### 2. Install Dependencies
This project uses **Pillow** (PIL fork) for high-performance, quality image scaling. Install it using `pip` in your command line:
```bash
pip install Pillow
```

### 3. Launch the Application
Run the Python script:
```bash
python resizer.py
```

---

## 📖 How to Use

1. Click the **Browse Images** button under section **1. Select Files**. Select one or more images (`.jpg`, `.jpeg`, `.png`, `.webp`) and click Open.
2. Enter your desired dimensions in section **2. Target Dimensions**:
   - To resize to a fixed custom resolution (e.g. `800x600`), enter both values.
   - To resize to a width of `1080` while automatically scaling the height relative to the image's original shape, enter `1080` in **Width** and leave **Height** blank.
3. Click the **Start Resizing** button under section **3. Execution & Logs**.
4. Monitor progress on the progress bar and read the scrolling logs.
5. Once completed, a summary popup will show. You can find the resized files in the `resized_images` folder next to your original photos.

---

## 🛡️ License

This project is open-source and available under the MIT License.
