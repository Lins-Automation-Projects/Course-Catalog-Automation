# %% [markdown]
# # Maximu (Main Authomation Script)
# 
# This is version 2.0 of the main automation script with some key updates and new capabilities. Changes made are:
# - Description Categorization 
# 
# Script Purpose:
# 
# This script processes the main ISRS dataset to generate an optimized and well-structured dataset that effectively organizes course content.
# 
# Step 1: Load the data

# %%
import pandas as pd

def load_csv_to_dataframe(file_path):
    """
    Loads a CSV file into a Pandas DataFrame.
    
    Parameters:
    file_path (str): The path to the CSV file.
    
    Returns:
    pd.DataFrame: A DataFrame containing the CSV data.
    """
    try:
        df = pd.read_csv(file_path)
        print("CSV file loaded successfully.")
        return df
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        return None

# Ask the user to input the file path
file_path = input("Enter the full file path of the CSV file: ")
main_record = load_csv_to_dataframe(file_path)

# %% [markdown]
# Change Naming of the Program in accordance to defined synax

# %%
# Modify ProgramName to include Degree and EmphasisName when applicable
def update_program_name(row):
    if pd.notna(row['EmphasisName']):
        return f"{row['ProgramName']} ({row['Degree']}) {row['EmphasisName']}"
    return f"{row['ProgramName']} ({row['Degree']})"

main_record['ProgramName'] = main_record.apply(update_program_name, axis=1)



# %% [markdown]
# Step 2: Check the existence of PreReqToMajor 

# %%

#TODO remove all this
# Create new DataFrame with required columns
new_df = pd.DataFrame(columns=["Program", "hasPrereqToMajor", "prereqToMajorList"])

has_prereq_to_major = False
# Process each unique program from main_record
for program in main_record["ProgramName"].unique():
    # Extract description for the program
    program_description = main_record.loc[main_record["ProgramName"] == program, "Description"].astype(str).tolist()

    # Check if "Prerequisites to the Major" exists in the description
    has_prereq_to_major = any("Prerequisites to the Major" in desc for desc in program_description)

    # Append the program details to new_df
    new_df = pd.concat([new_df, pd.DataFrame([{
        "Program": program,
        "hasPrereqToMajor": has_prereq_to_major,
    }])], ignore_index=True)



# %% [markdown]
# Step 3 If PreReqs Exist create a list of PreReqs

# %%
import pandas as pd
import re
import ast

def clean_credit_list(credit_list):
    """
    Cleans the credit list by:
    - Removing category notes from 'credits_X_CategoryNote', keeping only 'credits_X'.
    - If 'credits_unknown' is detected, returns only the course names.
    - Handles nested lists represented as strings and converts them to actual lists.

    Args:
        credit_list (list of lists or list of strings): A list where each sublist starts with a 'credits_X_CategoryNote' string.

    Returns:
        list: A cleaned list with properly formatted course data.
    """
    cleaned_list = []
    
    for sublist in credit_list:
        if isinstance(sublist, str):  
            try:
                sublist = ast.literal_eval(sublist)  # Convert string representation to a list
            except (SyntaxError, ValueError):
                continue  # Skip invalid entries

        if isinstance(sublist, list) and sublist:  # Ensure valid list
            if sublist[0] == 'credits_unknown':  
                cleaned_list.extend(sublist[1:])  # Extract only course names
            
            else:
                parts = sublist[0].split('_')
                cleaned_credit = parts[0] + "_" + parts[1] if len(parts) > 1 else sublist[0]
                cleaned_list.append([cleaned_credit] + sublist[1:])  # Keep 'credits_X' format
    
    return cleaned_list



# Function to extract credit labels with category notes
def extract_credits(description, category_note):
    """
    Extracts the first number from a 'Choose X Credit(s)' description and appends category notes to the label.
    
    Args:
        description (str): The input string containing the credit description.
        category_note (str): The category note to append for distinction.
        
    Returns:
        str: A string in the format 'credits_X_categorynote' if category note exists,
             otherwise 'credits_X'. Returns 'credits_unknown' if no number is found.
    """
    match = re.search(r'Choose\s*(\d+)', str(description))
    
    if match:
        credits = match.group(1)
        category_suffix = f"_{category_note}" if category_note else ""
        return f'credits_{credits}{category_suffix}'
    else:
        return 'credits_unknown'

# Add a new column 'hasPrereqToMajor' to new_df without re-creating it
new_df["hasPrereqToMajor"] = False

# Define keyword for prerequisites to the major
prereq_to_major_keyword = "Prerequisites to the Major"

