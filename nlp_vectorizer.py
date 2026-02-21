"""
NLP Vectorization Module with TF-IDF, Lemmatization, and Vocabulary Persistence
"""
import json
import pickle
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import nltk
import numpy as np

# Download required NLTK data on import
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)

try:
    nltk.data.find('corpora/omw-1.4')
except LookupError:
    nltk.download('omw-1.4', quiet=True)


class LemmatizingTfidfVectorizer:
    """
    TF-IDF vectorizer with built-in lemmatization and vocabulary persistence.
    
    Features:
    - Lemmatizes tokens before vectorization
    - Saves and loads vocabulary to/from JSON
    - Saves and loads fitted vectorizer to/from pickle
    - Category-aware corpus support (security, safety, serenity)
    """
    
    def __init__(self, 
                 max_features: int = 500,
                 min_df: int = 1,
                 max_df: float = 0.95,
                 ngram_range: Tuple[int, int] = (1, 2)):
        """
        Initialize the vectorizer.
        
        Args:
            max_features: Maximum number of features to extract
            min_df: Minimum document frequency (absolute count or ratio)
            max_df: Maximum document frequency (ratio)
            ngram_range: Range of n-gram sizes
        """
        self.lemmatizer = WordNetLemmatizer()
        self.max_features = max_features
        self.min_df = min_df
        self.max_df = max_df
        self.ngram_range = ngram_range
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.vocabulary_: Optional[Dict[str, int]] = None
        self._category_keywords: Dict[str, Set[str]] = {}
        
        # Load category keywords if available
        self._load_category_keywords()
    
    def _load_category_keywords(self) -> None:
        """Load predefined category keywords from corpus files."""
        categories = {
            'security': 'data/wordlists/security.txt',
            'safety': 'data/wordlists/safety.txt',
            'serenity': 'data/wordlists/serenity.txt'
        }
        
        for category, filepath in categories.items():
            try:
                p = Path(filepath)
                if p.is_file():
                    with p.open('r', encoding='utf-8') as f:
                        keywords = set(ln.strip().lower() 
                                     for ln in f if ln.strip())
                        self._category_keywords[category] = keywords
            except Exception as e:
                print(f"Warning: Could not load {category} keywords from {filepath}: {e}")
    
    def _lemmatize_tokens(self, text: str) -> str:
        """
        Tokenize and lemmatize text.
        
        Args:
            text: Input text
            
        Returns:
            Space-separated lemmatized tokens
        """
        try:
            tokens = word_tokenize(text.lower())
            lemmatized = [self.lemmatizer.lemmatize(token) for token in tokens]
            return ' '.join(lemmatized)
        except Exception:
            # Fallback to simple lowercasing if tokenization fails
            return text.lower()
    
    def fit(self, documents: List[str]) -> 'LemmatizingTfidfVectorizer':
        """
        Fit the TF-IDF vectorizer on documents.
        
        Args:
            documents: List of text documents
            
        Returns:
            Self
        """
        # Lemmatize all documents
        lemmatized_docs = [self._lemmatize_tokens(doc) for doc in documents]
        
        # Create and fit the vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            min_df=self.min_df,
            max_df=self.max_df,
            ngram_range=self.ngram_range
        )
        self.vectorizer.fit(lemmatized_docs)
        self.vocabulary_ = self.vectorizer.vocabulary_
        
        return self
    
    def transform(self, documents: List[str]) -> np.ndarray:
        """
        Transform documents to TF-IDF vectors.
        
        Args:
            documents: List of text documents
            
        Returns:
            Sparse matrix of TF-IDF vectors
        """
        if self.vectorizer is None:
            raise RuntimeError("Vectorizer not fitted. Call fit() first.")
        
        lemmatized_docs = [self._lemmatize_tokens(doc) for doc in documents]
        return self.vectorizer.transform(lemmatized_docs)
    
    def fit_transform(self, documents: List[str]) -> np.ndarray:
        """
        Fit and transform documents in one step.
        
        Args:
            documents: List of text documents
            
        Returns:
            Sparse matrix of TF-IDF vectors
        """
        self.fit(documents)
        return self.transform(documents)
    
    def get_feature_names_out(self) -> List[str]:
        """
        Get the output feature names.
        
        Returns:
            List of feature names (terms)
        """
        if self.vectorizer is None:
            raise RuntimeError("Vectorizer not fitted.")
        return self.vectorizer.get_feature_names_out().tolist()
    
    def save_vocabulary(self, filepath: str) -> None:
        """
        Save vocabulary to JSON file.
        
        Args:
            filepath: Path to save vocabulary JSON
        """
        if self.vocabulary_ is None:
            raise RuntimeError("No vocabulary to save. Call fit() first.")
        
        p = Path(filepath)
        p.parent.mkdir(parents=True, exist_ok=True)
        
        with p.open('w', encoding='utf-8') as f:
            json.dump(self.vocabulary_, f, indent=2, ensure_ascii=False)
        
        print(f"Vocabulary saved to {filepath}")
    
    def load_vocabulary(self, filepath: str) -> None:
        """
        Load vocabulary from JSON file.
        
        Args:
            filepath: Path to vocabulary JSON
        """
        p = Path(filepath)
        if not p.is_file():
            raise FileNotFoundError(f"Vocabulary file not found: {filepath}")
        
        with p.open('r', encoding='utf-8') as f:
            self.vocabulary_ = json.load(f)
        
        # Reconstruct vectorizer with loaded vocabulary
        if self.vectorizer is not None:
            self.vectorizer.vocabulary_ = self.vocabulary_
        
        print(f"Vocabulary loaded from {filepath}")
    
    def save_vectorizer(self, filepath: str) -> None:
        """
        Save fitted vectorizer to pickle file.
        
        Args:
            filepath: Path to save vectorizer pickle
        """
        if self.vectorizer is None:
            raise RuntimeError("No vectorizer to save. Call fit() first.")
        
        p = Path(filepath)
        p.parent.mkdir(parents=True, exist_ok=True)
        
        with p.open('wb') as f:
            pickle.dump(self.vectorizer, f)
        
        print(f"Vectorizer saved to {filepath}")
    
    def load_vectorizer(self, filepath: str) -> None:
        """
        Load fitted vectorizer from pickle file.
        
        Args:
            filepath: Path to vectorizer pickle
        """
        p = Path(filepath)
        if not p.is_file():
            raise FileNotFoundError(f"Vectorizer file not found: {filepath}")
        
        with p.open('rb') as f:
            self.vectorizer = pickle.load(f)
        
        if self.vectorizer.vocabulary_:
            self.vocabulary_ = self.vectorizer.vocabulary_
        
        print(f"Vectorizer loaded from {filepath}")
    
    def categorize_text(self, text: str) -> Dict[str, bool]:
        """
        Categorize text by checking for category-specific keywords.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with category: boolean flags
        """
        text_lower = text.lower()
        result = {}
        
        for category, keywords in self._category_keywords.items():
            result[category] = any(kw in text_lower for kw in keywords)
        
        return result
    
    def get_top_features(self, tfidf_vector, n: int = 10) -> List[Tuple[str, float]]:
        """
        Extract top N features from a TF-IDF vector.
        
        Args:
            tfidf_vector: A single TF-IDF vector (1D sparse matrix)
            n: Number of top features to return
            
        Returns:
            List of (feature_name, score) tuples
        """
        if self.vectorizer is None:
            raise RuntimeError("Vectorizer not fitted.")
        
        # Convert sparse vector to dense if needed
        if hasattr(tfidf_vector, 'toarray'):
            vector = tfidf_vector.toarray().flatten()
        else:
            vector = tfidf_vector
        
        feature_names = self.get_feature_names_out()
        top_indices = np.argsort(vector)[-n:][::-1]
        
        result = []
        for idx in top_indices:
            if vector[idx] > 0:
                result.append((feature_names[idx], float(vector[idx])))
        
        return result


