# Link Manager Desktop App

This is a simple, cross-platform desktop application built with Python and CustomTkinter to help you manage your links. This version includes the ability to export selected links as a PDF with their corresponding QR codes.

## 📁 Project Structure

```bash
link_manager/
├── links.json           # Stores your links (created automatically)
├── linkman.py           # The main application script
└── requirements.txt     # Lists all necessary dependencies
```

## 🚀 Getting Started

**Prerequisites**

- Python 3.8 or higher installed on your system.

1. **Generate & Activate The Virtual Environment:**

- Generating the virtual environment:
    ```bash
    python -m venv .venv
    ```

- Activating the virtual environment:
    - **On Windows (Command Prompt or PowerShell):**
        ```bash
        .\.venv\Scripts\activate
        ```
    - **On macOS and Linux (Bash or Zsh):**
        ```bash
        source .venv/bin/activate
        ```

2. **Install Dependencies:**

    After generating and activating the virtual environment, you must install the required packages to run this application. You can do this by opening a terminal in the project directory and running the following command:
    ```bash
    pip install -r requirements.txt
    ```

This will install all necessary libraries, including customtkinter, qrcode, and reportlab.

3. **Run the Application:**

    Once the dependencies are installed, you can start the application:

    ```bash
    python linkman.py
    ```

The app will launch in a new window. It will automatically create a links.json file to save your links.

## ✨ New Features

- **PDF Export:** Select one or more links using the checkboxes and click the "Export to PDF" button to save a document containing the link names and QR codes.