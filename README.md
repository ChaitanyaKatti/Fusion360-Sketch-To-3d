# Fusion360 Sketch To 3d

This project contains scripts for converrting 2D sketches oto 3d model using the Autodesk Fusion 360 API.

## Prerequisites

- Autodesk Fusion 360 installed
- Basic knowledge of Python programming
- Autodesk Fusion 360 API documentation

## Installation

1. Open "Command Prompt" and run the following commands to install the `ezdxf` module.
    ```sh
    # Replace <USERNAME> with your username
    cd C:\Users\<USERNAME>\AppData\Local\Autodesk\webdeploy\production\c4a5520f9bb0f0174c02662af8bd1ab67cee6298\Python
    
    # Open python
    .\python.exe
    
    # Install the ezdxf module
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'ezdxf'])
    exit()
    ```
2. Open Fusion 360 and go to the `Scripts and Add-Ins` panel. Create a new script.

3. Goto the Scipts folder and clone the repository.
    ```sh
    # Replace <USERNAME> with your username and <SCRIPT_NAME> with the name of the script
    cd C:\Users\<USERNAME>\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\Scripts\<SCRIPT_NAME>

    # Clone the repository
    git clone https://github.com/ChaitanyaKatti/Fusion360-Sketch-To-3d.git
    ```

## Usage

1. Open Autodesk Fusion 360.
2. Go to the `Scripts and Add-Ins` panel.
4. Click `Run` to execute the script.
