# 📷 Image Metadata Viewer

A simple, modern, and lightweight Python desktop application for viewing image information and EXIF metadata.

The project is designed with a clean two-layer structure: **image processing and application logic are handled in `main.py`, while the graphical interface is implemented in `GUI.py`.**

## ✨ Features

* 🖼️ Display basic image information

  * Format
  * Dimensions
  * File size
  * Color mode

* 📷 Extract and display EXIF metadata

  * Camera manufacturer
  * Camera model
  * Lens model
  * ISO
  * Aperture
  * Shutter speed
  * Focal length
  * Date taken
  * Flash
  * White balance

* 📊 RGB histogram visualization

  * Red, Green, and Blue channel histograms
  * Displayed directly below the image preview

* 🖼️ Image preview

* 🖱️ Drag & Drop support

  * Drag an image directly into the application to open it

* 🕘 Recent files

  * Automatically saves recently opened images
  * Recent files persist between application launches
  * Quickly reopen previously viewed images

* 📋 Copy Info

  * Copy image and EXIF metadata directly to the clipboard

* 🖥️ Modern minimal dark-themed GUI

* ⌨️ Terminal mode

  * Access the core image metadata functionality without the GUI

## 🛠️ Technologies

* Python
* Pillow
* piexif
* CustomTkinter
* tkinterdnd2

## 📁 Project Structure

```text
image-metadata/
├── main.py
├── GUI.py
├── recent_files.json
└── requirements.txt
```

### `main.py`

Contains the core application logic:

* Image loading and processing
* EXIF metadata extraction using `piexif`
* EXIF value conversion
* RGB histogram generation
* Recent file management
* Terminal mode

### `GUI.py`

Contains the graphical user interface:

* Image preview
* EXIF and file information display
* RGB histogram canvas
* Drag & Drop support
* Recent files menu
* Clipboard functionality
* GUI state management

## ▶️ Run the Application

Install the dependencies:

```bash
pip install -r requirements.txt
```

Then run the GUI:

```bash
python GUI.py
```

To use the terminal mode:

```bash
python main.py
```

## 🧩 Architecture

The project intentionally follows a simple two-layer architecture:

```text
GUI.py
   │
   ▼
main.py
   │
   ├── Image Processing
   ├── EXIF Extraction
   ├── Histogram Generation
   └── Recent File Management
```

The goal is to keep the project **simple, readable, and easy to extend** without introducing unnecessary architectural complexity.

## 📌 Version

**v1.30**
