import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProgressCounter:
    def __init__(self, total):
        self.lock = Lock()
        self.current = 0
        self.total = total
        self.success = 0
        self.failed = 0
    
    def increment(self, success=True):
        with self.lock:
            self.current += 1
            if success:
                self.success += 1
            else:
                self.failed += 1
            return self.current

def normalize_name(name):
    """Normalize athlete name for URL formatting."""
    if pd.isna(name):
        return None
    
    name = str(name).lower()
    # Remove accents and special characters
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'\s+', '-', name.strip())
    name = re.sub(r'-+', '-', name)
    return name

def clean_image_url(url):
    """
    Clean and validate image URL.
    Replaces template placeholders and ensures URL is complete.
    """
    if not url:
        return None
    
    # Replace template placeholders
    url = url.replace('{formatInstructions}', 't_1-1_300/f_auto')
    url = url.replace('{format}', 't_1-1_300/f_auto')
    url = url.replace('\\/', '/')
    
    # Check if URL is complete (should not end with incomplete template)
    if '{' in url or url.endswith('/private/'):
        logger.warning(f"Incomplete URL detected: {url[:100]}")
        return None
    
    # Ensure it's a valid Olympics image URL
    if 'img.olympics.com' not in url:
        return None
    
    return url

def get_name_variations(name):
    """
    Generate different name format variations to try.
    Handles cases like "LASTNAME Firstname" vs "Firstname LASTNAME"
    
    Returns list of normalized name variations to try.
    """
    if pd.isna(name):
        return []
    
    variations = []
    name_parts = str(name).strip().split()
    
    if len(name_parts) >= 2:
        # Original order: "LASTNAME Firstname" -> "lastname-firstname"
        original = normalize_name(name)
        if original:
            variations.append(original)
        
        # Reversed order: "Firstname LASTNAME" -> "firstname-lastname"
        reversed_name = ' '.join(reversed(name_parts))
        reversed_normalized = normalize_name(reversed_name)
        if reversed_normalized and reversed_normalized != original:
            variations.append(reversed_normalized)
        
        # Try with just first and last name (skip middle names)
        if len(name_parts) > 2:
            # First + Last
            first_last = f"{name_parts[0]} {name_parts[-1]}"
            first_last_norm = normalize_name(first_last)
            if first_last_norm and first_last_norm not in variations:
                variations.append(first_last_norm)
            
            # Last + First
            last_first = f"{name_parts[-1]} {name_parts[0]}"
            last_first_norm = normalize_name(last_first)
            if last_first_norm and last_first_norm not in variations:
                variations.append(last_first_norm)
    elif len(name_parts) == 1:
        # Single name
        normalized = normalize_name(name)
        if normalized:
            variations.append(normalized)
    
    return variations

