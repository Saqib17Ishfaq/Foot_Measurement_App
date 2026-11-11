# Foot Measurement App

A Kivy-based mobile application that measures foot length from a camera frame and recommends a shoe size. The app uses OpenCV for image preprocessing and calibration, MediaPipe Pose for foot landmarks, and a JSON chart for EU/US/UK size matching.

## Features

- Live camera preview with foot landmark detection.
- Calibration with either:
  - an A4 sheet of paper, or
  - the included 9x6 chessboard calibration pattern.
- Foot-length estimation in centimeters.
- Recommended EU shoe size with US and UK equivalents.
- Results screen with a captured image and a measure-again flow.

## Project structure

| Path | Purpose |
| --- | --- |
| `main.py` | Kivy application, camera screen, and results screen |
| `foot_detector.py` | MediaPipe Pose foot landmark detection |
| `measurement_logic.py` | Image preprocessing, reference detection, calibration, and measurement |
| `size_matcher.py` | Loads the shoe-size chart and selects a recommended size |
| `assets/shoe_size_chart.json` | Configurable EU/US/UK size ranges |
| `assets/calibration_pattern.png` | Optional chessboard reference |
| `ui/*.kv` | Kivy screen layouts |
| `Requirements.txt` | Python dependencies |
| `buildozer.spec.txt` | Android build configuration |

## Requirements

- Python 3.8 or newer
- A camera
- Windows for local development, or Linux/WSL for Buildozer Android packaging

## Run locally

Create and activate a virtual environment, then install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r Requirements.txt
python main.py
```

On Windows, camera access may need to be granted to the terminal/Python application in system privacy settings.

## How to use

1. Start the app and allow camera access.
2. Place an A4 sheet or the chessboard pattern beside the foot.
3. Press **Calibrate Reference**.
4. Keep the foot visible and press **Measure Foot**.
5. Review the measured length and recommended shoe size.

Calibration and measurement accuracy depend on camera angle, lighting, the reference object being fully visible, and the foot being inside the camera frame. The result is an estimate and should not replace a professional fitting.

## Android build

Buildozer normally expects the file to be named `buildozer.spec`. The repository keeps the existing configuration as `buildozer.spec.txt`; copy or rename it before building:

```bash
cp buildozer.spec.txt buildozer.spec
buildozer android debug
```

Android packaging with OpenCV and MediaPipe may require additional platform-specific recipe or dependency adjustments.

## Configuration

Edit `assets/shoe_size_chart.json` to change the supported size ranges. Each size contains `foot_length.min`, `foot_length.max`, and optional US/UK equivalents.

## License

No license has been specified yet. Add a license before distributing the application.
