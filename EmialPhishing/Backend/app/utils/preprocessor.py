import re
import pandas as pd
from typing import List, Tuple
from bs4 import BeautifulSoup
import logging
from app.config.settings import settings

logger = logging.getLogger(__name__)


class EmailPreprocessor:
    def __init__(self):
        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
        self.special_chars_pattern = re.compile(r'[^a-zA-Z0-9\s]')
        self.whitespace_pattern = re.compile(r'\s+')
        
    def clean_text(self, text: str) -> str:
        """Clean email text by removing HTML, URLs, emails, and special characters."""
        if not isinstance(text, str):
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove HTML tags
        text = self._remove_html_tags(text)
        
        # Remove URLs
        text = self.url_pattern.sub(' [URL] ', text)
        
        # Remove email addresses
        text = self.email_pattern.sub(' [EMAIL] ', text)
        
        # Remove phone numbers
        text = self.phone_pattern.sub(' [PHONE] ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\!\?\,\;\:]', ' ', text)
        
        # Normalize whitespace
        text = self.whitespace_pattern.sub(' ', text).strip()
        
        return text
    
    def _remove_html_tags(self, text: str) -> str:
        """Remove HTML tags using BeautifulSoup."""
        try:
            soup = BeautifulSoup(text, 'html.parser')
            return soup.get_text()
        except Exception as e:
            logger.warning(f"Error removing HTML tags: {e}")
            return text
    
    def load_and_preprocess_dataset(self, file_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load dataset and preprocess it."""
        try:
            logger.info(f"Loading dataset from {file_path}")
            
            # Load CSV
            df = pd.read_csv(file_path)
            
            # Rename columns
            df = df.rename(columns={
                'Email Text': 'text',
                'Email Type': 'label'
            })
            
            # Convert labels to binary
            df['label'] = df['label'].map({
                'Safe Email': 0,
                'Phishing Email': 1
            })
            
            # Remove rows with missing values
            df = df.dropna(subset=['text', 'label'])
            
            # Clean text
            logger.info("Preprocessing email texts...")
            df['cleaned_text'] = df['text'].apply(self.clean_text)
            
            # Remove empty texts after cleaning
            df = df[df['cleaned_text'].str.len() > 10]
            
            logger.info(f"Dataset loaded successfully. Shape: {df.shape}")
            logger.info(f"Label distribution: {df['label'].value_counts().to_dict()}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error loading dataset: {e}")
            raise
    
    def split_dataset(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Split dataset into train and test sets."""
        try:
            from sklearn.model_selection import train_test_split
            
            train_df, test_df = train_test_split(
                df,
                test_size=1 - settings.train_split,
                random_state=settings.random_seed,
                stratify=df['label']
            )
            
            logger.info(f"Train set size: {len(train_df)}")
            logger.info(f"Test set size: {len(test_df)}")
            
            return train_df, test_df
            
        except Exception as e:
            logger.error(f"Error splitting dataset: {e}")
            raise
    
    def extract_features_for_osint(self, text: str) -> dict:
        """Extract features for OSINT analysis."""
        features = {
            'url_count': len(self.url_pattern.findall(text)),
            'email_count': len(self.email_pattern.findall(text)),
            'phone_count': len(self.phone_pattern.findall(text)),
            'text_length': len(text),
            'word_count': len(text.split()),
            'has_html': bool(BeautifulSoup(text, 'html.parser').find())
        }
        
        return features
