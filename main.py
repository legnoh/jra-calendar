import os
import modules.jra as jra
import modules.ical as jraIcal
from selenium import webdriver
import chromedriver_binary
from icalendar import Calendar

# initialize
print("----Initialize")
options = webdriver.ChromeOptions()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)
driver.implicitly_wait(10)

# get all active year
print("----Get all active year")
years = jra.get_calendar_active_years(driver)

# get active link point settings
print("----Get active link point settings")
max_link_point = jra.get_max_link_point()

# get all grade race in all active year
print("----Get all grade race in all active year")
grade_races = []
for year in years:
    for month in range(1, 13):
        grade_races = grade_races + jra.get_grade_races_by_month(driver, year, month, max_link_point)

# compose iCalendar file
print("----Generate ical data")
cal = Calendar()
cal.add("X-WR-CALNAME", "中央競馬")
cal.add("X-APPLE-CALENDAR-COLOR", "#268300")
for race in grade_races:
    event = jraIcal.create_event_block(race)
    cal.add_component(event)

print("----Output ics file")
os.mkdir("./dist")
with open("./dist/jra-grade-races.ics", mode='w') as f:
    f.write(cal.to_ical().decode("utf-8"))
