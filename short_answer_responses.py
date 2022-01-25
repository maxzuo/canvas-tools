import re
import json
from collections import defaultdict, Counter
import argparse

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

import nltk
nltk.download('stopwords')

custom_stopwords = {"would", "could", "should", "like", "with", "without", "also", "way"}

def main(submissions_file:str, response_file:str, wordcount_file:str):
    ps = PorterStemmer()

    with open(submissions_file, 'r') as f:
        s = json.load(f)

    new_s = list(filter(lambda d: d, [{k:v[0]['answer'] for k,v in q["questions"].items() if "50" in k} for q in s]))
    save = defaultdict(list)
    for v in new_s:
        for q,a in v.items():
            save[q].append(a)

    with open(response_file, 'w') as f:
        json.dump(save, f, indent=2)

    stops = set([re.sub(r"[^-\w\s]+", "", w) for w in stopwords.words('english')])

    wordcount_data = {}
    for question, responses in save.items():
        q_words = re.sub(r"[^-\w\s]+", "", question).lower().split()
        q_2words = (f"{q_words[i]} {q_words[i+1]}" for i in range(len(q_words)-1))
        q_word_stems = (ps.stem(w) for w in q_words)

        q_words = set(q_words).union(q_2words).union(q_word_stems).union(custom_stopwords)


        words = [word for word in re.sub(r"[^\w\s-]|(?:\s+-\s+)", "", " ".join(responses).lower().strip()).split() if word not in stops and word not in q_words]
        words.extend(f"{words[i]} {words[i+1]}" for i in range(len(words)-1))

        wc = Counter(words)
        wordcount_data[question] = {w:wc[w] for w in reversed(sorted(wc, key=lambda w:wc[w]))}

    with open(wordcount_file, 'w') as f:
        json.dump(wordcount_data, f, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--submissions", '-s', help="source submissions.json filepath to read in", type=str, required=True)
    parser.add_argument("--stringresponse", "-r", help="output response.json filepath to write to", type=str, required=True)
    parser.add_argument("--wordcount", "-w", help="filepath to write the word counts to for each question", type=str, default="wordcount.json")

    args = parser.parse_args()

    main(args.submissions, args.stringresponse, args.wordcount)