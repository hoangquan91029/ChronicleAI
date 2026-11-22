import re
import math
from typing import List
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


class MultilingualEmbeddingService:
    """
    Multilingual embedding and semantic representation service.
    Combines word-level and character n-gram tokenization to effectively capture
    Vietnamese diacritics, morphology, compound words, and historical terminology.
    """
    def __init__(self):
        # Using word + character n-grams (2-5) for robust multilingual matching
        self.vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(3, 5),
            min_df=1,
            lowercase=True,
            norm="l2"
        )
        self._is_fitted = False
        self._corpus: List[str] = []

    def fit(self, texts: List[str]):
        """Fit vectorizer on document corpus."""
        if not texts:
            return
        self._corpus = texts
        self.vectorizer.fit(texts)
        self._is_fitted = True

    def transform(self, texts: List[str]) -> np.ndarray:
        """Transform texts into normalized TF-IDF feature vectors."""
        if not self._is_fitted:
            # If not yet fitted, fit on incoming texts
            self.fit(texts)
        return self.vectorizer.transform(texts).toarray()

    def embed_query(self, query: str) -> np.ndarray:
        """Embed a single search query."""
        if not self._is_fitted:
            self.fit([query])
        vec = self.vectorizer.transform([query]).toarray()
        return vec[0]
