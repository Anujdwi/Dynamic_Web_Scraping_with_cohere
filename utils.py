import requests
import cohere
from bs4 import BeautifulSoup
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.action_chains import ActionChains
import time
import re

api_key = 'COHERE_SECRET_KEY'

def fetch_css_selectors(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    css_selectors = {}

    # Regex patterns for identifying review components
    review_keywords = r"(review|comment|feedback|text|body|content|post|entry|description|testimonial|rev(iew)?|customer|summary)"
    author_keywords = r"(author|user|name|profile|by|writer|creator|reviewer|posted\sby|submitter)"
    rating_keywords = r"(rating|stars|score|rank|grade|level|points|rate|review\-score|feedback\-rating)"
    pagination_keywords = r"(next|pagination|nav|page|forward|load\-more|show\-more|continue|arrow\-right|scroll\-next)"
    review_title_keywords = r"(title|heading|subject|review-title)"
    exclude_patterns = r"(widg|wrap)"  
    combined_keywords = f"{review_keywords}|{author_keywords}|{rating_keywords}|{pagination_keywords}|{review_title_keywords}"

    def extract_selectors(element):
        tag = element.name
        classes = element.get("class", [])
        id_value = element.get("id")
        
        # Add class-based selectors
        if classes:
            for class_name in classes:
                selector = f".{class_name}"
                css_selectors[selector] = element.get_text(strip=True)[:15] if element.get_text(strip=True) else ""

        # Add ID-based selectors
        if id_value:
            selector = f"#{id_value}"
            css_selectors[selector] = element.get_text(strip=True)[:15] if element.get_text(strip=True) else ""

        # Add tag-based selectors
        if tag:
            selector = tag
            css_selectors[selector] = element.get_text(strip=True)[:15] if element.get_text(strip=True) else ""

        # Recursively process child elements
        for child in element.children:
            if hasattr(child, "children"):
                extract_selectors(child)

    # Start extraction from the body of the document
    extract_selectors(soup)

    # Filter CSS selectors based on keywords
    filtered_selectors = {
        selector: text
        for selector, text in css_selectors.items()
        if (
            re.search(combined_keywords, selector, re.IGNORECASE)  # Match keyword patterns
            and not re.search(exclude_patterns, selector, re.IGNORECASE)  # Exclude unwanted patterns
        )
    }
    return filtered_selectors

def get_tag_suggestions(css_selectors):
    # Initialize Cohere client
    co = cohere.Client(api_key)
    
    # Create the prompt
    prompt = f"""You are given a list of CSS selectors and some lines contained by them, extracted from a website:
{json.dumps(css_selectors, indent=2)}

Your task is to analyze these selectors and determine the best matches for the following elements:
1. Review title
2. Review text body
3. Author name
4. Rating element
5. Next pagination button (button element)

### Guidelines for Selection:
In case of CSS selectors with similar content, choose the one that contains only Review Title, Review Text, or Author Name. Do not choose tags that contain both or any other details. 
- **Review Title:** Look for selectors containing terms such as 'title', 'heading', 'subject', 'review-title', or similar keywords.
- **Review Text Body:** Look for classes, IDs, or tags containing terms such as 'review', 'comment', 'text', 'content', 'body', 'feedback', 'testimonial', or similar keywords.
- **Author Name:** Identify selectors containing words like 'author', 'user', 'name', 'profile', 'by', 'reviewer', 'creator', or 'submitter'.
- **Rating Element:** Focus on selectors with terms like 'rating', 'stars', 'score', 'rank', 'grade', 'review-score', or similar indicators of numeric or star-based ratings.
- **Next Pagination Button:** Look for terms such as 'next-page', 'next', 'pagination', 'nav', 'page', 'load-more', 'show-more', 'forward', 'arrow-right', or similar navigation elements. Ensure the pagination element is specifically a `<button>` tag.

### Constraints:
- Use regex patterns to identify relevant selectors for each element based on keyword matches in class names, IDs, and tag names.
- Prioritize selectors with multiple keyword matches or stronger indicators.
- Return only the most relevant selector for each category.

### Expected Output Format:
You must return only a JSON object in the following exact format, do not have any additional explanation:
{{
    "review_title_tag": "selector_for_review_title",
    "review_tag": "selector_for_review_body",
    "author_tag": "selector_for_author_name",
    "rating_tag": "selector_for_rating",
    "next_pagination_button_tag": "selector_for_next_button"
}}
"""
    
    # Query Cohere API
    try:
        response = co.generate(
            model='command-r-plus',
            prompt=prompt,
            max_tokens=300,
            temperature=0,
        )
        print("Cohere API Response:", response.generations)
        
        # Check if the response contains any generation and is non-empty
        if not response.generations or not response.generations[0].text:
            print("Error: Empty response from Cohere API")
            return {
                "review_title_tag": None,
                "review_tag": None,
                "author_tag": None,
                "rating_tag": None,
                "next_pagination_button_tag": None
            }

        # Clean the response text by removing the "```json" and "```" formatting
        response_text = response.generations[0].text.strip()
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        
        # Attempt to decode the cleaned response text as JSON
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return {
                "review_title_tag": None,
                "review_tag": None,
                "author_tag": None,
                "rating_tag": None,
                "next_pagination_button_tag": None
            }
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {
            "review_title_tag": None,
            "review_tag": None,
            "author_tag": None,
            "rating_tag": None,
            "next_pagination_button_tag": None
        }
    

def fetch_all_reviews(url, title_tag, review_tag, author_tag, rating_tag, next_page_button_tag):
    # Set up Selenium WebDriver
    service = Service("chromedriver.exe")  # Update this path
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()  # Maximize window for better visibility

    try:
        # Open the webpage
        driver.get(url)
        wait = WebDriverWait(driver, 10)  # Wait for elements to load

        all_reviews = []
        page_number = 1  # Track the current page number for debugging

        while True:
            handle_popups(driver)
            try:
                # Wait for the reviews section to load
                wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, review_tag)))

                # Get the current page source and parse it with BeautifulSoup
                soup = BeautifulSoup(driver.page_source, "html.parser")

                # Find all review elements using the passed review_tag, author_tag, and rating_tag
                title_elements = soup.select(title_tag)
                review_elements = soup.select(review_tag)
                author_elements = soup.select(author_tag)
                rating_elements = soup.select(rating_tag)

                # Extract reviews, authors, and ratings
                for title, review, author, rating in zip(title_elements, review_elements, author_elements, rating_elements):
                    title_text = title.get_text(strip=True)
                    review_text = review.get_text(strip=True)
                    author_name = author.get_text(strip=True)
                    rating_score = rating.get("data-score", "N/A")  # Extract 'data-score' or use 'N/A' if missing
                    all_reviews.append({
                        "title": title_text,
                        "body": review_text,
                        "rating": rating_score,
                        "reviewer": author_name,
                    })

                print(f"Page {page_number} scraped successfully with {len(review_elements)} reviews.")
                page_number += 1

                # Scroll the "Next Page" button into view and click it
                try:
                    next_page_button = driver.find_element(By.CSS_SELECTOR, next_page_button_tag)
                    driver.execute_script("arguments[0].scrollIntoView(true);", next_page_button)
                    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, next_page_button_tag))).click()
                    time.sleep(2)  # Small pause to ensure the page loads
                except (NoSuchElementException, TimeoutException):
                    print("No more pages to scrape or 'Next Page' button not found.")
                    break
                except ElementClickInterceptedException as e:
                    print(f"Click intercepted on page {page_number}: {str(e)}")
                    ActionChains(driver).move_to_element_with_offset(next_page_button, 0, 0).click().perform()
            except Exception as e:
                print(f"Error scraping page {page_number}: {str(e)}")
                break

    finally:
        # Ensure the browser is closed properly
        driver.quit()

    return all_reviews

