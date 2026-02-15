# src/scraper/infohub_scraper.py

import requests
from bs4 import BeautifulSoup
from pathlib import Path 
import time
import json 
import logging
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urljoin


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__) 


class InfoScraper:
    def __init__(self, base_url="https://infohub.rs.ge"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        self.pdf_dir = Path("data/raw/pdfs")
        self.pdf_dir.mkdir(parents=True, exist_ok=True)

        self.metadata_file = Path("data/raw/metadata.json")

        logger.info("InfoHubScraper initialized")
        logger.info(f"PDFs will be saved to: {self.pdf_dir}")
    
    def fetch_page_with_selenium(self, url):
       
        try:
            logger.info(f"Fetching with Selenium: {url}")
            
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            driver.get(url)
            
            logger.info("Waiting for page to load...")
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            time.sleep(3)
            
            page_source = driver.page_source
            driver.quit()
            
            logger.info("Successfully fetched page with Selenium!")
            
            soup = BeautifulSoup(page_source, 'html.parser')
            return soup
            
        except Exception as e:
            logger.error(f"Selenium fetch failed: {e}")
            if 'driver' in locals():
                driver.quit()
            return None
    
    def parse_document_cards(self, soup):
       
        documents = []
        
        cards = soup.find_all('div', class_=lambda x: x and 'card' in str(x).lower())
        
        if not cards:
            cards = soup.find_all('div', recursive=True)
            cards = [card for card in cards if card.find('a')]
        
        logger.info(f"Found {len(cards)}  cards")
        
        for card in cards:
            try:
                link = card.find('a', href=True)
                
                if not link:
                    continue
                
                href = link.get('href')
                
                if not href or href.startswith('#') or href.startswith('http'):
                    continue
                
                doc_info = {
                    'detail_url': href,
                    'title': self._extract_title_from_card(card),
                    'doc_number': self._extract_doc_number(card),
                    'date': self._extract_date_from_card(card),
                    'description': self._extract_description_from_card(card)
                }
                
                documents.append(doc_info)
                
            except Exception as e:
                logger.warning(f"Error parsing card: {e}")
                continue
        
        logger.info(f"Extracted {len(documents)} document cards")
        return documents
    
    def _extract_title_from_card(self, card):
       
        title_elem = (
            card.find('h1') or 
            card.find('h2') or 
            card.find('h3') or
            card.find(class_=lambda x: x and 'title' in str(x).lower())
        )
        
        if title_elem:
            return title_elem.get_text(strip=True)
        
        link = card.find('a')
        if link:
            return link.get_text(strip=True)
        
        return "Untitled"
    
    def _extract_doc_number(self, card):
        text = card.get_text()
        
        match = re.search(r'N\s*(\d+)', text)
        if match:
            return f"N {match.group(1)}"
        
        match = re.search(r'#:\s*(\d+)', text)
        if match:
            return match.group(1)
        
        return None
    
    def _extract_date_from_card(self, card):
        
        text = card.get_text()
        
        date_pattern = r'\d{1,2}\s+\S+\s+\d{4}'
        match = re.search(date_pattern, text)
        
        if match:
            return match.group(0)
        
        return None
    
    def _extract_description_from_card(self, card):
       
        desc_elem = card.find('p') or card.find(class_=lambda x: x and 'description' in str(x).lower())
        
        if desc_elem:
            return desc_elem.get_text(strip=True)
        
        return None
    
    def get_pdf_link_from_detail_page(self, detail_url):
       
        if not detail_url.startswith('http'):
            full_url = urljoin(self.base_url, detail_url)
        else:
            full_url = detail_url
        
        try:
            logger.info(f"Starting downloa d for :  {full_url}")
            
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            download_dir = str(Path("data/temp_downloads").absolute())
            Path(download_dir).mkdir(parents=True, exist_ok=True)
            
            prefs = {
                "download.default_directory": download_dir,
                "download.prompt_for_download": False,
                "plugins.always_open_pdf_externally": True
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            wait = WebDriverWait(driver, 20)
            
            driver.get(full_url)
            
            time.sleep(3)
            
            
            initial_files = set(Path(download_dir).glob("*.pdf"))
            
            try:
                download_btn = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//div[contains(@class, 'cursor-pointer') and contains(@class, 'gap-1-5') and .//rs-icon[@key='download-cloud']]")
                ))
                
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", download_btn)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", download_btn)
               
                time.sleep(2)
                
            except Exception as e:

                driver.quit()
                return None
            
            try:
                wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(text(), 'Adobe PDF')]")
                ))
                
                pdf_option = driver.find_element(By.XPATH, 
                    "//div[contains(text(), 'Adobe PDF')]/ancestor::div[contains(@class, 'cursor-pointer')] | //div[contains(text(), 'Adobe PDF')]"
                )
                driver.execute_script("arguments[0].click();", pdf_option)
             
                time.sleep(1)
                
            except Exception as e:
                logger.warning(f" not select PDF: {e}")
            
            try:
                final_btn = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(@class, 'bg-blue-primary') and contains(text(), 'ჩამოტვირთვა')]")
                ))
                driver.execute_script("arguments[0].click();", final_btn)
               
                time.sleep(5)
                
            except Exception as e:
                try:
                    modal = driver.find_element(By.CLASS_NAME, "cdk-overlay-pane")
                    buttons = modal.find_elements(By.TAG_NAME, "button")
                    
                    for btn in buttons:
                        if 'ჩამოტვირთვა' in btn.text:
                            driver.execute_script("arguments[0].click();", btn)
                           
                            time.sleep(5)
                            break
                    else:
                        raise Exception("No download button found")
                        
                except Exception as e2:
                    driver.quit()
                    return None
            
            time.sleep(2)
            current_files = set(Path(download_dir).glob("*.pdf"))
            new_files = current_files - initial_files
            
            if new_files:
                downloaded_file = list(new_files)[0]
                driver.quit()
                return str(downloaded_file)
            else:
                crdownload_files = list(Path(download_dir).glob("*.crdownload"))
                if crdownload_files:
                    time.sleep(10)
                    
                    current_files = set(Path(download_dir).glob("*.pdf"))
                    new_files = current_files - initial_files
                    
                    if new_files:
                        downloaded_file = list(new_files)[0]
                        driver.quit()
                        return str(downloaded_file)
                
                driver.quit()
                return None
            
        except Exception as e:
            if 'driver' in locals():
                driver.quit()
            return None
    
    def scrape_all_documents(self, search_url, max_documents=None):
       
        
        soup = self.fetch_page_with_selenium(search_url)
        
        if not soup:
            return []
        
        documents = self.parse_document_cards(soup)
        
        if not documents:
            return []
        
        
        if max_documents:
            documents = documents[:max_documents]
        
        
        successful_downloads = 0
        failed_downloads = 0
        
        for i, doc in enumerate(documents, 1):
            logger.info(f"\n[{i}/{len(documents)}] Processing: {doc['doc_number']}")
            
            try:
                pdf_path = self.get_pdf_link_from_detail_page(doc['detail_url'])
                
                if pdf_path:
                    doc['pdf_path'] = pdf_path
                    doc['download_status'] = 'success'
                    successful_downloads += 1
                else:
                    doc['pdf_path'] = None
                    doc['download_status'] = 'failed'
                    failed_downloads += 1
                
            except Exception as e:
                doc['pdf_path'] = None
                doc['download_status'] = 'error'
                doc['error'] = str(e)
                failed_downloads += 1
            
            time.sleep(2)
        
      

        self._save_metadata(documents)
        
        return documents
    
    def _save_metadata(self, documents):
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(documents, f, ensure_ascii=False, indent=2)
