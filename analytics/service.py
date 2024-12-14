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

def filter_collection_data(collector_id, grade=None, year=None, range_start_date=None, range_end_date=None):
    """
    Filters the data based on collector_id, grade, year, and date_range.
    Aggregates and returns the total collected amount, unpaid amount, monthly data, product-wise collections,
    and the number of students, along with the percentage of students who paid on time.
    Args:
        collector_id (int): The collector ID to filter by.
        grade (str): The grade to filter by.
        year (str): The year to filter by.
        date_range (tuple): The date range to filter by (start_date, end_date).
    Returns:
        dict: Aggregated response with total collected amount, unpaid amount, monthly data, product-wise collections,
              and the number of students, along with the on-time payment percentage.
    """
    data = STUDENT_FEE_COLLECTION
    filtered_data = []
    
    # Filter by collector_id, grade, and year
    for entry in data:
        if int(entry['collector_id']) == int(collector_id) and (not grade or entry['grade'] == grade):
            filtered_data.append(entry)
    
    
    # Use fiscal year logic or passed year for date range
    start_date, end_date = get_current_fiscal_year()
    if year:
        start_date, end_date = split_fiscal_year(year)

    if range_start_date and start_date< range_start_date:
        start_date = range_start_date
    
    if range_end_date and end_date > range_end_date:
        end_date = range_end_date

    updated_filtered_data = []
    for entry in filtered_data:
        if int(entry['collector_id']) == int(collector_id):
            if not year or entry['year'] == year:
                updated_filtered_data.append(entry)

    filtered_data = updated_filtered_data
    updated_filtered_data = []
    for entry in filtered_data:
        if int(entry['collector_id']) == int(collector_id):
            if (not range_start_date or not range_end_date) or range_start_date <= entry['paid_date'] <= range_end_date:
                updated_filtered_data.append(entry)

    filtered_data = updated_filtered_data
    print("========FILTER 3 ======", filtered_data)
    # Initialize aggregates
    total_collected_amount = 0
    total_expected_amount = 0
    monthly_data = defaultdict(lambda: {'expected_amount': 0, 'collected_amount': 0})
    product_wise_data = defaultdict(int)
    unique_students = set()
    on_time_payment_count = 0  # Track students who paid on time

    # Generate monthly data
    monthly_data = generate_monthly_data(start_date, end_date)

    # Process each entry in the filtered data
    for entry in filtered_data:
        total_collected_amount += entry['paid_amount']
        total_expected_amount += entry['expected_fees']
        
        # Parse the month from the paid_date
        print("==== PAID DATE =====", entry["paid_date"])
        month = datetime.strptime(entry['paid_date'], '%Y-%m-%d').strftime('%Y-%m')
        
        if month in monthly_data:
            # Update monthly data
            monthly_data[month]['expected_amount'] += entry['expected_fees']
            monthly_data[month]['collected_amount'] += entry['paid_amount']
        
        # Update product-wise data
        product_wise_data[entry['product']] += entry['paid_amount']
        
        # Add student_id to unique_students
        unique_students.add(entry['student_id'])
        
        # Check if the payment was made on time (paid_date <= due_date)
        paid_date = datetime.strptime(entry['paid_date'], "%Y-%m-%d")
        due_date = datetime.strptime(entry['due_date'], "%Y-%m-%d")
        
        if paid_date <= due_date:
            on_time_payment_count += 1

    # Calculate unpaid amount
    unpaid_amount = total_expected_amount - total_collected_amount
    
    # Calculate the percentage of students who paid on time
    total_students = len(unique_students)
    on_time_payment_percentage = (on_time_payment_count / total_students) * 100 if total_students > 0 else 0

    # Format the response
    response = {
        'total_collected_amount': total_collected_amount,
        'unpaid_amount': unpaid_amount,
        'monthly_data': dict(monthly_data),
        'product_wise_collected_amount': dict(product_wise_data),
        'number_of_students': total_students,
        'on_time_payment_percentage': on_time_payment_percentage
    }
    
    return response