def handle_popups(driver):
    try:
        popups = driver.find_elements(By.CSS_SELECTOR, "[role='dialog'], [class*='needsclick']")
        for popup in popups:
            if popup.is_displayed():
                print("Found and dismissing a popup.")
                close_button = popup.find_element(By.CSS_SELECTOR, "button, .close, .dismiss, [aria-label='Close']")
                if close_button.is_displayed() and close_button.is_enabled():
                    close_button.click()
                    time.sleep(1)  
                    return True
    except NoSuchElementException:
        print("No dismissable pop-ups found.")
    except Exception as e:
        print(f"Error while handling pop-ups: {e}")
    return False

# Save reviews to a JSON file
def save_reviews_to_file(reviews, filename="reviews.json"):
    data = {
        "reviews_count": len(reviews),
        "reviews": reviews,
    }
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    print(f"Reviews saved to {filename}")
    return data 

if __name__ == "__main__":
    # URL of the webpage to scrape
    url = "https://2717recovery.com/products/recovery-cream"  # Replace with the target URL
    
    start = time.time()
    # CSS Selectors for this specific site
    css_selectors = fetch_css_selectors(url)
    tag_suggestions = get_tag_suggestions(css_selectors)
    print(tag_suggestions)
    reviews = fetch_all_reviews(
        url,
        tag_suggestions['review_title_tag'],
        tag_suggestions['review_tag'],
        tag_suggestions['author_tag'],
        tag_suggestions['rating_tag'],
        tag_suggestions['next_pagination_button_tag']
    )
    save_reviews_to_file(reviews)
    end = time.time()
    print(end-start)