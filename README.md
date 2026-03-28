# Neurofeedback Odyssey

A neurofeedback-controlled spaceship game powered by EEG brainwaves through OpenViBE and LSL.

## Project Structure

- `assets/`: Image resources for the game (spaceship, asteroids, background).
- `notebooks/`: Jupyter Notebooks for experimentation and visualization.
  - `spaceship_game.ipynb`: Detailed guide and game launcher.
  - `signal_viewer.ipynb`: Real-time signal viewer for the EEG stream.
- `scenarios/`: OpenViBE XML scenario files.
  - `neurofeedback_videogame.xml`: The main neurofeedback game scenario.
  - `signal_viewer.xml`: Simple signal monitoring scenario.
- `src/`: Python source code.
  - `spaceship_game.py`: Core game logic using Pygame and PyLSL.
- `environment.yml`: Conda environment configuration.
- `openvibe.cmd`: Script to launch OpenViBE Designer with correct environment paths.

## How to Run

1.  **Launch OpenViBE**: Use `openvibe.cmd` to open OpenViBE Designer.
2.  **Load Scenario**: Open any scenario from the `scenarios/` directory.
3.  **Start LSL Export**: Ensure the LSL Export box is active and press Play.
4.  **Launch Game**: Run `python src/spaceship_game.py` or open the `spaceship_game.ipynb` notebook.

## Controls

- **Focused**: Maintain focus to make the spaceship fly UP.
- **Unfocused**: Relax to let the spaceship drift DOWN.
- **Mouse Fallback**: If no LSL stream is detected, use your mouse Y-position to control vertical movement (Above center = Fly Up).
