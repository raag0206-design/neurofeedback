# Neurofeedback Project

This project includes scripts and notebooks for running a neurofeedback spaceship game and viewing EEG signals.

## Environment Setup

You can set up the required environment using either **Conda** or Python's built-in **venv**. Both methods will install all necessary dependencies.

### 1. Using Conda
Create the environment using the provided `environment.yml` file:
```bash
conda env create -f environment.yml
conda activate openvibe_neurofeedback
```

### 2. Using Python venv
If you prefer using a standard virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

## Running the Code

### Scripts

**Spaceship Game:**
To start the main spaceship game, run the following command from the project root:
```bash
python src/spaceship_game.py
```
