# 📷 PhotoGrade

A modular Python desktop application for **technical photography grading** based on image metadata and configurable photography rules.

PhotoGrade is being developed as a **Smart Photography Grading Assistant** for photography teachers. It analyzes student photographs using EXIF metadata and a configurable Rule Engine, then combines the automated technical score with the teacher's manual evaluation.

## ✨ Features

* 👨‍🏫 Student-based photography grading workflow
* 📁 Select and scan a folder for each student
* 🖼️ Multi-image student submissions
* 📷 EXIF metadata extraction
* 📊 RGB histogram analysis
* ⚙️ Configurable Rule Engine with automatic tolerance
* 🟢🟡🔴 Technical evaluation using Green / Yellow / Red results
* 👤 Teacher Grading with configurable System / Human score weighting
* 🧮 Automatic Total Score calculation
* 🖱️ Drag & Drop image loading
* 🕘 Recent files
* 📋 Copy image and metadata information
* 📦 JSON / CSV export support

## 🧠 Python Concepts Used

The project applies practical Python development concepts, including:

* Modular project architecture
* Object-Oriented Programming
* Classes and data models
* Lists, dictionaries, and data processing
* File and folder handling
* Exception handling and input validation
* Unit and integration testing
* GUI development with Tkinter / CustomTkinter
* Image processing with Pillow
* EXIF processing with piexif

## 🏗️ Project Structure

```text
Image-Metadata/
│
├── app/
│   ├── core/
│   │   ├── image.py
│   │   ├── metadata.py
│   │   ├── histogram.py
│   │   ├── converters.py
│   │   ├── rules.py
│   │   ├── scoring.py
│   │   ├── student.py
│   │   ├── teacher_scoring.py
│   │   └── tolerance.py
│   │
│   ├── gui/
│   │   ├── app.py
│   │   ├── home_screen.py
│   │   ├── student_setup.py
│   │   ├── rule_engine.py
│   │   ├── image_viewer.py
│   │   ├── metadata_panel.py
│   │   ├── teacher_grading.py
│   │   ├── histogram_panel.py
│   │   └── widgets.py
│   │
│   └── storage/
│       ├── export.py
│       └── recent_files.py
│
├── tests/
├── main.py
├── requirements.txt
└── README.md
```

The application is separated into three main layers:

* **`app/core/`** — image processing, metadata, rules, scoring, and data models
* **`app/gui/`** — graphical interface and application workflow
* **`app/storage/`** — persistence and export functionality

This separation keeps the core logic independent from the GUI and makes the project easier to test and extend.

## ▶️ Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python main.py
```

## 🧪 Tests

Run the test suite:

```bash
python -m unittest discover
```

## 🚀 Vision

PhotoGrade is gradually evolving toward a **local-first, privacy-friendly photography grading system** where teachers can define technical requirements, automatically evaluate student photographs, and combine the results with their own assessment.

The long-term goal is to extend the system with student-level statistics, DataFrame-based analysis, grading reports, and optional AI-assisted photography evaluation.