# Process each unique program from main_record
for index, row in new_df.iterrows():
    program = row["Program"]

    # Extract description for the program
    program_description = main_record.loc[main_record["ProgramName"] == program, "Description"].astype(str).tolist()

    # Check if the prerequisite phrase exists in the description
    has_prereq_to_major = any(prereq_to_major_keyword in desc for desc in program_description)

    # Update the new_df with the new column value
    new_df.at[index, "hasPrereqToMajor"] = has_prereq_to_major

# --- PART 2: Extract Prerequisites to the Major Courses ---

# Ensure the new column 'prereqToMajorList' exists in new_df
new_df["prereqToMajorList"] = None

# Process only the programs where hasPrereqToMajor is True
for index, row in new_df.iterrows():
    if row["hasPrereqToMajor"]:
        # Extract relevant rows from main_record where description contains "Prerequisites to the Major"
        prereq_rows = main_record[
            main_record["Description"].astype(str).str.contains(prereq_to_major_keyword, na=False)
        ]

        prereq_list = []  # List to store processed prerequisite courses

        for _, prereq_row in prereq_rows.iterrows():
            subject_course = f"{prereq_row['SubjectAbbreviation']} {prereq_row['CourseNumber']}"

            # Get category note, ensuring it's a string and removing extra spaces
            category_note = str(prereq_row["Group_CategoryNotes"]).strip() if pd.notna(prereq_row["Group_CategoryNotes"]) else ""

            # Use extract_credits function to determine credit label with category note
            credit_label = extract_credits(prereq_row["GroupCredits"], category_note)

            # Check if this credit label already exists in the list
            found = False
            for prereq_entry in prereq_list:
                if prereq_entry[0] == credit_label:
                    prereq_entry.append(subject_course)
                    found = True
                    break

            if not found:
                prereq_list.append([credit_label, subject_course])

        # Update new_df with the formatted prerequisite list
        new_df.at[index, "prereqToMajorList"] = clean_credit_list(prereq_list)


# %% [markdown]
# Step 4 Check for Gen Eds

# %%
#TODO remove all this 

# Add a new column 'hasReqGenEds' to new_df without re-creating it
new_df["hasReqGenEds"] = False


hasReqGenEds = False
# Process each unique program from main_record
for index, row in new_df.iterrows():
    program = row["Program"]

    # Extract description for the program
    program_description = main_record.loc[main_record["ProgramName"] == program, "Description"].astype(str).tolist()

    # Check if "Required General Education" exists in the description
    has_req_gen_eds = any("Required General Education" in desc for desc in program_description)
    has_req_gen_eds =  any("General Electives" in desc for desc in main_record['ProgramName'])

    # Update the new_df with the new column value
    new_df.at[index, "hasReqGenEds"] = has_req_gen_eds

# %% [markdown]
# Step 6 Create the list of Gen Eds if it exists

# %%
# Add a new column 'hasReqGenEds' to new_df without re-creating it
new_df["hasReqGenEds"] = False

# Define keywords for required general education courses
req_gen_eds_keywords = ["Required General Education", "General Electives"]

# Process each unique program from main_record
for index, row in new_df.iterrows():
    program = row["Program"]

    # Extract description for the program
    program_description = main_record.loc[main_record["ProgramName"] == program, "Description"].astype(str).tolist()

    # Check if any general education phrases exist in the description
    has_req_gen_eds = any(
        any(keyword in desc for keyword in req_gen_eds_keywords) for desc in program_description
    )

    # Update the new_df with the new column value
    new_df.at[index, "hasReqGenEds"] = has_req_gen_eds

# --- PART 2: Extract Required General Education Courses ---

# Ensure the new column 'reqGenEdsList' exists in new_df
new_df["reqGenEdsList"] = None

# Process only the programs where hasReqGenEds is True
for index, row in new_df.iterrows():
    if row["hasReqGenEds"]:
        # Extract relevant rows from main_record where description contains required general education phrases
        gen_ed_rows = main_record[
            main_record["Description"].astype(str).str.contains('|'.join(req_gen_eds_keywords), na=False)
        ]
        
        gen_ed_list = []  # List to store processed general education courses
        
        for _, gen_ed_row in gen_ed_rows.iterrows():
            subject_course = f"{gen_ed_row['SubjectAbbreviation']} {gen_ed_row['CourseNumber']}"
            
            # Get category note, ensuring it's a string and removing extra spaces
            category_note = str(gen_ed_row["Group_CategoryNotes"]).strip() if pd.notna(gen_ed_row["Group_CategoryNotes"]) else ""

            # Use extract_credits function to determine credit label with category note
            credit_label = extract_credits(gen_ed_row["GroupCredits"], category_note)

            # Check if this credit label already exists in the list
            found = False
            for gen_ed_entry in gen_ed_list:
                if gen_ed_entry[0] == credit_label:
                    gen_ed_entry.append(subject_course)
                    found = True
                    break

            if not found:
                gen_ed_list.append([credit_label, subject_course])

        # Update new_df with the formatted general education list
        new_df.at[index, "reqGenEdsList"] = clean_credit_list(gen_ed_list)


