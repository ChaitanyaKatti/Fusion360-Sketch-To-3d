# Fusion360 Sketch To 3d

This project contains scripts for converrting 2D sketches oto 3d model using the Autodesk Fusion 360 API.

## Prerequisites

- Autodesk Fusion 360 installed
- Basic knowledge of Python programming
- Autodesk Fusion 360 API documentation

## Installation

1. Open "Command Prompt" and navigate to the `Scripts` folder.
    ```sh
    cd C:\Users\katti\AppData\Local\Autodesk\webdeploy\production\c4a5520f9bb0f0174c02662af8bd1ab67cee6298\Python
    
    # Open python
    .\python.exe
    
    # Install the ezdxf module
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'ezdxf'])
    exit()
    ```
2. Open Fusion 360 and go to the `Scripts and Add-Ins` panel. Create a new script.

3. Goto the Scipts folder and git clone the repository.
    ```sh
    git clone https://github.com/ChaitanyaKatti/Fusion360-Sketch-To-3d.git
    ```

## Usage

1. Open Autodesk Fusion 360.
2. Go to the `Scripts and Add-Ins` panel.
4. Click `Run` to execute the script.
