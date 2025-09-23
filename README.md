# Link Manager Desktop App

This is a simple, cross-platform desktop application built with Python and CustomTkinter to help you manage your links. This version includes the ability to export selected links as a PDF with their corresponding QR codes.

## 📁 Project Structure

```bash
link_manager/
├── links.json           # Stores your links (created automatically)
├── linkit.py            # The main application script
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
    python linkit.py
    ```

The app will launch in a new window. It will automatically create a links.json file to save your links.

## Compiling an Executable

The easiest way to compile your application into a self-contained executable is by using the **auto-py-to-exe** tool, which provides a user-friendly graphical interface.

**Prerequisites**

Make sure you have followed the steps to set up the project and install the dependencies listed in the **"Getting Started"** section. After activating your virtual environment, install the `auto-py-to-exe` tool:

```bash
pip install auto-py-to-exe
```

1. **Run the GUI:** Open your terminal in the project directory and run the tool by typing:

    ```bash
    auto-py-to-exe
    ```

2. **Configure the Application:** A graphical window will open. Use the following settings:

    - **Script Location:** Browse and select your `linkit.py` file.

    - **Onefile:** Select the "Onefile" option to create a single executable.

    - **Icon:** (Optional) If you have an icon file, you can browse and add it here.

    - **Additional Files:** This is the most important part for `customtkinter`. Go to the "Additional Files" section, click "Add Folder," and add the `customtkinter` folder from your Python `site-packages` directory. The destination should be `customtkinter`.

3. **Convert:** Click the blue "Convert .py to .exe" button at the bottom of the window.

The tool will compile your application, and the final executable will be placed in a new `output` folder.

### Running the Executable
Once the compilation is complete, you can find your platform-specific executable inside the newly created `output/` folder. Simply double-click the file to run the application without needing to use the command line or have Python installed on the target machine.

## ✨ Latest Update Features

*Last Update: 2025-09-22*

- **PDF Export:** Select one or more links using the checkboxes and click the "Export to PDF" button to save a document containing the link names and QR codes.