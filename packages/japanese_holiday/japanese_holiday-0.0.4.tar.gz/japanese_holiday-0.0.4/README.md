# Japanese Holiday

Get Japanese holidays from Google Calendar.

## Install

Use pip: `$ pip install japanese-holiday`

## Getting Started

* Access [Google Console API](https://code.google.com/apis/console).
* Calender API status turn on.
* Create access key.
* Set function "getholidays" first argument to your access key.


## Example

```python
    import japanese_holiday
    now = datetime.date.today()
    date_from = datetime.date(now.year-1, 1, 1)
    date_to = datetime.date(now.year+2, 12, 31)
    holidays = japanese_holiday.getholidays(
        "YOUR API KEY",
        japanese_holiday.HOLIDAY_TYPE_OFFICIAL_JA,
        date_from.strftime('%Y-%m-%d'),
        date_to.strftime('%Y-%m-%d')
    ) 
```

