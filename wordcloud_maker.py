from wordcloud import WordCloud

import matplotlib.pyplot as plt
import argparse
import json



def main(wordcount_file:str, outputfile:str):
    with open(wordcount_file, 'r') as f:
        wc = json.load(f)

    for i, (question, wordcount) in enumerate(wc.items()):
        cloud = WordCloud(background_color="white", width=1600, height=900, max_words=400).generate_from_frequencies(wordcount)

        figure = plt.figure(figsize=(16,9), dpi=300)


        plt.tight_layout()
        plt.axis('off')

        plt.title(question)
        plt.imshow(cloud, interpolation='bilinear')

        print(outputfile, i, outputfile.format(i))
        plt.savefig(outputfile.format(i))

        plt.clf()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--wordcount", '-w', help="wordcount filepath produced by whole_submission_to_response.py", type=str, required=True)
    parser.add_argument("--outputfile", '-o', help="filepath used to save wordcloud. Use format 'filepath_{}.py' \
                                                    with curly braces AND quotes to save multiple word clouds per run of the script",
                                                    type=str, default="wordcloud_{}.png")

    args = parser.parse_args()

    main(args.wordcount, args.outputfile)