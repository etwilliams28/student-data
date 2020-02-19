import unicodecsv
import pandas as pd


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
    if enrollment['is_udacity']=='True':
            udacity_test_accounts.add(enrollment['account_key'])
print(len(udacity_test_accounts))

""" looks like we added 6 different accounts to the udacity_test_accounts set"""

""" lets remove all the udacity_test_accounts from all csv files... because we do not want to look at non-students when
analysing our data"""


def remove_udacity_accounts(data):
    none_udacity_accounts = []
    for data_points in data:
        if data_points['account_key'] not in udacity_test_accounts:
            none_udacity_accounts.append(data_points)
    return none_udacity_accounts

new_enrollment_data = remove_udacity_accounts(enrollments)
new_engagement_data = remove_udacity_accounts(daily_engagement)
new_submissions_data = remove_udacity_accounts(project_submissions)

""" Now lets start analysing our dataframe

Question:

How does engagment differ from people who pass the first project to people who do
not pass the first project?

How:
To answer this question first I must filter out all current students that have been enrolled
for more then 7 days.

"""


paid_students = {}
for enrollment in new_enrollment_data:
    if not enrollment['is_canceled'] or enrollment['days_to_cancel'] > 7:
        account_key = enrollment['account_key']
        enrollment_date = enrollment['join_date']
    if account_key not in paid_students or enrollment_date > paid_students[account_key]:
        paid_students[account_key] = enrollment_date

print(len(paid_students))
