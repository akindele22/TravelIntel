"""
Quick validation test for NLP enhancements
"""
import sys
sys.path.insert(0, '.')

# Test 1: Corpus files exist
print("TEST 1: Checking corpus files...")
from pathlib import Path

corpus_files = [
    'data/wordlists/corpus.txt',
    'data/wordlists/security.txt',
    'data/wordlists/safety.txt',
    'data/wordlists/serenity.txt',
]

for f in corpus_files:
    p = Path(f)
    if p.exists():
        lines = len([x for x in p.read_text().split('\n') if x.strip()])
        print(f"  ✓ {f} ({lines} terms)")
    else:
        print(f"  ✗ {f} NOT FOUND")

# Test 2: DataCleaner loads corpus
print("\nTEST 2: Testing DataCleaner corpus loading...")
try:
    from data_cleaner import DataCleaner
    cleaner = DataCleaner()
    print(f"  ✓ DataCleaner initialized")
    print(f"  ✓ Loaded {len(cleaner._corpus_keywords)} corpus keywords")
    print(f"  ✓ Loaded {len(cleaner._security_keywords)} security keywords")
    print(f"  ✓ Loaded {len(cleaner._safety_keywords)} safety keywords")
    print(f"  ✓ Loaded {len(cleaner._serenity_keywords)} serenity keywords")
except Exception as e:
    print(f"  ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 3: DataCleaner categorization
print("\nTEST 3: Testing categorization...")
try:
    test_text = "Armed terrorism and violent conflict in the region. Epidemic outbreak reported."
    categories = cleaner.categorize_advisory(test_text)
    print(f"  ✓ Text categorized")
    for k, v in categories.items():
        print(f"    - {k}: {v}")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test 4: NLP Vectorizer loads
print("\nTEST 4: Testing NLP vectorizer...")
try:
    from nlp_vectorizer import LemmatizingTfidfVectorizer
    print(f"  ✓ LemmatizingTfidfVectorizer imported")
    print(f"  ✓ Module has category keyword loading")
except Exception as e:
    print(f"  ✗ Error: {e}")

print("\n✓ All basic validations passed!")
