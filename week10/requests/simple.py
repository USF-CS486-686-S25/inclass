#!/usr/bin/env python3
import sys
import requests

def fetch_url(url):
    """Fetch content from the specified URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

def main():
    """Main function to handle command-line arguments and fetch the URL."""
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <url>")
        sys.exit(1)
    
    url = sys.argv[1]
    content = fetch_url(url)
    print(content)

if __name__ == "__main__":
    main()