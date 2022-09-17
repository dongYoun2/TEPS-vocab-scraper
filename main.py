from typing import Dict
import requests
from bs4 import BeautifulSoup
from decouple import config

NOTION_KEY = config("NOTION_KEY")


def get_html(url: str) -> str:
    res = requests.get(url)
    res.encoding = "utf-8"
    return res.text


def parse_vocab(html: str):
    soup = BeautifulSoup(html, "html.parser")
    english_soups = [s.text.strip() for s in soup.find_all(class_="name")]
    korean_soups = [s.text.strip() for s in soup.find_all(class_="mean")]
    # TODO: 두 리스트 길이 다를 시 처리 필요
    vocab_dict = dict(reversed(list(zip(english_soups, korean_soups))))

    return vocab_dict


def insert_vocabs(table_id: str, vocab_dict: dict):
    def construct_vocab_payload(vocab_en: str, vocab_ko: str):
        return {
            "parent": {"database_id": table_id},
            "properties": {
                "title": {"title": []},
                "영단어": {"rich_text": [{"text": {"content": vocab_en}}]},
                "단어 뜻": {"rich_text": [{"text": {"content": vocab_ko}}]},
            },
        }

    url = "https://api.notion.com/v1/pages"
    headers = {"Authorization": NOTION_KEY, "Notion-Version": "2021-08-16"}
    payloads = [construct_vocab_payload(en, ko) for en, ko in vocab_dict.items()]

    for payload in payloads:
        res = requests.post(url, json=payload, headers=headers)
        if res.status_code >= 400:
            print(res.status_code)
            return


NOTION_DB_ID = config("NOTION_VOCAB_DB_ID")
FETCH_URL = config("VOCAB_FETCH_URL")

text = get_html(FETCH_URL)
vocab_dict = parse_vocab(text)
insert_vocabs(NOTION_DB_ID, vocab_dict)
