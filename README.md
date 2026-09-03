# 📷 Photography Grading Assistant

A modern, lightweight Python desktop application for analyzing images and extracting technical photography metadata.

The project is being developed as the foundation for a **Smart Photography Grading Assistant** designed to help photography teachers evaluate the technical aspects of student assignments automatically while keeping the final artistic evaluation in the hands of the teacher.

## ✨ Features

### 👨‍🏫 Student Workflow

* 👥 Create a photography session
* 📝 Add students to the session
* 🖼️ Assign images to students
* 🔄 Review student submissions sequentially
* 👤 Display the current student while reviewing their image

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

* Preview selected images directly inside the application

### 🖱️ Drag & Drop

* Drag images directly into the application to open them

### 🕘 Recent Files

* Automatically stores recently opened images
* Persists recent files between application launches
* Quickly reopen previously viewed images

### 📋 Copy Info

* Copy image and EXIF information directly to the clipboard

### 📦 Export

Metadata can be exported to:

* JSON
* CSV

The export functionality is currently implemented in the application core and is being prepared for further integration into the GUI workflow.

### 🖥️ Modern GUI

* Modern dark-themed interface
* Built with CustomTkinter
* Modular GUI components

### ⌨️ Terminal Mode

* Access core image analysis functionality without using the GUI

---

## 🛠️ Technologies

* **Python**
* **Pillow** — image processing
* **piexif** — EXIF metadata extraction
* **CustomTkinter** — desktop GUI
* **tkinterdnd2** — drag & drop support

---

## 📁 Project Structure

```text
Image-Metadata/
│
├── app/
│   ├── core/
│   │   ├── image.py
│   │   ├── metadata.py
│   │   ├── histogram.py
│   │   └── converters.py
│   │
│   ├── storage/
│   │   ├── recent_files.py
│   │   └── export.py
│   │
│   └── gui/
│       ├── app.py
│       ├── image_viewer.py
│       ├── metadata_panel.py
│       ├── histogram_panel.py
│       └── widgets.py
│
├── tests/
│   ├── test_image.py
│   ├── test_metadata.py
│   ├── test_histogram.py
│   ├── test_converters.py
│   └── test_export.py
│
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

### `app/core/`

Contains the core image-processing and metadata functionality.

* Image loading and processing
* EXIF metadata extraction
* EXIF value conversion
* RGB histogram generation

### `app/storage/`

Handles application data persistence and exporting.

* Recent file management
* JSON export
* CSV export

### `app/gui/`

Contains the graphical user interface and its individual components.

* Main application window
* Image preview
* Metadata panel
* Histogram panel
* Reusable GUI widgets
* Drag & Drop
* Student workflow

### `tests/`

Contains unit tests for the core functionality and storage components.

### `main.py`

The application entry point.

It initializes and launches the GUI:

```python
from app.gui.app import App

if __name__ == "__main__":
    app = App()
    app.mainloop()
```

---

## 🧩 Architecture

The application follows a modular architecture separating the GUI, core logic, and storage functionality.

```text
                    main.py
                       │
                       ▼
                  app/gui/app.py
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
      Image Viewer  Metadata    Histogram
          │          Panel         Panel
          │            │            │
          └────────────┼────────────┘
                       ▼
                    app/core/
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       image.py   metadata.py   histogram.py
                       │
                       ▼
                  converters.py

                    app/storage/
                       │
              ┌────────┴────────┐
              ▼                 ▼
        recent_files.py     export.py
```

This separation keeps the image-processing logic independent from the GUI, making the project easier to test, maintain, and extend.

---

## ▶️ Run the Application

Install the dependencies:

```bash
pip install -r requirements.txt
```

Run the GUI from the project root:

```bash
python main.py
```

The application can also be launched as a Python module:

```bash
python -m app.gui.app
```

---

## 🧪 Running Tests

Run the test suite with:

```bash
python -m unittest discover
```

---

## 🚀 Future Vision

Photography Grading Assistant is being developed incrementally toward a **Smart Photography Grading Assistant**.

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
Technical Score
    │
    ▼
Teacher Review
    │
    ▼
Final Grade
```

Planned features include:

* 📋 Assignment management
* ⚙️ Custom photography rules
* 📊 Batch image analysis
* 🐼 Pandas DataFrame integration
* 🎯 Automatic technical scoring
* 📄 Grading reports
* 📈 Student and assignment statistics
* 🤖 AI-assisted photography analysis

For example, a teacher could define a rule such as:

```text
ISO must be between 200 and 600
```

The application could then analyze an entire set of student photographs, evaluate their EXIF metadata against the defined rules, and generate a technical score.

The teacher would remain responsible for evaluating artistic aspects such as composition, creativity, storytelling, and visual style.

### 🎯 Long-Term Goal

The long-term goal is to build a **local-first, privacy-friendly desktop application** that helps photography teachers evaluate the technical aspects of student assignments efficiently.

The application is intentionally designed to keep student photographs and their metadata local rather than requiring them to be uploaded to a remote service.

---

## 📌 Project Status

**Current version: v2.1 — Modular Architecture**

The project has moved from a monolithic GUI/core structure to a modular architecture with separated:

* Core image processing
* Metadata extraction
* Histogram generation
* Storage and export
* GUI components
* Automated tests

The next development stages will focus on building the photography grading workflow on top of this architecture.
