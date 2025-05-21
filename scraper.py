import requests
from bs4 import BeautifulSoup
import time
from tqdm import tqdm
import json

BASE_URL = "https://www.deeplearning.ai"
BATCH_URL = f"{BASE_URL}/the-batch/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; Bot/1.0; +https://yourdomain.com)"
}

def get_issue_links():
    response = requests.get(BATCH_URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    issues = soup.select("a[href*='/the-batch/'][href*='-']")  # crude but works
    links = list({BASE_URL + a['href'] for a in issues if a['href'].startswith("/the-batch/")})
    return sorted(links)

def scrape_issue(url):
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    articles = []

    for article in soup.select("article"):
        title = article.find("h2") or article.find("h3")
        title_text = title.get_text(strip=True) if title else "No Title"
        summary = article.find("p")
        summary_text = summary.get_text(strip=True) if summary else "No Summary"
        img = article.find("img")
        img_url = img['src'] if img else None

        articles.append({
            "title": title_text,
            "summary": summary_text,
            "url": url,
            "image_url": img_url
        })

    return articles

def scrape_all_issues(max_issues=10, delay=2.0):
    issue_links = get_issue_links()[:max_issues]
    print(f"> There are {len(issue_links)} articles avaible")
    all_articles = []

    for link in tqdm(issue_links, desc="Scraping issues"):
        try:
            articles = scrape_issue(link)
            all_articles.extend(articles)
            time.sleep(delay)  # Be polite!
        except Exception as e:
            print(f"Failed to scrape {link}: {e}")

    return all_articles

if __name__ == "__main__":
    articles = scrape_all_issues(
        max_issues=100,
        delay=1.25,
    )
    with open("the_batch_articles.json", "w") as f:
        json.dump(articles, f, indent=2)