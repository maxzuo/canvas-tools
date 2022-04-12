import argparse
import os

import requests
from requests.structures import CaseInsensitiveDict

import json
import tqdm

course_id = "237466"
quiz_id  = "340313"
outdir = "event_data/"

base_url = "https://gatech.instructure.com"

with open("keys.txt", 'r') as f:
    bearer, username, password = [c.strip() for c in f.readlines()]

def main():
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = f"Bearer {bearer}"

    submissions = requests.get(f"{base_url}/api/v1/courses/{course_id}/quizzes/{quiz_id}/submissions?per_page=2000&include[]=submission_history", headers=headers).json()


    for submission in tqdm.tqdm(submissions['quiz_submissions']):
        attempt = submission['attempt']
        student_outdir = f"{outdir}{submission['user_id']}"
        os.makedirs(student_outdir, exist_ok=True)

        # assumes quiz submission takes last score (not highest score)
        while attempt > 0:
            total_info = None
            url = f"{base_url}/api/v1/courses/{course_id}/quizzes/{quiz_id}/submissions/{submission['id']}/events?attempt={attempt}&per_page=200000"
            while url is not None:
                submission_info = requests.get(url, headers=headers)
                if total_info is None:
                    total_info = submission_info.json()
                else:
                    total_info['quiz_submission_events'].extend(submission_info.json()['quiz_submission_events'])
                url = submission_info.links.get('next', dict(url=None))['url']

            with open(os.path.join(student_outdir, f"{submission['id']}_{attempt}.json"), 'w') as f:
                json.dump(total_info, f, indent=2)
            attempt -= 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--outdir", '-o', required=False, type=str)
    parser.add_argument("--courseid", '-c', required=False, type=str)
    parser.add_argument("--quizid", '-q', required=False, type=str)

    args = parser.parse_args()

    course_id = args.courseid if args.courseid else course_id
    quiz_id = args.quizid if args.quizid else quiz_id
    outdir = args.outdir if args.outdir else outdir

    main()