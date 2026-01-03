from reference_search import quote_to_article_llm, split_string

RAW_CONTENT = """
1. Zhang, S., Li, S. & Jordan, M. Artificial intelligence in biomedical engineering: a comprehensive review. Nat. Commun. 15, 102–115 (2024).
1. Zhang S, Li S, Jordan M. Artificial intelligence in biomedical engineering: a comprehensive review. Nat Commun. 2024;15(2):102-115.
[1] ZHANG S, LI S, JORDAN M. Artificial intelligence in biomedical engineering: a comprehensive review[J]. Nature Communications, 2024, 15(2): 102-115.
"""

#  RAW_ANSWER = """
#  artificial intelligence in biomedical engineering: a comprehensive review
#  artificial intelligence in biomedical engineering: a comprehensive review
#  artificial intelligence in biomedical engineering: a comprehensive review
#  """

nature, vancouver, GBT = split_string(RAW_CONTENT)
title = "artificial intelligence in biomedical engineering: a comprehensive review"
#  nature_title, vancouver_title, GBT_title = split_string(RAW_ANSWER)


def test_llm():
    assert (
        quote_to_article_llm(nature)
        == "artificial intelligence in biomedical engineering: a comprehensive review"
    )


def test_vancouver():
    assert (
        quote_to_article_llm(vancouver)
        == "artificial intelligence in biomedical engineering: a comprehensive review"
    )


def test_GBT():
    assert (
        quote_to_article_llm(GBT)
        == "artificial intelligence in biomedical engineering: a comprehensive review"
    )
