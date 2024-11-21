import json
import random
import time
from pprint import pprint

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service


class MinimalFirefoxScraper:
    def __init__(self, cookies_file=None):
        """Initialize Firefox WebDriver"""
        options = webdriver.FirefoxOptions()

        # Basic stealth settings
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference("useAutomationExtension", False)

        # Initialize driver
        service = Service()
        self.driver = webdriver.Firefox(service=service, options=options)
        self.driver.set_page_load_timeout(30)

        if cookies_file:
            self.load_cookies(cookies_file)

    def format_cookie(self, cookie):
        """Convert Cookie Quick Manager format to Selenium format"""
        # Extract domain from Host raw
        domain = (
            cookie.get("Host raw", "")
            .replace("https://", "")
            .replace("http://", "")
            .strip("./")
        )

        formatted = {
            "name": cookie.get("Name raw", ""),
            "value": cookie.get("Content raw", ""),
            "domain": domain,
            "path": cookie.get("Path raw", "/"),
            "secure": cookie.get("Send for raw", "true").lower() == "true",
            "httpOnly": cookie.get("HTTP only raw", "false").lower() == "true",
        }

        # Handle expiry
        if "Expires raw" in cookie:
            try:
                formatted["expiry"] = int(cookie["Expires raw"])
            except ValueError:
                pass

        # Handle SameSite
        same_site = cookie.get("SameSite raw", "")
        if same_site == "no_restriction":
            formatted["sameSite"] = "None"
        elif same_site.lower() == "strict":
            formatted["sameSite"] = "Strict"
        else:
            formatted["sameSite"] = "Lax"

        return formatted

    def load_cookies(self, file_path):
        """Load cookies from Cookie Quick Manager export"""
        # First visit the site
        self.driver.get("https://www.tiktok.com")
        time.sleep(2)

        try:
            with open(file_path) as f:
                cookies = json.load(f)

            # Add each cookie
            for cookie in cookies:
                try:
                    formatted_cookie = self.format_cookie(cookie)
                    if formatted_cookie["name"] and formatted_cookie["value"]:
                        self.driver.add_cookie(formatted_cookie)
                        print(f"Added cookie: {formatted_cookie['name']}")
                except Exception as e:
                    print(
                        f"Error adding cookie {cookie.get('Name raw', 'unknown')}: {str(e)}"
                    )

            print("Finished loading cookies")

            # Refresh to apply cookies
            self.driver.refresh()
            time.sleep(2)

        except Exception as e:
            print(f"Error loading cookies: {str(e)}")
            raise

    def random_sleep(self, min_sec=1, max_sec=3):
        """Sleep for a random duration"""
        time.sleep(random.uniform(min_sec, max_sec))

    def scroll_to_element(self, element):
        """Scroll element into view with a smooth motion"""
        self.driver.execute_script(
            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
            element,
        )
        self.random_sleep(0.5, 1)

    def extract_comments(self, url, max_comments=None, scroll_attempts=10):
        """Extract all level-1 comments from a page"""
        print(f"Loading page: {url}")
        self.driver.get(url)
        self.random_sleep(3, 5)  # Wait for initial load

        comments = []
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_count = 0
        seen_comments = set()  # Track unique comments

        print("Starting comment extraction...")
        while scroll_count < scroll_attempts:
            try:
                # Find all level-1 comments
                comment_elements = self.driver.find_elements(
                    By.CSS_SELECTOR, '[data-e2e="comment-level-1"]'
                )

                # Process new comments
                for element in comment_elements:
                    try:
                        # Get comment text
                        comment_text = element.text.strip()

                        # Skip if we've seen this comment or it's empty
                        if not comment_text or comment_text in seen_comments:
                            continue

                        # Add to our collections
                        comments.append(comment_text)
                        seen_comments.add(comment_text)

                        # Scroll to this comment (makes loading look more natural)
                        self.scroll_to_element(element)

                        print(f"Found comment {len(comments)}: {comment_text[:50]}...")

                        # Check if we've hit our limit
                        if max_comments and len(comments) >= max_comments:
                            print(f"Reached maximum comments limit: {max_comments}")
                            return comments

                    except Exception as e:
                        print(f"Error processing comment: {str(e)}")
                        continue

                # Scroll down
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);"
                )
                self.random_sleep(1, 2)

                # Check if we've reached the bottom
                new_height = self.driver.execute_script(
                    "return document.body.scrollHeight"
                )
                if new_height == last_height:
                    scroll_count += 1
                    print(
                        f"No new content loaded. Attempt {scroll_count}/{scroll_attempts}"
                    )
                else:
                    scroll_count = 0  # Reset counter if we found new content
                    print("Found new content. Continuing to scroll...")

                last_height = new_height

            except Exception as e:
                print(f"Error during scrolling: {str(e)}")
                scroll_count += 1

        print(f"Finished extracting comments. Found {len(comments)} unique comments.")
        return comments

    def close(self):
        """Close the browser"""
        self.driver.quit()


TEST_POST_URL = "https://www.tiktok.com/@tjrtrades/video/7379601136627518751"
COOKIES_FILE = "data/tiktok_cookies_firefox.json"


def main():
    scraper = None
    try:
        # Initialize scraper with cookies
        scraper = MinimalFirefoxScraper(cookies_file=COOKIES_FILE)

        # Try loading a page
        url = TEST_POST_URL  # Replace with actual username
        comments = scraper.extract_comments(url)

        pprint(comments)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        if scraper:
            scraper.close()


if __name__ == "__main__":
    main()
