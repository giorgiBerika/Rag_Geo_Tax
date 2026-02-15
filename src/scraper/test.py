from info_scraper import InfoScraper
from urllib.parse import urljoin
import json
scraper = InfoScraper()

search_url = "https://infohub.rs.ge/ka/search?types=1&types=15&types=16&types=17&types=75&types=76&types=77"

documents = scraper.scrape_all_documents(search_url, max_documents=20)



successful = [d for d in documents if d.get('download_status') == 'success']
failed = [d for d in documents if d.get('download_status') != 'success']



if successful:
 
    for i, doc in enumerate(successful[:5], 1):
        print(f"  {i}. {doc['doc_number']} - {doc['date']}")
    if len(successful) > 5:
        print(f"  and {len(successful) - 5} more")


