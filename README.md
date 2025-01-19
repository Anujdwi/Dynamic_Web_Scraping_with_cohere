---

# **Product Review Scraper API using Cohere (LLM)**

---

## **Description**
The project implements a Flask-based API to extract customer reviews from e-commerce product pages dynamically. It leverages browser automation (Selenium) to handle pagination, web scraping (BeautifulSoup) for parsing HTML content regardless of prompts, and AI-based CSS selector identification (Cohere API) to extract key components like review title, text, author, rating, and pagination. The solution is designed to dynamically adapt to various website structures, providing flexibility for scraping multiple sites.

---

## **Solution Approach**

1. **Input**  
   - A product page URL is passed as a query parameter to the API endpoint `/api/reviews`.

2. **Dynamic CSS Selector Extraction**  
   - The `fetch_css_selectors` function scrapes the page's HTML using BeautifulSoup to identify potential CSS selectors for elements related to reviews, authors, ratings, and pagination.

3. **AI-Powered Selector Identification**  
   - A hashmap of `<CSS Selectors, Text contained in them stripped to 10 tokens>` is generated and sent as a prompt to the Cohere API, which determines the best CSS selectors for the desired elements.

4. **Review Scraping**  
   - Selenium automates the browser to navigate through paginated pages, ensuring all reviews are fetched dynamically.
   - BeautifulSoup is used to scrape review details from the HTML content of each page, offering reliable parsing independent of AI-generated prompts.

5. **Output**  
   - The extracted reviews are saved in a JSON file (`reviews.json`) with details such as review title, text, rating, and reviewer name.

---

## **System Architecture**

Below is the architecture workflow:

1. **Flask API**: Acts as the entry point for the system.  
2. **CSS Selector Extraction**: Fetches potential CSS selectors for review-related elements.  
3. **Cohere API Integration**: Processes a hashmap of `<CSS Selectors, Text contained in them stripped to 10 tokens>` to refine and identify the best selectors.  
4. **Selenium Automation**: Handles pagination to dynamically load additional reviews.  
5. **BeautifulSoup Scraper**: Parses review content reliably, regardless of prompt-based selector accuracy.  
6. **JSON Storage**: Saves the extracted reviews locally for further analysis or use.  

### **System Workflow Diagram**:
```
    +-------------------------+
    |     Flask API Server    |
    +-------------------------+
              |
              v
+--------------------------+  +------------------------------------------------------+
| CSS Selector Extraction  |->| Cohere AI Tagging (Processes hashmap of selectors &  |
|                          |  | text content stripped to 10 tokens to identify tags) |
+--------------------------+  +------------------------------------------------------+
              |                           |
              v                           v
+-------------------------+      +-------------------------+
| BeautifulSoup Scraper   | ---->| Selenium for Pagination |
+-------------------------+      +-------------------------+
              |                           |
              v                           v
       +-------------------+      +------------------+
       | Reviews Extracted | ---->| JSON File Output |
       +-------------------+      +------------------+
```

---

## **How to Run the Project**

### **1. Prerequisites**  
- Python 3.11  
- Google Chrome and Chromedriver  
- Required Python libraries (install via `requirements.txt`):  
  ```bash
  pip install -v -r requirements.txt
  ```

### **2. Environment Setup**  
- Ensure `chromedriver` is installed and its path is correctly specified in `utils.py`.  
- Obtain a Cohere API key and replace `api_key` in `utils.py` with your key.  

### **3. Run the Flask Server**  
- Start the API server:  
  ```bash
  python main.py
  ```

### **4. Access the API**  
- Use the following endpoint:  
  ```
  GET /api/reviews?page=<URL>
  ```
- Example:  
  ```
  curl http://127.0.0.1:5000/api/reviews?page=https://example.com/product-page
  ```

### **5. Check Output**  
- Extracted reviews are saved in `reviews.json`.

---

## **API Usage Examples**

### **Request**:
```bash
curl "http://127.0.0.1:5000/api/reviews?page=https://2717recovery.com/products/recovery-cream"
```

### **Response**:
```json
{
    "reviews_count": 425,
    "reviews": [
        {
            "title": "",
            "body": "I love this stuff!",
            "rating": "5",
            "reviewer": "Shawna Churchill"
        },
        {
            "title": "",
            "body": "It’s amazing",
            "rating": "4",
            "reviewer": "Tania Patterson"
        }
   ]
}
```
---
