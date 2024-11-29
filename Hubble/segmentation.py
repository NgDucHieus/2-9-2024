import cv2
import numpy as np
from tkinter import Tk, Label, Button, Entry, filedialog, messagebox, Canvas
from PIL import Image, ImageTk
import threading


def detect_needle_by_segmentation(image, center_x, center_y, radius):
    """Phân đoạn hình ảnh và phát hiện kim bằng cách phân đoạn cạnh."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)  # Làm mờ để giảm nhiễu
    edges = cv2.Canny(blurred, 50, 150, apertureSize=3)

    # Chỉ quan tâm đến vùng quanh tâm với bán kính xác định
    mask = np.zeros_like(edges)
    cv2.circle(mask, (center_x, center_y), radius, 255, -1)
    segmented_edges = cv2.bitwise_and(edges, mask)

    # Phát hiện các đường thẳng bằng Hough Lines
    lines = cv2.HoughLinesP(segmented_edges, rho=1, theta=np.pi / 180, threshold=100, minLineLength=50, maxLineGap=10)
    
    return segmented_edges, lines


def calculate_angle(center_x, center_y, x1, y1, x2, y2):
    """Tính góc của kim đồng hồ dựa trên hai điểm của đường thẳng."""
    dist1_sq = (x1 - center_x)**2 + (y1 - center_y)**2
    dist2_sq = (x2 - center_x)**2 + (y2 - center_y)**2
    if dist1_sq > dist2_sq:
        x_tip, y_tip = x1, y1
    else:
        x_tip, y_tip = x2, y2
    dx = x_tip - center_x
    dy = center_y - y_tip
    angle = np.degrees(np.arctan2(dy, dx))
    return angle + 360 if angle < 0 else angle


def map_angle_to_value(angle, min_angle, max_angle, min_value, max_value):
    """Chuyển góc thành giá trị tương ứng trong phạm vi của đồng hồ đo."""
    if angle < min_angle:
        value = min_value + (max_value - min_value) * (min_angle - angle) / 270
    elif angle > max_angle:
        value = min_value + (max_value - min_value) * (angle - max_angle) / 270
    else:
        value = None
    return value


class VideoProcessorGUI:
    def __init__(self, master):
        self.master = master
        master.title("Gauge Video Processor")

        # Labels and Entries
        Label(master, text="Center X:").grid(row=0, column=0, sticky="w")
        self.center_x_entry = Entry(master)
        self.center_x_entry.insert(0, "279")
        self.center_x_entry.grid(row=0, column=1, sticky="w")

        Label(master, text="Center Y:").grid(row=1, column=0, sticky="w")
        self.center_y_entry = Entry(master)
        self.center_y_entry.insert(0, "331")
        self.center_y_entry.grid(row=1, column=1, sticky="w")

        Label(master, text="Radius:").grid(row=2, column=0, sticky="w")
        self.radius_entry = Entry(master)
        self.radius_entry.insert(0, "210")
        self.radius_entry.grid(row=2, column=1, sticky="w")

        Label(master, text="Min Angle:").grid(row=3, column=0, sticky="w")
        self.min_angle_entry = Entry(master)
        self.min_angle_entry.insert(0, "225")
        self.min_angle_entry.grid(row=3, column=1, sticky="w")

        Label(master, text="Max Angle:").grid(row=4, column=0, sticky="w")
        self.max_angle_entry = Entry(master)
        self.max_angle_entry.insert(0, "315")
        self.max_angle_entry.grid(row=4, column=1, sticky="w")

        Label(master, text="Min Value:").grid(row=5, column=0, sticky="w")
        self.min_value_entry = Entry(master)
        self.min_value_entry.insert(0, "0")
        self.min_value_entry.grid(row=5, column=1, sticky="w")

        Label(master, text="Max Value:").grid(row=6, column=0, sticky="w")
        self.max_value_entry = Entry(master)
        self.max_value_entry.insert(0, "4")
        self.max_value_entry.grid(row=6, column=1, sticky="w")

        # Buttons
        self.open_button = Button(master, text="Open Video", command=self.open_file)
        self.open_button.grid(row=7, column=0, sticky="w")

        self.process_button = Button(master, text="Process Video", command=self.process_video)
        self.process_button.grid(row=7, column=1, sticky="w")

        self.stop_button = Button(master, text="Stop Video", command=self.stop_video_processing)
        self.stop_button.grid(row=8, column=0, columnspan=2, sticky="w")

        # Canvas for Video Display
        self.canvas = Canvas(master, width=640, height=480, bg="black")
        self.canvas.grid(row=0, column=2, rowspan=8, padx=10, pady=10)

        self.video_path = None
        self.stop_video_flag = False

    def open_file(self):
        self.video_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi")])
        if self.video_path:
            messagebox.showinfo("File Selected", f"Selected File: {self.video_path}")

    def process_video(self):
        if not self.video_path:
            messagebox.showerror("Error", "Please select a video file first!")
            return

        try:
            center_x = int(self.center_x_entry.get())
            center_y = int(self.center_y_entry.get())
            radius = int(self.radius_entry.get())
            min_angle = int(self.min_angle_entry.get())
            max_angle = int(self.max_angle_entry.get())
            min_value = float(self.min_value_entry.get())
            max_value = float(self.max_value_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for the parameters!")
            return

        self.stop_video_flag = False

        # Start video processing in a separate thread
        threading.Thread(
            target=self.process_video_thread,
            args=(center_x, center_y, radius, min_angle, max_angle, min_value, max_value),
        ).start()

    def process_video_thread(self, center_x, center_y, radius, min_angle, max_angle, min_value, max_value):
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            messagebox.showerror("Error", "Cannot open video file.")
            return

        while cap.isOpened() and not self.stop_video_flag:
            ret, frame = cap.read()
            if not ret:
                break

            # Phát hiện kim bằng phân đoạn
            segmented_edges, lines = detect_needle_by_segmentation(frame, center_x, center_y, radius)
            output_frame = frame.copy()

            # Tính toán góc của kim đồng hồ
            needle_angle = None
            if lines:
                for x1, y1, x2, y2 in lines:
                    cv2.line(output_frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                    needle_angle = calculate_angle(center_x, center_y, x1, y1, x2, y2)
                    break

            gauge_value = None
            if needle_angle is not None:
                gauge_value = map_angle_to_value(needle_angle, min_angle, max_angle, min_value, max_value)

            # Vẽ hình tròn và tâm
            cv2.circle(output_frame, (center_x, center_y), radius, (0, 255, 0), 2)
            cv2.circle(output_frame, (center_x, center_y), 3, (0, 0, 255), -1)

            # Hiển thị giá trị đồng hồ đo
            if gauge_value is not None:
                cv2.putText(output_frame, f"Value: {gauge_value:.2f} bar", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Chuyển đổi ảnh OpenCV sang Tkinter để hiển thị
            frame_rgb = cv2.cvtColor(output_frame, cv2.COLOR_BGR2RGB)
            img = ImageTk.PhotoImage(image=Image.fromarray(frame_rgb))
            self.canvas.create_image(0, 0, anchor="nw", image=img)
            self.canvas.image = img

        cap.release()

    def stop_video_processing(self):
        """Dừng video processing bằng cách thay đổi cờ stop."""
        self.stop_video_flag = True
        messagebox.showinfo("Stopped", "Video processing has been stopped.")


# Create the Tkinter GUI
root = Tk()
video_processor_gui = VideoProcessorGUI(root)
root.mainloop()
