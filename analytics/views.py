import random
from django.http import JsonResponse
from analytics.service import filter_collection_data 

# Global data variable


# # Function to generate a list of dictionaries with random values for each key
# def generate_random_dicts(num_entries):
#     result = []
#     months = list()
#     for i in range(0,11):
#         months.append(random.randint(0,1000))
#     for _ in range(num_entries):
        
#         entry = {
#             'collector_id': random.choice(collector_ids),
#             'academic_year': random.choice(academic_years),
#             'grade': random.choice(grades),
#             'paid': random.randint(0, 1000),
#             'unpaid': random.randint(0, 1000),
#             'cred': random.randint(0, 1000),
#             'flex': random.randint(0, 1000),
#             'pay': random.randint(0, 1000),
#             "monthly": months
#         }
#         result.append(entry)
#     return result

# # Generate a list of 100 dictionaries
# random_dicts = generate_random_dicts(1000)

# def generate_random_data():
#     """Generate random values and store them in the global variable"""
#     total_paid = random.randint(0, 1000)  # Random number between 0 and 1000
#     total_unpaid = random.randint(0, 1000)  # Random number between 0 and 1000
#     total_number_of_students = total_paid + total_unpaid  # The total number is the sum of paid and unpaid students

#     # Store the generated data in the global variable
#     random_data = {
#         'total_paid': total_paid,
#         'total_unpaid': total_unpaid,
#         'total_number_of_students': total_number_of_students
#     }
#     return random_data  # Returning for potential use

def random_data_view(request):
    if request.method == 'GET':
        # Get the query parameters from the request
        collector_id = request.GET.get('collector_id')
        grade = request.GET.get('grade_id')
        academic_year = request.GET.get('academic_year')
        start_date = request.GET.get('range_start_date')
        end_date = request.GET.get('range_end_date')

        # Check if academic_year is provided and valid
        # if academic_year and academic_year not in academic_years:
        #     return JsonResponse({"error": "Invalid academic year format"}, status=400)

        final_response = filter_collection_data(collector_id, grade, academic_year, start_date, end_date)
        return JsonResponse(final_response, safe=False)  # safe=False to allow list of dictionaries


        # # Filter the list based on non-null query parameters
        # filtered_dicts = random_dicts

        # if collector_id:
        #     filtered_dicts = [dicts for dicts in filtered_dicts if str(dicts['collector_id']) == collector_id]
        # if grade:
        #     filtered_dicts = [dicts for dicts in filtered_dicts if dicts['grade'] == grade]
        # if academic_year:
        #     filtered_dicts = [dicts for dicts in filtered_dicts if dicts['academic_year'] == academic_year]

        # # Return the filtered data or an error if no match found
        # if filtered_dicts:
        #     total_paid = sum([dicts['paid'] for dicts in filtered_dicts])
        #     total_unpaid = sum([dicts['unpaid'] for dicts in filtered_dicts])
        #     total_flex = sum([dicts['flex'] for dicts in filtered_dicts])
        #     total_cred = sum([dicts['cred'] for dicts in filtered_dicts])
        #     total_pay = sum([dicts['pay'] for dicts in filtered_dicts])
        #     final_response={"total_number_of_students":len(filtered_dicts),"total_paid":total_paid,"total_unpaid":total_unpaid,'total':total_unpaid+total_paid, total_flex:"total_flex",total_cred:"total_cred", total_pay:"total_pay", monthly: filtered_dicts["monthly"]}
        # else:
        #     return JsonResponse({"error": "No data found for the provided parameters"}, status=404)

