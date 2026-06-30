# MedRad, based on ARVI-RX offer @ Mastercamp

Medical Radiography AI analysis for Mastercamp at EFREI.
This repository is split into two parts, one containing the web app that will be presented at the end with the complete solution, and a python folder for our model testing.

To test the application properly, follow these steps :

1. Open two powershell terminals.
2. Make sur that you have installed npm package manager and uvicorn on your terminals.
3. In the PyStruct folder, create a .env file using the structure of .env.example. Put the link to the api endpoint making the model available by your own means, and the necessary API token.
4. On the first one, for the backend, navigate with the terminal to the PyStruct folder and proceed with the command **"uvicorn arvi_api.main:app --reload"**.
5. On the second one, navigate to  WebApp/ARVI-RX, then launch the command **"npm run dev"**.

The app should be able to run on standalone on your computer :)

Datasets used :
- Anouk Stein, MD, Carol Wu, Chris Carr, George Shih, Jamie Dulkowski, kalpathy, Leon Chen, Luciano Prevedello, Marc Kohli, MD, Mark McDonald, Peter, Phil Culliton, Safwan Halabi MD, and Tian Xia. RSNA Pneumonia Detection Challenge. https://kaggle.com/competitions/rsna-pneumonia-detection-challenge, 2018. Kaggle.

Other graphical assets :
- Pictogrammers icon set available under Open Font License, made available by https://opensvg.dev/icons