class CorpusExpander:
    """
    Expand a corpus using lemmatization and related term generation.
    """
    
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
    
    def expand_corpus(self, corpus: List[str]) -> List[str]:
        """
        Expand corpus by adding lemmatized forms.
        
        Args:
            corpus: List of phrases/terms
            
        Returns:
            Expanded corpus with lemmatized variations
        """
        expanded = set()
        
        for term in corpus:
            expanded.add(term)
            
            # Add lemmatized version
            try:
                tokens = word_tokenize(term.lower())
                lemmatized = ' '.join(self.lemmatizer.lemmatize(token) 
                                     for token in tokens)
                if lemmatized != term:
                    expanded.add(lemmatized)
            except Exception:
                pass
        
        return sorted(list(expanded))
    
    def load_and_expand(self, filepath: str) -> List[str]:
        """
        Load corpus from file and expand it.
        
        Args:
            filepath: Path to corpus file
            
        Returns:
            Expanded corpus
        """
        p = Path(filepath)
        if not p.is_file():
            raise FileNotFoundError(f"Corpus file not found: {filepath}")
        
        with p.open('r', encoding='utf-8') as f:
            corpus = [ln.strip() for ln in f if ln.strip()]
        
        return self.expand_corpus(corpus)
    
    def save_expanded_corpus(self, corpus: List[str], filepath: str) -> None:
        """
        Save expanded corpus to file.
        
        Args:
            corpus: List of terms
            filepath: Path to save
        """
        p = Path(filepath)
        p.parent.mkdir(parents=True, exist_ok=True)
        
        with p.open('w', encoding='utf-8') as f:
            for term in corpus:
                f.write(term + '\n')
        
        print(f"Expanded corpus saved to {filepath}")
