# Sprint-Metrics-Generator
The Sprint Metrics Generator App is a Python application designed to process sprint data, calculate various metrics, and generate enriched data based on the provided input files.

## Features

- Loads sprint data, absences, holidays, and team data from CSV files.
- Calculates working days between two dates, considering holidays and absences.
- Processes sprint data to calculate metrics such as total story points planned/completed, total stories planned/completed, team capacity, sprint duration, completion rates, etc.
- Saves the processed data to an output CSV file with a timestamp.
- Handles cases where optional data files might not be present.

## Prerequisites

- Python 3.x
- Pandas library

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/sprint-data-processing-app.git
   ```

2. Navigate to the project directory:
   ```bash
   cd sprint-data-processing-app
   ```

3. Install the required dependencies:
   ```bash
   pip install pandas
   ```

## Usage

1. Place the input CSV files (`sprint_data.csv`, `absences.csv`, `holidays.csv`, and `team_data.csv`) in the data folder.

2. Run the `app.py` script:

   ```bash
   python app.py

3. The processed data will be saved to the output folder as `sprint_data_<timestamp>.csv`.

## File Structure

- `app.py`: Main Python script for data processing.
- `data/`: Folder containing input CSV files.
- `output/`: Folder where the processed data will be saved.
- `README.md`: This README file.

### Input File Descriptions

- `sprint_data.csv`: Contains sprint-related information such as issue type, key, summary, priority, status, dates, etc.
- `absences.csv`: Contains information about team member absences, including member ID, start date, and end date.
- `holidays.csv`: Contains holiday dates and locations.
- `team_data.csv`: Contains team information such as team ID, member ID, name, and location.

### Sample Output Data

- `sprint_data_<timestamp>.csv`: Processed sprint data with calculated metrics.

## Contributing

Contributions are welcome! Please create a new branch for your changes and submit a pull request.

## License
This project is licensed under the MIT License - see the [LICENSE](https://raw.githubusercontent.com/lopezbruce/Sprint-Metrics-Generator/main/LICENSE) file for details.
