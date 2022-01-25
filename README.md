# Canvas Tools
A set of scripts used by CS 4605/7470 at Georgia Tech for working with Canvas's quizzes (classic & new).

## Installation and Getting Started
### Dependencies
In order to use most of these tools, you will need to install the necessary dependencies listed in `requirements.txt` (`pip install -r requirements.txt`, a virtual environment is suggested). There may be some requirements that are not properly listed, but the txt file should cover all of them.

Since `selenium` is a dependency, please download the correct corresponding [Chromedrier](https://chromedriver.chromium.org/downloads) for your Chrome browser, or download a corresponding driver for whichever browser you wish to use. Remember to update the path in the code accordingly.

### Bearer Token, Username, & Password
A bearer token for your Canvas account is required to access the Canvas API. You can get one by creating a new access token by going to: Canvas Profile > [Settings](https://gatech.instructure.com/profile/settings) > +New Access Token. Place this as the first line in `keys.txt`. You also have the option of loading `keys.txt` with your username and password to Canvas as the second and third line, respectively, which never leaves your device. If you choose not to, please place two empty lines following your bearer token in `keys.txt` so that the file has 3 lines in total. You will then need to manually login each time the script is run.

## Usage
### New Quizzes Submissions
To scrape new quizzes, run the `scrape_new_quiz.py`. Use the `-h` flag for options. It will require the `keys.txt` folder to be in the same folder as where it is being run from, as well as a quiz id and a course id.

### Word Clouds
To generate word clouds, run the scripts in this order:
* `scrape_new_quiz.py`
* `short_answer_responses.py`
* `wordcloud_maker.py`

Again, make use of the `-h` flag for options for each of these files.