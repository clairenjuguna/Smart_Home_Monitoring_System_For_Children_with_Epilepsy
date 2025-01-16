import pandas as pd
import joblib
import time
from plyer import notification
try:
    import serial  # For Arduino connection
except ImportError:
    print("Serial module not found. Running in simulation mode.")
    serial = None

class EpilepsyMonitor:
    def __init__(self):
        self.model = joblib.load('epilepsy_model.pkl')
        self.scaler = joblib.load('scaler.pkl')
        self.threshold = 150  # Adjusted for thalach values
        self.serial_connection = None
        
        # Try to establish serial connection if available
        if serial:
            try:
                self.serial_connection = serial.Serial('COM3', 9600)  # Adjust COM port as needed
                print("Connected to Arduino")
            except:
                print("Arduino not connected. Running in simulation mode.")
        
    def send_notification(self, heart_rate):
        notification.notify(
            title='Epilepsy Warning',
            message=f'Abnormal heart rate detected: {heart_rate} BPM\nPossible episode incoming!',
            app_icon=None,
            timeout=10,
        )
    
    def monitor_heartbeat(self, heart_rate):
        # Scale the heart rate
        scaled_rate = self.scaler.transform([[heart_rate]])
        
        # Predict probability of episode
        prob = self.model.predict_proba(scaled_rate)[0][1]
        
        # Adjusted threshold based on thalach values
        if prob > 0.6 or heart_rate > self.threshold:  # More sensitive threshold
            self.send_notification(heart_rate)
            return True
        return False 