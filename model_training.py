import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

def prepare_data():
    # Load the data
    df = pd.read_csv(r"D:\archive (5)\heart.csv")
    
    print("Dataset shape:", df.shape)
    print("\nAvailable columns:", df.columns.tolist())
    
    # Use thalach (heart rate) as main feature
    features = ['thalach']  # You can add more relevant features here
    X = df[features]
    y = df['target']
    
    # Print some basic statistics
    print("\nHeart Rate (thalach) statistics:")
    print(X['thalach'].describe())
    
    return train_test_split(X, y, test_size=0.2, random_state=42)

def train_model():
    try:
        X_train, X_test, y_train, y_test = prepare_data()
        
        # Scale the features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train Random Forest model
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42
        )
        model.fit(X_train_scaled, y_train)
        
        # Save model and scaler
        joblib.dump(model, 'epilepsy_model.pkl')
        joblib.dump(scaler, 'scaler.pkl')
        
        # Evaluate model
        y_pred = model.predict(X_test_scaled)
        print("\nModel Performance:")
        print(classification_report(y_test, y_pred))
        
        # Print feature importance
        for feature, importance in zip(['thalach'], model.feature_importances_):
            print(f"\nImportance of {feature}: {importance:.4f}")
        
    except Exception as e:
        print(f"Error during model training: {str(e)}")

if __name__ == "__main__":
    train_model() 