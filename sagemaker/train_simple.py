#!/usr/bin/env python3
"""
Simplified SageMaker Training Script for Mental Health Risk Prediction
Works with a single training file and splits internally
"""

import argparse
import os
import json
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score, confusion_matrix
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Main training function"""
    parser = argparse.ArgumentParser()
    
    # Hyperparameters
    parser.add_argument('--n_estimators', type=int, default=200)
    parser.add_argument('--max_depth', type=int, default=10)
    parser.add_argument('--min_samples_split', type=int, default=5)
    
    # SageMaker specific arguments
    parser.add_argument('--model_dir', type=str, default=os.environ.get('SM_MODEL_DIR', '/opt/ml/model'))
    parser.add_argument('--train', type=str, default=os.environ.get('SM_CHANNEL_TRAINING', '/opt/ml/input/data/training'))
    
    args = parser.parse_args()
    
    logger.info("="*60)
    logger.info("Mental Health Risk Prediction Model Training")
    logger.info("="*60)
    logger.info(f"Hyperparameters:")
    logger.info(f"  n_estimators: {args.n_estimators}")
    logger.info(f"  max_depth: {args.max_depth}")
    logger.info(f"  min_samples_split: {args.min_samples_split}")
    logger.info(f"Training data path: {args.train}")
    logger.info(f"Model output path: {args.model_dir}")
    logger.info("="*60)
    
    # Load data - find any CSV file in the training directory
    train_files = [f for f in os.listdir(args.train) if f.endswith('.csv')]
    if not train_files:
        raise ValueError(f"No CSV files found in {args.train}")
    
    train_file = os.path.join(args.train, train_files[0])
    logger.info(f"Loading data from: {train_file}")
    
    df = pd.read_csv(train_file)
    logger.info(f"Total samples: {len(df)}")
    logger.info(f"Columns: {list(df.columns)}")
    
    # Prepare features
    exclude_cols = ['label', 'sample_id', 'userId']
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    
    X = df[feature_cols].fillna(df[feature_cols].median())
    y = df['label']
    
    logger.info(f"Features: {len(feature_cols)}")
    logger.info(f"Class distribution: {y.value_counts().to_dict()}")
    
    # Split into train and validation
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    logger.info(f"Training samples: {len(X_train)}")
    logger.info(f"Validation samples: {len(X_val)}")
    
    # Train Random Forest
    logger.info("Training Random Forest model...")
    rf_model = RandomForestClassifier(
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
        min_samples_split=args.min_samples_split,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    )
    rf_model.fit(X_train, y_train)
    logger.info("Random Forest training complete")
    
    # Train Gradient Boosting
    logger.info("Training Gradient Boosting model...")
    gb_model = GradientBoostingClassifier(
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
        learning_rate=0.1,
        random_state=42
    )
    gb_model.fit(X_train, y_train)
    logger.info("Gradient Boosting training complete")
    
    # Evaluate on validation set
    rf_prob = rf_model.predict_proba(X_val)[:, 1]
    gb_prob = gb_model.predict_proba(X_val)[:, 1]
    ensemble_prob = (rf_prob + gb_prob) / 2
    ensemble_pred = (ensemble_prob >= 0.5).astype(int)
    
    # Calculate metrics
    auc = roc_auc_score(y_val, ensemble_prob)
    precision = precision_score(y_val, ensemble_pred)
    recall = recall_score(y_val, ensemble_pred)
    f1 = f1_score(y_val, ensemble_pred)
    
    cm = confusion_matrix(y_val, ensemble_pred)
    tn, fp, fn, tp = cm.ravel()
    
    metrics = {
        'ensemble': {
            'auc': float(auc),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'accuracy': float((tp + tn) / (tp + tn + fp + fn)),
            'true_positives': int(tp),
            'true_negatives': int(tn),
            'false_positives': int(fp),
            'false_negatives': int(fn)
        },
        'training_samples': len(X_train),
        'validation_samples': len(X_val),
        'num_features': len(feature_cols)
    }
    
    logger.info("Ensemble Metrics:")
    logger.info(f"  AUC: {auc:.4f}")
    logger.info(f"  Precision: {precision:.4f}")
    logger.info(f"  Recall: {recall:.4f}")
    logger.info(f"  F1 Score: {f1:.4f}")
    logger.info(f"  Accuracy: {metrics['ensemble']['accuracy']:.4f}")
    
    # Feature importance
    rf_importance = rf_model.feature_importances_
    gb_importance = gb_model.feature_importances_
    avg_importance = (rf_importance + gb_importance) / 2
    
    importance_df = pd.DataFrame({
        'feature': feature_cols,
        'importance': avg_importance
    }).sort_values('importance', ascending=False)
    
    logger.info("Top 10 most important features:")
    for idx, row in importance_df.head(10).iterrows():
        logger.info(f"  {row['feature']}: {row['importance']:.4f}")
    
    # Save models and artifacts
    logger.info(f"Saving models to {args.model_dir}")
    os.makedirs(args.model_dir, exist_ok=True)
    
    joblib.dump(rf_model, os.path.join(args.model_dir, 'rf_model.pkl'))
    joblib.dump(gb_model, os.path.join(args.model_dir, 'gb_model.pkl'))
    importance_df.to_csv(os.path.join(args.model_dir, 'feature_importance.csv'), index=False)
    
    with open(os.path.join(args.model_dir, 'metrics.json'), 'w') as f:
        json.dump(metrics, f, indent=2)
    
    logger.info("="*60)
    logger.info("Training Complete!")
    logger.info(f"Final Ensemble AUC: {auc:.4f}")
    logger.info(f"Final Ensemble Recall: {recall:.4f}")
    logger.info("="*60)


if __name__ == '__main__':
    main()
