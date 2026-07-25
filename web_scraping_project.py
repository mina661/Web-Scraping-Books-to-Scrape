import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv

BASE_URL = "https://books.toscrape.com/"
books_details = []


# Get Book Details
def book_details(book_link):
    book_page = requests.get(book_link)
    src = book_page.content
    soup = BeautifulSoup(src, "lxml")

    category = soup.find(
        "ul", class_="breadcrumb"
    ).find_all("a")[2].text.strip()

    description_tag = soup.find("div", id="product_description")

    if description_tag:
        description = description_tag.find_next("p").text.strip()
    else:
        description = "No Description"

    table = soup.find("table", class_="table table-striped")

    upc = table.find_all("tr")[0].find("td").text.strip()
    product_type = table.find_all("tr")[1].find("td").text.strip()
    price_excl_tax = table.find_all("tr")[2].find("td").text.strip()
    price_incl_tax = table.find_all("tr")[3].find("td").text.strip()
    tax = table.find_all("tr")[4].find("td").text.strip()
    number_of_reviews = table.find_all("tr")[6].find("td").text.strip()

    return (
        category,
        description,
        upc,
        product_type,
        price_excl_tax,
        price_incl_tax,
        tax,
        number_of_reviews
    )


# Scrape One Page
def main(page):

    src = page.content
    soup = BeautifulSoup(src, "lxml")

    books = soup.find_all("article", class_="product_pod")

    print(f"Number of books in page: {len(books)}")

    for book in books:

        book_title = book.find("h3").find("a")["title"]

        book_price = book.find(
            "p",
            class_="price_color"
        ).text.strip()

        book_rating = book.find(
            "p",
            class_="star-rating"
        )["class"][1]

        book_availability = book.find(
            "p",
            class_="instock availability"
        ).text.strip()

        book_link = urljoin(
            page.url,
            book.find("h3").find("a")["href"]
                            )

        (
            category,
            description,
            upc,
            product_type,
            price_excl_tax,
            price_incl_tax,
            tax,
            number_of_reviews
        ) = book_details(book_link)

        book_info = {
            "Title": book_title,
            "Price": book_price,
            "Rating": book_rating,
            "Availability": book_availability,
            "Book Link": book_link,
            "Category": category,
            "Description": description,
            "UPC": upc,
            "Product Type": product_type,
            "Price (excl. tax)": price_excl_tax,
            "Price (incl. tax)": price_incl_tax,
            "Tax": tax,
            "Number of Reviews": number_of_reviews
        }

        books_details.append(book_info)


# Pagination
for page_num in range(1, 51):

    if page_num == 1:
        url = BASE_URL
    else:
        url = f"{BASE_URL}catalogue/page-{page_num}.html"

    print(f"\nScraping Page {page_num}")

    page = requests.get(url)

    main(page)


print(f"\nTotal Books: {len(books_details)}")

with open("books_data.csv", "w", newline="", encoding="utf-8-sig") as file:

    fieldnames = books_details[0].keys()

    writer = csv.DictWriter(file, fieldnames=fieldnames)

    writer.writeheader()

    writer.writerows(books_details)

print("CSV File Created Successfully.")