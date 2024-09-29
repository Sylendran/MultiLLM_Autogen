from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse

def scrape_website(base_url):
    visited_urls = set()
    content_list = []

    def scrape_page(url, depth=0, max_depth=1):

        if depth > max_depth:
            return
        
        if url in visited_urls:
            return
        
        visited_urls.add(url)

        try:
            response = requests.get(url)
            response.raise_for_status()
            html_content = response.text

            soup = BeautifulSoup(html_content, 'lxml')

            # Remove scripts and styles
            for script in soup(["script", "style"]):
                script.extract()

            # Extract text from the webpage
            text = soup.get_text(separator='\n')

            # Clean up the text
            lines = [line.strip() for line in text.splitlines()]
            text = '\n'.join(line for line in lines if line)
            content_list.append(text)

            # Find all internal links
            for link in soup.find_all('a', href=True):
                href = link['href']
                # Build absolute URL
                full_url = urljoin(url, href)
                # Check if the link is internal
                if is_internal_link(base_url, full_url):
                    scrape_page(full_url, depth = depth+1, max_depth=max_depth)

        except Exception as e:
            print(f"Error scraping {url}: {e}")

    def is_internal_link(base_url, url):
        # Compare the netloc (domain) of both URLs
        base_netloc = urlparse(base_url).netloc
        url_netloc = urlparse(url).netloc
        return base_netloc == url_netloc
    
    # Start scraping from the base URL
    scrape_page(base_url)

    # Combine all collected content into one string
    combined_content = '\n\n'.join(content_list)
    return combined_content