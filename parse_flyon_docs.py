import requests
from bs4 import BeautifulSoup
import os
import time
import re
import urllib.parse

BASE_URL = "https://flyonui.com"

def sanitize_filename(title):
    # Remove invalid characters from filename
    return re.sub(r'[<>:"/\\|?*]', '', title).strip()

def fetch_page_details(url):
    # Ensure URL is absolute
    if not url.startswith(('http://', 'https://')):
        url = urllib.parse.urljoin(BASE_URL, url)
    
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('title').get_text() if soup.find('title') else "No title found"
        article = soup.find('article')
        article = article.prettify() if article else "No article found"
        return {
            "title": title,
            "article": article
        }
    else:
        return {
            "title": None,
            "article": f"Failed to retrieve the page. Status code: {response.status_code}"
        }

def get_flyonui_docs_links(url):
    # Ensure URL is absolute
    if not url.startswith(('http://', 'https://')):
        url = urllib.parse.urljoin(BASE_URL, url)
        
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a', href=True)
        flyonui_docs_links = [
            {"title": link.get_text(strip=True), "link": link['href']} 
            for link in links 
            if '/docs' in link['href']
        ]
        return flyonui_docs_links
    else:
        return []

def download_articles():
    # Create directory if it doesn't exist
    docs_dir = "flyonui-docs"
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)

    all_links = get_flyonui_docs_links("/docs/getting-started/quick-start/")
    print(f"Found {len(all_links)} articles to download")

    for idx, link_info in enumerate(all_links, 1):
        title = sanitize_filename(link_info['title'])
        if not title:
            title = f"article_{idx}"
            
        filename = os.path.join(docs_dir, f"{title}.html")
        print(f"Downloading {idx}/{len(all_links)}: {title}")
        
        article_data = fetch_page_details(link_info['link'])
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(article_data['article'])
            
        # Add 1 second delay between requests
        time.sleep(1)
        
    print("Download completed!")

if __name__ == "__main__":
    download_articles()
