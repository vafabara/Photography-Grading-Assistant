# 📷 PhotoGrade

A simple, modern, and lightweight Python desktop application for analyzing image information and EXIF metadata as the foundation for a future photography grading assistant.

The project is designed with a clean two-layer structure: **image processing and application logic are handled in `main.py`, while the graphical interface is implemented in `GUI.py`.**

## ✨ Features

### 👨‍🏫 Student Workflow

* 👥 Create a photography session by entering the number of students
* 📝 Enter student names one by one
* 🖼️ Assign one image to each student
* 🔄 Review students sequentially
* 👤 Display the current student's name while reviewing their image
* ⏭️ Navigate between students with a `Next` button
* ✅ Finish the review with a `Done` state

### 🖼️ Image Information

* Format
* Dimensions
* File size
* Color mode

### 📷 EXIF Metadata

Extract and display available metadata, including:

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

### 📊 RGB Histogram

* Red, Green, and Blue channel histograms
* Displayed directly below the image preview

### 🖼️ Image Preview

* Preview the selected image directly inside the application

### 🖱️ Drag & Drop

* Drag an image directly into the application to open it

### 🕘 Recent Files

* Automatically saves recently opened images
* Recent files persist between application launches
* Quickly reopen previously viewed images

### 📋 Copy Info

* Copy image and EXIF metadata directly to the clipboard

### 🖥️ Modern GUI

* Minimal dark-themed interface
* Built with CustomTkinter

### ⌨️ Terminal Mode

* Access the core image metadata functionality without the GUI

### 📦 Export

The core application logic currently supports exporting metadata to:

* JSON
* CSV

Export functionality is implemented in `main.py` but is **not currently exposed through the graphical interface**.

## 🛠️ Technologies

* Python
* Pillow
* piexif
* CustomTkinter
* tkinterdnd2

## 📁 Project Structure

```text
PhotoGrade/

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
* JSON export
* CSV export
* Terminal mode

### `GUI.py`

Contains the graphical user interface:

* Student setup workflow
* Student management
* Image selection
* Sequential student review
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

The project currently follows a simple two-layer architecture:

```text
GUI.py
   │
   ▼
main.py
   │
   ├── Image Processing
   ├── EXIF Extraction
   ├── Histogram Generation
   ├── Recent File Management
   ├── JSON / CSV Export
   └── Terminal Mode
```

The student workflow is currently managed by the GUI and uses a simple in-memory structure for each student:

```text
Student
├── name
└── image_path
```

This structure is intentionally simple and designed to be extended in future versions with metadata, rules, evaluation results, and technical scores.

## 🚀 Future Vision

PhotoGrade is being developed incrementally toward a **Smart Photography Grading Assistant**.

The planned workflow is:

```text
Students
    │
    ▼
Photos
    │
    ▼
EXIF Metadata
    │
    ▼
Photography Rules
    │
    ▼
Automatic Technical Evaluation
    │
    ▼
Score
    │
    ▼
Teacher Review
```

Future versions may introduce:

* 📋 Assignment management
* ⚙️ Custom photography rules
* 📊 Batch image analysis
* 🐼 Pandas DataFrame integration
* 🎯 Technical scoring
* 📄 Grading reports
* 🤖 AI-assisted photography analysis

The long-term goal is to build a **local-first and privacy-friendly desktop application** that helps photography teachers evaluate the technical aspects of student assignments while keeping the final artistic evaluation in the hands of the teacher.

## 📌 Version

**v2.0**
