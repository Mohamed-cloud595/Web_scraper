import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Optional
from urllib.parse import urljoin
import time
import csv
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('book_scraper.log'),
        logging.StreamHandler()
    ]
)

class BookScraper:
    """
    A web scraper for extracting book information from books.toscrape.com
    """
    
    def __init__(self, base_url: str = "https://books.toscrape.com/"):
        """
        Initialize the scraper with the base URL
        
        Args:
            base_url (str): The base URL of the website to scrape
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def _get_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """
        Retrieve and parse the content of a webpage
        
        Args:
            url (str): URL of the page to scrape
            
        Returns:
            Optional[BeautifulSoup]: Parsed HTML content or None if request fails
        """
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            # Add delay to be polite to the server
            time.sleep(1)
            
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching {url}: {e}")
            return None
    
    def _extract_book_data(self, book: BeautifulSoup) -> Dict[str, str]:
        """
        Extract data from a single book element
        
        Args:
            book (BeautifulSoup): BeautifulSoup object of a book element
            
        Returns:
            Dict[str, str]: Dictionary containing book details
        """
        try:
            title = book.h3.a['title']
            price = book.find('p', class_='price_color').text.strip()
            
            # Extract rating (convert from word to number)
            rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
            rating_class = book.find('p', class_='star-rating')['class'][1]
            rating = rating_map.get(rating_class, 'N/A')
            
            # Extract availability
            availability = book.find('p', class_='instock availability').text.strip()
            
            # Extract relative book URL and convert to absolute
            relative_url = book.h3.a['href']
            book_url = urljoin(self.base_url, relative_url)
            
            return {
                'title': title,
                'price': price,
                'rating': rating,
                'availability': availability,
                'url': book_url
            }
        except Exception as e:
            logging.error(f"Error extracting book data: {e}")
            return {}
    
    def scrape_books(self, output_file: str = 'books.csv') -> List[Dict[str, str]]:
        """
        Scrape all books from the website and save to CSV
        
        Args:
            output_file (str): Path to the output CSV file
            
        Returns:
            List[Dict[str, str]]: List of dictionaries containing book data
        """
        all_books = []
        current_url = self.base_url
        
        try:
            while current_url:
                logging.info(f"Scraping page: {current_url}")
                
                soup = self._get_page_content(current_url)
                if not soup:
                    break
                
                # Find all book items on the page
                books = soup.find_all('article', class_='product_pod')
                
                # Extract data from each book
                for book in books:
                    book_data = self._extract_book_data(book)
                    if book_data:
                        all_books.append(book_data)
                
                # Check for next page
                next_button = soup.find('li', class_='next')
                if next_button:
                    relative_next_url = next_button.a['href']
                    current_url = urljoin(current_url, relative_next_url)
                else:
                    current_url = None
            
            # Save to CSV
            self._save_to_csv(all_books, output_file)
            logging.info(f"Successfully scraped {len(all_books)} books. Data saved to {output_file}")
            
            return all_books
        except Exception as e:
            logging.error(f"Error during scraping: {e}")
            return []
    
    def _save_to_csv(self, data: List[Dict[str, str]], filename: str) -> None:
        """
        Save scraped data to a CSV file
        
        Args:
            data (List[Dict[str, str]]): List of dictionaries containing book data
            filename (str): Path to the output CSV file
        """
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                if data:
                    fieldnames = data[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    writer.writerows(data)
        except Exception as e:
            logging.error(f"Error saving to CSV: {e}")

if __name__ == "__main__":
    # Example usage
    scraper = BookScraper()
    books_data = scraper.scrape_books(output_file='data/books.csv')
    
    # Print first 5 books as a sample
    for book in books_data[:5]:
        print(f"Title: {book['title']}")
        print(f"Price: {book['price']}")
        print(f"Rating: {book['rating']}/5")
        print(f"Availability: {book['availability']}")
        print(f"URL: {book['url']}")
        print("-" * 50)