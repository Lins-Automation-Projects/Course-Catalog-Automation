import pandas as pd
import ast
import os 
# Prompt the user to input the file path
input_file_path = input("Enter the path to the CSV file you want to verify: ")

# Check if the file exists
if not os.path.exists(input_file_path):
    print(f"Error: The file '{input_file_path}' does not exist.")
    exit()

# Read the CSV file
df = pd.read_csv(input_file_path)
possible_subgraphs=["prereqToMajorList","reqGenEdsList","majorCommonCoreList","ChooseThesisCapstone","majorRestrictiveElectivesList","majorUnrestrictedElectivesList"]            

#this is a for loop
for i, row in df.iterrows():
    program_name = row["Program"]
    #this is another for loop
    for subgraph in possible_subgraphs:
        required_course_list=row[subgraph]
        #this is a if statment
        if type(required_course_list)==str:
            #this is a try catch block
            try: 
                required_course_list=ast.literal_eval(required_course_list)
            except:
                print(f"Program: {program_name} has error in following string: {required_course_list}")

