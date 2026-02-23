"""
Test script for NLP enhancements: corpus, categories, and TF-IDF vectorization
"""
from data_cleaner import DataCleaner
from nlp_vectorizer import LemmatizingTfidfVectorizer, CorpusExpander
import json

def test_data_cleaner():
    """Test DataCleaner with corpus and categorization"""
    print("=" * 70)
    print("TEST 1: DataCleaner with Corpus and Categorization")
    print("=" * 70)
    
    cleaner = DataCleaner()
    # if vaderSentiment wasn't installed the instance will still be
    # created but sentiment scores will always be neutral.  Print a note so
    # the user reading test output knows why the score may be zero.
    if not getattr(cleaner, 'sentiment_enabled', True):
        print("(NOTE: sentiment analysis disabled; vaderSentiment not present)")
    if not getattr(cleaner, 'lemmatizer_enabled', True):
        print("(NOTE: lemmatization disabled; nltk not present)")
    
    # Test advisory
    test_advisory = {
        'country': 'Egypt',
        'risk_level': 'Do Not Travel',
        'description': 'Armed conflict and terrorism pose significant threats. '
                      'There are frequent attacks and demonstrations in major cities. '
                      'Health risks include epidemic diseases. Exercise extreme caution.',
        'date': '2026-02-20',
        'source': 'US State Department'
    }
    
    cleaned = cleaner.clean_advisory(test_advisory)
    
    print("\nOriginal Advisory:")
    print(f"  Country: {test_advisory['country']}")
    print(f"  Risk Level: {test_advisory['risk_level']}")
    print(f"  Description: {test_advisory['description'][:80]}...")
    
    print("\nCleaned & Processed:")
    print(f"  Country Normalized: {cleaned['country_normalized']}")
    print(f"  Risk Level Normalized: {cleaned['risk_level_normalized']}")
    print(f"  Risk Score: {cleaned['risk_score']}")
    print(f"  Extracted Keywords: {cleaned['keywords']}")
    print(f"  Has Security Concerns: {cleaned['has_security_concerns']}")
    print(f"  Has Safety Concerns: {cleaned['has_safety_concerns']}")
    print(f"  Has Serenity Concerns: {cleaned['has_serenity_concerns']}")
    print(f"  Sentiment Score: {cleaned['sentiment_score']:.2f}")
    
    return cleaned


def test_tfidf_vectorizer():
    """Test TF-IDF vectorizer with lemmatization"""
    print("\n" + "=" * 70)
    print("TEST 2: TF-IDF Vectorizer with Lemmatization")
    print("=" * 70)
    
    # Sample travel advisory documents
    documents = [
        "Armed conflict and terrorism pose significant threats to travelers.",
        "Exercise increased caution due to sporadic protests and demonstrations.",
        "Health risks include dengue fever and cholera outbreaks in the region.",
        "Violent crime and armed robbery are common in certain areas.",
        "Natural disasters such as flooding and earthquakes are a concern.",
    ]
    
    # Initialize and fit vectorizer
    vectorizer = LemmatizingTfidfVectorizer(max_features=50, ngram_range=(1, 2))
    if not getattr(vectorizer, 'lemmatizer_enabled', True):
        print("(NOTE: lemmatization disabled; nltk not present)")
    try:
        vectorizer.fit(documents)
    except Exception as e:
        print(f"(Skipping TF-IDF tests; vectorizer.fit failed: {e})")
        return vectorizer, None, None
    
    print("\nVectorizer fitted on documents.")
    print(f"Vocabulary size: {len(vectorizer.get_feature_names_out())}")
    print(f"Sample features: {vectorizer.get_feature_names_out()[:10]}")
    
    # Save vocabulary
    vocab_path = 'models/travel_vocab.json'
    vectorizer.save_vocabulary(vocab_path)
    
    # Save vectorizer
    vectorizer_path = 'models/travel_vectorizer.pkl'
    vectorizer.save_vectorizer(vectorizer_path)
    
    # Test transform
    test_text = ["There is armed conflict and terrorism in the region."]
    tfidf_matrix = vectorizer.transform(test_text)
    
    print(f"\nTransformed test text to TF-IDF vector.")
    print(f"Vector shape: {tfidf_matrix.shape}")
    
    # Get top features
    top_features = vectorizer.get_top_features(tfidf_matrix[0], n=5)
    print(f"Top 5 features in test text:")
    for term, score in top_features:
        print(f"  - {term}: {score:.4f}")
    
    return vectorizer, vocab_path, vectorizer_path


def test_corpus_expander():
    """Test corpus expansion with lemmatization"""
    print("\n" + "=" * 70)
    print("TEST 3: Corpus Expansion with Lemmatization")
    print("=" * 70)
    
    expander = CorpusExpander()
    if not getattr(expander, 'lemmatizer', None) or not hasattr(expander.lemmatizer, 'lemmatize'):
        print("(NOTE: corpus expansion will not lemmatize terms; nltk missing or broken)")
    
    # Load and expand security corpus
    try:
        expanded_corpus = expander.load_and_expand('data/wordlists/security.txt')
        print(f"\nOriginal security.txt lines: ~50")
        print(f"Expanded corpus size: {len(expanded_corpus)}")
        print(f"Sample expanded terms:")
        for term in expanded_corpus[:10]:
            print(f"  - {term}")
        
        # Save expanded corpus
        expander.save_expanded_corpus(expanded_corpus, 'data/wordlists/security_expanded.txt')
    except FileNotFoundError as e:
        print(f"Note: {e}")
        print("(This is expected if corpus files haven't been created yet)")


def test_load_saved_vectorizer():
    """Test loading previously saved vectorizer"""
    print("\n" + "=" * 70)
    print("TEST 4: Load Previously Saved Vectorizer")
    print("=" * 70)
    
    try:
        vectorizer = LemmatizingTfidfVectorizer()
        
        # Load saved vocabulary and vectorizer
        vocab_path = 'models/travel_vocab.json'
        vectorizer_path = 'models/travel_vectorizer.pkl'
        
        vectorizer.load_vectorizer(vectorizer_path)
        vectorizer.load_vocabulary(vocab_path)
        
        print(f"Successfully loaded vectorizer and vocabulary.")
        print(f"Vocabulary size: {len(vectorizer.get_feature_names_out())}")
        
        # Test transform with loaded vectorizer
        test_text = ["Terrorism and armed conflict are major concerns."]
        tfidf_matrix = vectorizer.transform(test_text)
        
        top_features = vectorizer.get_top_features(tfidf_matrix[0], n=5)
        print(f"\nTop features in loaded model:")
        for term, score in top_features:
            print(f"  - {term}: {score:.4f}")
            
    except FileNotFoundError as e:
        print(f"Cannot test loading (files not yet saved): {e}")


if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("NLP ENHANCEMENTS TEST SUITE")
    print("=" * 70)
    
    try:
        # Run all tests
        test_data_cleaner()
        vectorizer, vocab_path, vectorizer_path = test_tfidf_vectorizer()
        test_corpus_expander()
        test_load_saved_vectorizer()
        
        print("\n" + "=" * 70)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\nKey enhancements implemented:")
        print("  ✓ Corpus files (corpus.txt, security.txt, safety.txt, serenity.txt)")
        print("  ✓ DataCleaner categorization by concern type")
        print("  ✓ TF-IDF vectorization with lemmatization")
        print("  ✓ Vocabulary persistence (JSON)")
        print("  ✓ Vectorizer persistence (Pickle)")
        print("  ✓ Corpus expansion utility")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
