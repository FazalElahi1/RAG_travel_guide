# Generated from: travel guide.ipynb
# Converted at: 2026-05-11T13:50:05.061Z
# Next step (optional): refactor into modules & generate tests with RunCell
# Quick start: pip install runcell

# # Installing Libraries


import os
os.environ['CUDA_LAUNCH_BLOCKING'] = '1'


!pip install bs4
!pip install wikitextparser
!pip install sentence-transformers
!pip install faiss-cpu

import requests
from bs4 import BeautifulSoup
import wikitextparser as wtp
from transformers import pipeline
import time
import json
import re
import nltk
import string
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize, sent_tokenize
import faiss
from collections import Counter
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sentence_transformers import SentenceTransformer
nltk.download('wordnet')

# # Scraping nomadicMatt.com



HEADERS = {"User-Agent":"Mozilla/5.0"}
BASE = "https://www.nomadicmatt.com"


guide_urls = [
    "https://www.nomadicmatt.com/travel-guides/europe-travel-tips/",
    "https://www.nomadicmatt.com/travel-guides/southeast-asia-travel-tips/",
    "https://www.nomadicmatt.com/travel-guides/",
    "https://www.nomadicmatt.com/travel-guides/caribbean-travel-tips/",
    "https://www.nomadicmatt.com/travel-guides/central-america-travel-tips/"
]

link_cache_path = "guide_article_links.json"

if os.path.exists(link_cache_path):
    with open(link_cache_path, "r", encoding="utf-8") as f:
        guide_to_links = json.load(f)
else:
    guide_to_links = {}

def is_valid_article_url(href):
    return (
        href and
        href.startswith("https://www.nomadicmatt.com/travel-guides/") and
        href.count("/") > 4 and
        not any(x in href for x in ["#", "mailto:", ".pdf"])
    )

