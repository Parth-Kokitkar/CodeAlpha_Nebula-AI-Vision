import customtkinter as ctk
from PIL import Image
import cv2
import threading
import time
import psutil
from datetime import datetime
from ultralytics import YOLO
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class NebulaVision(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("NEBULA AI VISION PRO")
        self.state("zoomed")  # Full screen on Windows
        self.configure(fg_color="#0B0F14")
 
        self.grid_columnconfigure(0, weight=4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
 
        self.camera_frame = ctk.CTkFrame(
            self,
            corner_radius=25,
            fg_color="#161B22",
        )

        self.camera_frame.grid(
            row=0,
            column=0,
            padx=20,
            pady=20,
            sticky="nsew"
        )

        self.camera_label = ctk.CTkLabel(
            self.camera_frame,
            text="Starting Camera...",
            font=("Segoe UI", 28, "bold")
        )

        self.camera_label.pack(expand=True)

      
        self.dashboard = ctk.CTkFrame(
            self,
             corner_radius=25,
             fg_color="#1B1F27",
             width=380,
        )

        self.dashboard.grid(
            row=0,
            column=1,
            padx=(0, 20),
            pady=20,
            sticky="nsew"
        )

        self.build_dashboard()

        self.cap = cv2.VideoCapture(0)
        self.model = YOLO("yolov8n.pt")
        self.prev_time = time.time()
        self.running = True
        self.status_list = [
              "🟢 SCANNING",
              "🟡 ANALYZING",
              "🔵 TRACKING",
              "🟢 MONITORING"
             ]

        self.status_index = 0
        self.last_status_update = time.time()

        threading.Thread(
             target=self.update_camera,
             daemon=True
        ).start()

    def build_dashboard(self):

        title = ctk.CTkLabel(
            self.dashboard,
             text="NEBULA\nAI VISION",
             font=("Segoe UI", 34, "bold"),
             text_color="#00E5FF",
        )

        title.pack(pady=(40,20))

        self.status = ctk.CTkLabel(
            self.dashboard,
            text="🟢 LIVE",
            font=("Segoe UI",24,"bold"),
            text_color="#22C55E"
        )
        
        self.status.pack(pady=20)

        self.fps = ctk.CTkLabel(
            self.dashboard,
            text="FPS : 0",
            font=("Segoe UI", 18)
        )

        self.fps.pack(pady=10)

        self.objects = ctk.CTkLabel(
            self.dashboard,
            text="Objects : 0",
            font=("Segoe UI", 18)
        )

        self.objects.pack(pady=10)

        self.persons = ctk.CTkLabel(
            self.dashboard,
            text="Persons : 0",
            font=("Segoe UI", 18)
        )

        self.persons.pack(pady=10)

        self.phones = ctk.CTkLabel(
            self.dashboard,
            text="Phones : 0",
            font=("Segoe UI", 18)
        )

        self.phones.pack(pady=10)

        self.bottles = ctk.CTkLabel(
            self.dashboard,
            text="Bottles : 0",
            font=("Segoe UI", 18)
        )

        self.bottles.pack(pady=10)

        self.chairs = ctk.CTkLabel(
            self.dashboard,
            text="Chairs : 0",
            font=("Segoe UI", 18)
        )

        self.chairs.pack(pady=10)

        self.laptops = ctk.CTkLabel(
            self.dashboard,
            text="Laptops : 0",
            font=("Segoe UI", 18)
        )

        self.laptops.pack(pady=10)

        self.cpu = ctk.CTkLabel(
             self.dashboard,
             text="CPU : 0%",
             font=("Segoe UI", 18)
        )
        self.cpu.pack(pady=10)

        self.ram = ctk.CTkLabel(
               self.dashboard,
             text="RAM : 0%",
             font=("Segoe UI", 18)
        )
        self.ram.pack(pady=10)

        self.clock = ctk.CTkLabel(
             self.dashboard,
              text="00:00:00",
             font=("Segoe UI", 18, "bold"),
              text_color="#00E5FF"
        )
        self.clock.pack(pady=15)


        
        ctk.CTkButton(
              self.dashboard,
              text="📸 Screenshot",
             width=240,
             height=55,
              corner_radius=15,
             fg_color="#2563EB",
             hover_color="#1D4ED8",
             font=("Segoe UI", 17, "bold"),
             command=self.take_screenshot
        ).pack(pady=(35,10))

        ctk.CTkButton(
              self.dashboard,
              text="✕ Exit",
              width=240,
             height=55,
               corner_radius=15,
              fg_color="#DC2626",
             hover_color="#B91C1C",
             font=("Segoe UI",17,"bold"),
              command=self.close_app
        ).pack()

        

    def update_camera(self):

     while self.running:

        success, frame = self.cap.read()

        if not success:
            continue

       
        results = self.model.track(
            frame,
            persist=True,
            tracker="bytetrack.yaml",
            conf=0.35,
            verbose=False
        )

        result = results[0]

        persons = 0
        phones = 0
        bottles = 0
        chairs = 0
        laptops = 0
        cups = 0
        books = 0
        backpacks = 0
        vases = 0

        if result.boxes is not None:

            for box in result.boxes:

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                cls = int(box.cls[0])
                name = self.model.names[cls]

                confidence = float(box.conf[0])

                if box.id is not None:
                    track_id = int(box.id[0])
                else:
                    track_id = -1

                # Count Objects
                if name == "person":
                    persons += 1

                elif name == "cell phone":
                    phones += 1

                elif name == "bottle":
                     bottles += 1

                elif name == "chair":
                     chairs += 1
 
                elif name == "laptop":
                      laptops += 1

                elif name == "cup":
                      cups += 1

                elif name == "book":
                      books += 1

                elif name == "backpack":
                      backpacks += 1

                elif name == "vase":
                     vases += 1

                cv2.rectangle(
                    frame,
                 (x1, y1),
                   (x2, y2),
                 (0, 220, 255),    
                        2
                )

                label = f"{name.upper()} | ID {track_id} | {confidence*100:.0f}%"

                (text_width, text_height), _ = cv2.getTextSize(
                           label,
                           cv2.FONT_HERSHEY_COMPLEX,
                          0.55,
                            1
                )

 
                overlay = frame.copy()

                cv2.rectangle(
                   overlay,
                  (x1, y1 - text_height - 14),
                  (x1 + text_width + 10, y1),
                  (30, 30, 30),
                   -1
                )

                alpha = 0.65

                cv2.addWeighted(
                   overlay,
                   alpha,
                    frame,
                  1 - alpha,
                       0,
                    frame
                )

 
                cv2.rectangle(
                    frame,
                  (x1, y1),
                  (x2, y2),
                  (0, 220, 255),
                     2
                )

 
                cv2.putText(
                   frame,
                   label,
                 (x1 + 5, y1 - 8),
                 cv2.FONT_HERSHEY_COMPLEX,
                 0.55,
                 (255, 255, 255),
                    1
                )

 
         
        self.last_frame = frame.copy()

         
        current_time = time.time()
        fps = 1 / (current_time - self.prev_time)
        self.prev_time = current_time

        
        if current_time - self.last_status_update >= 1:

            self.status.configure(
                text=self.status_list[self.status_index]
            )

            self.status_index = (
                self.status_index + 1
            ) % len(self.status_list)

            self.last_status_update = current_time

      
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (1100, 760))

        image = Image.fromarray(frame)

        photo = ctk.CTkImage(
            light_image=image,
            dark_image=image,
            size=(1100, 760)
        )

        self.camera_label.configure(
            image=photo,
            text=""
        )

        self.camera_label.image = photo

       
        total = (
                persons +
                phones +
                bottles +
                chairs +
               laptops +
                cups +
               books +
              backpacks +
               vases
            )

        self.fps.configure(
            text=f"FPS : {int(fps)}"
        )

        self.objects.configure(
            text=f"Objects : {total}"
        )

        self.persons.configure(
            text=f"Persons : {persons}"
        )

        self.phones.configure(
            text=f"Phones : {phones}"
        )

        self.bottles.configure(
            text=f"Bottles : {bottles}"
        )

        self.chairs.configure(
            text=f"Chairs : {chairs}"
        )

        self.laptops.configure(
            text=f"Laptops : {laptops}"
        )

        self.cpu.configure(
            text=f"CPU : {psutil.cpu_percent()}%"
        )

        self.ram.configure(
            text=f"RAM : {psutil.virtual_memory().percent}%"
        )

        self.clock.configure(
            text=datetime.now().strftime("%H:%M:%S")
        )

    def take_screenshot(self):

        if hasattr(self, "last_frame"):

          filename = f"screenshots/{datetime.now().strftime('%H-%M-%S')}.png"

          cv2.imwrite(filename, self.last_frame)

          print("Screenshot Saved:", filename)

    def close_app(self):

        self.running = False

        if self.cap.isOpened():
            self.cap.release()

        self.destroy()