from pathlib import Path
import matplotlib
import pandas as pd
from matplotlib import pyplot as plt

matplotlib.rc('figure', figsize=(20, 10))
FILE_PATH = "sms-spam-corpus.csv"
REPLACE_DICTIONARY = {r'[^A-Za-z ]+': ''}
SPACES_DICTIONARY = {r'\s\s+': ' ', r'(?=^|\n)\s': ''}
OUTPUT_FOLDER = "output"
STOP_LIST = ["a", "the", "in", "to"]


def format_text(text):
    text.replace(REPLACE_DICTIONARY, regex=True, inplace=True)
    for word in STOP_LIST:
        text.replace(r'(?=\b)' + word + r'(?=\b)', '', regex=True, inplace=True)
    text.replace(SPACES_DICTIONARY, regex=True, inplace=True)


def content_length(message):
    return pd.Series(message).str.len().sort_values(ascending=False)


def avg_content_length(messages_length, rows):
    return messages_length.sum() / len(rows)


def get_20_and_normalize(content):
    temp_content = content.head(20)
    temp_content.loc[:, 'count'] /= pd.Series(temp_content['count']).sum()
    return temp_content


df = pd.read_csv(FILE_PATH, encoding="cp1251")
df = df.applymap(lambda s: s.lower() if isinstance(s, str) else s)
format_text(df)
ham = df[df.v1 == "ham"]
spam = df[df.v1 == "spam"]

ham_count_words = ham['v2'].str.split().explode().value_counts()
spam_count_words = spam['v2'].str.split().explode().value_counts()

ham_count_words = ham_count_words.to_frame().reset_index().rename(columns={'index': 'word', 'v2': 'count'})
spam_count_words = spam_count_words.to_frame().reset_index().rename(columns={'index': 'word', 'v2': 'count'})
ham_words_length = content_length(ham_count_words['word'])
spam_words_length = content_length(spam_count_words['word'])
ham_avg_words_length = avg_content_length(ham_words_length, ham_count_words)
spam_avg_words_length = avg_content_length(spam_words_length, spam_count_words)
ham_words_length = ham_words_length.to_frame().reset_index()
# ham_words_length.drop('index', inplace=True, axis=1)
ham_word_normalize = pd.Series(ham_words_length['word']).max()
ham_words_length.loc[:, 'word'] /= ham_word_normalize
# ham_words_length = ham_words_length.sort_values(by=['word']).reset_index()
ham_avg_words_length /= ham_word_normalize
spam_words_length = spam_words_length.to_frame().reset_index()
# spam_words_length.drop('index', inplace=True, axis=1)
spam_word_normalize = pd.Series(spam_words_length['word']).max()
spam_words_length.loc[:, 'word'] /= spam_word_normalize
spam_avg_words_length /= spam_word_normalize
# spam_words_length = spam_words_length.sort_values(by=['word']).reset_index()
ham_20_words = get_20_and_normalize(ham_count_words)
spam_20_words = get_20_and_normalize(spam_count_words)

Path(OUTPUT_FOLDER).mkdir(parents=True, exist_ok=True)
ham_count_words.to_csv(OUTPUT_FOLDER + '/hamCounter.csv', index=False, sep='-')
spam_count_words.to_csv(OUTPUT_FOLDER + '/spamCounter.csv', index=False, sep='-')

ham_message_length = content_length(ham['v2'])
spam_message_length = content_length(spam['v2'])
spam_avg_message_length = avg_content_length(spam_message_length, spam)
ham_avg_message_length = avg_content_length(ham_message_length, ham)
spam_message_length = spam_message_length.to_frame().reset_index()
# spam_message_length.drop('index', inplace=True, axis=1)
spam_message_normalize = pd.Series(spam_message_length['v2']).max()
spam_message_length.loc[:, 'v2'] /= spam_message_normalize
spam_avg_message_length /= spam_message_normalize
ham_message_length = ham_message_length.to_frame().reset_index()
# ham_message_length.drop('index', inplace=True, axis=1)
ham_message_normalize = pd.Series(ham_message_length['v2']).max()
ham_message_length.loc[:, 'v2'] /= ham_message_normalize
ham_avg_message_length /= ham_message_normalize

fig1, (ax1, ax2) = plt.subplots(1, 2)
ax1.set_title("ham")
ax1.bar(ham_20_words['word'], ham_20_words['count'])
ax2.set_title("spam")
ax2.bar(spam_20_words['word'], spam_20_words['count'])
fig1.autofmt_xdate(rotation=45)
fig1.show()
fig1.savefig(OUTPUT_FOLDER + "/20words.png")

fig2, (ax1, ax2) = plt.subplots(1, 2)
ax1.set_title("ham")
ax2.set_title("spam")
ax1.plot(ham_words_length['word'])
ax1.axhline(ham_avg_words_length, color="r")
ax1.legend(["length", "average"])
ax2.plot(spam_words_length['word'])
ax2.axhline(spam_avg_words_length, color="r")
ax2.legend(["length", "average"])
fig2.show()
fig2.savefig(OUTPUT_FOLDER + "/wordsLength.png")

fig3, (ax1, ax2) = plt.subplots(1, 2)
ax1.set_title("ham")
ax2.set_title("spam")
ax1.plot(ham_message_length['v2'])
ax1.axhline(ham_avg_message_length, color="r")
ax1.legend(["length", "average"])
ax2.plot(spam_message_length['v2'])
ax2.axhline(spam_avg_message_length, color="r")
ax2.legend(["length", "average"])
fig3.show()
fig3.savefig(OUTPUT_FOLDER + "/messageLength.png")
