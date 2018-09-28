"""
Script to import members from excel sheets
"""

# Make sure django setting environment is set
import os
from datetime import datetime
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "temas_db.settings")

# Make sure Application registry is setup properly
import django
django.setup()

import pandas as pd
from restapi.models import *




def create_and_subscribe_member(row, course_name):
    member = Member.objects.get_or_create(first_name=row['Vorname'],
                          last_name=row['Nachname'],
                          birthday=parse_birthday(row['Geburtsdatum']),
                          address=parse_address(row['Straße'], row['PLZ']),
                          phone=row['Telefon'],
                          mail=row['E-Mail'],
                          guardian=row['Erziehungsberechtigter'],
                          picked_up=make_boolean(row['Wird abgeholt?'])
                          )
    course = Course.objects.get(name=course_name)
    subscription = Subscription.objects.get_or_create(member=member,
                                                      course=course,
                                                      start_date=datetime.date(year=2018, month=10, day=1),
                                                      value=20
                                                      )


def parse_birthday(excel_string):
    """
    Parse date string in format DD/MM/YYYY into datetime object
    :param excel_string:
    :return:
    """
    print(excel_string)
    if pd.isnull(excel_string):
        return datetime.date.today()
    else:
        return excel_string


def parse_address(street, plz):
    """
    Combine address fields street and plz into one
    :param street:
    :param plz:
    :return:
    """
    return str(street) + '\n' + str(plz)


def make_boolean(bool_string):
    """
    Parse string with "Ja" or "Nein" into boolean
    :param bool_string:
    :return: bool
    """
    if bool_string is 'ja':
        return True
    else:
        return False

if __name__ == "__main__":
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, '../montag.xlsx')
    df = pd.read_excel(filename)
    print(df.columns.values)

    for index, row in df.iterrows():
        if not pd.isnull(row['Vorname']) and not pd.isnull(row['Nachname']):
            # only if legitimate member data is in row
            create_and_subscribe_member(row, 'PK-Montag-12-14')
            print('done ', index)




