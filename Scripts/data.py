# OLD WORK FROM PREVIOUS TEAM
# OLD AS OF 12-07-2024

import pandas as pd

# Load the data
isrs_courses = pd.read_csv(r"C:\Users\Araya\Desktop\software & parallel engineering\Undergraduate_Courses.csv")
user_courses = pd.read_csv(r"C:\Users\Araya\Desktop\software & parallel engineering\Final (Sorted and Reformatted).csv")

isrs_courses['SUBJ_COU_NBR'] = isrs_courses['SUBJ_COU_NBR'].str.strip()
user_courses['Course ID'] = user_courses['Course ID'].str.strip()

missing_from_user = isrs_courses[~isrs_courses['SUBJ_COU_NBR'].isin(user_courses['Course ID'])]
missing_from_user = missing_from_user[['SUBJ_COU_NBR']].rename(columns={'SUBJ_COU_NBR': 'Course ID'})
missing_from_user.to_csv(r"C:\Users\Araya\Desktop\software & parallel engineering\Missing_Courses_From_User_List.csv", index=False)

missing_from_isrs = user_courses[~user_courses['Course ID'].isin(isrs_courses['SUBJ_COU_NBR'])]
missing_from_isrs = missing_from_isrs[['Course ID']]
missing_from_isrs.to_csv(r"C:\Users\Araya\Desktop\software & parallel engineering\Missing_Courses_From_ISRS_List.csv", index=False)

print("File saved: 'Missing_Courses_From_User_List.csv'")
print(f"Total missing courses from user list: {len(missing_from_user)}")

print("File saved: 'Missing_Courses_From_ISRS_List.csv'")
print(f"Total missing courses from ISRS list: {len(missing_from_isrs)}")