def extract_image_url_enhanced(html_content, athlete_name):
    """
    Enhanced image URL extraction targeting athlete profile images specifically.
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Strategy 1: Look for athlete-image div or similar athlete photo containers
        athlete_containers = [
            soup.find('div', class_=re.compile(r'athlete.*image', re.I)),
            soup.find('div', class_=re.compile(r'profile.*image', re.I)),
            soup.find('div', class_=re.compile(r'player.*image', re.I)),
            soup.find('figure', class_=re.compile(r'athlete', re.I)),
        ]
        
        for container in athlete_containers:
            if container:
                # Look for img tag in this container
                img = container.find('img')
                if img:
                    src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                    if src and 'img.olympics.com' in src:
                        # Clean up the URL
                        src = src.replace('{formatInstructions}', 't_1-1_300/f_auto')
                        src = src.replace('{format}', 't_1-1_300/f_auto')
                        return src
        
        # Strategy 2: Look for Next.js JSON data - target athlete images specifically
        scripts = soup.find_all('script', {'id': '__NEXT_DATA__'})
        for script in scripts:
            if script.string:
                # Look for athlete-specific image patterns in JSON
                patterns = [
                    r'"athlete"[^}]*?"imageUrl":"([^"]+)"',
                    r'"profile"[^}]*?"imageUrl":"([^"]+)"',
                    r'"headshot"[^}]*?"url":"([^"]+)"',
                    r'"photo"[^}]*?"url":"([^"]+)"',
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, script.string, re.DOTALL)
                    if matches:
                        url = matches[0]
                        url = url.replace('\\/', '/')
                        url = url.replace('{formatInstructions}', 't_1-1_300/f_auto')
                        url = url.replace('{format}', 't_1-1_300/f_auto')
                        if 'img.olympics.com' in url:
                            return url
        
        # Strategy 3: Look in __NEXT_DATA__ for any athlete image
        for script in scripts:
            if script.string:
                # Find URLs that contain athlete-related paths
                urls = re.findall(r'https://img\.olympics\.com/images/image/private/[^"\\]+', script.string)
                if urls:
                    for url in urls:
                        url = url.replace('\\/', '/')
                        # Skip logos and icons
                        if any(x in url.lower() for x in ['/logo', '/icon', '/flag', '/symbol']):
                            continue
                        # Prefer athlete/headshot URLs
                        if any(x in url.lower() for x in ['athlete', 'headshot', 'profile', 'player']):
                            url = url.replace('{formatInstructions}', 't_1-1_300/f_auto')
                            url = url.replace('{format}', 't_1-1_300/f_auto')
                            return url
                    # If no specific athlete URL, return first non-logo image
                    if urls:
                        url = urls[0].replace('{formatInstructions}', 't_1-1_300/f_auto')
                        url = url.replace('{format}', 't_1-1_300/f_auto')
                        return url
        
        # Strategy 4: Meta tags (og:image often has athlete photo)
        meta_tags = [
            ('property', 'og:image'),
            ('name', 'twitter:image'),
        ]
        
        for attr, value in meta_tags:
            tag = soup.find('meta', {attr: value})
            if tag and tag.get('content'):
                img_url = tag.get('content')
                if 'img.olympics.com' in img_url and '/logo' not in img_url.lower():
                    img_url = img_url.replace('{formatInstructions}', 't_1-1_300/f_auto')
                    return img_url
        
        # Strategy 5: Direct img tags with athlete class
        img_tags = soup.find_all('img', class_=re.compile(r'athlete|profile|headshot', re.I))
        for img in img_tags:
            src = img.get('src') or img.get('data-src')
            if src and 'img.olympics.com' in src:
                src = src.replace('{formatInstructions}', 't_1-1_300/f_auto')
                return src
        
        return None
        
    except Exception as e:
        logger.error(f"Error extracting image URL for {athlete_name}: {e}")
        return None

def scrape_athlete_image(athlete_name, base_url="https://www.olympics.com/fr/athletes/"):
    """
    Scrape athlete image URL from Olympics website.
    Tries multiple name format variations.
    """
    if not athlete_name or pd.isna(athlete_name):
        return None
    
    # Get all possible name variations
    name_variations = get_name_variations(athlete_name)
    
    if not name_variations:
        logger.warning(f"Could not generate name variations for: {athlete_name}")
        return None
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
    }
    
    # Try each name variation
    for i, normalized_name in enumerate(name_variations):
        url = f"{base_url}{normalized_name}"
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                image_url = extract_image_url_enhanced(response.text, athlete_name)
                if image_url:
                    # Clean and validate the URL
                    image_url = clean_image_url(image_url)
                    if image_url:
                        if i > 0:  # Log if we found it with an alternative format
                            logger.info(f"  → Found using variation #{i+1}: {normalized_name}")
                        return image_url
            elif response.status_code == 404:
                logger.debug(f"404 for variation: {normalized_name}")
            else:
                logger.warning(f"HTTP {response.status_code} for {normalized_name}")
            
            # Small delay between attempts to be polite
            if i < len(name_variations) - 1:
                time.sleep(0.2)
                
        except requests.Timeout:
            logger.warning(f"Timeout for {normalized_name}")
            continue
        except Exception as e:
            logger.error(f"Error for {normalized_name}: {e}")
            continue
    
    # If we tried all variations and found nothing
    logger.debug(f"No image found after trying {len(name_variations)} variations: {', '.join(name_variations)}")
    return None

def debug_single_athlete(athlete_name, save_html=False):
    """
    Debug helper to examine HTML structure for a single athlete.
    Shows all name variations being tried and returns the found URL.
    """
    print(f"\n{'='*60}")
    print(f"DEBUGGING: {athlete_name}")
    print(f"{'='*60}\n")
    
    name_variations = get_name_variations(athlete_name)
    print(f"Name variations to try ({len(name_variations)}):")
    for i, var in enumerate(name_variations, 1):
        print(f"  {i}. {var}")
    print()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    
    for i, normalized_name in enumerate(name_variations, 1):
        url = f"https://www.olympics.com/fr/athletes/{normalized_name}"
        print(f"Attempt {i}/{len(name_variations)}: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            print(f"  Status Code: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Save HTML if requested (only for successful response)
                if save_html:
                    filename = f"debug_{normalized_name}.html"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    print(f"  HTML saved to: {filename}")
                
                # Look for athlete-image divs
                athlete_divs = soup.find_all('div', class_=re.compile(r'athlete.*image', re.I))
                if athlete_divs:
                    print(f"  Found {len(athlete_divs)} div(s) with 'athlete-image' class:")
                    for j, div in enumerate(athlete_divs[:3], 1):
                        print(f"    Div {j}: classes = {div.get('class')}")
                        img = div.find('img')
                        if img:
                            src = img.get('src') or img.get('data-src')
                            print(f"      → img src: {src[:80] if src else 'None'}...")
                
                # Try to extract image
                image_url = extract_image_url_enhanced(response.text, athlete_name)
                
                if image_url:
                    # Clean and validate
                    image_url = clean_image_url(image_url)
                    if image_url:
                        print(f"  ✓ Image found: {image_url}")
                        print(f"\n{'='*60}")
                        print(f"SUCCESS! Image found with variation #{i}")
                        print(f"{'='*60}\n")
                        return image_url  # Return the URL instead of just returning
                    else:
                        print(f"  ⚠ Image URL found but incomplete/invalid")
                else:
                    print(f"  ✗ No image found in response")
                    
                    # Search for any img.olympics.com URLs
                    olympics_urls = re.findall(r'https://[^"\']*img\.olympics\.com[^"\']*', response.text)
                    if olympics_urls:
                        print(f"  Found {len(olympics_urls)} Olympics image URLs:")
                        for j, u in enumerate(olympics_urls[:3], 1):
                            print(f"    {j}. {u[:70]}...")
            elif response.status_code == 404:
                print(f"  ✗ Page not found (404)")
            else:
                print(f"  ✗ Unexpected status")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
        
        print()  # Blank line between attempts
    
    print(f"{'='*60}")
    print(f"RESULT: No image found after trying all variations")
    print(f"{'='*60}\n")
    return None  # Return None if no image found

def scrape_single_athlete(args):
    """Wrapper function for thread pool execution."""
    idx, athlete_name, counter = args
    current = counter.increment(success=False)
    logger.info(f"[{current}/{counter.total}] Processing: {athlete_name}")
    
    image_url = scrape_athlete_image(athlete_name)
    
    if image_url:
        counter.success += 1
        counter.failed -= 1
        logger.info(f"✓ Found image for {athlete_name}")
    else:
        logger.warning(f"✗ No image found for {athlete_name}")
    
    return idx, image_url

def test_first_n_rows(input_file, name_column='name', n=10, max_workers=5):
    """Test the scraper on the first N rows."""
    logger.info(f"Reading CSV file: {input_file}")
    
    try:
        df = pd.read_csv(input_file)
    except Exception as e:
        logger.error(f"Error reading CSV: {e}")
        return None
    
    if name_column not in df.columns:
        logger.error(f"Column '{name_column}' not found. Available: {df.columns.tolist()}")
        return None
    
    df_test = df.head(n).copy()
    df_test['image_url'] = None
    
    logger.info(f"\n{'='*60}")
    logger.info(f"TESTING WITH FIRST {n} ROWS")
    logger.info(f"Using {max_workers} concurrent threads")
    logger.info(f"{'='*60}\n")
    
    logger.info("Athletes to process:")
    for idx, name in enumerate(df_test[name_column], 1):
        logger.info(f"  {idx}. {name}")
    logger.info("")
    
    counter = ProgressCounter(len(df_test))
    
    args_list = [
        (idx, row[name_column], counter)
        for idx, row in df_test.iterrows()
    ]
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(scrape_single_athlete, args): args for args in args_list}
        
        for future in as_completed(futures):
            try:
                idx, image_url = future.result()
                df_test.loc[idx, 'image_url'] = image_url
            except Exception as e:
                logger.error(f"Thread execution error: {e}")
    
    elapsed_time = time.time() - start_time
    
    logger.info(f"\n{'='*60}")
    logger.info(f"TEST RESULTS:")
    logger.info(f"{'='*60}")
    logger.info(f"Total processed: {len(df_test)}")
    logger.info(f"Images found: {counter.success} ({counter.success/len(df_test)*100:.1f}%)")
    logger.info(f"Images missing: {counter.failed} ({counter.failed/len(df_test)*100:.1f}%)")
    logger.info(f"Time elapsed: {elapsed_time:.2f} seconds")
    logger.info(f"Average time per athlete: {elapsed_time/len(df_test):.2f} seconds")
    logger.info(f"{'='*60}\n")
    
    logger.info("DETAILED RESULTS:")
    for idx, row in df_test.iterrows():
        status = "✓" if pd.notna(row['image_url']) else "✗"
        url_preview = row['image_url'] if pd.notna(row['image_url']) else "N/A"
        logger.info(f"{status} {row[name_column]}: {url_preview}")
    
    return df_test

def process_athletes_csv_multithreaded(input_file, output_file, name_column='name', 
                                      max_workers=10, limit=None):
    """Process the full CSV with multithreading."""
    logger.info(f"Reading CSV file: {input_file}")
    
    try:
        df = pd.read_csv(input_file)
    except Exception as e:
        logger.error(f"Error reading CSV: {e}")
        return
    
    if name_column not in df.columns:
        logger.error(f"Column '{name_column}' not found. Available: {df.columns.tolist()}")
        return
    
    if 'image_url' not in df.columns:
        df['image_url'] = None
    
    if limit:
        df_process = df.head(limit).copy()
    else:
        df_process = df.copy()
    
    total_rows = len(df_process)
    logger.info(f"Processing {total_rows} athletes with {max_workers} threads...")
    
    counter = ProgressCounter(total_rows)
    
    args_list = [
        (idx, row[name_column], counter)
        for idx, row in df_process.iterrows()
        if pd.isna(row['image_url'])
    ]
    
    if not args_list:
        logger.info("All athletes already have image URLs!")
        return
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(scrape_single_athlete, args): args for args in args_list}
        
        for future in as_completed(futures):
            try:
                idx, image_url = future.result()
                df.loc[idx, 'image_url'] = image_url
            except Exception as e:
                logger.error(f"Thread execution error: {e}")
    
    elapsed_time = time.time() - start_time
    
    logger.info(f"Saving results to: {output_file}")
    df.to_csv(output_file, index=False)
    
    total = len(df_process)
    with_images = df_process['image_url'].notna().sum()
    
    logger.info(f"\n{'='*60}")
    logger.info(f"FINAL SUMMARY:")
    logger.info(f"Total athletes: {total}")
    logger.info(f"Images found: {with_images} ({with_images/total*100:.1f}%)")
    logger.info(f"Images missing: {total-with_images} ({(total-with_images)/total*100:.1f}%)")
    logger.info(f"Time elapsed: {elapsed_time:.2f} seconds")
    logger.info(f"Average time per athlete: {elapsed_time/total:.2f} seconds")
    logger.info(f"{'='*60}\n")


if __name__ == "__main__":
    INPUT_CSV = "athletes.csv"
    NAME_COLUMN = "name"
    
    # Option 1: Debug a single athlete to see what's happening
    print("\nDEBUG MODE: Testing single athlete")
    print("="*60)
    debug_single_athlete("ALEKSANYAN Artur", save_html=True)
    
    # Option 2: Run test on first 10 rows
    print("\n\nTEST MODE: Testing first 10 rows")
    print("="*60)
    test_results = test_first_n_rows(
        input_file=INPUT_CSV,
        name_column=NAME_COLUMN,
        n=10,
        max_workers=10
    )
    
    if test_results is not None and test_results['image_url'].notna().any():
        proceed = input("\n✓ Some images found! Process full CSV? (yes/no): ").strip().lower()
        if proceed == 'yes':
            OUTPUT_CSV = "athletes_with_images.csv"
            process_athletes_csv_multithreaded(
                input_file=INPUT_CSV,
                output_file=OUTPUT_CSV,
                name_column=NAME_COLUMN,
                max_workers=10,
                limit=None
            )
    else:
        print("\n✗ No images found. Check the debug output and saved HTML file.")
        print("The website structure may have changed or athletes may not have pages.")