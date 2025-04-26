import requests
from bs4 import BeautifulSoup

def scrape_books(url):
    # Send a GET request to the website
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to retrieve the website. Status code: {response.status_code}")
        return

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all book items
    books = soup.find_all('article', class_='product_pod')

    # Loop through each book and extract the title, price, and rating
    for book in books:
        # Extract the title
        title = book.h3.a['title']

        # Extract the price
        price = book.find('p', class_='price_color').text

        # Extract the rating
        rating_class = book.find('p', class_='star-rating')['class']
        rating = rating_class[1]  # The second class contains the rating (e.g., "One", "Two")

        # Print the details
        print(f"Title: {title}\nRating: {rating}\nPrice: {price}\n")

if __name__ == "__main__":
    # URL of the website
    url = "https://books.toscrape.com/"
    scrape_books(url)
