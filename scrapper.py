import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse

visited_urls = set()
results_found = set()

def extract_matches(text, pattern):
    return set(re.findall(pattern, text))

def is_valid_url(url, base_domain):
    parsed = urlparse(url)
    return parsed.scheme in ['http', 'https'] and base_domain in parsed.netloc

def scrape_pattern_from_url(url, base_domain, pattern, depth=1):
    if url in visited_urls or depth < 0:
        return
    try:
        print(f"🔍 Scanning: {url}")
        visited_urls.add(url)
        response = requests.get(url, timeout=10)
        content = response.text
        matches = extract_matches(content, pattern)
        results_found.update(matches)

        soup = BeautifulSoup(content, 'html.parser')
        for link in soup.find_all('a', href=True):
            next_url = urljoin(url, link['href'])
            if is_valid_url(next_url, base_domain):
                scrape_pattern_from_url(next_url, base_domain, pattern, depth - 1)
    except Exception as e:
        print(f"⚠️ Error: {e}")

# === USER INPUT ===
start_url = input("🌐 Enter the starting URL: ").strip()
depth_input = input("🔁 Enter crawl depth (0 = main page only): ").strip()
search_type = input("🔎 What to search? [email / phone / custom]: ").strip().lower()

# Define the regex pattern
if search_type == "email":
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    output_file = "emails_found.txt"
elif search_type == "phone":
    pattern = r'\b(?:\+407\d{8}|07\d{8})\b'
    output_file = "phone_numbers_found.txt"
elif search_type == "custom":
    pattern = input("🧠 Enter your custom regex: ").strip()
    output_file = "custom_matches.txt"
else:
    print("❌ Invalid search type. Exiting.")
    exit()

try:
    max_depth = int(depth_input)
except ValueError:
    print("❌ Invalid depth. Using default = 1.")
    max_depth = 1

# Start crawling
domain = urlparse(start_url).netloc
scrape_pattern_from_url(start_url, domain, pattern, max_depth)

# Save output
with open(output_file, "w") as f:
    for item in sorted(results_found):
        f.write(item + "\n")

print(f"\n✅ Total matches found: {len(results_found)}")
print(f"📁 Results saved to: {output_file}")
