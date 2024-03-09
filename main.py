import datetime,json,logging,os
import modules.jra as jra
import modules.nar as nar
import modules.ical as jraIcal
import modules.json as jraJson
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from icalendar import Calendar

log_format = '%(asctime)s[%(filename)s:%(lineno)d][%(levelname)s] %(message)s'
logging.basicConfig(format=log_format, datefmt='%Y-%m-%d %H:%M:%S%z', level=logging.INFO)

if __name__ == '__main__':

    # initialize
    logging.info("# Initialize")
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')

    driver = webdriver.Chrome(service=Service(), options=options)
    driver.implicitly_wait(10)

    logging.info("# JRA")

    ## get active link point settings
    logging.info("## Get active link point settings")
    max_link_point = jra.get_max_link_point()
    
    ## get all active year
    logging.info("## Get all active year")
    years:list[str] = jra.get_calendar_active_years(driver)

    ## get all JRA grade race in all active year
    logging.info("## Get all JRA grade race in all active year")
    jra_grade_races = []
    for year in years:
        for month in range(1, 13):
            jra_grade_races = jra_grade_races + jra.get_grade_races_by_month(driver, year, month, max_link_point)
    
    logging.info("# NAR")

    ## get all active year
    logging.info("## Get all active year")
    years:list[str] = nar.get_calendar_active_years(driver)

    ## get all NAR grade race in all active year
    logging.info("## Get all Dirt grade race in all active year")
    dirt_grade_races = []
    for year in years:
        dirt_grade_races = dirt_grade_races + nar.get_grade_races_by_year(driver, year)

    # # compose iCalendar file
    logging.info("# Generate ical data")
    cal = Calendar()
    cal.add("X-WR-CALNAME", "競馬重賞")
    cal.add("X-APPLE-CALENDAR-COLOR", "#268300")
    for race in jra_grade_races:
        event = jraIcal.create_event_block(race)
        cal.add_component(event)
    for race in dirt_grade_races:
        event = jraIcal.create_event_block(race)
        cal.add_component(event)
    
    cal_jra = Calendar()
    cal_jra.add("X-WR-CALNAME", "競馬重賞(中央)")
    cal_jra.add("X-APPLE-CALENDAR-COLOR", "#268300")
    for race in jra_grade_races:
        event = jraIcal.create_event_block(race)
        cal_jra.add_component(event)
    
    cal_nar = Calendar()
    cal_nar.add("X-WR-CALNAME", "競馬重賞(地方)")
    cal_nar.add("X-APPLE-CALENDAR-COLOR", "#268300")
    for race in dirt_grade_races:
        event = jraIcal.create_event_block(race)
        cal_nar.add_component(event)

    logging.info("# Output ics file")
    if not os.path.exists("./dist"):
        os.mkdir("./dist")
    with open("./dist/graderaces.ics", mode='w') as f:
        f.write(cal.to_ical().decode("utf-8"))
    with open("./dist/graderaces_jra.ics", mode='w') as f:
        f.write(cal_jra.to_ical().decode("utf-8"))
    with open("./dist/graderaces_dirtgrade.ics", mode='w') as f:
        f.write(cal_nar.to_ical().decode("utf-8"))

    logging.info("# Output json file")
    now = datetime.datetime.now()
    all_grade_races = jra_grade_races + dirt_grade_races
    with open("./dist/graderaces.json", mode='w') as f:
        d = { "updated_at": now, "races": all_grade_races }
        json.dump(d, f, indent=2, default=jraJson.json_serial)
    with open("./dist/graderaces_jra.json", mode='w') as f:
        d = { "updated_at": now, "races": jra_grade_races }
        json.dump(d, f, indent=2, default=jraJson.json_serial)
    with open("./dist/graderaces_dirtgrade.json", mode='w') as f:
        d = { "updated_at": now, "races": dirt_grade_races }
        json.dump(d, f, indent=2, default=jraJson.json_serial)

    logging.info("All process was done successfully.")
