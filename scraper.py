from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import argparse

import requests
from requests.structures import CaseInsensitiveDict

import json

from time import sleep

from bs4 import BeautifulSoup

course_id = "197116"
quiz_id  = "311535"

base_url = "https://gatech.instructure.com"

with open("keys.txt", 'r') as f:
    bearer, username, password = [c.strip() for c in f.readlines()]


webdriver_exec ="./venv/chromedriver.exe"


def login(driver, wait):
    driver.get(base_url)
    try:
        wait.until(EC.element_to_be_clickable((By.ID, "username"))).send_keys(username)
        wait.until(EC.element_to_be_clickable((By.ID, "password"))).send_keys(password)
    except Exception as e:
        raise e

    driver.find_element(By.CSS_SELECTOR, "#login > section.btn-row.buttons > input.btn.btn-submit.button").click()

    try:
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "duo_iframe")))
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#auth_methods > fieldset > div.row-label.push-label > button"))).click()

        driver.switch_to.parent_frame()
    except:
        pass

    login_wait = WebDriverWait(driver, 25)
    try:
        login_wait.until(EC.element_to_be_clickable((By.ID, "planner-today-btn")))
    except:
        pass


def main():
    # get all submission info first
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = f"Bearer {bearer}"

    submissions = requests.get(f"{base_url}/api/v1/courses/{course_id}/quizzes/{quiz_id}/submissions", headers=headers).json()

    with open("submissions_overview.json", 'w') as f:
        json.dump(submissions, f, indent=2)

    driver = webdriver.Chrome(webdriver_exec)
    wait = WebDriverWait(driver, 10)

    login(driver, wait)

    for submission in submissions['quiz_submissions']:
        driver.get(f"{submission['html_url']}/log/")
        submission['attempts'] = []

        wait.until(EC.presence_of_element_located((By.ID, "ic-QuizInspector__Session")))
        for i in range(2,15):
            if driver.find_element(By.CSS_SELECTOR, f"#breadcrumbs > ul > li:nth-child({i}) > a > span").text == "Log":
                submission['student'] = driver.find_element(By.CSS_SELECTOR, f"#breadcrumbs > ul > li:nth-child({i-1}) > a > span").text.strip()
                break

        attempts = max(1,len(driver.find_elements(By.CSS_SELECTOR, ".ic-AttemptController__Attempt")))
        print(attempts)

        for attempt in range(1,attempts+1):
            driver.get(f"{submission['html_url']}/log/?attempt={attempt}")
            wait.until(EC.presence_of_element_located((By.ID, "ic-QuizInspector__Session")))
            sleep(1)

            log = {}

            log['attempt'] = attempt
            log['start'] = driver.find_element(By.CSS_SELECTOR, "#ic-QuizInspector__Session > table > tbody > tr:nth-child(1) > td").text.strip()

            log['log'] = []

            log_soup = BeautifulSoup(driver.find_element(By.ID, "ic-EventStream__ActionLog").get_attribute('innerHTML'), "html.parser")
            for l in log_soup:
                log['log'].append({
                                    "timestamp":l.select(".ic-ActionLog__EntryTimestamp")[0].text.strip(),
                                    "class":l.find('svg').get('name'),
                                    "description":l.select(".ic-ActionLog__EntryDescription")[0].text.strip()
                                  })

            submission['attempts'].append(log)

    with open("submissions_details.json", 'w') as f:
        json.dump(submissions, f, indent=2)
    # driver.close()


if __name__ == "__main__":
    main()
