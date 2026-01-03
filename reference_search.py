# vim: set foldmethod=indent foldlevel=0:
"""
用谷歌学术搜索参考文献。
主要是校对的时候的辅助工具
这个项目的idea是正则表达式。但实际上的文本很可能有点小问题，比如说et al.的处理，比如说
可能会把.笔误成;。明天可以再写个llm版本的。
"""

import os
import re
import time
import urllib.parse
import webbrowser
from functools import wraps

import ollama
from dotenv import load_dotenv
from ollama import ChatResponse, chat

# 用.env文件储存信息。当然你也可以直接写进来
load_dotenv()
ollama_model = os.getenv("OLLAMA_MODEL_REFERENCE")
RAW_CONTENT = os.getenv("RAW_CONTENT_REFERENCE")


#  RAW_CONTENT = """
#  """


def sleep_after(seconds: float = 1.0):
    """
    Decorator factory: sleep for `seconds` after the wrapped function finishes.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            time.sleep(seconds)
            return result

        return wrapper

    return decorator


def quote_to_article(citation: str) -> str:
    """
    string -> string
    Vancoveour格式，删掉大写字母.以前，以及下一个句号以后的所有内容
    """
    pattern = re.compile(r".*[A-Z]\.")
    match = pattern.search(citation)

    if match:
        remaining = citation[match.end() :].strip()
    else:
        remaining = citation.strip()

    first_dot_index = remaining.find(".")

    if first_dot_index != -1:
        return remaining[:first_dot_index].strip()

    return remaining


def quote_to_article_llm(citation: str) -> str:
    """
    用llm换取更加稳健的parse能力，对诸如;/.和et al.等有更好的支持。
    考虑到任务的轻量和时间不敏感特点，我用了比较省钱的ollama。
    """
    # implementing

    messages = [
        {
            "role": "system",
            "content": (
                """
                *ROLE:* Senior Librarian

                *MISSION OVERVIEW:* Filter the title of the citation from the full
                reference.

                *DETAILED INSTRUCTION:*
                1. Read the  reference text inputed.
                2. Record the place where the title starts.
                3. Record the title, until it ends and other information (journal
                name etc.) begins 
                4. output the title AS IS, without any syntatic notation such as ""s.

                *EXAMPLE PAIRS OF INPUT AND OUTPUT:*
                Given in Pythonic dict:
                {
                "1. Zhang, S., Li, S. & Jordan, M. Artificial intelligence in biomedical
                engineering: a comprehensive review. Nat. Commun. 15, 102–115 (2024).":
                "Artificial intelligence in biomedical engineering: a comprehensive
                review",

                "1. Zhang S, Li S, Jordan M. Artificial intelligence in biomedical 
                engineering: a comprehensive review. Nat Commun. 2024;15(2):102-115.":
                "Artificial intelligence in biomedical engineering: a comprehensive
                review",

                "[1] ZHANG S, LI S, JORDAN M. Artificial intelligence in biomedical 
                engineering: a comprehensive review[J]. Nature Communications, 2024,
                15(2): 102-115.":"Artificial intelligence in biomedical engineering: a 
                comprehensive review"
                }

                """
            ),
        },
        {
            "role": "user",
            "content": citation,
        },
    ]

    options = {"temperature": 0.1}

    try:
        response: ChatResponse = chat(
            model=ollama_model,
            messages=messages,
            options=options,
        )
        # 生产模式
        answer_raw = response.message.content
        return answer_raw.lower().strip().strip('"')
    except ollama.ResponseError as e:
        print("Error:", e.Error)
        return ""


@sleep_after()
def string_search(query: str) -> None:
    """
    string -> IO
    将处理后的标题发送至谷歌学术搜索
    """
    if not query:
        return

    # 对字符串进行 URL 编码
    encoded_query = urllib.parse.quote(query)
    url = f"https://scholar.google.com/scholar?q={encoded_query}"
    print(f"正在搜索文章标题: {query}")
    # 使用系统默认浏览器打开
    webbrowser.open(url)


def split_string(raw_input: str) -> list[str]:
    """
    string -> list[string]
    模拟分割完整的参考文献列表，这里假设每条引用占一行
    """
    # 过滤掉空行
    return [line.strip() for line in raw_input.split("\n") if line.strip()]


def main():
    """
    IO action
    """
    # 读取需要处理的信息
    raw_content = RAW_CONTENT

    # 1. 获得完整的参考文献列表
    list_of_quotation = split_string(raw_content)

    # 2. 将引用转换为文章标题 (map)
    list_of_article = list(map(quote_to_article_llm, list_of_quotation))

    # 3. 执行搜索 (map/loop)
    # 注意：Python 的 map 是惰性的，为了触发 IO，我们需要遍历它
    for article in list_of_article:
        if article:  # 确保不是空字符串
            string_search(article)


if __name__ == "__main__":
    main()
