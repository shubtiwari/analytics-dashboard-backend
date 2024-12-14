from collections import defaultdict
from datetime import datetime
from .database.student import STUDENT_FEE_COLLECTION

def split_fiscal_year(year):
    # Split the given year string into start and end years
    start_year, end_year = year.split('-')
    
    # Handle cases where end_year might be two digits
    if len(end_year) == 2:
        end_year = f"20{end_year}"
    
    # Format the start and end dates in yyyy-mm-dd
    start = f"{start_year}-04-01"
    end = f"{end_year}-03-31"
    
    return start, end

def get_current_fiscal_year():
    # Get the current year and month
    today = datetime.today()
    current_year = today.year
    current_month = today.month

    # Determine the fiscal year based on the current month
    if current_month >= 4:  # If current month is April or later, start year is the current year
        start_year = current_year
        end_year = current_year + 1
    else:  # If current month is before April, start year is the previous year
        start_year = current_year - 1
        end_year = current_year

    # Format the fiscal year start and end dates in yyyy-mm-dd
    start_date = f"{start_year}-04-01"
    end_date = f"{end_year}-03-31"

    return start_date, end_date


def generate_monthly_data(start_date, end_date):
    # Convert start_date and end_date to datetime objects
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    
    # List to hold monthly data dictionaries
    monthly_data_list = {}
    
    # Iterate over the months in the range from start_date to end_date
    current_date = start_date
    while current_date <= end_date:
        month_key = f"{current_date.year}-{current_date.month:02d}"
        monthly_data = {'expected_amount': 0, 'collected_amount': 0}
        
        # Add the month_key and monthly data to the list
        monthly_data_list[month_key]= monthly_data
        
        # Move to the next month
        current_date = datetime(current_date.year + (current_date.month // 12), (current_date.month % 12) + 1, 1)

    return monthly_data_list

def filter_collection_data(collector_id, grade=None, year=None):
    """
    Filters the data based on collector_id, grade, and year.
    Aggregates and returns the total collected amount, unpaid amount, monthly data, product-wise collections,
    and the number of students.
    Args:
        collector_id (int): The collector ID to filter by.
        grade (str): The grade to filter by.
        year (str): The year to filter by.
    Returns:
        dict: Aggregated response with total collected amount, unpaid amount, monthly data, product-wise collections,
              and the number of students.
    """
    print(collector_id, grade, year)
    data = STUDENT_FEE_COLLECTION
    filtered_data = []
    for entry in data:
        # Filter by collector_id and grade
        if int(entry['collector_id']) == int(collector_id) and (not grade or entry['grade'] == grade):
                filtered_data.append(entry)
    
    print(filtered_data)
    
    start_date, end_date=get_current_fiscal_year()
    if year:
        start_date, end_date=split_fiscal_year(year)


    updated_filtered_data = []
    for entry in filtered_data:
        if int(entry['collector_id']) == int(collector_id):
            if start_date<=entry['paid_date'] and entry['paid_date']<=end_date:
                updated_filtered_data.append(entry)

    filtered_data=updated_filtered_data

    print(filtered_data)
    # Initialize aggregates
    total_collected_amount = 0
    total_expected_amount = 0
    monthly_data = defaultdict(lambda: {'expected_amount': 0, 'collected_amount': 0})
    product_wise_data = defaultdict(int)
    unique_students = set()
    # # If no data is found for the provided year, we need to get the last 12 months data
    # if not filtered_data:
    #     current_date = datetime.now()
    #     start_month = 4  # Start from April
    #     # Generate the last 12 months including months from April to March
    #     months = [(current_date.year - 1, start_month + i) if (start_month + i) > 12 else (current_date.year, start_month + i) for i in range(12)]
    #     # Add zero values for months without data
    #     for month in months:
    #         month_key = f"{month[0]}-{month[1]:02d}"
    #         monthly_data[month_key] = {'expected_amount': 0, 'collected_amount': 0}


    monthly_data = generate_monthly_data(start_date, end_date)
    # Process each entry in the filtered data
    for entry in filtered_data:
        total_collected_amount += entry['paid_amount']
        total_expected_amount += entry['expected_fees']
        # Parse the month from the paid_date
        month = datetime.strptime(entry['paid_date'], '%Y-%m-%d').strftime('%Y-%m')
        # Update monthly data
        monthly_data[month]['expected_amount'] += entry['expected_fees']
        monthly_data[month]['collected_amount'] += entry['paid_amount']
        # Update product-wise data
        product_wise_data[entry['product']] += entry['paid_amount']
        # Add student_id to unique_students
        unique_students.add(entry['student_id'])
    
    # Calculate unpaid amount
    unpaid_amount = total_expected_amount - total_collected_amount
    # Format the response
    response = {
        'total_collected_amount': total_collected_amount,
        'unpaid_amount': unpaid_amount,
        'monthly_data': dict(monthly_data),
        'product_wise_collected_amount': dict(product_wise_data),
        'number_of_students': len(unique_students)
    }
    return response