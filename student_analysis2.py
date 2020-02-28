import unicodecsv
import pandas as pd
import numpy as np


""" using unicodecsv to read csv files """

def read_csv(filename):
    with open(filename, 'rb') as f:
        reader = unicodecsv.DictReader(f)
        return list(reader)

enrollments = read_csv('enrollments.csv')
daily_engagement = read_csv('daily_engagement.csv')
project_submissions = read_csv('project_submissions.csv')


print(enrollments[0])



from datetime import datetime as dt

def parse_date(date):
    if date == '':
        return None
    else:
        return dt.strptime(date, '%Y-%m-%d')

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

for engagement in daily_engagement:
    engagement['lessons_completed'] = int(float(engagement['lessons_completed']))
    engagement['num_courses_visited'] = int(float(engagement['num_courses_visited']))
    engagement['projects_completed'] = int(float(engagement['projects_completed']))
    engagement['total_minutes_visited'] = float(engagement['total_minutes_visited'])
    engagement['utc_date'] = parse_date(engagement['utc_date'])

for submission in project_submissions:
    submission['completion_date'] = parse_date(submission['completion_date'])
    submission['creation_date'] = parse_date(submission['creation_date'])


""" Looping through the daily_enagement file to change the delete the column nanme 'acct'
and change it to 'account_key'
"""

for engagement in daily_engagement:
    engagement['account_key'] = engagement['acct']
    del(engagement['acct'])

"""Printing out the total number of rows in all three data files to better understand what
we are dealing withh """

print("Total amount of rows in enrollments: {}".format(len(enrollments)))
print("Total amount of rows in daily engagement: {}".format(len(daily_engagement)))
print("Total amount of rows in project submissions: {}".format(len(project_submissions)))

""" Now I want to see the number of unique accounts in the files"""

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


"""The information above showed me that the enrollment data and the engagement data does not match.
This is odd becuase at the very least the engagement data should be equal or greater to the enrollment data as
you must be using the site (engaged) in order to be enrolled. The loop below is checking to see what enrollment account key is not
in the unique engagement student set from above. Looking at what ever accounts are not in this set will give us a understanding of What
if anything went wrong.
"""

for enrollment in enrollments:
    student = enrollment['account_key']
    if student not in unique_engagement_students:
        print(enrollment)
        break


""" after analysing the printout from above we can see that the accounts not in the engagement records are the ones with join_date and cancel_date dates
as the same. Looks like udacity does not count engagement if students have been enrolled for less then one day """


""" lets take a look if there are any more problems in the files. Below i am iterating through the enrollment table and checking to see if there
are any extra accounts that are not in the unique engagement set and that have not started and canceled on the same day. This will show me any
remaining problems"""

count_problem_students = 0
for enrollment in enrollments:
    student = enrollment['account_key']
    if (student not in unique_engagement_students and enrollment['join_date'] != enrollment['cancel_date']):
        print(enrollment)
        count_problem_students += 1

print(count_problem_students)

""" Looks like there are three remaining problem accounts remaining. From the looks of it these problem accounts are not in the unique_ set
because they they are udacity members. So when is_udacity is True.. This means they are udacity members and do not want to count them as students"""

""" lets create a set that that has all the udacity member accounts in it """

udacity_test_accounts = set()
for enrollment in enrollments:
    if enrollment['is_udacity']:
            udacity_test_accounts.add(enrollment['account_key'])
print(len(udacity_test_accounts))

""" looks like we added 6 different accounts to the udacity_test_accounts set"""

""" lets remove all the udacity_test_accounts from all csv files... because we do not want to look at non-students when
analysing our data"""

""" Testing another way to remove not udacity user from data_point. IT WORKS !

def remove_udacity_test(data):
    none_udacity_data = []
    for data_points in data:
        student = data_points['account_key']
        if not data_points['is_udacity']:
            none_udacity_data.append(student)
    return none_udacity_data
"""



def remove_udacity_accounts(data):
    none_udacity_data = []
    for data_points in data:
        if data_points['account_key'] not in udacity_test_accounts:
            none_udacity_data.append(data_points)
    return none_udacity_data

new_enrollment_data = remove_udacity_accounts(enrollments)
new_engagement_data = remove_udacity_accounts(daily_engagement)
new_submissions_data = remove_udacity_accounts(project_submissions)

print(len(new_enrollment_data))
print(len(new_engagement_data))
print(len(new_submissions_data))

""" Now lets start analysing our dataframe

Question:

How does engagment differ from people who pass the first project to people who do
not pass the first project?

How:
To answer this question first I must filter out all current students that have been enrolled
for more then 7 days.

problems:
- students must be enrolled for more than 7 days_to_cancel
- students must not have canceled from the course
- need to create a dictionary called paid students


"""