# %% [markdown]
# Step 7 Check for Major Common Core and Compliling a list of major courses

# %%
import pandas as pd

# Add a new column 'hasMajorCommonCore' to new_df without re-creating it
new_df["hasMajorCommonCore"] = False

# Define keywords for major common core courses
major_common_core_keywords = [
    "Major Common Core", "Common Core", "Emphasis Common Core",
    "Major Emphasis", "Major EmphasisHUMAN RESOURCE MANAGEMENT"
]

# Process each unique program from main_record
for index, row in new_df.iterrows():
    program = row["Program"]

    # Extract descriptions for the program
    program_descriptions = main_record.loc[main_record["ProgramName"] == program, "Description"].astype(str).tolist()

    # Check if any of the major common core phrases exist in any description
    has_major_common_core = any(
        any(keyword in desc for keyword in major_common_core_keywords) for desc in program_descriptions
    )

    # Update new_df with the new column value
    new_df.at[index, "hasMajorCommonCore"] = has_major_common_core

# --- PART 2: Extract Major Common Core Courses ---

# Ensure the new column 'majorCommonCoreList' exists in new_df
new_df["majorCommonCoreList"] = None

# Process only the programs where hasMajorCommonCore is True
for index, row in new_df.iterrows():
    if row["hasMajorCommonCore"]:
        # Extract relevant rows from main_record where the description contains any of the major common core phrases
        common_core_rows = main_record[
            main_record["Description"].astype(str).apply(
                lambda desc: any(keyword in desc for keyword in major_common_core_keywords)
            )
        ]
        
        common_core_list = []  # List to store processed common core courses
        
        for _, common_core_row in common_core_rows.iterrows():
            subject_course = f"{common_core_row['SubjectAbbreviation']} {common_core_row['CourseNumber']}"
            
            # Get category note, ensuring it's a string and removing extra spaces
            category_note = str(common_core_row["Group_CategoryNotes"]).strip() if pd.notna(common_core_row["Group_CategoryNotes"]) else ""

            # Use extract_credits function to determine credit label with category note
            credit_label = extract_credits(common_core_row["GroupCredits"], category_note)

            # Check if this credit label already exists in the list
            found = False
            for core_entry in common_core_list:
                if core_entry[0] == credit_label:
                    core_entry.append(subject_course)
                    found = True
                    break

            if not found:
                common_core_list.append([credit_label, subject_course])

        # Update new_df with the formatted common core list
        new_df.at[index, "majorCommonCoreList"] = clean_credit_list(common_core_list)


# %% [markdown]
# Step 8 Check for Thesis Capstone and Populate List Accordingly

# %%
import pandas as pd
import re

# Add a new column 'hasThesisCapstone' to new_df without re-creating it
new_df["hasThesisCapstone"] = False

# Define keyword for thesis/capstone courses
thesis_capstone_keyword = "Capstone Course"

# Process each unique program from main_record
for index, row in new_df.iterrows():
    program = row["Program"]

    # Extract description for the program
    program_description = main_record.loc[main_record["ProgramName"] == program, "Description"].astype(str).tolist()

    # Check if "Capstone Course" exists in the description
    has_thesis_capstone = any(thesis_capstone_keyword in desc for desc in program_description)

    # Update the new_df with the new column value
    new_df.at[index, "hasThesisCapstone"] = has_thesis_capstone

# --- PART 2: Extract Capstone Courses ---

# Ensure the new column 'ChooseThesisCapstone' exists in new_df
new_df["ChooseThesisCapstone"] = None

