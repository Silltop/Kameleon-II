import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import Optional, Tuple
import os
import chardet  # For detecting character encoding
import codecs  # For handling manual decoding attempts


# Load maintenance keywords from the file
def load_maintenance_keywords(file_path: str) -> list[str]:
    try:
        with open(file_path, 'r') as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []


# Define constants
maintenance_keywords = load_maintenance_keywords(os.path.join(os.getcwd(), "maintenance_keywords.txt"))
error_keywords = load_maintenance_keywords(os.path.join(os.getcwd(), "error.txt"))
required_elements = ["div", "head", "body"]

# Weights for different checks
STATUS_CODE_PENALTY = 0.8  # Subtract 70% if the status code is not 200
MAINTENANCE_PENALTY = 0.2  # Subtract 50% if maintenance keywords are found
ERROR_PENALTY = 0.5  # Subtract 30% if PHP errors are found
MISSING_CONTENT_PENALTY = 0.5  # Subtract 20% if required elements are missing
ENCODING_ISSUE_PENALTY = 0.1  # Subtract 20% if there is a detected encoding issue


# Helper function to fetch page content asynchronously
async def fetch_page(url: str, session: aiohttp.ClientSession) -> tuple[int, str, str, str | None | float] | tuple[
    None, None]:
    try:
        async with session.get(url, timeout=10) as response:
            content = await response.text()
            encoding = response.headers.get('Content-Type', '').lower()
            if 'charset=' in encoding:
                encoding = encoding.split('charset=')[-1]
            else:
                # Default to utf-8 if no charset is found
                encoding = 'utf-8'
            detected_encoding = chardet.detect(content.encode())
            return response.status, content, encoding, detected_encoding['encoding']
    except aiohttp.ClientError as e:
        print(f"Error accessing {url}: {e}")
        return None, None


# Method 1: Check page status code and fetch content
async def check_page_status(url: str, session: aiohttp.ClientSession) -> Optional[int]:
    status, content, _, _ = await fetch_page(url, session)
    return status


# Method 2: Check for maintenance and PHP error keywords
async def check_keywords(url: str, content: str) -> float:
    maintenance_confidence = 0
    for keyword in maintenance_keywords:
        if keyword in content:
            print(f"Maintenance keyword '{keyword}' detected at {url}")
            maintenance_confidence = MAINTENANCE_PENALTY  # Negative impact
            break

    error_confidence = 0
    for error in error_keywords:
        if error in content:
            print(f"Page error occurrence {error} detected on the page at {url}")
            error_confidence = ERROR_PENALTY  # Negative impact
            break

    return maintenance_confidence + error_confidence


# Method 3: Check for required elements in the content using BeautifulSoup
async def check_required_elements(url: str, content: str) -> float:
    soup = BeautifulSoup(content, 'html.parser')
    missing_elements = 0
    for element in required_elements:
        if not soup.find_all(lambda tag: tag.name == element):
            print(f"Critical content missing: {element} at {url}")
            missing_elements += 1

    # Return the penalty based on how many elements are missing
    return MISSING_CONTENT_PENALTY * missing_elements


async def check_encoding_issues(content: str, encoding: str, detected_encoding: str = "utf-8") -> float:
    try:
        # Try to decode the content with the detected encoding
        decoded_content = content.encode(detected_encoding).decode(encoding)
        # Check if the content is still garbled
        if "�" in decoded_content:  # common placeholder for unrecognized characters
            print(f"Content is unreadable due to encoding issue.")
            return ENCODING_ISSUE_PENALTY  # Penalty for encoding issues
        return 0
    except LookupError:
        print("Encoding issue detected")
        return ENCODING_ISSUE_PENALTY  # Penalty for encoding issues
    except UnicodeDecodeError:
        print("Encoding issue detected")
        return ENCODING_ISSUE_PENALTY  # Penalty for encoding issues


# Main method to orchestrate all checks asynchronously and calculate confidence
async def check_page(url: str) -> float:
    async with aiohttp.ClientSession() as session:
        # Check page status and fetch content
        status = await check_page_status(url, session)

        # Initialize confidence score
        confidence_score = 1.0  # Start with 100% confidence

        if status != 200:
            print(f"Page status is not accessible, got: {status} at {url}")
            # Apply penalty for non-200 status code
            confidence_score -= STATUS_CODE_PENALTY  # Subtract 70% confidence

        if status == 200:
            # Fetch content and proceed with other checks
            _, content, encoding, detected_encoding = await fetch_page(url, session)

            # Run all checks asynchronously
            tasks = [
                check_keywords(url, content),
                check_required_elements(url, content),
                check_encoding_issues(content, encoding, detected_encoding)
            ]
            results = await asyncio.gather(*tasks)

            # Apply penalties based on the checks
            for result in results:
                confidence_score -= result

            # Ensure the confidence score stays between 0 and 1 (i.e., 0% and 100%)
            confidence_score = max(0, min(1, confidence_score))  # Normalize to 0-1 range

        # Convert the score to a percentage (0-100)
        return confidence_score * 100


# Example URL to check
url = "https://kki-bci.pl/"
confidence = asyncio.run(check_page(url))
print(f"Confidence that the page {url} is working: {confidence:.2f}%")
url = "https://albert.kki.pl/"
confidence = asyncio.run(check_page(url))
print(f"Confidence that the page {url} is working: {confidence:.2f}%")
