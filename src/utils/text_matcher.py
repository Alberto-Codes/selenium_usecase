import re
from fuzzywuzzy import fuzz

class PayeeMatcher:
    """
    A class responsible for matching payee names in OCR-extracted text.
    """

    def __init__(self, threshold=80):
        """
        Initialize the PayeeMatcher with a threshold for fuzzy matching.

        Args:
            threshold (int): The minimum fuzzy match score to consider a match valid. Defaults to 80.
        """
        self.threshold = threshold

    def clean_text_for_matching(self, text):
        """
        Clean and prepare text for matching by removing special characters and multiple spaces.
        
        Args:
            text (str): The text to clean.

        Returns:
            str: The cleaned and normalized text.
        """
        text = re.sub(r'\s+', ' ', text)  # Normalize all whitespace to a single space
        text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation and special characters
        return text.strip().lower()

    def fuzzy_match_text(self, extracted_text, payee):
        """
        Perform fuzzy matching between the extracted text and the payee.

        Args:
            extracted_text (str): The text extracted by OCR.
            payee (str): The payee name to match against.

        Returns:
            int: The fuzzy match score.
        """
        match_score = fuzz.partial_ratio(payee, extracted_text)
        return match_score

    def match_payees(self, extracted_text, payees):
        """
        Match multiple payees against the extracted text.

        Args:
            extracted_text (str): The text extracted by OCR.
            payees (list of str): List of payee names to match against.

        Returns:
            dict: A dictionary containing match results and possible matches.
        """
        extracted_text_clean = self.clean_text_for_matching(extracted_text)
        matched = {}
        possible_matches = {}

        for payee in payees:
            if not payee:
                continue

            payee_clean = self.clean_text_for_matching(payee)

            # Use exact match first
            exact_match = re.search(re.escape(payee_clean), extracted_text_clean)
            if exact_match:
                matched[payee] = True
                possible_matches[payee] = exact_match.group()
                continue  # Skip to the next payee if an exact match is found

            # Use fuzzy matching as a fallback
            match_score = self.fuzzy_match_text(extracted_text_clean, payee_clean)
            if match_score >= self.threshold:
                matched[payee] = True
                possible_matches[payee] = f"Fuzzy match ({match_score}%)"
            else:
                matched[payee] = False

        return matched, possible_matches