# Process only the programs where hasThesisCapstone is True
for index, row in new_df.iterrows():
    if row["hasThesisCapstone"]:
        # Extract relevant rows from main_record where description contains "Capstone Course"
        capstone_rows = main_record[
            main_record["Description"].astype(str).str.contains(thesis_capstone_keyword, na=False)
        ]
        
        capstone_list = []  # List to store processed capstone courses
        
        for _, capstone_row in capstone_rows.iterrows():
            subject_course = f"{capstone_row['SubjectAbbreviation']} {capstone_row['CourseNumber']}"
            
            # Get category note, ensuring it's a string and removing extra spaces
            category_note = str(capstone_row["Group_CategoryNotes"]).strip() if pd.notna(capstone_row["Group_CategoryNotes"]) else ""

            # Use extract_credits function to determine credit label with category note
            credit_label = extract_credits(capstone_row["GroupCredits"], category_note)

            # Check if this credit label already exists in the list
            found = False
            for capstone_entry in capstone_list:
                if capstone_entry[0] == credit_label:
                    capstone_entry.append(subject_course)
                    found = True
                    break

            if not found:
                capstone_list.append([credit_label, subject_course])

        # Update new_df with the formatted capstone list
        new_df.at[index, "ChooseThesisCapstone"] = clean_credit_list(capstone_list)


# %% [markdown]
# Step 9 Check for Major Restricted Electives and Populate List Accordingly

# %%


# Add a new column 'hasMajorRestrictiveElectives' to new_df without re-creating it
new_df["hasMajorRestrictiveElectives"] = False

# Define keywords for restricted electives
major_restrictive_electives_keywords = [
    "Major Restricted Electives", "Emphasis Restricted Electives", "Restricted Electives"
]

# Process each unique program from main_record
for index, row in new_df.iterrows():
    program = row["Program"]

    # Extract description for the program
    program_description = main_record.loc[main_record["ProgramName"] == program, "Description"].astype(str).tolist()

    # Check if any restricted electives phrases exist in the description
    has_major_restrictive_electives = any(
        any(keyword in desc for keyword in major_restrictive_electives_keywords) for desc in program_description
    )

    # Update the new_df with the new column value
    new_df.at[index, "hasMajorRestrictiveElectives"] = has_major_restrictive_electives

# --- PART 2: Extract Major Restricted Electives Courses ---

# Ensure the new column 'majorRestrictiveElectivesList' exists in new_df
new_df["majorRestrictiveElectivesList"] = None

# Process only the programs where hasMajorRestrictiveElectives is True
for index, row in new_df.iterrows():
    if row["hasMajorRestrictiveElectives"]:
        # Extract relevant rows from main_record where description contains any restricted elective phrases
        restricted_electives_rows = main_record[
            main_record["Description"].astype(str).str.contains('|'.join(major_restrictive_electives_keywords), na=False)
        ]

        restricted_electives_list = []  # List to store processed elective courses
        
        for _, restricted_electives_row in restricted_electives_rows.iterrows():
            subject_course = f"{restricted_electives_row['SubjectAbbreviation']} {restricted_electives_row['CourseNumber']}"
            
            # Get category note, ensuring it's a string and removing extra spaces
            category_note = str(restricted_electives_row["Group_CategoryNotes"]).strip() if pd.notna(restricted_electives_row["Group_CategoryNotes"]) else ""

            # Use extract_credits function to determine credit label with category note
            credit_label = extract_credits(restricted_electives_row["GroupCredits"], category_note)

            # Check if this credit label already exists in the list
            found = False
            for elective_entry in restricted_electives_list:
                if elective_entry[0] == credit_label:
                    elective_entry.append(subject_course)
                    found = True
                    break
            
            if not found:
                restricted_electives_list.append([credit_label, subject_course])
        
        # Update new_df with the formatted elective list
        
        new_df.at[index, "majorRestrictiveElectivesList"] = clean_credit_list(restricted_electives_list)


# %% [markdown]
# Step 10 Check for Major Unresticted Electives

# %%
import pandas as pd
import re

# Add a new column 'hasMajorUnrestrictedElectives' to new_df without re-creating it
new_df["hasMajorUnrestrictedElectives"] = False

# Define keywords for unrestricted electives
major_unrestricted_electives_keywords = [
    "Major Unrestricted Electives", "Emphasis Unrestricted Electives", "Major Unrestricted"
]

# Process each unique program from main_record
for index, row in new_df.iterrows():
    program = row["Program"]

    # Extract description for the program
    program_description = main_record.loc[main_record["ProgramName"] == program, "Description"].astype(str).tolist()

    # Check if any unrestricted electives phrases exist in the description
    has_major_unrestricted_electives = any(
        any(keyword in desc for keyword in major_unrestricted_electives_keywords) for desc in program_description
    )

    # Update the new_df with the new column value
    new_df.at[index, "hasMajorUnrestrictedElectives"] = has_major_unrestricted_electives

# --- PART 2: Extract Major Unrestricted Electives Courses ---

