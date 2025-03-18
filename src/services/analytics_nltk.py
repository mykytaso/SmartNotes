import string

import nltk
from nltk import word_tokenize, FreqDist
from nltk.util import ngrams

from config import get_settings

settings = get_settings()


# # Ensure NLTK looks for data in this directory
nltk.data.path.append(settings.NLTK_DATA_PATH)
nltk.download("punkt_tab", download_dir=str(settings.NLTK_DATA_PATH))


async def get_common_words_phrases(notes, max_phrase_length: int):

    # Tokenize the content
    word_tokenized = word_tokenize(" ".join(notes))

    # Initialize a frequency distribution
    fd = FreqDist()

    # For each possible phrase length from 1 to max_phrase_length (in this case 3)
    for n in range(1, max_phrase_length + 1):
        # Generate n-grams and update frequency distribution
        for phrase in ngrams(word_tokenized, n):
            fd[" ".join(phrase)] += 1

    return {
        common: appearance
        for common, appearance in fd.most_common()
        if appearance > 1
        and common not in string.punctuation
        and common
        not in [
            "'",
            "’",
            "—",
        ]
    }
