import os
os.system('python -m pip install textblob')

import requests
from bs4 import BeautifulSoup
from textblob import TextBlob

import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from googlesearch import search
import time

# ==========================================
# STEP 1: THE AMAZON SCRAPER
# ==========================================
def scrape_amazon(product_url, api_key):
    print(f"\n[System] Scraping Amazon customer reviews...")
    payload = {'api_key': api_key, 'url': product_url, 'premium': 'true', 'render': 'true'}
    
    try:
        response = requests.get('http://api.scraperapi.com', params=payload)
        soup = BeautifulSoup(response.text, 'html.parser')
        reviews = []
        
        elements = soup.find_all('span', {'data-hook': 'review-body'})
        if not elements: elements = soup.find_all('span', class_='review-text-content')
            
        for el in elements:
            clean = el.text.strip()
            if clean: reviews.append(clean)
                
        print(f"[System] Extracted {len(reviews)} Amazon reviews.")
        return reviews
    except Exception as e:
        print(f"[Error] Amazon Scrape Failed: {e}")
        return []

# ==========================================
# STEP 2: THE GOOGLE SNIPPET BYPASS
# ==========================================
def get_web_sentiment_from_google(product_name, api_key):
    print(f"\n[System] Bypassing target site bot-walls...")
    print(f"[System] Extracting review summaries directly from Google Search Results...")
    
    query = f"{product_name} professional review"
    google_url = f"https://www.google.com/search?q={query.replace(' ', '+')}&hl=en"
    
    # Ask ScraperAPI to load the Google Search page
    payload = {'api_key': api_key, 'url': google_url, 'premium': 'true'}
    snippets = []
    
    try:
        response = requests.get('http://api.scraperapi.com', params=payload)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Target the specific HTML class Google uses for search result snippets
        snippet_elements = soup.find_all('div', class_='VwiC3b')
        
        # Fallback if Google changes their class names
        if not snippet_elements:
            snippet_elements = soup.find_all('div', {'style': '-webkit-line-clamp:2'})
            
        for el in snippet_elements[:5]: # Grab up to 5 snippets
            text = el.text.strip()
            if len(text) > 30: # Ensure it's an actual paragraph
                snippets.append(text)
                print(f" -> Extracted Snippet: {text[:60]}...")
                
        if not snippets:
            print("    -> [Warning] Failed to extract snippets. Google's HTML may have changed.")
            
        return snippets
    except Exception as e:
        print(f"[Error] Search Bypass Failed: {e}")
        return []
# ==========================================
# STEP 3: THE NLP SENTIMENT ENGINE
# ==========================================
def analyze_sentiment(text):
    # TextBlob returns a polarity from -1.0 (Negative) to 1.0 (Positive)
    analysis = TextBlob(text)
    
    # Convert the -1 to 1 scale into a 0 to 100 percentage score
    score = ((analysis.sentiment.polarity + 1) / 2) * 100
    return score

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    print("========================================")
    print("  OMNI-CHANNEL PRODUCT SENTIMENT ENGINE ")
    print("========================================")
    
    api_key = "b13ee45775ba1333d42aaba6fdd29e2c"
    
    target_url = input("Paste the Amazon product URL: ").strip()
    product_name = input("Type the exact Product Name (e.g., 'Sony WH-1000XM5'): ").strip()
    
    if not target_url or not product_name or api_key == "YOUR_API_KEY_HERE":
        print("[Error] Missing URL, Product Name, or API Key. Exiting...")
    else:
        # 1. Get Amazon Sentiment
        amazon_reviews = scrape_amazon(target_url, api_key)
        amz_scores = [analyze_sentiment(r) for r in amazon_reviews]
        avg_amz_score = sum(amz_scores) / len(amz_scores) if amz_scores else 0
        
# 2. Get Professional Web Sentiment (VIA GOOGLE BYPASS)
        web_snippets = get_web_sentiment_from_google(product_name, api_key)
        web_scores = []
        
        for snippet in web_snippets:
            score = analyze_sentiment(snippet)
            web_scores.append(score)
                
        avg_web_score = sum(web_scores) / len(web_scores) if web_scores else 0
        
        # 3. Calculate Final Weighted Verdict
        # We give professional web reviews a bit more weight (60%) than Amazon reviews (40%)
        if avg_amz_score > 0 and avg_web_score > 0:
            final_score = (avg_amz_score * 0.40) + (avg_web_score * 0.60)
        else:
            final_score = max(avg_amz_score, avg_web_score) # Fallback if one fails

        # Recommendation Logic based on TextBlob's scale
        if final_score >= 65:
            verdict = "✅ HIGHLY RECOMMENDED. Both consumers and critics love it."
        elif final_score >= 50:
            verdict = "⚠️ MIXED CONSENSUS. Has flaws. Read specific reviews before buying."
        else:
            verdict = "❌ DO NOT BUY. Critics and consumers report significant issues."

        # 4. Display Dashboard
        print("\n========================================")
        print("          OMNI-CHANNE DASHBOARD")
        print("========================================")
        print(f"Product: {product_name}")
        print(f"Amazon Customer Score:    {avg_amz_score:.1f} / 100")
        print(f"Professional Web Score:   {avg_web_score:.1f} / 100")
        print(f"Combined Master Score:    {final_score:.1f} / 100")
        print("----------------------------------------")
        print(f"DETAILED VERDICT: {verdict}")
        print("========================================\n")