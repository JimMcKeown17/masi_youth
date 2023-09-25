import pandas as pd
import openpyxl

# Total hours worked
# % of days on time
# # days worked per month
# Flagging people that have worked more than their allocated hours
# Flagging people that are habitually late

# Load the data
df = pd.read_excel("Schools Attendance Register - 19.08.2023.xlsx", sheet_name="Timesheet", skiprows=1)

# Extract staff details
staff_details = df.iloc[:, :10]

time_columns = [col for col in df.columns if "Check-in" in col or "Check-out" in col]
checkin_columns = time_columns[::2]
checkout_columns = time_columns[1::2]

# Calculate hours worked
hours_worked = []
for checkin, checkout in zip(checkin_columns, checkout_columns):
    start_delta = df[checkin]
    end_delta = df[checkout]

    # Compute hours with NaN handling
    hours = ((end_delta - start_delta).dt.total_seconds().fillna(0) / 3600)
    hours_worked.append(hours)

hours_df = pd.concat(hours_worked, axis=1)

# Adjust start times
eight_am = pd.to_datetime("08:00:00").time()
for col in checkin_columns:
    df[col] = df[col].apply(lambda x: x if pd.isna(x) or x >= eight_am else eight_am)



# Recalculate hours worked after adjustments
adjusted_hours_worked = []
for checkin, checkout in zip(checkin_columns, checkout_columns):
    hours = ((df[checkout] - df[checkin]).dt.total_seconds().fillna(0) / 3600)
    adjusted_hours_worked.append(hours)

adjusted_hours_df = pd.concat(adjusted_hours_worked, axis=1)

# Extract dates for column renaming
date_columns = df.columns[10::2]
dates = df.loc[0, date_columns].tolist()
adjusted_hours_df.columns = dates

# Count days worked
days_worked = (adjusted_hours_df > 0).sum(axis=1)

# Combine results and rename columns
result_df_with_dates = pd.concat([staff_details, adjusted_hours_df, days_worked], axis=1)
result_df_with_dates.rename(columns={0: 'Total Days Worked'}, inplace=True)

# Save results (Optional)
result_df_with_dates.to_csv("hours_results.csv", index=False)
