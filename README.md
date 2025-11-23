# 🧠 Sign Language Translator

A real-time **Indian Sign Language (ISL) alphabet detection system** built using **YOLOv11**, **OpenCV**, and **MediaPipe**.
This project captures hand signs through a webcam and classifies them into alphabets (A-Z), enabling fast and accessible gesture-to-text translation.

---

## 🚀 Features

* 🔍 **Real-time hand sign detection** using YOLOv11
* 🎥 **Live webcam-based inference**
* 🖐 **Robust hand landmark detection** (MediaPipe)
* 🧾 **Dataset preprocessing and custom model training**
* ⚡ **Fast inference** optimized for CPU/GPU
* 🔤 **Outputs predicted alphabet on-screen**

---

## 📁 Project Structure

```
sign-language-translator/
│
├── SignCam.py                # Real-time sign detection
├── body.py                   # Data collection + preprocessing
├── requirements.txt          # Dependencies
├── signLang/
│   ├── weights/
│   │     └── best1.pt        # Trained YOLOv11 model
│   └── data.yaml             # Class labels + dataset config
├── dataset/
│   ├── train/
│   ├── val/
│   └── test/
└── README.md
```

---

## 📦 Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/sonalikaaaaa/sign-language-translator.git
cd sign-language-translator
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🏋️‍♀️ Training the YOLOv11 Model

### **Prepare Dataset**

Place your dataset inside:

```
signLang/dataset/
```

Ensure your `data.yaml` is inside:

```
signLang/data.yaml
```

### **Train**

```bash
yolo train model=yolo11n.pt data=signLang/data.yaml epochs=50 imgsz=640 project=runs/train name=sign_lang
```

---

## 📊 Evaluation & Curves

### 📈 Confusion Matrix

```python
from IPython.display import Image
Image("/content/runs/detect/train/confusion_matrix.png", width=600)
```

### 📉 Precision Curve

```python
from IPython.display import Image
Image("/content/runs/detect/train/PR_curve.png", width=600)
```

(*Your file path may be `/content/runs/train/sign_lang/PR_curve.png` depending on project name.*)

---

## 🎥 Running Real-Time Detection

### Run Webcam Script

```bash
python SignCam.py
```

### Run Data Collection Script

```bash
python body.py
```

---

## 🧪 Model Used

* **YOLOv11 (Ultralytics)**
* Custom-trained on **Indian Sign Language alphabet gestures**

---

## 🙌 Team

* **Pragati Das**
* **Sonalika Panda**
* **Aiswarya**
* **Pawani**
* **Tilottama**

---

## ⭐ Contribute

Feel free to submit issues or pull requests!

---

## 📜 License

This project is open-source under the MIT License.
