import requests
import os
from bs4 import BeautifulSoup
from time import sleep

PEERS = [
    {"ticker": "PLTR", "cik": "0001321655"},
    {"ticker": "CRWD", "cik": "0001535527"},
    {"ticker": "NET", "cik": "0001477333"},
    {"ticker": "NOW", "cik": "0001373715"},
    {"ticker": "PANW", "cik": "0001327567"},
    {"ticker": "TEAM", "cik": "0001650372"},
    {"ticker": "SNOW", "cik": "0001640147"},
    {"ticker": "DDOG", "cik": "0001561550"},
    {"ticker": "ZS", "cik": "0001713683"},
    {"ticker": "SAIL", "cik": "0002030781"},
    {"ticker": "CYBR", "cik": "0001598110"},
    {"ticker": "OKTA", "cik": "0001660134"},
    {"ticker": "S", "cik": "0001583708"},
    {"ticker": "CHKP", "cik": "0001015922"}
]

HEADERS = {"User-Agent": "IR-Research-Bot contact@yourdomain.com"}

def get_latest_edgar_filing(cik, form_type):
    base_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    r = requests.get(base_url, headers=HEADERS)
    if r.status_code != 200:
        print(f"Failed to fetch submissions for CIK {cik}")
        return None
    data = r.json()
    recent = data.get("filings", {}).get("recent", {})
    for i, form in enumerate(recent.get("form", [])):
        if form == form_type:
            accession = recent["accessionNumber"][i].replace("-", "")
            doc_base = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/"
            index_url = doc_base + "index.json"
            idx_r = requests.get(index_url, headers=HEADERS)
            if idx_r.status_code != 200:
                continue
            idx_data = idx_r.json()
            # Try to find the main filing (HTML or PDF)
            for file in idx_data.get("directory", {}).get("item", []):
                if "10-q" in file["name"].lower() or "10-k" in file["name"].lower():
                    return doc_base + file["name"]
            # Fallback: Return the first HTML in the folder
            for file in idx_data.get("directory", {}).get("item", []):
                if file["name"].endswith(".htm") or file["name"].endswith(".html"):
                    return doc_base + file["name"]
    return None

def download_file(url, dest_path):
    try:
        r = requests.get(url, headers=HEADERS)
        if r.status_code == 200:
            with open(dest_path, "wb") as f:
                f.write(r.content)
            print(f"Downloaded: {dest_path}")
            return True
        else:
            print(f"Failed to download {url}")
            return False
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def get_latest_transcript_yahoo(ticker):
    transcript_url = f"https://finance.yahoo.com/quote/{ticker}/earnings-call-transcript"
    r = requests.get(transcript_url, headers=HEADERS)
    if r.status_code != 200:
        return None
    soup = BeautifulSoup(r.text, "lxml")
    # Yahoo usually puts transcript text in <article> or <section>
    article = soup.find("article") or soup.find("section")
    if article:
        return article.get_text(separator="\n")
    # Fallback: get all paragraph text
    return "\n".join([p.get_text() for p in soup.find_all("p")])

def save_text(content, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    os.makedirs("output", exist_ok=True)
    for peer in PEERS:
        ticker = peer["ticker"]
        cik = peer["cik"]
        peer_dir = os.path.join("output", ticker)
        os.makedirs(peer_dir, exist_ok=True)

        # Download latest 10-Q
        q_url = get_latest_edgar_filing(cik, "10-Q")
        if q_url:
            q_path = os.path.join(peer_dir, "latest_10Q.html")
            download_file(q_url, q_path)
        else:
            print(f"No 10-Q found for {ticker}")

        # Download latest 10-K
        k_url = get_latest_edgar_filing(cik, "10-K")
        if k_url:
            k_path = os.path.join(peer_dir, "latest_10K.html")
            download_file(k_url, k_path)
        else:
            print(f"No 10-K found for {ticker}")

        # Download transcript from Yahoo
        transcript = get_latest_transcript_yahoo(ticker)
        if transcript and len(transcript) > 1000:
            t_path = os.path.join(peer_dir, "latest_transcript.txt")
            save_text(transcript, t_path)
            print(f"Transcript saved for {ticker}")
        else:
            print(f"No transcript found for {ticker}")

        sleep(1) # Respectful delay for SEC and Yahoo

if __name__ == "__main__":
    main()