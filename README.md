# How to Run

## Environment Setup

### 1. Using Conda (Recommended)
Create the environment using the provided `environment.yml` file:
```bash
conda env create -f environment.yml
conda activate openvibe_neurofeedback
```

### 2. Using Python venv (.env)
If you prefer using a standard virtual environment:
```bash
python -m venv .env
source .env/bin/activate  # On Windows: .env\Scripts\activate
pip install pygame pylsl numpy matplotlib
```

## Dependencies
The project requires the following libraries:
- `pygame`
- `pylsl`
- `numpy`
- `matplotlib`

## Running the Code
To start the spaceship game, run the following command from the project root:
```bash
python src/spaceship_game.py
```
