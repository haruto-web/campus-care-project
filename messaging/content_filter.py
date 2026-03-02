import re

# List of inappropriate words/phrases to filter
INAPPROPRIATE_WORDS = [
    # Filipino curse words
    'putangina', 'putang ina', 'puta', 'gago', 'bobo', 'tanga', 'ulol', 'leche',
    'bwisit', 'peste', 'kingina', 'tangina', 'pakyu', 'fuck you',
    'pakingshet', 'burat', 'tite', 'bilat', 'puke', 'tarantado', 'hinayupak',
    'punyeta', 'hudas', 'pokpok', 'bayot',
    
    # English inappropriate words
    'fuck', 'shit', 'damn', 'bitch', 'asshole', 'bastard', 'whore', 'slut',
    'cunt', 'dick', 'cock', 'pussy', 'tits', 'boobs', 'nude', 'naked',
    'sex', 'porn', 'masturbate', 'orgasm', 'penis', 'vagina',
    
    # Variations and leetspeak
    'f*ck', 'sh*t', 'b*tch', 'a$$', 'fck', 'sht', 'btch', 'fuk', 'fuc',
    'p0rn', 'n4ked', 's3x', 'b00bs', 'a$$h0le',
]

def contains_inappropriate_content(text):
    """
    Check if text contains inappropriate words or phrases.
    Returns tuple (is_inappropriate, filtered_words_found)
    """
    if not text:
        return False, []
    
    # Convert to lowercase for checking
    text_lower = text.lower()
    
    # Remove special characters and normalize spaces
    normalized_text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text_lower)
    normalized_text = re.sub(r'\s+', ' ', normalized_text).strip()
    
    found_words = []
    
    for word in INAPPROPRIATE_WORDS:
        # Check exact word match with word boundaries
        pattern = r'\b' + re.escape(word.lower()) + r'\b'
        if re.search(pattern, normalized_text):
            found_words.append(word)
        
        # Also check without word boundaries for compound words
        if word.lower() in normalized_text:
            if word not in found_words:
                found_words.append(word)
    
    return len(found_words) > 0, found_words

def filter_message_content(text):
    """
    Replace inappropriate words with asterisks while preserving message structure.
    """
    if not text:
        return text
    
    filtered_text = text
    text_lower = text.lower()
    
    for word in INAPPROPRIATE_WORDS:
        # Replace with asterisks of same length
        replacement = '*' * len(word)
        
        # Case-insensitive replacement
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        filtered_text = pattern.sub(replacement, filtered_text)
    
    return filtered_text