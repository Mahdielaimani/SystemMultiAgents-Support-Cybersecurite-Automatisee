import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

class GuardianRobot:
    def __init__(self, initial_url, max_depth=3, timeout=5, user_agent=None):
        """
        Initializes the GuardianRobot with a starting URL, maximum depth to crawl,
        request timeout, and a custom User-Agent.
        """
        self.initial_url = initial_url
        self.max_depth = max_depth
        self.timeout = timeout
        self.user_agent = user_agent or "GuardianRobot/1.0"
        self.visited = set()
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
        self.vulnerabilities = []

    def crawl(self):
        """
        Initiates the crawling process from the initial URL.
        """
        self._crawl_recursive(self.initial_url, depth=0)
        return self.vulnerabilities

    def _crawl_recursive(self, url, depth):
        """
        Recursively crawls the web pages up to the maximum depth.
        """
        if depth > self.max_depth or url in self.visited:
            return

        self.visited.add(url)

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

            soup = BeautifulSoup(response.content, "html.parser")

            self.scan_page(url, response, soup)

            for link in soup.find_all("a", href=True):
                absolute_url = urljoin(url, link["href"])
                parsed_url = urlparse(absolute_url)

                # Only crawl HTTP and HTTPS links on the same domain
                if parsed_url.scheme in ("http", "https") and parsed_url.netloc == urlparse(self.initial_url).netloc:
                    self._crawl_recursive(absolute_url, depth + 1)

        except requests.exceptions.RequestException as e:
            print(f"Error crawling {url}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while crawling {url}: {e}")

    def scan_page(self, url, response, soup):
        """
        Scans a single web page for common vulnerabilities.
        """
        self.check_xss(url, response, soup)
        self.check_sql_injection(url, response)
        self.check_csrf(url, response, soup)
        self.check_open_redirect(url, response)
        self.check_insecure_cookies(url, response)

    def check_xss(self, url, response, soup):
        """
        Checks for potential Cross-Site Scripting (XSS) vulnerabilities.
        """
        # Look for input fields without proper encoding
        for input_field in soup.find_all("input"):
            if input_field.get("type") != "hidden":
                self.vulnerabilities.append({
                    "url": url,
                    "vulnerability": "Potential XSS vulnerability",
                    "details": f"Unencoded input field: {input_field}"
                })

    def check_sql_injection(self, url, response):
        """
        Checks for potential SQL Injection vulnerabilities by analyzing the URL and form submissions.
        This is a basic check and may require more sophisticated techniques.
        """
        # Check for common SQL injection patterns in the URL
        sql_patterns = [r"['\"]?\s*(?:SELECT|INSERT|UPDATE|DELETE|UNION|DROP)\s+.*?(?:FROM|INTO|TABLE|DATABASE)",
                        r".*?\s*;\s*.*?",
                        r".*?\s*--\s*.*?"]

        if response.request.method == 'GET':
            for pattern in sql_patterns:
                if re.search(pattern, url):
                    self.vulnerabilities.append({
                        "url": url,
                        "vulnerability": "Potential SQL Injection vulnerability (GET)",
                        "details": f"Suspicious pattern found in URL: {pattern}"
                    })

    def check_csrf(self, url, response, soup):
        """
        Checks for potential Cross-Site Request Forgery (CSRF) vulnerabilities.
        """
        # Look for forms without CSRF protection tokens
        forms = soup.find_all("form")
        for form in forms:
            if form.get("method", "").lower() == "post":
                # Check if the form contains a CSRF token field
                csrf_token_present = False
                for input_field in form.find_all("input"):
                    if input_field.get("name") == "csrf_token" or input_field.get("name") == "csrf" or input_field.get("name", "").lower().endswith("_token"):
                        csrf_token_present = True
                        break

                if not csrf_token_present:
                    # Regex to find forms without CSRF protection - LIGNE CORRIGÉE
                    if re.search(r'<form[^>]*method\s*=\s*["|\']post["|\'][^>]*>(?!.*csrf)', str(form), re.IGNORECASE):
                        self.vulnerabilities.append({
                            "url": url,
                            "vulnerability": "Potential CSRF vulnerability",
                            "details": "Form without CSRF protection token"
                        })

    def check_open_redirect(self, url, response):
        """
        Checks for potential Open Redirect vulnerabilities.
        """
        # Look for redirects to external domains
        if response.history:
            for redirect in response.history:
                if urlparse(redirect.url).netloc != urlparse(url).netloc:
                    self.vulnerabilities.append({
                        "url": url,
                        "vulnerability": "Potential Open Redirect vulnerability",
                        "details": f"Redirects to external domain: {redirect.url}"
                    })

    def check_insecure_cookies(self, url, response):
        """
        Checks for insecure cookie attributes (e.g., missing Secure or HttpOnly flags).
        """
        for cookie in response.cookies:
            if not cookie.secure:
                self.vulnerabilities.append({
                    "url": url,
                    "vulnerability": "Insecure Cookie",
                    "details": f"Cookie '{cookie.name}' is missing the Secure flag"
                })
            if not cookie.has_non_standard_attr("httponly"):
                self.vulnerabilities.append({
                    "url": url,
                    "vulnerability": "Insecure Cookie",
                    "details": f"Cookie '{cookie.name}' is missing the HttpOnly flag"
                })

# Création d'une instance pour l'importation
guardian_robot = GuardianRobot("http://example.com")
