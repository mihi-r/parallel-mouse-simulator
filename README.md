# Parallel Mouse Simulation
An application created in PyQt5 and Numba to demonstrate the speed of parallel computations.

# Set-up Instructions
Prerequisites:
- Anaconda Navigator
- Visual Studio Code
- Python Extension for VS Code

1. With Anaconda Navigator, create an environment with Python 3.8
2. `git clone` this repository.
3. Open Visual Studio Code and open this repository's directory as your workspace.
4. Set the newly created Anaconda environment as the environment in Visual Studio Code.
5. Open the terminal in VS Code and run `conda activate <your-environment-name>`.
6. Install all of the required packages with `pip3 install -r requirements.txt`.
7. Run the code in the terminal with `python3 main.py`.

# Usage
Simply utilize the grid editor to edit the grid to your liking. Press "Play Mouse" to start animating the mouse. To enable running the application in parellel on CPU, check the "Parallel" option. The first run of the parallel application will take longer than normal due to the need for Numba to compile, however, subsequent runs will be faster. 
