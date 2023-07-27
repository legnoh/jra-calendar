import logging,os,platform
import modules.jra as jra
import modules.ical as jraIcal
from selenium.webdriver.chrome.service import Service as ChromiumService
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium import webdriver
from icalendar import Calendar

log_format = '%(asctime)s[%(filename)s:%(lineno)d][%(levelname)s] %(message)s'
logging.basicConfig(format=log_format, datefmt='%Y-%m-%d %H:%M:%S%z', level=logging.INFO)

if __name__ == '__main__':

    # initialize
    logging.info("----Initialize")
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')

    if platform.system() == 'Linux':
        driver = webdriver.Chrome(service=ChromiumService(), options=options)
    else:
        driver = webdriver.Chrome(service=ChromeService(), options=options)
    driver.implicitly_wait(10)

    # get all active year
    logging.info("----Get all active year")
    years = jra.get_calendar_active_years(driver)

    # get active link point settings
    logging.info("----Get active link point settings")
    max_link_point = jra.get_max_link_point()

    # get all grade race in all active year
    logging.info("----Get all grade race in all active year")
    grade_races = []
    for year in years:
        for month in range(1, 13):
            grade_races = grade_races + jra.get_grade_races_by_month(driver, year, month, max_link_point)

    # compose iCalendar file
    logging.info("----Generate ical data")
    cal = Calendar()
    cal.add("X-WR-CALNAME", "中央競馬")
    cal.add("X-APPLE-CALENDAR-COLOR", "#268300")
    for race in grade_races:
        event = jraIcal.create_event_block(race)
        cal.add_component(event)

    logging.info("----Output ics file")
    os.mkdir("./dist")
    with open("./dist/graderaces.ics", mode='w') as f:
        f.write(cal.to_ical().decode("utf-8"))
