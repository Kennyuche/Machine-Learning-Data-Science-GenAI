# Dog Breed Image Classification using CNNs

## 📌 Project Overview
This project focuses on **using Python to evaluate and compare deep learning–based image classifiers** for identifying dogs and dog breeds from images. The primary goal is to strengthen practical Python programming skills while working with a pre-built convolutional neural network (CNN) classifier.

The project is based on a real-world scenario where a citywide dog show requires an automated way to verify whether submitted images actually contain dogs and to correctly identify their breeds. Some users may attempt to register animals that are not dogs, so an automated validation system is necessary.

Rather than building a model from scratch, this project uses a **pre-trained CNN classifier** trained on the **ImageNet dataset (over 1.2 million images)**. The emphasis is on:
- Writing efficient Python code
- Running experiments with multiple CNN architectures
- Evaluating accuracy and performance
- Comparing results based on both correctness and computation time

---

## 🧠 Technologies & Models Used
Three well-known CNN architectures are evaluated:
- **AlexNet**
- **VGG**
- **ResNet**

These models are used through a provided Python helper function (`classifier.py`), while the core implementation and evaluation logic are handled in Python scripts.

---

## 🎯 Project Objectives
The main objectives of this project are to:

1. **Correctly identify which images contain dogs** (even if the specific breed is misclassified).
2. **Accurately classify the dog breed** for images that contain dogs.
3. **Compare AlexNet, VGG, and ResNet** to determine which architecture performs best for:
   - Dog detection
   - Dog breed classification
4. **Analyze execution time vs. accuracy** to determine whether a faster model can provide a “good enough” solution compared to slower, more accurate models.

---

## ⚠️ Classification Challenges
Some dog breeds have very similar visual features, making classification more difficult. Common examples include:
- Great Pyrenees vs. Kuvasz  
- German Shepherd vs. Malinois  
- Beagle vs. Walker Hound  

Performance depends heavily on how well each model learned to distinguish these subtle differences during training.

---

## ✅ Key Skills Demonstrated
- Python programming for machine learning workflows  
- Image classification using pre-trained CNNs  
- Model evaluation and performance comparison  
- Accuracy vs. computational efficiency analysis  
- Practical application of deep learning in a real-world use case  

---

## 👤 Author
**Kennedy**