# Ensure the new column 'majorUnrestrictedElectivesList' exists in new_df
new_df["majorUnrestrictedElectivesList"] = None

# Process only the programs where hasMajorUnrestrictedElectives is True
for index, row in new_df.iterrows():
    if row["hasMajorUnrestrictedElectives"]:
        # Extract relevant rows from main_record where description contains any unrestricted elective phrases
        unrestricted_electives_rows = main_record[
            main_record["Description"].astype(str).str.contains('|'.join(major_unrestricted_electives_keywords), na=False)
        ]

        unrestricted_electives_list = []  # List to store processed elective courses
        
        for _, unrestricted_electives_row in unrestricted_electives_rows.iterrows():
            subject_course = f"{unrestricted_electives_row['SubjectAbbreviation']} {unrestricted_electives_row['CourseNumber']}"
            
            # Get category note, ensuring it's a string and removing extra spaces
            category_note = str(unrestricted_electives_row["Group_CategoryNotes"]).strip() if pd.notna(unrestricted_electives_row["Group_CategoryNotes"]) else ""

            # Use extract_credits function to determine credit label with category note
            credit_label = extract_credits(unrestricted_electives_row["GroupCredits"], category_note)

            # Check if this credit label already exists in the list
            found = False
            for elective_entry in unrestricted_electives_list:
                if elective_entry[0] == credit_label:
                    elective_entry.append(subject_course)
                    found = True
                    break
            
            if not found:
                unrestricted_electives_list.append([credit_label, subject_course])
        
        # Update new_df with the formatted elective list
        new_df.at[index, "majorUnrestrictedElectivesList"] = clean_credit_list(unrestricted_electives_list)


# %% [markdown]
# Step 11 Check for other Gradrequirements and create a list for that

# %%
import pandas as pd
import re

# Add a new column 'hasOtherGradReq' to new_df without re-creating it
new_df["hasOtherGradReq"] = False

# Define keywords for other graduation requirements
other_grad_req_keywords = [
    "Other Graduation Requirements", "Research/Methods Course(s)"
]

# Process each unique program from main_record
for index, row in new_df.iterrows():
    program = row["Program"]

    # Extract description for the program
    program_description = main_record.loc[main_record["ProgramName"] == program, "Description"].astype(str).tolist()

    # Check if any relevant graduation requirement phrases exist in the description
    has_other_grad_req = any(
        any(keyword in desc for keyword in other_grad_req_keywords) for desc in program_description
    )

    # Update the new_df with the new column value
    new_df.at[index, "hasOtherGradReq"] = has_other_grad_req

# --- PART 2: Extract Other Graduation Requirements ---

# Ensure the new column 'otherGradReq' exists in new_df
new_df["otherGradReq"] = None

# Process only the programs where hasOtherGradReq is True
for index, row in new_df.iterrows():
    if row["hasOtherGradReq"]:
        # Extract relevant rows from main_record where description contains relevant graduation requirement phrases
        grad_req_rows = main_record[
            main_record["Description"].astype(str).str.contains('|'.join(other_grad_req_keywords), na=False)
        ]

        grad_req_list = []  # List to store processed graduation requirement courses
        
        for _, grad_req_row in grad_req_rows.iterrows():
            subject_course = f"{grad_req_row['SubjectAbbreviation']} {grad_req_row['CourseNumber']}"
            
            # Get category note, ensuring it's a string and removing extra spaces
            category_note = str(grad_req_row["Group_CategoryNotes"]).strip() if pd.notna(grad_req_row["Group_CategoryNotes"]) else ""

            # Use extract_credits function to determine credit label with category note
            credit_label = extract_credits(grad_req_row["GroupCredits"], category_note)

            # Check if this credit label already exists in the list
            found = False
            for grad_req_entry in grad_req_list:
                if grad_req_entry[0] == credit_label:
                    grad_req_entry.append(subject_course)
                    found = True
                    break
            
            if not found:
                grad_req_list.append([credit_label, subject_course])
        
        # Update new_df with the formatted graduation requirement list
        new_df.at[index, "otherGradReq"] = clean_credit_list(grad_req_list)


# %% [markdown]
# Add the dataframe to the csv

# %%
import os

output_file = "Parsing Scripts/Scripts/new_csv.csv" 

# Append to existing CSV or create a new one if it doesn't exist
if os.path.exists(output_file):
    new_df.to_csv(output_file, mode='a', header=False, index=False)
else:
    new_df.to_csv(output_file, mode='w', header=True, index=False)

print(f"Data appended to {output_file} successfully!")