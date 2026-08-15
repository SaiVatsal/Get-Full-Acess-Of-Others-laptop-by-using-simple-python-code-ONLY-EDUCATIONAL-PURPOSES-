
```python
import customtkinter as ctk
import psutil
import subprocess
import threading
import time
import os
import json
import urllib.request
import geopy.geocoders
import cv2
import pyaudio
from plyer import notification
from datetime import datetime

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class LaptopTracker(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Laptop Tracker & Controller")
        self.geometry("520x680")
        self.resizable(False, False)

        # UI Components
        ctk.CTkLabel(self, text="🔌 WiFi Monitor", font=("Arial", 14, "bold")).pack(pady=10)
        self.wifi_label = ctk.CTkLabel(self, text="Checking...", fg_color="#2b2b2b", width=480, anchor="w")
        self.wifi_label.pack(padx=20, pady=5, fill="x")

        ctk.CTkButton(self, text="📍 Get Location", command=self.get_location).pack(pady=5)
        self.location_label = ctk.CTkLabel(self, text="Location: Not fetched", fg_color="#1f1f1f", width=480, anchor="w")
        self.location_label.pack(padx=20, pady=5, fill="x")

        ctk.CTkButton(self, text="📷 Take Photo", command=self.take_photo).pack(pady=5)
        ctk.CTkButton(self, text="🎤 Record Audio (3s)", command=self.record_audio).pack(pady=5)

        self.reset_frame = ctk.CTkFrame(self, fg_color="#2b2b2b")
        self.reset_frame.pack(padx=20, pady=15, fill="x")
        self.confirm_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(self.reset_frame, text="I confirm factory reset", variable=self.confirm_var).pack()
        self.reset_btn = ctk.CTkButton(self.reset_frame, text="🔄 Factory Reset",
                                       command=self.factory_reset, state="disabled")
        self.reset_btn.pack(pady=5)

        self.log_box = ctk.CTkTextbox(self, height=200, font=("Consolas", 11))
        self.log_box.pack(padx=20, pady=(10, 5), fill="both", expand=True)
        self.log("✅ App started. Monitoring WiFi...")

        # Background monitor
        self.wifi_thread = threading.Thread(target=self.monitor_wifi, daemon=True)
        self.wifi_thread.start()

    def log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_box.insert("end", f"[{ts}] {msg}\n")
        self.log_box.see("end")

    def monitor_wifi(self):
        prev_state = None
        while True:
            try:
                # Check default gateway ping + internet reachability
                out = subprocess.run(["ping", "-n", "1", "1.1.1.1"], capture_output=True, text=True)
                connected = out.returncode == 0

                if connected != prev_state:
                    state = "🟢 Connected" if connected else "🔴 Disconnected"
                    self.wifi_label.configure(text=state)
                    notification.notify(
                        title="WiFi Status", message=f"Laptop {state.replace('🟢 ', '').replace('🔴 ', '')}",
                        timeout=5, app_name="LaptopTracker"
                    )
                    self.log(f"WiFi: {state}")
                prev_state = connected
            except Exception as e:
                self.log(f"[!] WiFi check error: {e}")
            time.sleep(10)

    def get_location(self):
        try:
            with urllib.request.urlopen("https://ipinfo.io/json") as resp:
                data = json.loads(resp.read())

            lat, lon = map(float, data["loc"].split(","))
            geolocator = geopy.geocoders.Nominatim(user_agent="laptop_tracker")
            loc = geolocator.reverse(f"{lat},{lon}", exactly_one=True)
            city = loc.address.split(",")[0] if loc else "Unknown"

            self.location_label.configure(text=f"📍 {city} ({lat:.4f}, {lon:.4f})")
            self.log(f"Location: {city}")
        except Exception as e:
            self.log(f"[!] Location error: {e}")

    def take_photo(self):
        try:
            cam = cv2.VideoCapture(0)
            if not cam.isOpened():
                self.log("📷 Camera not found")
                return
            ret, frame = cam.read()
            cam.release()
            if ret:
                path = f"photo_{datetime.now().strftime('%H%M%S')}.jpg"
                cv2.imwrite(path, frame)
                self.log(f"📷 Photo saved: {path}")
        except Exception as e:
            self.log(f"[!] Camera error: {e}")

    def record_audio(self):
        try:
            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
            self.log("🎤 Recording...")
            frames = []
            for _ in range(int(44100 / 1024 * 3)):
                data = stream.read(1024)
                frames.append(data)
            stream.stop_stream()
            stream.close()

            path = f"audio_{datetime.now().strftime('%H%M%S')}.wav"
            wf = open(path, "wb")
            wf.setnchannels(1); wf.setsampwidth(p.get_sample_size(pyaudio.paInt16)); wf.setframerate(44100)
            wf.writeframes(b"".join(frames))
            wf.close()
            self.log(f"🎤 Audio saved: {path}")
        except Exception as e:
            self.log(f"[!] Mic error: {e}")

    def factory_reset(self):
        try:
            os.startfile("shutdown", None)  # fallback, but we use subprocess below
            cmd = ['systemreset', '-factoryreset'] if os.name == 'nt' and os.path.exists('C:/Windows/System32/systemreset.exe') else ['shutdown',
'/r', '/t', '0']
            subprocess.Popen(cmd)
            self.log("🔄 Factory reset initiated!")
        except Exception as e:
            self.log(f"[!] Reset error: {e}")

# UI Toggle logic for confirmation checkbox
tracker = LaptopTracker()
def update_reset_state(*_):
    tracker.reset_btn.configure(state="normal" if tracker.confirm_var.get() else "disabled")
tracker.confirm_var.trace_add("write", lambda *_: update_reset_state())

tracker.mainloop()