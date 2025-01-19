---

# **Product Review Scraper API using Cohere (LLM)**

---

## **Description**
The project implements a Flask-based API to extract customer reviews from e-commerce product pages dynamically. It leverages browser automation (Selenium) to handle pagination, web scraping (BeautifulSoup) for parsing HTML content regardless of prompts, and AI-based CSS selector identification (Cohere API) to extract key components like review title, text, author, rating, and pagination. The solution is designed to dynamically adapt to various website structures, providing flexibility for scraping multiple sites.

---

## **Solution Approach**
---
#### **1: API Input and Initialization**
- **Start**: Represented as a start node.
- **API Input**:
  - A user sends a GET request to `/api/reviews?page=<URL>`.
  - The URL of the product page is extracted from the query parameter.
- **Validation**:
  - Check if the URL is provided. If not, return an error response (`Missing 'page' query parameter`).
#### **2: CSS Selector Extraction**
- **Request Page HTML**:
  - Use the `requests` library to fetch the HTML content of the page.
- **Parse HTML**:
  - Parse the content with BeautifulSoup.
- **Extract Potential Selectors**:
  - Identify potential CSS selectors for reviews, authors, ratings, etc., using regex patterns (`fetch_css_selectors()` function).
- **Generate HashMap**:
  - Create a hashmap `<CSS Selector, Text (first 10 tokens)>` from parsed content.
#### **3: AI Tagging with Cohere API**
- **Send Prompt to Cohere**:
  - Send the hashmap of CSS selectors to the Cohere API.
  - The API analyzes and identifies the most relevant selectors for:
    - Review title
    - Review text body
    - Author name
    - Rating
    - Next pagination button
- **Receive AI Response**:
  - Receive the tagged selectors from the API (`get_tag_suggestions()` function).
#### **4: Dynamic Review Scraping**
- **Setup Selenium**:
  - Initialize a Selenium WebDriver.
  - Open the target URL in a browser.
- **Handle Popups**:
  - Dismiss any pop-ups or dialog boxes using the `handle_popups()` function.
- **Extract Review Data**:
  - Use BeautifulSoup and Selenium to locate and extract:
    - Review title
    - Review text body
    - Author name
    - Rating
- **Handle Pagination**:
  - Navigate through paginated pages by identifying and clicking the "Next Page" button dynamically with Selenium.
#### **5: Save Reviews and Output**
- **Compile Reviews**:
  - Combine review data (title, text, author, rating) into a structured format.
- **Save to JSON**:
  - Save all the extracted reviews to a `reviews.json` file (`save_reviews_to_file()` function).
- **End**:
  - Stop the Selenium WebDriver and terminate the process.
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
