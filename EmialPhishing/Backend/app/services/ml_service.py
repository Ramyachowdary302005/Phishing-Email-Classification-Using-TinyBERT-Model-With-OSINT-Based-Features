import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from transformers import pipeline
import pandas as pd
from datasets import Dataset
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report
import logging
from typing import Dict, Tuple, Optional
from pathlib import Path
import numpy as np
from app.config.settings import settings

logger = logging.getLogger(__name__)


class MLService:
    def __init__(self):
        self.model_name = settings.model_name
        self.max_length = settings.max_token_length
        self.model_cache_dir = settings.model_cache_dir
        self.model = None
        self.tokenizer = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Create model cache directory
        Path(self.model_cache_dir).mkdir(parents=True, exist_ok=True)
        
    def load_model_and_tokenizer(self, model_path: Optional[str] = None):
        """Load pre-trained model and tokenizer."""
        try:
            model_path = model_path or self.model_cache_dir
            
            if Path(model_path).exists() and any(Path(model_path).iterdir()):
                logger.info(f"Loading fine-tuned model from {model_path}")
                self.tokenizer = AutoTokenizer.from_pretrained(model_path)
                self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
            else:
                logger.info(f"Loading pre-trained model {self.model_name}")
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name, num_labels=2)
            
            # Move to device
            self.model.to(self.device)
            
            logger.info(f"Model loaded successfully on device: {self.device}")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def preprocess_data(self, texts: pd.Series, labels: pd.Series) -> Dataset:
        """Preprocess data for training."""
        def tokenize_function(examples):
            return self.tokenizer(
                examples["text"],
                truncation=True,
                padding="max_length",
                max_length=self.max_length,
                return_tensors="pt"
            )
        
        # Create dataset
        df = pd.DataFrame({
            'text': texts,
            'label': labels
        })
        
        dataset = Dataset.from_pandas(df)
        
        # Tokenize
        tokenized_dataset = dataset.map(tokenize_function, batched=True)
        
        # Set format for PyTorch
        tokenized_dataset.set_format("torch", columns=["input_ids", "attention_mask", "label"])
        
        return tokenized_dataset
    
    def train_model(self, train_df: pd.DataFrame, test_df: pd.DataFrame) -> Dict:
        """Train the TinyBERT model."""
        try:
            logger.info("Starting model training...")
            
            # Load model and tokenizer
            self.load_model_and_tokenizer()
            
            # Preprocess data
            train_dataset = self.preprocess_data(train_df['cleaned_text'], train_df['label'])
            test_dataset = self.preprocess_data(test_df['cleaned_text'], test_df['label'])
            
            # Define training arguments
            training_args = TrainingArguments(
                output_dir=self.model_cache_dir,
                num_train_epochs=3,
                per_device_train_batch_size=16,
                per_device_eval_batch_size=16,
                warmup_steps=500,
                weight_decay=0.01,
                logging_dir=f"{self.model_cache_dir}/logs",
                logging_steps=100,
                evaluation_strategy="epoch",
                save_strategy="epoch",
                load_best_model_at_end=True,
                metric_for_best_model="f1",
                greater_is_better=True,
                seed=settings.random_seed
            )
            
            # Define metrics function
            def compute_metrics(eval_pred):
                predictions, labels = eval_pred
                predictions = np.argmax(predictions, axis=1)
                
                precision, recall, f1, _ = precision_recall_fscore_support(labels, predictions, average='binary')
                accuracy = accuracy_score(labels, predictions)
                
                return {
                    'accuracy': accuracy,
                    'f1': f1,
                    'precision': precision,
                    'recall': recall
                }
            
            # Create trainer
            trainer = Trainer(
                model=self.model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=test_dataset,
                compute_metrics=compute_metrics
            )
            
            # Train model
            trainer.train()
            
            # Evaluate model
            eval_results = trainer.evaluate()
            
            # Save model
            trainer.save_model(self.model_cache_dir)
            self.tokenizer.save_pretrained(self.model_cache_dir)
            
            logger.info(f"Training completed. Results: {eval_results}")
            
            return {
                'training_results': eval_results,
                'model_path': self.model_cache_dir,
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            raise
    
    def predict(self, text: str) -> Dict:
        """Make prediction on a single email text."""
        try:
            if not self.model or not self.tokenizer:
                self.load_model_and_tokenizer()
            
            # Tokenize input
            inputs = self.tokenizer(
                text,
                truncation=True,
                padding="max_length",
                max_length=self.max_length,
                return_tensors="pt"
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Make prediction
            with torch.no_grad():
                outputs = self.model(**inputs)
                probabilities = torch.softmax(outputs.logits, dim=-1)
                predicted_class = torch.argmax(probabilities, dim=-1).item()
                confidence = probabilities[0][predicted_class].item()
            
            # Convert to label
            label = "Phishing" if predicted_class == 1 else "Legitimate"
            
            return {
                'prediction': label,
                'confidence': confidence,
                'probabilities': {
                    'legitimate': probabilities[0][0].item(),
                    'phishing': probabilities[0][1].item()
                }
            }
            
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            return {
                'prediction': 'Error',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def evaluate_model(self, test_df: pd.DataFrame) -> Dict:
        """Evaluate model on test dataset."""
        try:
            if not self.model or not self.tokenizer:
                self.load_model_and_tokenizer()
            
            # Preprocess test data
            test_dataset = self.preprocess_data(test_df['cleaned_text'], test_df['label'])
            
            # Create trainer for evaluation
            trainer = Trainer(
                model=self.model,
                args=TrainingArguments(output_dir=self.model_cache_dir),
                compute_metrics=lambda eval_pred: {
                    'accuracy': accuracy_score(eval_pred[1], np.argmax(eval_pred[0], axis=1)),
                    'precision': precision_recall_fscore_support(eval_pred[1], np.argmax(eval_pred[0], axis=1), average='binary')[0],
                    'recall': precision_recall_fscore_support(eval_pred[1], np.argmax(eval_pred[0], axis=1), average='binary')[1],
                    'f1': precision_recall_fscore_support(eval_pred[1], np.argmax(eval_pred[0], axis=1), average='binary')[2]
                }
            )
            
            # Evaluate
            results = trainer.evaluate(test_dataset)
            
            # Get detailed classification report
            predictions = trainer.predict(test_dataset)
            y_pred = np.argmax(predictions.predictions, axis=1)
            y_true = predictions.label_ids
            
            classification_rep = classification_report(y_true, y_pred, target_names=['Legitimate', 'Phishing'])
            
            logger.info(f"Model evaluation completed: {results}")
            
            return {
                'metrics': results,
                'classification_report': classification_rep,
                'predictions': y_pred.tolist(),
                'true_labels': y_true.tolist()
            }
            
        except Exception as e:
            logger.error(f"Error evaluating model: {e}")
            raise
    
    def get_model_info(self) -> Dict:
        """Get model information."""
        return {
            'model_name': self.model_name,
            'max_length': self.max_length,
            'device': str(self.device),
            'model_loaded': self.model is not None,
            'tokenizer_loaded': self.tokenizer is not None,
            'cache_dir': self.model_cache_dir
        }
