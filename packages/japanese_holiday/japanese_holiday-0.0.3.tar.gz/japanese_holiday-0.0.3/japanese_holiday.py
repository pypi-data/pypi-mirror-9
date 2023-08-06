# -*- coding: utf-8 -*-
#!/usr/bin/env python
import sys, codecs
import dateutil.parser
import httplib2
import argparse
import json


HOLIDAY_TYPE_MOZILLA = 'outid3el0qkcrsuf89fltf7a4qbacgt9@import.calendar.google.com'
HOLIDAY_TYPE_OFFICIAL_JA = 'japanese__ja@holiday.calendar.google.com'
HOLIDAY_TYPE_OFFICIAL = 'japanese@holiday.calendar.google.com'

def getholidays(apitokenid, holiday_type, date_from, date_to, limit=200):
    assert isinstance(apitokenid, str)
    assert holiday_type in (HOLIDAY_TYPE_MOZILLA, HOLIDAY_TYPE_OFFICIAL_JA, HOLIDAY_TYPE_OFFICIAL)
    context = (
        holiday_type,
        apitokenid,
        dateutil.parser.parse(date_from).strftime('%Y-%m-%dT00:00:00Z'),
        dateutil.parser.parse(date_to).strftime('%Y-%m-%dT00:00:00Z'),
        limit)
    print context
    url = 'https://www.googleapis.com/calendar/v3/calendars/%s/events?' \
          'key=%s&timeMin=%s&timeMax=%s&maxResults=%d&orderBy=startTime&singleEvents=true' % context
    h = httplib2.Http('.cache')
    res, content = h.request(url, 'GET')
    if res.status != 200:
        return None
    return json.loads(content)['items']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('apitokenid',
        metavar='CID',
        type=str,
        help='GoogleCalendar API KEY.')
    parser.add_argument('date_from',
        metavar='START_DATE',
        type=str,
        help='Get from. ex) 2015-01-01')
    parser.add_argument('date_to',
        metavar='END_DATE',
        type=str,
        help='Get to. ex) 2015-12-31')
    parser.add_argument('--type',
        action='store',
        type=int,
        dest='type',
        default=0,
        help='0: mozilla, 1: google official(JP), 2:google official(EN). Default is 1.')

    args = parser.parse_args()
    holidays = getholidays(
        args.apitokenid,
        (HOLIDAY_TYPE_MOZILLA, HOLIDAY_TYPE_OFFICIAL_JA, HOLIDAY_TYPE_OFFICIAL)[args.type],
        args.date_from,
        args.date_to)

    for day in [{'day': day['start']['date'], 'summary': day['summary'].split('/')[0]} for day in holidays]:
        print u"summary: {summary}, date: {day}".format(**day)

if __name__ == '__main__':
    main()