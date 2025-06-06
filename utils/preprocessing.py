"""
Preprocessing utilities for NetGuardian.
"""
import re
from typing import List, Dict, Any, Optional

def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace and normalizing.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text

def extract_urls(text: str) -> List[str]:
    """
    Extract URLs from text.
    
    Args:
        text: Text to extract URLs from
        
    Returns:
        List of extracted URLs
    """
    # Simple URL regex pattern
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    
    # Find all URLs
    urls = re.findall(url_pattern, text)
    
    return urls

def extract_ip_addresses(text: str) -> List[str]:
    """
    Extract IP addresses from text.
    
    Args:
        text: Text to extract IP addresses from
        
    Returns:
        List of extracted IP addresses
    """
    # IPv4 regex pattern
    ipv4_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    
    # Find all IPv4 addresses
    ipv4_addresses = re.findall(ipv4_pattern, text)
    
    # Filter valid IP addresses
    valid_ips = []
    for ip in ipv4_addresses:
        octets = ip.split('.')
        if all(0 <= int(octet) <= 255 for octet in octets):
            valid_ips.append(ip)
    
    return valid_ips

def extract_email_addresses(text: str) -> List[str]:
    """
    Extract email addresses from text.
    
    Args:
        text: Text to extract email addresses from
        
    Returns:
        List of extracted email addresses
    """
    # Email regex pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    # Find all email addresses
    emails = re.findall(email_pattern, text)
    
    return emails

def normalize_query(query: str) -> str:
    """
    Normalize a query for consistent processing.
    
    Args:
        query: Query to normalize
        
    Returns:
        Normalized query
    """
    # Convert to lowercase
    query = query.lower()
    
    # Remove punctuation
    query = re.sub(r'[^\w\s]', ' ', query)
    
    # Clean whitespace
    query = clean_text(query)
    
    return query

def extract_security_terms(text: str) -> List[str]:
    """
    Extract security-related terms from text.
    
    Args:
        text: Text to extract terms from
        
    Returns:
        List of extracted security terms
    """
    # List of common security terms
    security_terms = [
        "vulnerability", "exploit", "malware", "virus", "ransomware",
        "phishing", "attack", "breach", "hack", "security", "firewall",
        "encryption", "authentication", "authorization", "xss", "csrf",
        "sql injection", "ddos", "mitm", "man in the middle", "backdoor",
        "zero-day", "patch", "cve", "threat", "risk", "compliance"
    ]
    
    # Find all security terms
    found_terms = []
    for term in security_terms:
        if re.search(r'\b' + re.escape(term) + r'\b', text.lower()):
            found_terms.append(term)
    
    return found_terms