for guide_url in guide_urls:
    if guide_url in guide_to_links:
        print(f"[CACHE] Skipping already scanned: {guide_url}")
        continue

    print(f"[FETCH] Scraping guide: {guide_url}")
    try:
        res = requests.get(guide_url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        links = set()

        for a in soup.find_all("a", href=True):
            href = a['href'].strip()
            if is_valid_article_url(href):
                links.add(href)

        guide_to_links[guide_url] = sorted(links)

    except Exception as e:
        print(f"Error scraping {guide_url}: {e}")

with open(link_cache_path, "w", encoding="utf-8") as f:
    json.dump(guide_to_links, f, indent=2)

print(f"Finished. Saved article links in: {link_cache_path}")


link_cache_path = "guide_article_links.json"
if not os.path.exists(link_cache_path):
    raise FileNotFoundError(f"{link_cache_path} not found.")
with open(link_cache_path, "r", encoding="utf-8") as f:
    guide_to_links = json.load(f)

all_article_urls = [url for urls in guide_to_links.values() for url in urls]
print(f"Total article links found: {len(all_article_urls)}")

output_dir = "normadicMatt_articles"
os.makedirs(output_dir, exist_ok=True)

def clean_filename(text):
    return re.sub(r'[\\/*?:"<>|]', "_", text).strip().replace(" ", "_")[:100]

def show_article_structure(url, index):
    print(f"\nScraping: {url}")
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        if "nomadicmatt.com" not in res.url:
            print(f"Redirected to non-target domain: {res.url}")
            return
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return

    soup = BeautifulSoup(res.text, "html.parser")

    title_tag = soup.find("h1")
    if not title_tag:
        print(f"No title found — skipping: {url}")
        return

    title = title_tag.get_text(strip=True).strip()
    if not title:
        print(f"No title found — skipping: {url}")
        return

    filename = clean_filename(title)

    content_div = soup.find("div", class_="entry-content") or soup.find("div", class_="kt-inside-inner-col")
    if not content_div:
        print(f"No content found — skipping: {url}")
        return

    sections = {"Introduction": []}
    current = "Introduction"

    for tag in content_div.find_all(["h2", "h3", "h4", "h5", "p", "ul"]):
        if tag.name in ["h2", "h3", "h4", "h5"]:
            current = tag.get_text(strip=True) or current
            sections.setdefault(current, [])
        elif tag.name == "p":
            text = tag.get_text(strip=True)
            if text:
                sections[current].append(text)
        elif tag.name == "ul" and "wp-block-list" in (tag.get("class") or []):
            links, items = [], []
            for li in tag.find_all("li"):
                a = li.find("a", href=True)
                if a:
                    links.append({"text": a.get_text(strip=True), "href": a["href"]})
                else:
                    t = li.get_text(strip=True)
                    if t:
                        items.append(t)
            block = {}
            if links:
                block["links"] = links
            if items:
                block["items"] = items
            if block:
                sections[current].append(block)

    article_data = {
        "title": title,
        "sections": sections
    }

    if not any(sections.values()):
        print("No meaningful sections parsed — skipping file save.")
        return

    file_path = os.path.join(output_dir, f"{filename}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(article_data, f, indent=2, ensure_ascii=False)
    print(f"Saved: {file_path}")
    time.sleep(1)


for idx, url in enumerate(all_article_urls, start=1):
    print(f"\n======= [{idx}] =======")
    show_article_structure(url, idx)
    time.sleep(1)


with open("normadicMatt_articles/Mexico_Travel_Guide.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(json.dumps(data, indent=2, ensure_ascii=False))


# # Scraping Guide to Pakistan


main_url = "https://guidetopakistan.pk/"

response = requests.get(main_url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")

    extracted_links = []

    for item in soup.select(".elementor-image-box-title a"):
        link = item['href']
        extracted_links.append(link)

    print("Extracted Links:")
    for link in extracted_links:
        print(link)
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")


output_directory = "guide_to_pakistan_articles"
os.makedirs(output_directory, exist_ok=True)

def extract_paragraphs(content_div):
    paragraphs = []
    for elem in content_div.descendants:
        if elem.name in ["p", "b", "h4"] or (elem.name is None and str(elem).strip()):
            for tag in getattr(elem, 'find_all', lambda *_: [])(["a", "span"]):
                tag.unwrap()
            text = elem.get_text(strip=True) if hasattr(elem, "get_text") else str(elem).strip()
            if text:
                paragraphs.append(text)
    return paragraphs

def scrape_tour_pages(tour_urls):

    for url in tour_urls:
        try:
            res = requests.get(url)
            res.raise_for_status()
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")
            continue

        page = BeautifulSoup(res.text, "html.parser")

        title_tag = page.find("h1")
        title = title_tag.get_text(strip=True) if title_tag else "tour_page"


        filename =clean_filename(title)
        file_path = os.path.join(output_directory, f"{filename}.json")

        tabs = []
        for tab_title in page.select("div.elementor-tab-title"):
            title_id = tab_title.get("id")
            title_tag = tab_title.select_one("a.elementor-toggle-title")
            if not title_id or not title_tag:
                continue

            heading = title_tag.get_text(strip=True)
            content_id = title_id.replace("title", "content")
            content_div = page.find("div", id=content_id)

            if content_div:
                paragraphs = extract_paragraphs(content_div)
                if paragraphs:
                    tabs.append({"heading": heading, "paragraphs": paragraphs})

        tour_data = {"title": title, "tabs": tabs}

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(tour_data, f, indent=2, ensure_ascii=False)
        print(f"Saved tour: {file_path}")
        time.sleep(1)


def extract_content(page, banned_phrases):
    content = []
    for tag in page.find_all(["h1", "h2", "h3", "p"]):
        text = tag.get_text(strip=True)
        if text and text not in banned_phrases:
            if tag.name in ["h1", "h2", "h3"]:
                content.append(f"\n{text}\n")
            else:
                content.append(text)
    return content

def extract_sections(page):
    sections = []
    for heading_tag in page.find_all(["h2", "h3"]):
        heading = heading_tag.get_text(strip=True)
        paragraph = ""

        next_p = heading_tag.find_next_sibling()
        while next_p and next_p.name != "p":
            next_p = next_p.find_next_sibling()
        if next_p and next_p.name == "p":
            paragraph = next_p.get_text(strip=True)

        if heading:
            sections.append({"heading": heading})
        if paragraph:
            sections.append({"paragraph": paragraph})
    return sections

def scrape_destination_pages(main_url):
    response = requests.get(main_url)
    if response.status_code != 200:
        print("Failed to load main page.")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    destination_links = [item['href'] for item in soup.select(".elementor-image-box-title a") if "destination" in item['href']]

    banned_phrases = {
        "Customised Tour Package", "Corporate Tour", "HoneyMoon Package",
        "Pakistan Cultural and Religious tour", "Gilgit Baltistan",
        "Khyber Pakhtunkhwa", "Islamabad", "Punjab", "Sindh",
        "Balochistan", "Kashmir", "@Copyright 2025 Guide To Pakistan | Powered by CyberX Studio",
        "WhatsApp us", "Recent posts", "Get up to 30% off on all customized Tour packages."
    }

    for url in destination_links:

        try:
            res = requests.get(url)
            res.raise_for_status()
            page = BeautifulSoup(res.text, "html.parser")
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")
            continue

        title_tag = page.find("h1")
        title = title_tag.get_text(strip=True) if title_tag else url.split("/")[-2]


        content = extract_content(page, banned_phrases)
        sections = extract_sections(page)

        filename =clean_filename(title)
        file_path = os.path.join("guide_to_pakistan_articles", f"{filename}.json")

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({
                "title": title,
                "content": content,
                "sections": sections
            }, f, indent=2, ensure_ascii=False)

        print(f"Saved destination: {file_path}")
        time.sleep(1)


if __name__ == "__main__":
    main_url = "https://guidetopakistan.pk/"
    tour_urls = [
    "https://guidetopakistan.pk/tour/sharan-honeymoon-tour-package/",
    "https://guidetopakistan.pk/tour/chitral-honeymoon-tour-package/",
    "https://guidetopakistan.pk/tour/naran-honeymoon-tour-package/",
    "https://guidetopakistan.pk/tour/kashmir-honeymoon-tour-package/",
    "https://guidetopakistan.pk/tour/murree-honeymoon-tour-package/",
    "https://guidetopakistan.pk/tour/hunza-skardu-tour/",
    "https://guidetopakistan.pk/tour/golf-tour/"
]
    tour_data = scrape_tour_pages(tour_urls)
    destination_data = scrape_destination_pages(main_url)

    print("\n All pages scraped and saved to folder guide_to_pakistan_articles.")


with open("guide_to_pakistan_articles/Sharan_Honeymoon_Tour_Package.json", "r", encoding="utf-8") as f:
    answer = json.load(f)

print(json.dumps(answer, indent=2, ensure_ascii=False))


# # Scraping wikivoyage


output_dir = "wikivoyage_articles"
os.makedirs(output_dir, exist_ok=True)

API_URL = "https://en.wikivoyage.org/w/api.php"
HEADERS = {
    "User-Agent": "RAGDataCollector/1.0 (contact@example.com)" # custom user-agent string
}

def get_wikitext(title, retries=3, delay=3):
    for attempt in range(retries):
        try:
            resp = requests.get(API_URL, headers=HEADERS, params={
                "action": "query",
                "format": "json",
                "titles": title,
                "prop": "revisions",
                "rvprop": "content",
                "rvslots": "*",
                "formatversion": "2"
            })
            resp.raise_for_status()
            pages = resp.json()["query"]["pages"]
            return pages[0]["revisions"][0]["slots"]["main"]["content"]
        except requests.exceptions.HTTPError as e:
            if resp.status_code == 429:
                print("Rate limited. Retrying after delay...")
                time.sleep(delay)
            else:
                print(f"HTTP error for {title}: {e}")
                return None
        except Exception as e:
            print(f"Error fetching {title}: {e}")
            return None
    return None

def parse_sections(wikitext):
    doc = wtp.parse(wikitext)
    sections = {}
    for sect in doc.get_sections(include_subsections=True):
        title = (sect.title or "").strip("=").strip() or "Introduction"
        sec_data = {"text": sect.plain_text().strip()}

        lists = [lst.items for lst in sect.get_lists()]
        if lists:
            sec_data["lists"] = lists

        tables = [tbl.data() for tbl in sect.tables]
        if tables:
            sec_data["tables"] = tables

        sections[title] = sec_data
    return sections

def scrape_countries(countries):
    for country in countries:
        print(f"\nScraping: {country}")
        wikitext = get_wikitext(country)
        if not wikitext:
            print(f"Skipping {country} due to failed fetch.")
            continue

        data = parse_sections(wikitext)
        filename = country.lower().replace(" ", "_") + ".json"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved to: {filepath}")
        time.sleep(2)

if __name__ == "__main__":
    countries = [
        "Pakistan", "Turkey", "England", "Japan", "Australia",
        "United States of America", "Germany", "France", "India",
        "South Africa", "Saudi Arabia", "Iran", "China"
    ]
    scrape_countries(countries)


with open("wikivoyage_articles/united_states_of_america.json", "r", encoding="utf-8") as f:
    wiki = json.load(f)

print(json.dumps(wiki, indent=2, ensure_ascii=False))


# # RAG


# ## Preprocessing data of files


nltk.download("punkt")
nltk.download("punkt_tab")
nltk.download("stopwords")
nltk.download("omw-1.4")

stop_words = set(stopwords.words("english"))

lemmatizer = WordNetLemmatizer()

def clean_html(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(separator=" ", strip=True)


def remove_duplicate_sentences(text):
    sentences = sent_tokenize(text)
    seen = set()
    unique_sentences = []

    for s in sentences:
        s_clean = s.strip()
        s_key = s_clean.lower()
        if s_clean and s_key not in seen:
            seen.add(s_key)
            unique_sentences.append(s_clean)

    return " ".join(unique_sentences)

def preprocess_text_for_chunking(text):
    text = clean_html(text)
    text = text.replace("’", "'").replace("“", '"').replace("”", '"')
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    text = re.sub(r'([.,;:!?])([^\s])', r'\1 \2', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return remove_duplicate_sentences(text)

def preprocess_text_for_query_expansion(text):
    text = clean_html(text)
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))

    tokens = nltk.word_tokenize(text)
    clean_tokens = []
    prev_token = None

    for token in tokens:
        if token in stop_words:
            continue
        lemma = lemmatizer.lemmatize(token)
        if lemma != prev_token:
            clean_tokens.append(lemma)
            prev_token = lemma

    return " ".join(clean_tokens)


def extract_text(data):
    text_chunks = []

    if "sections" in data and isinstance(data["sections"], dict):
        for section in data["sections"].values():
            if isinstance(section, list):
                for item in section:
                    if isinstance(item, str):
                        text_chunks.append(item)
                    elif isinstance(item, dict):
                        if "text" in item and isinstance(item["text"], str):
                            text_chunks.append(item["text"])
                        if "items" in item and isinstance(item["items"], list):
                            text_chunks.extend(
                                i for i in item["items"] if isinstance(i, str)
                            )
            elif isinstance(section, str):
                text_chunks.append(section)

    elif isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict):
                if "text" in value and isinstance(value["text"], str):
                    text_chunks.append(value["text"])
                if "items" in value and isinstance(value["items"], list):
                    text_chunks.extend([i for i in value["items"] if isinstance(i, str)])
                if "paragraphs" in value and isinstance(value["paragraphs"], list):
                    text_chunks.extend([p for p in value["paragraphs"] if isinstance(p, str)])
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        text_chunks.append(item)
                    elif isinstance(item, dict):
                        text_chunks.extend(extract_text(item).split('\n'))
            elif isinstance(value, str):
                text_chunks.append(value)

    elif isinstance(data, list):
        for item in data:
            if isinstance(item, str):
                text_chunks.append(item)
            elif isinstance(item, dict):
                text_chunks.extend(extract_text(item).split('\n'))

    return "\n".join(text_chunks)



def preprocess_all_articles(base_dirs):
    all_docs = []
    total_files = 0
    skipped_files = []

    for folder in base_dirs:
        print(f"\nProcessing folder: {folder}")
        for filename in os.listdir(folder):
            if not filename.lower().endswith(".json"):
                continue

            total_files += 1
            file_path = os.path.join(folder, filename)

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                title = data.get("title", filename.replace(".json", ""))
                raw_text = extract_text(data)
                cleaned_text = preprocess_text_for_chunking(raw_text)

                if len(cleaned_text.split()) > 50:
                    all_docs.append({
                        "title": title.strip(),
                        "text": cleaned_text
                    })
                else:
                    skipped_files.append((filename, "Too short after cleaning"))

            except json.JSONDecodeError:
                skipped_files.append((filename, "Invalid JSON"))
            except Exception as e:
                skipped_files.append((filename, f"Other error: {str(e)}"))

    print(f"\nPreprocessed: {len(all_docs)} / {total_files} files")
    if skipped_files:
        print("\nSkipped Files:")
        for name, reason in skipped_files:
            print(f" - {name}: {reason}")

    return all_docs

base_dirs = [
    "/content/guide_to_pakistan_articles",
    "/content/normadicMatt_articles",
    "/content/wikivoyage_articles"
]

docs = preprocess_all_articles(base_dirs)

# 


output_path = "/content/cleaned_docs.jsonl"

with open(output_path, "w", encoding="utf-8") as f:
    for doc in docs:
        json.dump(doc, f, ensure_ascii=False)
        f.write("\n")

print(f"Saved {len(docs)} documents to {output_path}")


# # Creating Chunks of Data


from nltk.tokenize import sent_tokenize

def split_into_chunks(text, chunk_size=400, overlap=100, max_words=500):
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = []
    current_len = 0

    for sentence in sentences:
        words = sentence.split()
        sent_len = len(words)

        if current_len + sent_len > chunk_size:
            if current_chunk:
                chunk_text = " ".join(current_chunk)
                if len(chunk_text.split()) <= max_words:
                    chunks.append(chunk_text)
                else:
                    chunks.append(" ".join(chunk_text.split()[:max_words]))

            overlap_sentences = []
            total_overlap = 0
            for prev_sentence in reversed(current_chunk):
                w_len = len(prev_sentence.split())
                if total_overlap + w_len <= overlap:
                    overlap_sentences.insert(0, prev_sentence)
                    total_overlap += w_len
                else:
                    break

            current_chunk = overlap_sentences + [sentence]
            current_len = total_overlap + sent_len
        else:
            current_chunk.append(sentence)
            current_len += sent_len

    if current_chunk:
        chunk_text = " ".join(current_chunk)
        if len(chunk_text.split()) <= max_words:
            chunks.append(chunk_text)
        else:
            chunks.append(" ".join(chunk_text.split()[:max_words]))

    return chunks


def prepare_chunked_docs(all_docs, chunk_size=400, overlap=100, max_words=500):
    chunked = []
    for doc in all_docs:
        title = doc.get('title', 'unknown')
        text = doc.get('text', '')
        chunks = split_into_chunks(text, chunk_size, overlap, max_words)

        for idx, chunk in enumerate(chunks):
            chunked.append({
                "title": title,
                "chunk_id": f"{title.replace(' ', '_').lower()}_{idx}",
                "text": chunk
            })

    return chunked


# # Saving chunking data in file


def save_chunked_data(chunked_docs, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        for entry in chunked_docs:
            json.dump(entry, f)
            f.write("\n")


if __name__ == "__main__":

    chunked_docs = prepare_chunked_docs(docs, chunk_size=400, overlap=100)

    save_chunked_data(chunked_docs, "chunked_documents.jsonl")

    print(f"\nChunked documents saved to 'chunked_documents.jsonl'")


# ## Embedding, Indexing, Retreiving


def embed_texts(texts, model):
    emb = model.encode(texts, show_progress_bar=True)
    faiss.normalize_L2(emb)
    return emb

def build_index(embeddings):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    return index

def retrieval_top_k(query_text, model, index, documents, k=4):
    query_emb = model.encode([query_text], normalize_embeddings=True)
    scores, indices = index.search(query_emb, k)
    return indices[0], scores[0]



# ## Summarizing


from transformers import BartTokenizer, BartForConditionalGeneration

bart_tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
bart_model = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")

def summarize_text(text, model=bart_model, tokenizer=bart_tokenizer, max_input_length=1024, max_output_length=250):
    input_text = text.strip().replace("\n", " ")
    inputs = tokenizer.encode(input_text, return_tensors="pt", max_length=max_input_length, truncation=True)

    summary_ids = model.generate(inputs, max_length=max_output_length, num_beams=4, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary.strip()


def compute_term_distribution(docs):
    tokens = []
    for doc in docs:
        cleaned = preprocess_text_for_query_expansion(doc)
        tokens.extend(cleaned.split())

    total = len(tokens)
    if total == 0:
        return {}

    freqs = Counter(tokens)
    return {term: freq / total for term, freq in freqs.items()}


def query_expansion(original_query, top_docs, top_n=5, prob_threshold=0.01):
    if not top_docs:
        return original_query

    old_terms = set(preprocess_text_for_query_expansion(original_query).split())
    term_probs = compute_term_distribution(top_docs)

    filtered = [
        (term, prob) for term, prob in term_probs.items()
        if term not in old_terms and prob > prob_threshold
    ]

    top_terms = sorted(filtered, key=lambda x: x[1], reverse=True)[:top_n]

    if not top_terms:
        return original_query

    expansion = " ".join(t for t, _ in top_terms)
    expanded_query = original_query + " " + expansion

    print(f"Query expanded with: {[t for t, _ in top_terms]}")
    return expanded_query


def load_jsonl(file_path):
    titles, texts = [], []
    with open(file_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            obj = json.loads(line)
            text = obj.get("text", "").strip()
            if not text:
                continue

            title = obj.get("title", "").strip()
            if not title or title.lower() == "untitled":
                preview = " ".join(text.split()[:8]) + "..."
                title = f"[Preview] {preview}"

            titles.append(title)
            texts.append(text)
    return titles, texts

def re_retrieve_and_answer(summary, query, index, embedding_model, corpus_chunks, summarizer_fn, titles=None, top_k=5):
    print("\n=== Re-Retrieval Phase ===")

    reformulated_query = summary
    query_embedding = embedding_model.encode(reformulated_query, convert_to_tensor=True)
    D, I = index.search(query_embedding.cpu().numpy().reshape(1, -1), top_k)
    top_docs_reretrieved_indices = I[0].tolist()

    retrieved_docs = []
    top_chunks = []

    for idx in top_docs_reretrieved_indices:
        if idx < len(corpus_chunks):
            top_chunks.append(corpus_chunks[idx])
            retrieved_docs.append({
                "title": titles[idx] if titles else f"Chunk {idx}",
                "text": corpus_chunks[idx],
                "similarity": float(D[0][top_docs_reretrieved_indices.index(idx)])
            })

    print("\n=== Re-Retrieved Documents with Summaries ===")
    per_chunk_summaries = []
    for i, doc in enumerate(retrieved_docs):
        print(f"\nDocument {i+1}:")
        print(f"Title: {doc['title']}")
        print(f"Score: {doc['similarity']:.4f}")
        summary = summarizer_fn(doc['text'])
        per_chunk_summaries.append(summary)
        print(summary)

    combined_summary_input = " ".join(per_chunk_summaries)
    final_summary = summarizer_fn(combined_summary_input)


    return final_summary.strip() if final_summary.strip() else "No relevant summary could be generated."


# # Main function


from collections import OrderedDict

if __name__ == "__main__":

    model = SentenceTransformer("multi-qa-mpnet-base-dot-v1", device='cuda')

    file_path = "chunked_documents.jsonl"
    titles, texts = load_jsonl(file_path)
    embeddings = embed_texts(texts, model)
    index = build_index(embeddings)

    while True:
        query = input("\nAsk your travel question (or type 'quit' to exit): ")
        if query.lower() in ['quit', 'exit']:
            print("Exiting.")
            break

        total_start = time.time()

        # Step 1: Retrieval
        retrieval_start = time.time()
        initial_indices, scores = retrieval_top_k(query, model, index, texts, k=5)

        top_docs = []
        retrieved_docs = []

        for pos, i in enumerate(initial_indices[:5]):

            if i < len(titles) and i < len(texts):
                top_docs.append(texts[i])
                retrieved_docs.append({
                    "title": titles[i],
                    "text": texts[i],
                    "similarity": float(scores[pos])
            })
        retrieval_time = time.time() - retrieval_start

        if not retrieved_docs:
            print("No relevant documents found.")
            continue

        # Step 2: Query Expansion
        query_expansion_start = time.time()
        print("\nExpanded Query:")
        expanded_query = query_expansion(query, top_docs)
        print(expanded_query)
        query_expansion_time = time.time() - query_expansion_start

        # Step 3: Summarization
        print("\n Retrieving Documents with Summaries.............")
        summarization_start = time.time()
        chunk_summaries = [summarize_text(doc) for doc in top_docs]
        chunk_summaries = list(OrderedDict.fromkeys(chunk_summaries))  # Deduplicate


        for i, doc in enumerate(retrieved_docs):
            print(f"Document {i+1}:")
            print(f"Title: {doc['title']}")
            print(f"Score: {doc['similarity']:.4f}")
            print(chunk_summaries[i])
            print("\n")

        combined_summary_text = " ".join(chunk_summaries)
        if len(combined_summary_text.split()) > 100:
            refined_summary = summarize_text(combined_summary_text)
        else:
            refined_summary = combined_summary_text
        summarization_time = time.time() - summarization_start

        reretrieve_start = time.time()
        final_answer = re_retrieve_and_answer(
            summary=refined_summary,
            query=query,
            index=index,
            embedding_model=model,
            corpus_chunks=texts,
            summarizer_fn=summarize_text,
            titles= titles
        )
        reretrieve_time = time.time() - reretrieve_start

        print("\n=== Final Answer After Re-retrieval and Summarization ===")
        print(final_answer)

        total_time = time.time() - total_start

        # Latency report
        print("\n=== Latency Report ===")
        print(f"Retrieval time:        {retrieval_time:.2f} sec")
        print(f"Query expansion time:  {query_expansion_time:.2f} sec")
        print(f"Summarization time:    {summarization_time:.2f} sec")
        print(f"Re-retrieval time:     {reretrieve_time:.2f} sec")
        print(f"Total time:            {total_time:.2f} sec")