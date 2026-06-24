Water Quality Monitoring System

A desktop application built with Python and Tkinter for reporting and
monitoring local water quality. Users can sign up, submit water issue
reports, view a color-coded map of reported locations, track alerts, and
manage their profile. Admins get a dashboard to verify reports and manage
users.

 Features

- User signup and login (email/password, validated)
- Dashboard with overall water status (Good / Moderate / Bad) and stats
- Report Issue screen — submit a location, status, and description
- Map screen — visual pin map of all reported locations, color-coded by
  status, with tap-to-view details (built entirely with Tkinter Canvas,
  no external map API or libraries)
- My Reports screen — search and filter your submitted reports
- Alerts screen — status badges grouped by safe/moderate/unsafe
- Profile screen — preset avatar picker, edit profile, change password
- Admin Dashboard — overview stats, manage users, verify/unverify
  reports, system activity log

Requirements

- Python 3.8 or later
- No external libraries — uses only `tkinter`, `json`, `os`, and
  `datetime` from the standard library

Project Structure
