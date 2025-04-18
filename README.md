# Course Catalog Automation Project

## Minnesota State University, Mankato

Developed by: **Catalog Wizards**  
**Team Members:**  
- **Adam Chase** (Team Lead)  
- **Evan Darling** (AI Specialist and Technical Lead)  
- **Logan Loch** (Data Analysis and Visualization Lead)  
- **Tinsay Gebremariam** (Data Engineering Lead)

---

## 📖 Overview

This repository contains the codebase and supporting documentation for the **Course Catalog Automation Tool**, developed to enhance course catalog management at Minnesota State University, Mankato. The tool uses AI data analytics and Python Scripts to streamline catalog analysis, ensuring consistency and boosting operational efficiency.

This repository is a work in progress with the Enrollment Projection Team, which is the Partner CS team we worked with throughout the semester to provide them with the data about the Course Catalog from the University in a clean, organized fashion.

Please see our Handover Documentation for further details about the project:
[HandoverDocumentation](https://docs.google.com/document/d/1cGDePDSeqsEZEynMIXdLtys_tKGcuo_o/edit?usp=sharing&ouid=111109381263984826684&rtpof=true&sd=true)

Link to Handover Documentation Main Folder (all handover documentation is located here):
[HandoverDocFolderMAIN](https://drive.google.com/drive/folders/1QzcPhiwN3tsmDp8o_IQDrD6uY_9eQmZk?usp=drive_link)

---

## 🔎 How to navigate the GitHub

There are **five** main folders in the main branch

The **first** folder (Data) contains our **Data**, which is all of the data we used throughout the project, including the isrs CSV file with every required course for all of the programs.
Then, we also included a DOC and PDF file containing the entire course catalog as of 2024-2025 school year.

The **second** folder (New_Work) contains all of our new work, which contains all of our CSV files that we were able to output and work with throughout the semester. Inside there, the **Seperate programs and degrees CSV files** is the main folder that we were able to take as Input files for our Maximus script. In here there is also the **cleaned_course_list.csv** which was a very important aspect for the Partner CS Enrollement Projection Team. 

The **third** folder (Old_Work_from_Previous_team) contains all of the previous teams work, which is all old files they worked with. May be useful if needed, but ignored and extracted important files from it.

The **fourth** folder (Parsing Scripts/Scripts) contains our parsing scripts and all the scripts we used to create the output CSV files for the University's Programs. Also contains Maximus script. Uses Jupyter Notebook here. **MaximusV2.py** is the main script that we used to work on the project.

The **fifth** folder (Scripts) contains all of the scripts we used throughout the project. The **Alphabetical** script would organize the **new_csv.csv** file in alphabetical order, and the **BetterVerifyCSVFileIsCorrect.py** script allowed us to get a better feel for the correct Syntax for the **new_csv.csv** file for the Partner CS Enrollment Projection team. 


---

## ☁️ Dependencies 

Dependencies needed to run the scripts

**Ensure Python 3.11 or higher && .net 9.0 or higher for Jupyter Notebook**

When you go to run the **.ipynb** file it will or _should_ automatically prompt you to download **ipykernel** from Jupyter. Install this to be able to run the **.ipynb** file.

When you run the file, you will also have to select the specific _kernel_ you will want to run it in. This button will be in the upper right corner of the **.ipynb** file. 

When you run the **.ipynb** file, MAKE SURE TO HIT THE **Run All** button in the top bar / top part of the file.

It will then prompt you to input a CSV file, copy the path to any CSV file in the **Seperate_Programs_and_degrees-CSV_Files** folder, then put that into the input. The program then should take that data and output it into the **new_csv.csv** that is in the same folder with the script. 

These **.ipynb** files are also extracted into normal **.py** files with the same name if you are having issues with running **.ipynb** files.

[.net_9.0_Download_Link](https://dotnet.microsoft.com/en-us/download/dotnet/9.0)

[Python_3_Or-Higher_Download_Link](https://www.python.org/downloads/)

[VS_Code](https://code.visualstudio.com/)

**Required Libraries (There may be more that will be prompted to you if needed by VSCode):**

Windows:
```
pip install pandas
pip install openpyxl
```

---
## Running the Scripts

To run the script, we are looking at the maximusV2.py file which is located in Parsing Scripts/Scripts folder. When you run this file (run as a Python file), you will input a CSV file from the seperate_programs_and_degress-CSV_files folder. This will then run the script and output the results into the new_csv.csv file, where you can then look at the University website at the specific major you ran to manually verify if needed (recommended). 

Please see our documentation on the Maximus script to get further details on running it:
[MaximusOperatingGuide](https://docs.google.com/document/d/1lRv_oX56ReinbQxL4zgjadUbcDbfe6tm1i3ecoDD274/edit?usp=sharing)

---

## 🚀 Features

- **Data Standardization**: Automated cleaning and structuring of course catalog data for machine-readability.
- **AI-Driven Insights**: Tools for analyzing course offerings and recommending improvements.
- **Scalable Design**: Flexible architecture designed to expand across multiple university programs.
- **Readability**: Allowing for easier readability for the course catalog data. 

---
