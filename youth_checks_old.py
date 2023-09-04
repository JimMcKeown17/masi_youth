import pandas as pd
import re

# Import CSV and create initial DFs
all_youth = pd.read_csv("20230707_youth.csv", dtype={'RSA ID Number': str})
youth = all_youth[all_youth['Employment Status'] == 'Active'].copy()
active_youth = youth['Employment Status'].count()
total_youth = all_youth['Employee Number'].nunique()

# List of columns that should not be blank
required_cols = ['Employee Number', 'Employment Status', 'Mentor', 'Gender', 'Race',
                 'Site Placement', 'First Names', 'Last Name', 'Job Title',
                 'Start Date', 'Attachment: ID Document', 'Attachment: Bank Details',
                 'Attachment: MOU/Contract', 'Attachment: Info Sheet',
                 'Attachment: SARS Notice of registration', 'Cell Phone Number', 'Email', 'Income Tax Number']

# Add new columns for error flag and description
youth['error_flag'] = 0
youth['error_description'] = ''

# Iterate over the required columns
for col in required_cols:
    # Find rows where this column is blank
    missing = youth[col].isnull()

    # Update error flag and description for these rows
    youth.loc[missing, 'error_flag'] = 1
    youth.loc[missing, 'error_description'] += col + ' is missing; '

# List of columns to check for duplicates
duplicate_cols = ['Employee Number', 'Account number', 'RSA ID Number']

for col in duplicate_cols:
    # Drop the empty/missing values before checking for duplicates
    duplicates = youth[youth[col].notna() & (youth[col] != '')][col].duplicated(keep=False)

    if duplicates.sum() > 0:
        youth.loc[duplicates, 'error_flag'] = 1
        youth.loc[duplicates, 'error_description'] = youth.loc[duplicates, 'error_description'] + f'; Duplicate {col}'

# Add a combined check for 'RSA ID Number' and 'Foreign ID Number'
no_id = youth[(youth['RSA ID Number'].isna() | (youth['RSA ID Number'] == '')) &
              (youth['Foreign ID Number'].isna() | (youth['Foreign ID Number'] == ''))].index

if len(no_id) > 0:
    youth.loc[no_id, 'error_flag'] = 1
    youth.loc[no_id, 'error_description'] = youth.loc[no_id, 'error_description'] + '; RSA ID Number and Foreign ID Number both blank'

# Define the columns that should be dates
date_cols = ['DOB', 'Start Date']

# Define the columns that should contain certain characters
contains_checks = {'Email': '@'}

# Iterate over the date columns
for col in date_cols:
    # Convert the column to the date format
    youth[col] = pd.to_datetime(youth[col], errors='coerce')

    # Find rows where this conversion resulted in NaT (not a time)
    bad_dates = youth[col].isnull()

    # Update error flag and description for these rows
    youth.loc[bad_dates, 'error_flag'] = 1
    youth.loc[bad_dates, 'error_description'] += col + ' is not a valid date; '

# 'End Date' should be a proper date only for non-active employees
non_active = youth['Employment Status'] != 'Active'
youth.loc[non_active, 'End Date'] = pd.to_datetime(youth.loc[non_active, 'End Date'], errors='coerce')

# Find rows where this conversion resulted in NaT (not a time)
bad_dates_non_active = youth.loc[non_active, 'End Date'].isnull()

# Update error flag and description for these rows
youth.loc[bad_dates_non_active & non_active, 'error_flag'] = 1
youth.loc[bad_dates_non_active & non_active, 'error_description'] += 'End Date' + ' is not a valid date; '

# Iterate over the contains check columns
for col, char in contains_checks.items():
    # Find rows where this column does not contain the required character
    missing_char = ~youth[col].apply(lambda x: char in str(x))

    # Update error flag and description for these rows
    youth.loc[missing_char, 'error_flag'] = 1
    youth.loc[missing_char, 'error_description'] += col + ' does not contain ' + char + '; '

# If 'Employment Status' is not 'Active', there must be an 'End Date'
inactive_without_enddate = (youth['Employment Status'] != 'Active') & youth['End Date'].isna()
if inactive_without_enddate.sum() > 0:
    youth.loc[inactive_without_enddate, 'error_flag'] = 1
    youth.loc[inactive_without_enddate, 'error_description'] = youth.loc[inactive_without_enddate, 'error_description'] + '; Inactive employment status without End Date'

# If there's an 'End Date', there must be a 'Reason for Leaving' value
end_date_without_reason = youth['End Date'].notna() & youth['Reason for Leaving'].isna()
if end_date_without_reason.sum() > 0:
    youth.loc[end_date_without_reason, 'error_flag'] = 1
    youth.loc[end_date_without_reason, 'error_description'] = youth.loc[end_date_without_reason, 'error_description'] + '; End Date present but no Reason for Leaving'

from datetime import datetime

# Assuming DOB is in the format 'yyyy-mm-dd'
youth['DOB'] = pd.to_datetime(youth['DOB'])

# Calculate age
now = pd.Timestamp(datetime.now())
youth['Age'] = (now - youth['DOB']).astype('<m8[Y]')

# Check if anyone is over 35 or under 18
age_invalid = (youth['Age'] > 35) | (youth['Age'] < 18)
if age_invalid.sum() > 0:
    youth.loc[age_invalid, 'error_flag'] = 1
    youth.loc[age_invalid, 'error_description'] = youth.loc[age_invalid, 'error_description'] + '; Age is either over 35 or under 18'

# After all the checks
youth_errors = youth[youth['error_flag'] == 1][['Employee Number', 'error_description']]
youth_errors.to_csv('youth_errors.csv', index=False)

# Update the errors DataFrame and output it to a CSV again
errors = youth[youth['error_flag'] == 1]
errors.to_csv('youth_errors.csv', index=False)




