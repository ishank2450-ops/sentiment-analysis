import requests
from bs4 import BeautifulSoup
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# ==========================================
# STEP 1: THE SCRAPER (API-Based)
# ==========================================
def scrape_reviews_with_api(product_url, api_key):
    print(f"\n[System] Connecting to ScraperAPI to bypass security...")
    
    payload = {
        'api_key': api_key, 
        'url': product_url,
        'premium': 'true',
        'country_code': 'in', # Setup for Amazon India
        'render': 'true'      # Forces ScraperAPI to wait for JS to load the reviews
    }
    
    try:
        response = requests.get('http://api.scraperapi.com', params=payload)
        
        if response.status_code != 200:
            print(f"[Error] Failed to retrieve page. Status code: {response.status_code}")
            return []
            
        print("[System] Saving a snapshot of the hidden HTML...")
        with open("debug_amazon.html", "w", encoding="utf-8") as file:
            file.write(response.text)
        print("[System] Snapshot saved as 'debug_amazon.html'.")

        soup = BeautifulSoup(response.text, 'html.parser')
        reviews = []
        
        # Searching for standard Amazon review classes
        review_elements = soup.find_all('span', {'data-hook': 'review-body'})
        
        if not review_elements:
            review_elements = soup.find_all('span', class_='review-text-content')
            
        if not review_elements:
             review_elements = soup.find_all('div', class_='cm_cr_grid_center_right_non_images_widgets')

        for element in review_elements:
            clean_text = element.text.strip()
            if clean_text:
                reviews.append(clean_text)
                
        print(f"[System] Successfully extracted {len(reviews)} reviews.\n")
        return reviews

    except Exception as e:
        print(f"[Error] An error occurred: {e}")
        return []

# ==========================================
# STEP 2: THE ML ANALYZER 
# ==========================================
def setup_sentiment_model():
    # Our baseline training data
    training_data = {
        "review": [
            "Absolutely love this product, it works perfectly!",
            "Terrible quality. It broke after one use.",
            "Decent for the price, but shipping was slow.",
            "I am so happy with my purchase, highly recommend.",
            "Waste of money. Do not buy this.",
            "The battery life is amazing and the screen is sharp.",
            "Customer service was rude and the item arrived damaged.",
            "Good build quality, meets my expectations."
        ],
        "sentiment": ["positive", "negative", "negative", "positive", 
                      "negative", "positive", "negative", "positive"]
    }
    
    df = pd.DataFrame(training_data)
    vectorizer = TfidfVectorizer(stop_words='english')
    model = LogisticRegression()
    
    X_train_vectorized = vectorizer.fit_transform(df['review'])
    model.fit(X_train_vectorized, df['sentiment'])
    
    return vectorizer, model

# ==========================================
# MAIN EXECUTION (INTERACTIVE)
# ==========================================
if __name__ == "__main__":
    print("========================================")
    print("  DYNAMIC PRODUCT SENTIMENT ANALYZER")
    print("========================================")
    
    # 1. Ask the user for the URL
    target_url = input("Paste the product review URL: ").strip()
    
    # 2. Hardcoded API Key
    # IMPORTANT: Replace the string below with your actual API key
    api_key = "b13ee45775ba1333d42aaba6fdd29e2c"
    
    if not target_url or not api_key or api_key == "YOUR_API_KEY_HERE":
        print("[Error] You must provide both a valid URL and an API key. Exiting...")
    else:
        # 3. Scrape the data
        scraped_reviews = scrape_reviews_with_api(target_url, api_key)
        
        if len(scraped_reviews) > 0:
            print("[System] Initializing Machine Learning model...")
            vectorizer, model = setup_sentiment_model()
            
            # 4. Analyze
            scraped_vectorized = vectorizer.transform(scraped_reviews)
            predictions = model.predict(scraped_vectorized)
            
            # 5. Display Results
            positive_count = 0
            negative_count = 0
            
            print("\n--- INDIVIDUAL REVIEWS ---")
            for review, sentiment in zip(scraped_reviews, predictions):
                snippet = review[:75] + "..." if len(review) > 75 else review
                print(f"[{sentiment.upper()}] - {snippet}")
                
                if sentiment == 'positive':
                    positive_count += 1
                else:
                    negative_count += 1
                    
            # 6. Dashboard & Recommendation Logic
            total = len(scraped_reviews)
            positive_pct = (positive_count / total) * 100
            negative_pct = (negative_count / total) * 100
            
            # Determine Buying Recommendation
            if positive_pct >= 70:
                verdict = "✅ YES, BUY IT. The overwhelming majority of customers are satisfied."
            elif positive_pct >= 40:
                verdict = "⚠️ BUY WITH CAUTION. Reviews are mixed. Read carefully before purchasing."
            else:
                verdict = "❌ DO NOT BUY. Most customers had a negative experience."

            print("\n========================================")
            print("          SUMMARY DASHBOARD")
            print("========================================")
            print(f"Total Reviews Analyzed: {total}")
            print(f"Positive Sentiment: {positive_pct:.1f}%")
            print(f"Negative Sentiment: {negative_pct:.1f}%")
            print("----------------------------------------")
            print(f"FINAL VERDICT: {verdict}")
            print("========================================\n")
        else:
            print("[System] No reviews were analyzed. Please check the URL or try a different product.")