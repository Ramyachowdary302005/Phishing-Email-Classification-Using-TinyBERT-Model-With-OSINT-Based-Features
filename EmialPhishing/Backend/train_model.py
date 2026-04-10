#!/usr/bin/env python3
"""
TinyBERT phishing detection training script.
Supports resuming from the latest checkpoint automatically.
"""

import sys
import os
import time
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def main():
    start_time = time.time()

    logger.info("=" * 60)
    logger.info("PhishGuard AI — TinyBERT Training (CPU Optimized)")
    logger.info("=" * 60)

    # ── Step 1: Load dataset ─────────────────────────────────────
    logger.info("[1/5] Loading dataset...")
    import pandas as pd
    from sklearn.model_selection import train_test_split

    df = pd.read_csv('./dataset/Phishing_Email.csv')
    df = df.rename(columns={'Email Text': 'text', 'Email Type': 'label'})
    df['label'] = df['label'].map({'Safe Email': 0, 'Phishing Email': 1})
    df = df.dropna(subset=['text', 'label'])
    df = df[df['text'].str.strip().str.len() > 10]
    df['label'] = df['label'].astype(int)

    logger.info(f"  Total samples: {len(df)}")
    logger.info(f"  Safe: {(df['label']==0).sum()}  |  Phishing: {(df['label']==1).sum()}")

    # ── Step 2: Balance & sample for CPU speed ───────────────────
    logger.info("[2/5] Preparing 60% balanced dataset (faster CPU training)...")

    # Use 60% of dataset split evenly per class
    DATASET_FRACTION = 0.60
    safe_df  = df[df['label'] == 0]
    phish_df = df[df['label'] == 1]
    n_per_class = min(len(safe_df), len(phish_df))   # balance classes
    n_per_class = int(n_per_class * DATASET_FRACTION) # use 60%
    safe_df  = safe_df.sample(n=n_per_class, random_state=42)
    phish_df = phish_df.sample(n=n_per_class, random_state=42)
    df_balanced = pd.concat([safe_df, phish_df]).sample(frac=1, random_state=42).reset_index(drop=True)

    logger.info(f"  Using 60% of data: {len(df_balanced)} emails ({n_per_class} per class)")

    # Clean text lightly (lowercase + strip + truncate)
    df_balanced['cleaned_text'] = df_balanced['text'].str.lower().str.strip().str[:400]

    train_df, test_df = train_test_split(
        df_balanced, test_size=0.2, stratify=df_balanced['label'], random_state=42
    )
    logger.info(f"  Train: {len(train_df)}  |  Test: {len(test_df)}")

    # ── Step 3: Load model & tokenizer ───────────────────────────
    logger.info("[3/5] Loading TinyBERT model & tokenizer from HuggingFace...")
    logger.info("  (First run may download ~50MB of model files)")
    import torch
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    from transformers import TrainingArguments, Trainer
    from datasets import Dataset
    import numpy as np
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support

    MODEL_NAME = "huawei-noah/TinyBERT_General_4L_312D"
    MAX_LENGTH = 128   # reduced from 512 — 4x faster on CPU
    OUTPUT_DIR = "./models"
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, cache_dir=OUTPUT_DIR)
    model     = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME, num_labels=2, cache_dir=OUTPUT_DIR
    )
    logger.info(f"  Model loaded on: {'GPU' if torch.cuda.is_available() else 'CPU'}")

    # ── Step 4: Tokenize ─────────────────────────────────────────
    logger.info("[4/5] Tokenizing emails...")

    def tokenize(batch):
        return tokenizer(
            batch['text'],
            truncation=True,
            padding='max_length',
            max_length=MAX_LENGTH,
        )

    train_ds = Dataset.from_dict({'text': train_df['cleaned_text'].tolist(), 'label': train_df['label'].tolist()})
    test_ds  = Dataset.from_dict({'text': test_df['cleaned_text'].tolist(),  'label': test_df['label'].tolist()})

    train_ds = train_ds.map(tokenize, batched=True)
    test_ds  = test_ds.map(tokenize, batched=True)

    train_ds.set_format('torch', columns=['input_ids', 'attention_mask', 'label'])
    test_ds.set_format('torch',  columns=['input_ids', 'attention_mask', 'label'])

    logger.info(f"  Tokenization complete.")

    # ── Step 5: Resume checkpoint detection ─────────────────────
    import glob
    resume_checkpoint = None
    checkpoints = glob.glob(os.path.join(OUTPUT_DIR, "checkpoint-*"))
    if checkpoints:
        # Pick the checkpoint with the highest step number
        resume_checkpoint = max(checkpoints, key=lambda x: int(x.split("-")[-1]))
        logger.info(f"  ✅ Resuming from checkpoint: {resume_checkpoint}")
    else:
        logger.info("  🆕 No checkpoint found — starting fresh training.")

    # ── Step 6: Train ────────────────────────────────────────────
    logger.info("[5/5] Training TinyBERT...")
    logger.info("  Configuration:")
    logger.info(f"    Epochs:     3")
    logger.info(f"    Batch size: 8")
    logger.info(f"    Max length: {MAX_LENGTH} tokens")
    logger.info(f"    Train size: {len(train_ds)}")
    logger.info(f"    Estimated time: ~30–60 min for final epoch on CPU")
    logger.info("")

    def compute_metrics(eval_pred):
        preds, labels = eval_pred
        preds = np.argmax(preds, axis=1)
        precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='binary')
        acc = accuracy_score(labels, preds)
        return {'accuracy': acc, 'f1': f1, 'precision': precision, 'recall': recall}

    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=3,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=16,
        warmup_steps=200,
        weight_decay=0.01,
        logging_steps=100,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        seed=42,
        use_cpu=not torch.cuda.is_available(),
        dataloader_num_workers=0,   # safe for Windows
        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=test_ds,
        compute_metrics=compute_metrics,
    )

    trainer.train(resume_from_checkpoint=resume_checkpoint)

    # ── Save model ───────────────────────────────────────────────
    logger.info("Saving fine-tuned model...")
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    # ── Evaluate ─────────────────────────────────────────────────
    results = trainer.evaluate()
    elapsed = time.time() - start_time
    elapsed_min = elapsed / 60

    logger.info("")
    logger.info("=" * 60)
    logger.info("TRAINING COMPLETE!")
    logger.info(f"  Time taken    : {elapsed_min:.1f} minutes")
    logger.info(f"  Accuracy      : {results.get('eval_accuracy', 0):.4f}")
    logger.info(f"  F1 Score      : {results.get('eval_f1', 0):.4f}")
    logger.info(f"  Precision     : {results.get('eval_precision', 0):.4f}")
    logger.info(f"  Recall        : {results.get('eval_recall', 0):.4f}")
    logger.info(f"  Model saved to: {OUTPUT_DIR}")
    logger.info("=" * 60)
    logger.info("")
    logger.info("The backend will now use this fine-tuned model for all predictions.")
    logger.info("Restart the backend server to load the new model.")


if __name__ == "__main__":
    main()
