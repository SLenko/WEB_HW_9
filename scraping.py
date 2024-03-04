import requests
import json
from bs4 import BeautifulSoup
from pymongo import MongoClient
import os

# Функція для отримання даних з однієї сторінки
def scrape_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    quotes = []
    for quote in soup.find_all('div', class_='quote'):
        text = quote.find('span', class_='text').get_text()
        author = quote.find('small', class_='author').get_text()
        tags = [tag.get_text() for tag in quote.find_all('a', class_='tag')]
        quotes.append({
            'text': text,
            'author': author,
            'tags': tags
        })
    
    return quotes

# Функція для отримання всіх сторінок та додавання цитат
def scrape_all_pages():
    base_url = 'http://quotes.toscrape.com'
    quotes = []
    page = 1
    while True:
        url = f'{base_url}/page/{page}/'
        response = requests.get(url)
        if response.status_code == 200:
            quotes += scrape_page(url)
            page += 1
        else:
            break
    return quotes

# Підключення до MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['quotes_database']  # Вибираємо або створюємо базу даних

# Отримання всіх цитат
all_quotes = scrape_all_pages()

# Отримання поточної робочої директорії
current_dir = os.path.dirname(os.path.abspath(__file__))

# Шлях до файлів
quotes_file = os.path.join(current_dir, 'quotes.json')
authors_file = os.path.join(current_dir, 'authors.json')

# Створення quotes.json
formatted_quotes = []
for quote in all_quotes:
    formatted_quote = {
        'text': quote['text'],
        'author': quote['author'],
        'tags': quote['tags']
    }
    formatted_quotes.append(formatted_quote)

with open(quotes_file, 'w') as f:
    json.dump(formatted_quotes, f, indent=4)


# Створення authors.json
authors_set = set(quote['author'] for quote in all_quotes)
authors = [{'fullname': author} for author in authors_set]
with open(authors_file, 'w') as f:
    json.dump(authors, f, indent=4)

# Завантаження quotes.json
with open(quotes_file, 'r') as f:
    quotes_data = json.load(f)

# Вставка даних в колекцію quotes
quotes_collection = db['quotes']
quotes_collection.insert_many(quotes_data)

# Завантаження authors.json
with open(authors_file, 'r') as f:
    authors_data = json.load(f)

# Вставка даних в колекцію authors
authors_collection = db['authors']
authors_collection.insert_many(authors_data)

print("Дані успішно завантажено до бази даних MongoDB.")
