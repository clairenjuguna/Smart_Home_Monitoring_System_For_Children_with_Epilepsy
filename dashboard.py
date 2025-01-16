import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import calendar
from monitor import EpilepsyMonitor

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    print("Plotly not available. Using simplified charts.")
    PLOTLY_AVAILABLE = False

st.set_page_config(
    page_title="Smart Home Epilepsy Monitoring System",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Smart Home Monitoring System for Children with Epilepsy v1.0"
    }
)

class Dashboard:
    def __init__(self):
        self.monitor = EpilepsyMonitor()
        self.heart_rates = []
        self.timestamps = []
        self.warning_threshold = 150
        self.episodes = []
        # Motion and camera data
        self.motion_detected = False
        self.camera_active = True
        self.room_motion = {
            "Bedroom": False,
            "Living Room": False,
            "Bathroom": False
        }
        self.last_location = "Bedroom"
        
    def simulate_motion_data(self):
        # Simulate motion detection data
        for room in self.room_motion:
            self.room_motion[room] = np.random.choice([True, False], p=[0.3, 0.7])
        self.motion_detected = any(self.room_motion.values())
        if self.motion_detected:
            self.last_location = [room for room, motion in self.room_motion.items() if motion][0]

    def create_room_status(self):
        st.write("### Room Monitoring")
        cols = st.columns(len(self.room_motion))
        for i, (room, motion) in enumerate(self.room_motion.items()):
            with cols[i]:
                if motion:
                    st.error(f"📍 Motion in {room}")
                else:
                    st.success(f"✓ {room} Clear")
                if room == self.last_location:
                    st.info("👤 Last Seen Here")

    def create_camera_feed(self):
        st.write("### Camera Feed")
        camera_cols = st.columns(2)
        with camera_cols[0]:
            st.camera_input("Live Feed")
        with camera_cols[1]:
            st.write("Camera Controls")
            st.checkbox("Enable Night Vision", value=True)
            st.checkbox("Motion Detection", value=True)
            st.checkbox("Record on Motion", value=True)
            st.slider("Camera Sensitivity", 0, 100, 50)

    def update_data(self, heart_rate):
        self.heart_rates.append(heart_rate)
        current_time = pd.Timestamp.now()
        self.timestamps.append(current_time)
        
        # If it's an episode, store the timestamp
        if self.monitor.monitor_heartbeat(heart_rate):
            self.episodes.append(current_time)
        
        # Keep only last 100 readings
        if len(self.heart_rates) > 100:
            self.heart_rates.pop(0)
            self.timestamps.pop(0)
    
    def create_calendar(self):
        # Get current month and year
        now = datetime.now()
        year = now.year
        month = now.month
        
        # Create calendar HTML
        cal = calendar.monthcalendar(year, month)
        month_name = calendar.month_name[month]
        
        # Convert episodes to dates
        episode_dates = [ep.date() for ep in self.episodes]
        
        # Create calendar UI
        st.write(f"### Episodes Calendar - {month_name} {year}")
        
        # Create calendar grid
        cols = st.columns(7)
        for i, day in enumerate(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']):
            cols[i].write(f"**{day}**")
        
        for week in cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                if day == 0:
                    cols[i].write("")
                else:
                    date = datetime(year, month, day).date()
                    if date in episode_dates:
                        cols[i].markdown(f"<div style='background-color: #ff4b4b; padding: 5px; border-radius: 5px; text-align: center;'>{day}</div>", unsafe_allow_html=True)
                    else:
                        cols[i].markdown(f"<div style='background-color: #f0f2f6; padding: 5px; border-radius: 5px; text-align: center;'>{day}</div>", unsafe_allow_html=True)
    
    def create_chart(self, chart):
        if PLOTLY_AVAILABLE:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=self.timestamps,
                y=self.heart_rates,
                mode='lines',
                name='Heart Rate'
            ))
            fig.add_hline(y=self.warning_threshold, line_color="red", line_dash="dash")
            fig.update_layout(
                xaxis_title="Time",
                yaxis_title="Heart Rate (BPM)",
                height=400
            )
            chart.plotly_chart(fig, use_container_width=True)
        else:
            # Fallback to streamlit's native line chart
            chart.line_chart(pd.DataFrame({
                'Heart Rate': self.heart_rates
            }))

    def run(self):
        # Title and description
        st.title("Smart Home Monitoring System for Children with Epilepsy")
        st.markdown("""
        This system provides comprehensive monitoring through vital signs tracking, 
        motion detection, and smart camera integration for enhanced safety.
        """)
        
        # Enhanced sidebar
        st.sidebar.title("System Information")
        st.sidebar.info("""
        💗 Normal Heart Rate Range: 40-200 BPM
        ⚠️ Warning Threshold: 150 BPM
        🎯 Model Accuracy: 67%
        📱 Notifications: Enabled
        🏠 Smart Home Integration: Active
        🎥 Cameras: Online
        """)
        
        # Updated tab structure
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "Real-time Monitoring",
            "Room Monitoring",
            "Camera Feed",
            "Environmental Controls",
            "Calendar",
            "Settings"
        ])
        
        with tab1:
            # Real-time heart rate monitoring (remains the same)
            col1, col2, col3 = st.columns([2,2,1])
            with col1:
                st.subheader("Current Status")
                current_hr = st.empty()
                status = st.empty()
            with col2:
                st.subheader("Heart Rate History")
                chart = st.empty()
            with col3:
                st.subheader("Quick Stats")
                stats = st.empty()
        
        with tab2:
            # Room Monitoring
            st.subheader("Room Status Overview")
            self.create_room_status()
            
            # Additional room sensors
            st.write("### Room Sensors")
            sensor_cols = st.columns(3)
            with sensor_cols[0]:
                st.metric("Door Status", "Closed", "Locked")
            with sensor_cols[1]:
                st.metric("Window Status", "Closed", "Secured")
            with sensor_cols[2]:
                st.metric("Movement Level", "Low", "-2%")
        
        with tab3:
            # Camera Feed
            st.subheader("Smart Camera System")
            self.create_camera_feed()
            
            # Additional camera features
            st.write("### Advanced Camera Features")
            feature_cols = st.columns(3)
            with feature_cols[0]:
                st.checkbox("Face Detection", value=True)
                st.checkbox("Fall Detection", value=True)
            with feature_cols[1]:
                st.checkbox("Sound Detection", value=True)
                st.checkbox("Night Vision", value=True)
            with feature_cols[2]:
                st.slider("Detection Sensitivity", 0, 100, 75)
                st.select_slider("Video Quality", 
                    options=["Low", "Medium", "High", "Ultra HD"])
        
        with tab4:
            # Environmental Controls
            st.subheader("Environmental Monitoring & Control")
            
            # Temperature Control
            st.write("### Temperature Management")
            temp_cols = st.columns(2)
            with temp_cols[0]:
                st.metric("Current Temperature", "22°C", "0.5°C")
                st.slider("Set Temperature (°C)", 18, 30, 22)
            with temp_cols[1]:
                st.metric("Humidity", "45%", "-2%")
                st.slider("Target Humidity (%)", 30, 60, 45)
            
            # Lighting Control
            st.write("### Lighting Control")
            light_cols = st.columns(3)
            with light_cols[0]:
                st.write("Main Light")
                st.select_slider("Brightness", 
                    options=["Off", "Low", "Medium", "High"])
            with light_cols[1]:
                st.write("Night Light")
                st.select_slider("Night Light", 
                    options=["Off", "Dim", "Medium"])
            with light_cols[2]:
                st.write("Auto Adjustment")
                st.checkbox("Auto-adjust based on time", value=True)
                st.checkbox("Motion-activated", value=True)
            
            # Air Quality
            st.write("### Air Quality Monitoring")
            air_cols = st.columns(4)
            with air_cols[0]:
                st.metric("CO2 Level", "400 ppm", "-5 ppm")
            with air_cols[1]:
                st.metric("Air Quality", "Good", "+1%")
            with air_cols[2]:
                st.metric("VOC Level", "Low", "stable")
            with air_cols[3]:
                st.checkbox("Auto Air Purifier", value=True)
        
        with tab5:
            # Calendar (remains the same)
            self.create_calendar()
            if self.episodes:
                st.write("### Episode History")
                for ep in self.episodes[-5:]:
                    st.write(f"⚠️ Episode detected at: {ep.strftime('%Y-%m-%d %H:%M:%S')}")
                    st.write(f"📍 Location: {self.last_location}")
            else:
                st.info("✅ No episodes detected yet")
        
        with tab6:
            # Settings (remains the same)
            # Enhanced settings
            st.subheader("System Settings")
            
            # Alert settings
            st.write("### Alert Settings")
            cols = st.columns(2)
            with cols[0]:
                st.slider("Heart Rate Warning Threshold (BPM)", 100, 200, 150)
                st.checkbox("Enable SMS Notifications", value=True)
                st.checkbox("Enable Email Alerts", value=True)
            with cols[1]:
                st.checkbox("Enable Camera Alerts", value=True)
                st.checkbox("Enable Motion Alerts", value=True)
                st.checkbox("Enable Smart Light Alerts", value=True)
            
            # Emergency contacts
            st.write("### Emergency Contacts")
            cols = st.columns(2)
            with cols[0]:
                st.text_input("Primary Caregiver Name")
                st.text_input("Primary Caregiver Phone")
                st.text_input("Healthcare Provider Email")
            with cols[1]:
                st.text_input("Secondary Contact Name")
                st.text_input("Secondary Contact Phone")
                st.text_input("Hospital Emergency Number")
            
            # Camera settings
            st.write("### Camera Settings")
            cols = st.columns(3)
            with cols[0]:
                st.multiselect(
                    "Active Cameras",
                    ["Bedroom", "Living Room", "Bathroom"],
                    ["Bedroom", "Living Room"]
                )
            with cols[1]:
                st.select_slider(
                    "Recording Quality",
                    options=["Low", "Medium", "High", "Ultra"]
                )
            with cols[2]:
                st.number_input("Recording Duration (minutes)", 1, 60, 30)
        
        # Simulate real-time monitoring
        while True:
            heart_rate = np.random.normal(146, 27)
            self.update_data(heart_rate)
            self.simulate_motion_data()
            
            with tab1:
                current_hr.metric(
                    "Heart Rate", 
                    f"{heart_rate:.0f} BPM",
                    delta=f"{heart_rate - 146:.0f} from mean"
                )
                
                if self.monitor.monitor_heartbeat(heart_rate):
                    status.error(f"⚠️ Warning: Possible Episode Detected!\n📍 Location: {self.last_location}")
                else:
                    status.success("✅ Normal - Child is Safe")
                
                self.create_chart(chart)
                
                if self.heart_rates:
                    stats.write(f"""
                    💗 Current: {heart_rate:.0f} BPM
                    📊 Mean: {np.mean(self.heart_rates):.0f} BPM
                    📈 Max: {np.max(self.heart_rates):.0f} BPM
                    📉 Min: {np.min(self.heart_rates):.0f} BPM
                    ⚠️ Episodes Today: {len([ep for ep in self.episodes if ep.date() == datetime.now().date()])}
                    📍 Current Location: {self.last_location}
                    """)
            
            time.sleep(1)

if __name__ == "__main__":
    dashboard = Dashboard()
    dashboard.run() 