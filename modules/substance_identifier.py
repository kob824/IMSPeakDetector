import numpy as np
from modules import sqlite_helper

# Default tolerance for K0 value matching
DEFAULT_K0_TOLERANCE = 0.02

def identify_substances(pos_k0_values, neg_k0_values, tolerance=DEFAULT_K0_TOLERANCE):
    """
    Identify substances by comparing K0 values with the library.
    Returns a list of identified substances.
    """
    library = sqlite_helper.get_substance_library()
    identified_substances = []
    
    for _, substance in library.iterrows():
        substance_name = substance['substance_name']
        
        # Check positive spectrum K0 values
        pos_matches = []
        for i in range(1, 4):  # Check k0_pos_1, k0_pos_2, k0_pos_3
            k0_col = f'k0_pos_{i}'
            if substance[k0_col] > 0:  # Only check non-zero values
                # Check if this K0 value matches any in our detected peaks
                for k0 in pos_k0_values:
                    if abs(k0 - substance[k0_col]) <= tolerance:
                        pos_matches.append((k0_col, k0, substance[k0_col]))
                        break
        
        # Check negative spectrum K0 values
        neg_matches = []
        for i in range(1, 4):  # Check k0_neg_1, k0_neg_2, k0_neg_3
            k0_col = f'k0_neg_{i}'
            if substance[k0_col] > 0:  # Only check non-zero values
                # Check if this K0 value matches any in our detected peaks
                for k0 in neg_k0_values:
                    if abs(k0 - substance[k0_col]) <= tolerance:
                        neg_matches.append((k0_col, k0, substance[k0_col]))
                        break
        
        # Count required matches (non-zero K0 values in library)
        required_pos_matches = sum(1 for i in range(1, 4) if substance[f'k0_pos_{i}'] > 0)
        required_neg_matches = sum(1 for i in range(1, 4) if substance[f'k0_neg_{i}'] > 0)
        
        # Substance is identified if all required K0 values match
        if (len(pos_matches) == required_pos_matches and required_pos_matches > 0) or \
           (len(neg_matches) == required_neg_matches and required_neg_matches > 0):
            identified_substances.append({
                'name': substance_name,
                'pos_matches': pos_matches,
                'neg_matches': neg_matches
            })
    
    return identified_substances