paid_students = {}
for enrollment in new_enrollment_data:
    if (not enrollment['is_canceled'] or
            enrollment['days_to_cancel'] > 7):
        account_key = enrollment['account_key']
        enrollment_date = enrollment['join_date']
        if (account_key not in paid_students or
                enrollment_date > paid_students[account_key]):
            paid_students[account_key] = enrollment_date
print(len(paid_students))


""" create a function to return true if engagement_record
record happend within one week of student joining """

def within_one_week(join_date, engagement_date):
    time_delta = engagement_date - join_date
    return time_delta.days < 7 and time_delta.days >= 0

def remove_free_trial_cancels(data):
    new_data = []
    for data_point in data:
        if data_point['account_key'] in paid_students:
            new_data.append(data_point)
    return new_data

paid_enrollments = remove_free_trial_cancels(new_enrollment_data)
paid_engagement = remove_free_trial_cancels(new_engagement_data)
paid_submissions = remove_free_trial_cancels(new_submissions_data)

print(len(paid_enrollments))
print(len(paid_engagement))
print(len(paid_submissions))




paid_engagement_in_first_week = []
for engagement_record in paid_engagement:
    account_key = engagement_record['account_key']
    join_date = paid_students[account_key]
    engagement_record_date = engagement_record['utc_date']

    if within_one_week(join_date, engagement_record_date):
         paid_engagement_in_first_week.append(engagement_record)
    if engagement_record['num_courses_visited'] > 0:
        engagement_record['has_visited'] = 1
    else:
        engagement_record['has_visited'] = 0

print(len(paid_engagement_in_first_week))


from collections import defaultdict


""" created a dictionary to group engagement data by the account key """

def group_data(data, key_name):
    grouped_data = defaultdict(list)
    for data_point in data:
        key = data_point[key_name]
        grouped_data[key].append(data_point)
    return grouped_data

engagement_by_account = group_data(paid_engagement_in_first_week, 'account_key')

def sum_data(grouped_data, field_name):
    sum_of_data = {}
    for key, data_points in grouped_data.items():
        total = 0
        for data_point in data_points:
            total += data_point[field_name]
            sum_of_data[key] = total
    return sum_of_data

total_minutes_by_account = sum_data(engagement_by_account,'total_minutes_visited')

total_minutes = list(total_minutes_by_account.values())
import statistics
import numpy as np
print(np.mean(total_minutes))
print(np.max(total_minutes))
print(np.min(total_minutes))
print(np.std(total_minutes))


student_with_max_minutes = None
max_minutes = 0

for student, total_minutes in total_minutes_by_account.items():# I am looping through the keys and values of the total_minutes_by_account.
    if total_minutes > max_minutes:# if the total minutes > then max minutes then
        max_minutes = total_minutes
        student_with_max_minutes = student
print(max_minutes)

for engagement_record in paid_engagement_in_first_week:
    if engagement_record['account_key'] == student_with_max_minutes:
        print(engagement_record)


""" I want to find how many lessons students completed in their first within_one_week.
Similar to what i did above

going to create three functions:

1. to group records together by account keys
2. sum up all records by account key
3. to print up statsitic summaries
"""

total_minutes_by_account = sum_data(engagement_by_account, 'lessons_completed')

def describe_data(data):
    print(np.mean(data))
    print(np.max(data))
    print(np.min(data))
    print(np.std(data))

summed_data = list(total_minutes_by_account.values())
print(describe_data(summed_data))


""" I want to see the amount of days student visit courses in their first week

To do this I will create new feild called has_visited and set 1 for visited or 0 for not
visited in that day """

print(paid_engagement_in_first_week[0])


days_visited_by_account = sum_data(engagement_by_account, 'has_visited')

visited_sum = list(days_visited_by_account.values())
print(describe_data(visited_sum))


subway_project_lesson_keys = ['746169184', '3176718735']

pass_subway_project = set()

for submission in paid_submissions:
    project = submission['lesson_key']
    rating = submission['assigned_rating']

    if ((project in subway_project_lesson_keys) and
            (rating == 'PASSED' or rating == 'DISTINCTION')):
        pass_subway_project.add(submission['account_key'])

print(len(pass_subway_project))

passing_engagement = []
non_passing_engagement = []

for engagement_record in paid_engagement_in_first_week:
    if engagement_record['account_key'] in pass_subway_project:
        passing_engagement.append(engagement_record)
    else:
        non_passing_engagement.append(engagement_record)

print(len(passing_engagement))
print(len(non_passing_engagement))


passing_engagement_by_account = group_data(passing_engagement, 'account_key')
passing_minutes = sum_data(passing_engagement_by_account,'total_minutes_visited')
passing_summed_data = list(passing_minutes.values())
print("Passing Students")
print(describe_data(passing_summed_data))
