import pandas as pd
from datetime import datetime
import os

# Define the folder paths
input_folder = 'data'
output_folder = 'output'

# Load the datasets
sprint_data = pd.read_csv(os.path.join(input_folder, 'sprint_data.csv'))

# Attempt to load optional data
try:
    team_data = pd.read_csv(os.path.join(input_folder, 'team_data.csv'))
    team_provided = True
except FileNotFoundError:
    team_provided = False
    print("Team data not provided. Proceeding without team-specific calculations.")

try:
    absences = pd.read_csv(os.path.join(input_folder, 'absences.csv'))
    absences_provided = True
except FileNotFoundError:
    absences_provided = False
    print("Absence data not provided. Proceeding without absence-specific calculations.")

try:
    holidays = pd.read_csv(os.path.join(input_folder, 'holidays.csv'))
    holidays['date'] = pd.to_datetime(holidays['date'])
except FileNotFoundError:
    holidays = pd.DataFrame(columns=['date', 'location'])
    print("Holidays data not provided. Proceeding without holiday-specific calculations.")

# Convert dates in sprint_data to datetime objects
sprint_data['Created date'] = pd.to_datetime(sprint_data['Created date'])
sprint_data['Updated date'] = pd.to_datetime(sprint_data['Updated date'])

def get_applicable_holidays(member_location):
    """
    Filters holidays based on the team member's location.
    
    Args:
        member_location (str): The location of the team member.
        
    Returns:
        pandas.Series: Series containing the applicable holidays' dates.
    """
    country = member_location.split('_')[0]
    applicable_holidays = holidays[(holidays['location'] == 'US') | 
                                   (holidays['location'] == country) | 
                                   (holidays['location'] == member_location)]
    return applicable_holidays['date']

def calculate_working_days(start_date, end_date, member_id=None, member_location=None):
    """
    Calculates the number of working days between two dates, considering holidays and absences.
    
    Args:
        start_date (datetime): The start date.
        end_date (datetime): The end date.
        member_id (str): ID of the team member (default=None).
        member_location (str): Location of the team member (default=None).
        
    Returns:
        int: Number of working days.
    """
    total_days = pd.date_range(start=start_date, end=end_date, freq='B')
    if member_location:
        applicable_holidays = get_applicable_holidays(member_location)
        total_days = total_days[~total_days.isin(applicable_holidays)]
    if absences_provided and member_id is not None:
        member_absences = absences[absences['member_id'] == member_id]
        for _, absence in member_absences.iterrows():
            absence_range = pd.date_range(start=absence['start_date'], end=absence['end_date'], freq='B')
            total_days = total_days.difference(absence_range)
    tuesdays = [day for day in total_days if day.weekday() == 1]
    if tuesdays:
        last_tuesday = max(tuesdays)
        total_days = total_days[total_days != last_tuesday]
    return len(total_days)

# Process sprints considering only initially planned stories
sprint_data['sprint_year'] = sprint_data['First sprint'].str.extract(r'Q[1-4]S[1-4](\d{4})').astype(str)

def parse_date_with_year(date_str, year, is_end_date=False):
    """
    Parses a date string and appends the extracted year. Adjusts the year for end dates that roll over to the next year.
    
    Args:
        date_str (str): Date string in the format 'mm/dd'.
        year (str): Year as a string.
        is_end_date (bool): Flag to indicate if the date is an end date, to adjust year if necessary.
    
    Returns:
        datetime or None: The parsed datetime object if valid, else None.
    """
    if year == 'nan' or not date_str or '/' not in date_str:
        return None
    try:
        # Adjust the year for end dates if necessary
        if is_end_date:
            month = int(date_str.split('/')[0])
            if month == 1:  # Assuming the sprint starts in December and rolls over to January
                year = str(int(year) + 1)
        return datetime.strptime(f"{date_str}/{year}", '%m/%d/%Y')
    except ValueError:
        return None

# Process sprints considering only initially planned stories
sprint_data['sprint_range'] = sprint_data['First sprint'].str.extract(r'(\d{2}/\d{2} to \d{2}/\d{2})')
unique_sprints = sprint_data['sprint_range'].dropna().unique()
processed_data = []

current_date = datetime.now()
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

for sprint in unique_sprints:
    sprint_year = sprint_data[sprint_data['sprint_range'] == sprint]['sprint_year'].iloc[0]
    if sprint_year == 'nan':
        sprint_year = str(sprint_data[sprint_data['sprint_range'] == sprint]['Created date'].dt.year.iloc[0])

    sprint_start, sprint_end = sprint.split(' to ')
    sprint_start_date = parse_date_with_year(sprint_start, sprint_year)
    # Pass True for is_end_date to correctly adjust the year if necessary
    sprint_end_date = parse_date_with_year(sprint_end, sprint_year, is_end_date=True)

    print(sprint_start_date)
    print(sprint_end_date)

    # Skip this sprint if either date is None
    if sprint_start_date is None or sprint_end_date is None:
        continue
    
    if current_date >= sprint_start_date and current_date <= sprint_end_date:
        continue
    
    initially_planned_issues = sprint_data[(sprint_data['Created date'] <= sprint_start_date) & (sprint_data['sprint_range'] == sprint)]
    
    total_story_points_planned = initially_planned_issues[initially_planned_issues['Issue type'] == 'Story']['Story points'].sum()
    total_stories_planned = initially_planned_issues[initially_planned_issues['Issue type'] == 'Story'].shape[0]
    
    total_story_points_done = initially_planned_issues[initially_planned_issues['Status'] == 'Done']['Story points'].sum()
    total_stories_completed = initially_planned_issues[initially_planned_issues['Status'] == 'Done'].shape[0]

    team_capacity = 0
    if team_provided:
        for _, member in team_data.iterrows():
            team_capacity += calculate_working_days(sprint_start_date, sprint_end_date, member['member_id'], member['location'])
    max_capacity = calculate_working_days(sprint_start_date, sprint_end_date) * (len(team_data) if team_provided else 1)
    
    sprint_duration_days = (sprint_end_date - sprint_start_date).days + 1
    sprint_completion_rate = (total_story_points_done / total_story_points_planned) * 100 if total_story_points_planned > 0 else 0
    story_completion_success_rate = (total_stories_completed / total_stories_planned) * 100 if total_stories_planned > 0 else 0

    processed_data.append({
        'Sprint': sprint,
        'Start Date': sprint_start_date.strftime('%Y-%m-%d'),
        'End Date': sprint_end_date.strftime('%Y-%m-%d'),
        'Sprint Duration': sprint_duration_days,
        'Total Story Points Planned': total_story_points_planned,
        'Total Story Points Completed': total_story_points_done,
        'Total Stories Planned': total_stories_planned,
        'Total Stories Completed': total_stories_completed,
        'Team Capacity': team_capacity,
        'Max Possible Capacity': max_capacity,
        'Sprint Completion Rate': sprint_completion_rate,
        'Story Completion Success Rate': story_completion_success_rate
    })

processed_sprint_data = pd.DataFrame(processed_data)

# Make sure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Save the processed data to the output CSV file
output_file_path = f'{output_folder}/sprint_data_{timestamp}.csv'
processed_sprint_data.to_csv(output_file_path, index=False)

print(f"Enriched sprint data has been saved to '{output_file_path}'.")
