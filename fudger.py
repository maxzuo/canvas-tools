from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import argparse

import requests
from requests.structures import CaseInsensitiveDict

import csv

from bs4 import BeautifulSoup
import tqdm

from scraper import login
from time import sleep

course_id = "237466"
quiz_id  = "340313"

base_url = "https://gatech.instructure.com"
webdriver_exec = "./venv/chromedriver.exe"

# NOTE:
# To use this script, it requires a keys.txt file in the same folder as the script
# with the bearer token, username, and password for a Canvas account
with open("keys.txt", 'r') as f:
    bearer, username, password = [c.strip() for c in f.readlines()]

def main(quiz_id:str=quiz_id, course_id:str=course_id, fudgefile:str="fudge.csv"):
    with open(fudgefile, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = {name:index for index,name in enumerate(next(reader))}

        fudge = []
        for row in reader:
            fudge.append([row[headers['id']], row[headers['attempt']], row[headers['fudge points']]])

    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = f"Bearer {bearer}"

    driver = webdriver.Chrome(webdriver_exec)
    wait = WebDriverWait(driver, 10)

    login(driver, wait)

    for student_id, attempt, fudge_points in tqdm.tqdm(fudge):
        driver.get(f"{base_url}/courses/{course_id}/quizzes/{quiz_id}/history?version={attempt}&user_id={student_id}")

        wait.until(EC.element_to_be_clickable((By.ID, "fudge_points_entry"))).send_keys(Keys.BACKSPACE * 20 + fudge_points + Keys.RETURN)

        sleep(0.1)
        wait.until(EC.element_to_be_clickable((By.ID, "fudge_points_entry")))

if __name__ == "__main__":

    parser = argparse.ArgumentParser('Required headers: "id", "attempt", "fudge points"')

    parser.add_argument("--quiz_id", '-q', help="6-digit ID for the quiz you want to scrape (can be found in URL)", type=str, default=quiz_id)
    parser.add_argument("--course_id", '-c', help="6-digit ID for the course you want to scrape from (can be found in URL)", type=str, default=course_id)
    parser.add_argument("--fudgefile", '-f', help="filepath to the csv of the fudge file you read from", type=str, default="fudge.csv")

    args = parser.parse_args()

    main(args.quiz_id, args.course_id, args.fudgefile)
