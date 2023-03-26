# Tennis_court_reservations

# USAGE:

To use the script type in console (for example linux terminal or windows cmd/powershell):
```
python app.py
```
After that you will be presented with choice whether or not to use sqlite database. If you input yes you will be prompted to input
the name of the database, if the provided name won't be found in the project's folder it will create a new database. You can also fill
new database with some sample data. Then you will be presented with a menu that allows you to:

1. Make a reservation
2. Cancel a reservation
3. Print schedule
4. Save schedule to a file
5. Exit

After picking an option you will be instructed to provide some necessary data, if there is something wron with your input you will
be informed of that and prompted to retype it.
All of the dates you will be asked to provide need to be in format {DD.MM.YYYY HH:MM} (example: 01.01.2023 10:00).

Making a reservation fails if:
    * User has more than 2 reservations already this week
    * The date user gives is less than one hour from now
If the court is already reserved for specified time the system will attempt to propose a different time, but will also fail
if there won't be any time available for the given day.

Cancelling a reservation fails if:
    * There is no reservation for this user on specified date
    * The date user gives is less than one hour from now

###### Filip Zygmuntowicz 2023
