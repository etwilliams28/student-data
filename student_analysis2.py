import unicodecsv
import pandas as pd

'''
def read_csv(filename):
    with open(filename, 'rb') as f:
        reader = unicodecsv.DictReader(f)
        return list(reader)

enrollments = read_csv('enrollments.csv')
daily_enagement = read_csv('daily_engagement.csv')
project_submissions = read_csv('project_submissions.csv')
'''

def read_csv(filename):
    with open(filename, 'rb') as f:
        reader = unicodecsv.DictReader(f)
        return list(reader)

enrollments = read_csv('enrollments.csv')
daily_engagement = read_csv('daily_engagement.csv')
project_submissions = read_csv('project_submissions.csv')


print(enrollments[0])



from datetime import datetime as dt
"""
def parse_date(date):
    if date == '':
        return None
    else:
        return dt.strptime(date, '%y-%m-%d')

def parse_maybe_int(i):
    if i == '':
        return None
    else:
        return int(float(i))
#cleaing up the data in the enrollment table
for enrollment in enrollments:
    enrollment['join_date'] = parse_date(enrollment['join_date'])
    enrollment['cancel_date'] = parse_date(enrollment['cancel_date'])
    enrollment['days_to_cancel'] = parse_maybe_int(enrollment['days_to_cancel'])
    enrollment['is_udacity'] = enrollment['is_udacity'] == 'True'
    enrollment['is_canceled'] = enrollment['is_canceled'] == 'True'
"""
""" This data does not match very well, so we need to figure out why"""

for engagement in daily_engagement:
    engagement['account_key'] = engagement['acct']
    del(engagement['acct'])

print("Total amount of rows in enrollments: {}".format(len(enrollments)))
print("Total amount of rows in daily engagement: {}".format(len(daily_engagement)))
print("Total amount of rows in project submissions: {}".format(len(project_submissions)))


unique_enrolled_students = set()
for enrollment in enrollments:
    unique_enrolled_students.add(enrollment['account_key'])
print("Unique Enrolled Students for enrollments: {}".format(len(unique_enrolled_students)))


unique_engagement_students = set()
for engagement_record in daily_engagement:
    unique_engagement_students.add(engagement_record['account_key'])
print("Unique Enrolled Students for enagements: {}".format(len(unique_engagement_students)))


unique_project_submitters = set()
for submission in project_submissions:
    unique_project_submitters.add(submission['account_key'])
print("Unique Enrolled Students for submissions: {}".format(len(unique_project_submitters)))


""" I want to find the unique_values in this data set, to do so I
need to loop through the the data and pull unique rows."""

for enrollment in enrollments:
    student = enrollment['account_key']
    if student not in unique_engagement_students:
        print(enrollment)
        break

count_problem_students = 0
for enrollment in enrollments:
    student = enrollment['account_key']
    if (student not in unique_engagement_students and enrollment['join_date'] != enrollment['cancel_date']):
        print(enrollment)
        count_problem_students += 1

print(count_problem_students)
