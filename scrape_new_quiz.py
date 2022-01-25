from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import argparse

import requests
from requests.structures import CaseInsensitiveDict

import json
from time import sleep
import re

from bs4 import BeautifulSoup
import tqdm

from scraper import login

course_id = "237466"
new_quiz_id  = "991206"

base_url = "https://gatech.instructure.com"
webdriver_exec = "./venv/chromedriver.exe"

# NOTE:
# To use this script, it requires a keys.txt file in the same folder as the script
# with the bearer token, username, and password for a Canvas account
with open("keys.txt", 'r') as f:
    bearer, username, password = [c.strip() for c in f.readlines()]

def main(course_id:str=course_id, new_quiz_id:int=new_quiz_id, outfile:str="submissions.json"):
    # get all submission info first
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = f"Bearer {bearer}"

    submissions = requests.get(f"{base_url}/api/v1/courses/{course_id}/assignments/{new_quiz_id}/submissions?per_page=200", headers=headers).json()

    driver = webdriver.Chrome(webdriver_exec)
    wait = WebDriverWait(driver, 10)

    login(driver, wait)

    wait = WebDriverWait(driver, 2)

    for submission in tqdm.tqdm(submissions):
        preview_url = submission['preview_url']
        submission['questions'] = {}

        driver.get(preview_url)
        # classes "eRBXN_caGd gmVuP_esVF" queries the string of all questions "div.eRBXN_caGd.gmVuP_esVF > p"
        # "dzXeD_czRh" question object "div.dzXeD_czRh"

        # "eoadt_bGBk" is an answer choice, marked with either a check mark or x (options with no issue are marked with nothing)

        # "eoadt_cnmA" is the "X" mark (wrong answer choice)
        # "eoadt_EKAb" is the check mark (correct answer choice)

        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.fVJbh_bGBk")))

            soup = BeautifulSoup(driver.find_element(By.CSS_SELECTOR, "div.fOyUs_bGBk").get_attribute("innerHTML"), "html.parser")
            for question in soup.select("div.dzXeD_czRh"):
                question_text = re.sub(r"\s{2,}", " ", question.select_one("div.eRBXN_caGd.gmVuP_esVF > p").getText().strip())
                responses = []

                for response in question.select(".eoadt_bGBk"):
                    answer_str = re.sub(r"\s{2,}", " ", response.getText().strip())
                    colon = answer_str.find(":")
                    answer_type = answer_str[:colon].lower()
                    answer = answer_str[colon+1:]

                    responses.append({"type": answer_type, "answer": answer})

                submission['questions'][question_text] = responses
        except:
            pass

    with open(outfile, 'w') as f:
        json.dump(submissions, f, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--quiz_id", '-q', help="6-digit ID for the quiz you want to scrape (can be found in URL)", type=str, default=new_quiz_id)
    parser.add_argument("--course_id", '-c', help="6-digit ID for the course you want to scrape from (can be found in URL)", type=str, default=course_id)
    parser.add_argument("--outputfile", '-o', help="filepath to the json file you wish to write to", type=str, default="submissions.json")

    args = parser.parse_args()


    main(args.course_id, args.quiz_id, args.outputfile)