import re
import json
import time
import hashlib
import requests
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus, urljoin
from bs4 import BeautifulSoup
import trafilatura
from config import get_config

class LinkedInSearcher:
    def __init__(self):
        """Initialize LinkedIn searcher with configuration"""
        self.config = get_config()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def _extract_linkedin_urls(self, html_content: str) -> List[str]:
        """Extract LinkedIn profile URLs from search results HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        urls = []
        
        # Look for LinkedIn URLs in various link elements
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'linkedin.com/in/' in href:
                # Clean the URL
                if href.startswith('/url?q='):
                    # Google redirect URL
                    href = href.split('/url?q=')[1].split('&')[0]
                
                # Ensure it's a proper LinkedIn profile URL
                if 'linkedin.com/in/' in href and href not in urls:
                    urls.append(href)
        
        return urls[:self.config["max_candidates"]]
    
    def _google_search_fallback(self, query: str) -> List[str]:
        """Fallback Google search using web scraping"""
        search_url = f"https://www.google.com/search?q={quote_plus(query)}&num=50"
        
        try:
            response = self.session.get(search_url, timeout=self.config["timeout_seconds"])
            if response.status_code == 200:
                return self._extract_linkedin_urls(response.text)
        except Exception as e:
            print(f"Fallback search failed: {e}")
        
        return []
    
    def _google_custom_search(self, query: str) -> List[str]:
        """Use Google Custom Search API if available"""
        api_key = self.config["google_search_api_key"]
        engine_id = self.config["google_search_engine_id"]
        
        if not api_key or not engine_id:
            return []
        
        search_url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': api_key,
            'cx': engine_id,
            'q': query,
            'num': 10,
            'start': 1
        }
        
        urls = []
        try:
            for start_index in [1, 11]:  # Get up to 20 results
                params['start'] = start_index
                response = requests.get(search_url, params=params, timeout=self.config["timeout_seconds"])
                
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get('items', []):
                        link = item.get('link', '')
                        if 'linkedin.com/in/' in link and link not in urls:
                            urls.append(link)
                else:
                    print(f"Google Custom Search API error: {response.status_code}")
                    break
                    
                time.sleep(0.1)  # Rate limiting
                
        except Exception as e:
            print(f"Google Custom Search failed: {e}")
        
        return urls[:self.config["max_candidates"]]
    
    def _serpapi_search(self, query: str) -> List[str]:
        """Use SerpAPI if available"""
        api_key = self.config["serpapi_key"]
        if not api_key:
            return []
        
        search_url = "https://serpapi.com/search"
        params = {
            'api_key': api_key,
            'engine': 'google',
            'q': query,
            'num': 20
        }
        
        try:
            response = requests.get(search_url, params=params, timeout=self.config["timeout_seconds"])
            if response.status_code == 200:
                data = response.json()
                urls = []
                
                for result in data.get('organic_results', []):
                    link = result.get('link', '')
                    if 'linkedin.com/in/' in link and link not in urls:
                        urls.append(link)
                
                return urls[:self.config["max_candidates"]]
            else:
                print(f"SerpAPI error: {response.status_code}")
                
        except Exception as e:
            print(f"SerpAPI search failed: {e}")
        
        return []
    
    def _extract_profile_info(self, url: str) -> Dict[str, Any]:
        """Extract basic profile information from LinkedIn URL"""
        try:
            # Try to get content using trafilatura
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                text_content = trafilatura.extract(downloaded)
                if text_content:
                    # Extract name from URL or content
                    profile_id = url.split('/in/')[-1].split('/')[0].split('?')[0]
                    name = profile_id.replace('-', ' ').title()
                    
                    # Try to extract more info from text content
                    lines = text_content.split('\n')[:10]  # First 10 lines usually contain key info
                    
                    return {
                        'url': url,
                        'name': name,
                        'profile_text': text_content[:500] + '...' if len(text_content) > 500 else text_content,
                        'snippet': ' '.join(lines[:3])
                    }
        except Exception as e:
            print(f"Failed to extract profile info from {url}: {e}")
        
        # Fallback with minimal info
        profile_id = url.split('/in/')[-1].split('/')[0].split('?')[0]
        name = profile_id.replace('-', ' ').title()
        
        return {
            'url': url,
            'name': name,
            'profile_text': f"LinkedIn profile for {name}",
            'snippet': f"LinkedIn profile: {name}"
        }
    
    def search_candidates(self, job_description: str, job_requirements: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for LinkedIn candidates based on job description"""
        # Build search query
        query_parts = ['site:linkedin.com/in']
        
        # Try to extract a job title and location from the job description
        title = ''
        location = ''
        if job_requirements:
            title = job_requirements.get('title', '')
            location = job_requirements.get('location', '')
        
        # Fallback: extract key terms from job description
        words = job_description.split()
        key_terms = []
        job_keywords = ['engineer', 'developer', 'manager', 'analyst', 'specialist',
                       'director', 'senior', 'lead', 'python', 'java', 'react',
                       'ml', 'ai', 'data', 'software', 'frontend', 'backend',
                       'research', 'machine learning', 'neural networks', 'llm',
                       'mountain view', 'san francisco', 'bay area', 'california']
        location_keywords = ['mountain view', 'san francisco', 'bay area', 'california', 'ca']
        found_location = False
        for word in words:
            clean_word = re.sub(r'[^\w\s]', '', word.lower())
            if clean_word in location_keywords and not found_location:
                key_terms.append(f'"{clean_word}"')
                found_location = True
            elif clean_word in job_keywords and f'"{clean_word}"' not in key_terms:
                key_terms.append(f'"{clean_word}"')
            if len(key_terms) >= 3:
                break
        if len(key_terms) < 2:
            key_terms = ['"software engineer"', '"machine learning"']
        query_parts.extend(key_terms)
        if location:
            query_parts.append(f'"{location}"')
        if title:
            query_parts.append(f'"{title}"')
        search_query = ' '.join(query_parts)
        print(f"Searching with query: {search_query}")
        urls = []
        # 1. Try SerpAPI first
        if self.config["serpapi_key"]:
            print("Trying SerpAPI...")
            urls = self._serpapi_search(search_query)
        # 2. Try Google Custom Search API
        if not urls and self.config["google_search_api_key"]:
            print("Trying Google Custom Search API...")
            urls = self._google_custom_search(search_query)
        # 3. Fallback to web scraping
        if not urls:
            print("Using fallback search method...")
            urls = self._google_search_fallback(search_query)
        # 4. If still no results, try a very general query
        if not urls:
            general_query = 'site:linkedin.com/in "software engineer" "machine learning"'
            print(f"Trying general query: {general_query}")
            urls = self._google_search_fallback(general_query)
        print(f"Found {len(urls)} LinkedIn profile URLs")
        candidates = []
        for url in urls:
            try:
                profile_info = self._extract_profile_info(url)
                # Add headline if possible (from snippet or profile_text)
                headline = profile_info.get('snippet', '')
                candidate = {
                    'name': profile_info.get('name', ''),
                    'linkedin_url': profile_info.get('url', ''),
                    'headline': headline,
                    'profile_text': profile_info.get('profile_text', ''),
                    'snippet': headline
                }
                candidates.append(candidate)
                time.sleep(0.5)
            except Exception as e:
                print(f"Failed to process profile {url}: {e}")
                continue
        print(f"Successfully processed {len(candidates)} candidate profiles")
        return candidates
    
    def get_profile_hash(self, url: str) -> str:
        """Generate hash for profile URL to avoid duplicates"""
        return hashlib.md5(url.encode()).hexdigest()
