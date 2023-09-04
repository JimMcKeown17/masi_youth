import pandas as pd
import re
from datetime import datetime

def update_errors(df, condition, error_message):
    df.loc[condition, 'error_flag'] = 1
    df.loc[condition, 'error_description'] += error_message + '; '

def check_required_cols(df, required_cols):
    for col in required_cols:
        missing = df[col].isnull()
        update_errors(df, missing, f'{col} is missing')


def check_duplicates(df, duplicate_cols):
    for col in duplicate_cols:
        # Create a boolean Series with the same index as df
        duplicates = df[col].duplicated(keep=False) & df[col].notna() & (df[col] != '')
        update_errors(df, duplicates, f'Duplicate {col}')

def check_id_numbers(df):
    no_id = df[(df['RSA ID Number'].isna() | (df['RSA ID Number'] == '')) &
               (df['Foreign ID Number'].isna() | (df['Foreign ID Number'] == ''))].index
    update_errors(df, no_id, 'RSA ID Number and Foreign ID Number both blank')

def check_dates(df, date_cols):
    for col in date_cols:
        not_blank = df[col].notna() & (df[col] != '')
        df.loc[not_blank, df.columns[df.columns.get_loc(col)]] = pd.to_datetime(df[not_blank][col], errors='coerce')
        bad_dates = not_blank & df[col].isnull()
        update_errors(df, bad_dates, f'{col} is not a valid date')


def check_contains(df, contains_checks):
    for col, char in contains_checks.items():
        missing_char = ~df[col].apply(lambda x: char in str(x))
        update_errors(df, missing_char, f'{col} does not contain {char}')

def check_employment_status(df):
    inactive_without_enddate = (df['Employment Status'] != 'Active') & df['End Date'].isna()
    update_errors(df, inactive_without_enddate, 'Inactive employment status without End Date')

    end_date_without_reason = df['End Date'].notna() & df['Reason for Leaving'].isna()
    update_errors(df, end_date_without_reason, 'End Date present but no Reason for Leaving')

def check_age(df):
    now = pd.Timestamp(datetime.now())
    df['Age'] = (now - df['DOB']).astype('<m8[Y]')
    age_invalid = (df['Age'] > 35) | (df['Age'] < 18)
    update_errors(df, age_invalid, 'Age is either over 35 or under 18')

def check_end_date(df):
    end_date_filled = df['End Date'].notna()
    invalid_end_date = end_date_filled & (df['End Date'] < df['Start Date'])
    update_errors(df, invalid_end_date, 'End Date is before Start Date')

def check_phone_number(df):
    invalid_phone_number = df['Cell Phone Number'].str.replace('\D', '', regex=True).str.len() != 10
    update_errors(df, invalid_phone_number, 'Cell Phone Number does not contain exactly 10 digits')

def check_rsa_id_number(df):
    df_rsa_id = df['RSA ID Number'].notna() & (df['RSA ID Number'] != '')
    invalid_rsa_id = df_rsa_id & (df['RSA ID Number'].str.len() != 13)
    update_errors(df, invalid_rsa_id, 'RSA ID Number does not contain exactly 13 digits')

def check_data_integrity(df):
    required_cols = ['Employee Number', 'Employment Status', 'Mentor', 'Gender', 'Race',
                 'Site Placement', 'First Names', 'Last Name', 'Job Title',
                 'Start Date', 'Attachment: ID Document', 'Attachment: Bank Details',
                 'Attachment: MOU/Contract', 'Attachment: Info Sheet',
                 'Attachment: SARS Notice of registration', 'Cell Phone Number', 'Email', 'Income Tax Number']
    duplicate_cols = ['Employee Number', 'Account number', 'RSA ID Number']
    date_cols = ['Start Date', 'End Date', 'DOB']
    contains_checks = {'Email': '@'}

    df['error_flag'] = 0
    df['error_description'] = ''

    check_required_cols(df, required_cols)
    check_duplicates(df, duplicate_cols)
    check_id_numbers(df)
    check_dates(df, date_cols)
    check_contains(df, contains_checks)
    check_employment_status(df)
    check_age(df)
    check_end_date(df)
    check_phone_number(df)
    # check_rsa_id_number(df) -- I'll have to fix this; the .csv from airtable removes leading zeros

    return df

def load_data(filename):
    all_youth = pd.read_csv(filename, dtype={'RSA ID Number': str})
    return all_youth[all_youth['Employment Status'] == 'Active'].copy()

def save_errors(df, filename):
    errors = df[df['error_flag'] == 1]
    errors.to_csv(filename, index=False)

def main():
    df = load_data('20230904 - Combined Youth Data.csv')
    df = check_data_integrity(df)
    save_errors(df, 'youth_errors.csv')

if __name__ == '__main__':
    main()
