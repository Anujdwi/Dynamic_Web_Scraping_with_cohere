---

# **Product Review Scraper API**

---

## **Description**
The project implements a Flask-based API to extract customer reviews from e-commerce product pages dynamically. It leverages browser automation (Selenium), web scraping (BeautifulSoup), and AI-based CSS selector identification (Cohere API) to extract key components like review title, text, author, rating, and pagination. The solution is designed to dynamically adapt to various website structures, providing flexibility for scraping multiple sites.

---

## **Solution Approach**

1. **Input**  
   - A product page URL is passed as a query parameter to the API endpoint `/api/reviews`.

2. **Dynamic CSS Selector Extraction**  
   - The `fetch_css_selectors` function scrapes the page's HTML using BeautifulSoup to identify potential CSS selectors for elements related to reviews, authors, ratings, and pagination.

3. **AI-Powered Selector Identification**  
   - The `get_tag_suggestions` function leverages Cohere's natural language processing capabilities to determine the best CSS selectors for the desired elements.

4. **Review Scraping**  
   - Selenium automates the browser to fetch all reviews across paginated pages by identifying and interacting with elements dynamically.

5. **Output**  
   - The extracted reviews are saved in a JSON file (`reviews.json`) with details such as review title, text, rating, and reviewer name.

---

## **System Architecture**

Below is the architecture workflow:

1. **Flask API**: Acts as the entry point for the system.  
2. **CSS Selector Extraction**: Fetches potential CSS selectors for review-related elements.  
3. **Cohere API Integration**: Processes and refines the CSS selectors for accurate identification.  
4. **Selenium Automation**: Interacts with the website to scrape review details dynamically.  
5. **JSON Storage**: Saves the extracted reviews locally for further analysis or use.  

### **System Workflow Diagram**:
```
    +-------------------------+
    |     Flask API Server    |
    +-------------------------+
              |
              v
+--------------------------+  +-------------------------+
| CSS Selector Extraction  |->|   Cohere AI Tagging    |
+--------------------------+  +-------------------------+
              |                           |
              v                           v
     +-------------------+      +------------------+
     | Selenium Scraper  | ---->| JSON File Output |
     +-------------------+      +------------------+
```

---

## **How to Run the Project**

### **1. Prerequisites**  
- Python 3.8 or higher  
- Google Chrome and Chromedriver  
- Required Python libraries (install via `requirements.txt`):  
  ```bash
  pip install flask requests beautifulsoup4 selenium cohere
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
  http://127.0.0.1:5000/api/reviews?page=https://example.com/product-page
  ```

### **5. Check Output**  
- Extracted reviews are saved in `reviews.json`.

---

## **API Usage Examples**

### **Request**:
```bash
curl "http://127.0.0.1:5000/api/reviews?page=https://example.com/product-page"
```

### **Response**:
```json
{
    "reviews_count": 2,
    "reviews": [
        {
            "title": "Amazing Product!",
            "body": "This cream worked wonders for me.",
            "rating": "5",
            "reviewer": "John Doe"
        },
        {
            "title": "Not as Expected",
            "body": "I was disappointed with the results.",
            "rating": "2",
            "reviewer": "Jane Smith"
        }
    ]
}
```

---

## **Diagrams**
Refer to the **System Workflow Diagram** (above in ASCII) for better understanding.

---
