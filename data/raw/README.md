RetinalAI Dataset Sources and Placement

Place each downloaded dataset under its corresponding folder:

- data/raw/DIARETDB1
- data/raw/APTOS2019
- data/raw/MESSIDOR2
- data/raw/ORIGA
- data/raw/DRIVE
- data/raw/RFMiD

Notes:
- Keep original filenames when possible.
- The unified loader scans recursively for .png/.jpg/.jpeg files.
- Labels are normalized into: dr_grade (0-4), glaucoma (0/1), cdr (float).

Recommended sources (official/commonly used mirrors):
- DIARETDB1: https://www.it.lut.fi/project/imageret/diaretdb1/
- APTOS 2019: https://www.kaggle.com/c/aptos2019-blindness-detection
- MESSIDOR-2: https://www.adcis.net/en/third-party/messidor2/
- ORIGA: https://imed.nimte.ac.cn/ORIGA-dataset/
- DRIVE: https://drive.grand-challenge.org/
- RFMiD: https://ieee-dataport.org/open-access/retinal-fundus-multi-disease-image-dataset-rfmid
