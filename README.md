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

## Compiling an Executable

**Prerequisites**

Make sure you have followed the steps to set up the project and install the dependencies listed in the **"Getting Started"** section of the original guide. After activating your virtual environment, install PyInstaller:

```bash
pip install pyinstaller
```

- **Windows**

1. Open a **Command Prompt** or **PowerShell** window in the `link_manager/` directory.

2. Activate your virtual environment if it isn't already active:

    ```bash
    .\.venv\Scripts\activate
    ```

3. Run the PyInstaller command to create the executable. The `--onefile` flag bundles everything into a single file, and the `--noconsole` flag prevents a console window from popping up when the app runs.

    ```bash
    pyinstaller --onefile --noconsole linkman.py
    ```

4. After the command finishes, your executable file (`linkman.exe`) will be in the `dist/` directory inside your `link_manager/` folder.

**macOS**

1. Open a Terminal window in the `link_manager/` directory.

2. Activate your virtual environment if it isn't already active:

    ```bash
    source .venv/bin/activate
    ```

3. Run the PyInstaller command. The `--onefile` and `--noconsole` flags function the same way as in the Windows command. The `--osx-entitlements` flag is necessary for the app to function correctly on modern macOS versions.

    ```bash
    pyinstaller --onefile --noconsole --osx-entitlements linkman.entitlements linkman.py
    ```

Note: You may need to create a `linkman.entitlements` file with specific permissions if you encounter issues. For a basic app, this is often a placeholder.

4. The executable file (`linkman`) will be located in the `dist/` directory.

**Linux**

1. Open a **Terminal** window in the `link_manager/` directory.

2. Activate your virtual environment if it isn't already active:

    ```bash
    source .venv/bin/activate
    ```

3. Run the PyInstaller command to create the executable. The `--onefile` and `--noconsole` flags are used here as well.

    ```bash
    pyinstaller --onefile --noconsole linkman.py
    ```

4. The executable file (`linkman`) will be in the `dist/` directory.

### Running the Executable

Once the compilation is complete, you can find your platform-specific executable inside the newly created `dist/` folder. Simply double-click the file to run the application without needing to use the command line or have Python installed on the target machine.

## ✨ Latest Update Features

*Last Update: 2025-09-22*

- **PDF Export:** Select one or more links using the checkboxes and click the "Export to PDF" button to save a document containing the link names and QR codes.