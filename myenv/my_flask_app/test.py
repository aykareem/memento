import os
if not os.path.exists(".../intel/face-detection-adas-0001/FP16/face-detection-adas-0001.xml"):
    raise FileNotFoundError("Model file not found")
