import glob
import queue
import threading
import tkinter as tk
from tkinter import PhotoImage, ttk
import vlc
from tkinter import filedialog
from datetime import timedelta
import os
from YoutubeDownloader import YoutubeDownloader

current_script_path = os.path.dirname(os.path.realpath(__file__))
def do_nothing():
    pass
class YoutubePlayer(tk.Toplevel):
    def __init__(self, parent, q, w, e, Count):
        super().__init__(parent)
        self.title("Youtube Player")
        self.geometry("800x700+700+200")
        self.configure(bg="#f0f0f0")
        #icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.png')
        #icon_image = PhotoImage(file=icon_path)
        #parent.iconphoto(False, icon_image)
        self.is_update = False
        self.q = q
        self.w = w
        self.e = e
        self.temp = 0
        self.downloader = None
        self.initialize_player()
        self.check_mouse_position()
        self.update_video_progress()
        self.Count = Count
        self.parent = parent
        #self.play_video()

    def initialize_player(self):
        self.instance = vlc.Instance("--avcodec-hw=none")
        self.media_player = self.instance.media_player_new()
        self.video_url = None
        self.playing_video = False
        self.video_paused = False
        self.bottom_frame = tk.Frame(self, bg="#f0f0f0")
        self.media_canvas = None
        self.progress_bar = None
        self.video_url_entry = None
        self.create_widgets()
        self.ydl_opts = None
    def on_focus_in(self, event):
        self.video_url_entry.configure(state='normal')

    def on_focus_out(self, event):
        self.video_url_entry.configure(state='disabled')    
    def create_widgets(self):
        self.media_canvas = tk.Canvas(self, bg="black", width=800, height=400)
        self.media_canvas.pack(pady=10, fill=tk.BOTH, expand=True)

        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.video_url_label = ttk.Label(self.bottom_frame, text=" [F11/ESC=OFF]:FULL SCREEN ON")
        self.video_url_label.pack(pady=10)

        self.video_url_entry = ttk.Entry(self.bottom_frame, width=50)
        self.video_url_entry.insert(0, "                             INSERT YOUTUBE URL")
        self.video_url_entry.pack(pady=10)
        self.video_url_entry.bind("<FocusIn>", self.on_focus_in)
        self.video_url_entry.bind("<FocusOut>", self.on_focus_out)
        self.time_label = tk.Label(
            self.bottom_frame,
            text="00:00:00 / 00:00:00",
            font=("Arial", 12, "bold"),
            fg="#555555",
            bg="#f0f0f0",
        )
        self.time_label.pack(pady=5)
        self.control_buttons_frame1 = tk.Frame(self.bottom_frame, bg="#f0f0f0")
        self.control_buttons_frame1.pack(pady=5)

        self.video_url = self.video_url_entry.get()

        global DownloadFile
        global TerminateFile
        global FastForwardFile
        global rewindFile
        image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloadFile.png')
        DownloadFile = PhotoImage(file=image_path)
        self.download_button = tk.Button(
        self.control_buttons_frame1,
        image=DownloadFile,
        borderwidth=0, 
        highlightthickness=0,
        command= lambda : self.download_video(self.video_url_entry.get()),)
        self.download_button.pack(side=tk.LEFT, padx=5, pady=5)

        image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'TerminateFile.png')
        TerminateFile = PhotoImage(file=image_path)
        self.stop_button = tk.Button(
        self.control_buttons_frame1,
        image=TerminateFile,
        borderwidth=0, 
        highlightthickness=0,
        command=self.stop,)
        self.stop_button.pack(side=tk.LEFT, pady=5)

        volume_var = tk.DoubleVar()
        volume_var.set(50)
        self.Volume_Slider = tk.Scale(self.control_buttons_frame1, 
                              from_=0, to=100, 
                              orient="horizontal",
                              variable=volume_var,
                              font=("Arial", 7, "bold"),
                              bg="#FF7F00",
                              fg="black") 
        self.Volume_Slider.pack(padx=5, pady=5)
        self.Volume_Slider.config(command=self.set_volume)

        self.control_buttons_frame2 = tk.Frame(self.bottom_frame, bg="#f0f0f0")
        self.control_buttons_frame2.pack(pady=5)

        
        image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'FastForwardFile.png')
        FastForwardFile = PhotoImage(file=image_path)
        self.fast_forward_button = tk.Button(
        self.control_buttons_frame2,
        image=FastForwardFile,
        borderwidth=0, 
        highlightthickness=0,
        command=self.fast_forward,)
        self.fast_forward_button.pack(side=tk.LEFT, padx=5, pady=5)    

        global pauseFile
        global resumeFile
        image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pauseFile.png')
        pauseFile = PhotoImage(file=image_path)
        image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resumeFile.png')
        resumeFile = PhotoImage(file=image_path)
        self.pause_button = tk.Button(
            self.control_buttons_frame2,
            image=pauseFile,
            borderwidth=0, 
            highlightthickness=0,
            command=self.pause_video,)
        self.pause_button.pack(side=tk.LEFT, padx=5, pady=5) 

        image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rewindFile.png')
        rewindFile = PhotoImage(file=image_path)

        self.rewind_button = tk.Button(
        self.control_buttons_frame2,
        image=rewindFile,
        borderwidth=0, 
        highlightthickness=0,
        command=self.rewind,)
        self.rewind_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.progress_bar = VideoProgressBar(
            self.bottom_frame, self.set_video_position, self.is_update, bg="#e0e0e0", highlightthickness=0
        )
        self.progress_bar.pack(fill=tk.X, padx=10, pady=5)
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Escape>", self.exit_fullscreen)
        self.bind("<Right>", self.fast_forward)
        self.bind("<Left>", self.rewind)
        self.bind("<space>", self.pause_video)
    def set_volume(self, val):
        volume = int(val)
        self.media_player.audio_set_volume(volume)
    def check_mouse_position(self):
        if self.attributes("-fullscreen"):
            x, y = self.winfo_pointerxy()
            widget = self.winfo_containing(x, y)
            if widget == self.bottom_frame or self.bottom_frame.winfo_containing(x, y):
                self.show_bottom_frame()
            else:
                self.hide_bottom_frame()
        else:
            self.show_bottom_frame()
        self.after(100, self.check_mouse_position)  # Check every 100 ms

    def show_bottom_frame(self):
        self.bottom_frame.pack(pady=5, side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def hide_bottom_frame(self):
        self.bottom_frame.pack_forget()

    def toggle_fullscreen(self, event=None):
        self.attributes("-fullscreen", not self.attributes("-fullscreen"))
        self.media_canvas.config(width=1920, height=1080)
        if self.attributes("-fullscreen"):
            self.media_canvas.config(width=1920, height=1080)
        else:
            self.attributes("-fullscreen", False)
            canvas_width = 800
            canvas_height = 400
            self.media_canvas.config(width=canvas_width, height=canvas_height)
            self.control_buttons_frame.pack(pady=5) 

    def exit_fullscreen(self, event=None):
        self.attributes("-fullscreen", False)
        canvas_width = 800
        canvas_height = 400
        self.media_canvas.config(width=canvas_width, height=canvas_height)
        self.media_player.set_hwnd(self.media_canvas.winfo_id()) 
        #self.media_canvas.pack(pady=10, fill=tk.BOTH, expand=True)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.control_buttons_frame.pack(pady=5)
        # 전체 화면에서 나오면 다시 초기 크기로 Canvas 생성
        #self.media_canvas.pack_forget()
        #self.media_canvas = tk.Canvas(self, bg="black", width=800, height=400)
        #self.media_canvas.pack(pady=10, fill=tk.BOTH, expand=True)

    def get_duration_str(self):
        length = self.media_player.get_length()  # 밀리세컨드 단위로 미디어의 길이를 가져옴
        if length != -1:  # 미디어의 길이가 제대로 가져와졌는지 확인
            length = length // 1000  # 밀리세컨드 단위를 초 단위로 변
            hours = length // 3600
            minutes = (length % 3600) // 60
            seconds = length % 60
            return f"{hours:02}:{minutes:02}:{seconds:02}"
        else:
            return "00:00:00"  

    def remove_file(self, remove_file=False):
        if remove_file == False:
            try:
                os.remove("output0.mp4")
                os.remove("output0.m4a")
            except FileNotFoundError:
                self.w.put("FailedLoad")
        else:
            for file in glob.glob("output*.mp4"):
                os.remove(file)          
        self.after(100, self.check_mouse_position)

    def play_video(self, video="output1.mp4"):
        file_path = video
        print(file_path)
        print(self.playing_video)

        if self.playing_video == False:
            self.Count.set_VideoCount(video)
            if not os.path.exists(file_path):
                file_path = "output1.mp4"
                self.Count.set_VideoCount(file_path)
            print(file_path)
            media = self.instance.media_new_path(file_path)
            self.media_player.set_media(media)
            self.media_player.set_hwnd(self.media_canvas.winfo_id())
            self.media_player.play()
            self.playing_video = True
    def Create_YoutubeDownloader_thread(self, q, youtube_url, Count):
            self.downloader = YoutubeDownloader(q, self.w, Count)
            self.downloader.download_and_merge(youtube_url)
            self.remove_file(False)
            self.play_video("output" + str(self.Count.get_count()) + ".mp4")

    def download_video(self, youtube_url):
        thread = threading.Thread(target=self.Create_YoutubeDownloader_thread, args=(self.q, youtube_url, self.Count), daemon = True)
        thread.start()
            

    def fast_forward(self, event=None):
        if self.playing_video:
            current_time = self.media_player.get_time() + 10000
            self.media_player.set_time(current_time)

    def rewind(self, event=None):
        if self.playing_video:
            current_time = self.media_player.get_time() - 10000
            if current_time < 0:
                current_time = 0
            self.media_player.set_time(current_time)


    def pause_video(self, event=None):
        if self.playing_video:
            if self.video_paused:
                self.media_player.play()
                self.video_paused = False
                self.pause_button.config(image=pauseFile)
            else:
                self.media_player.pause()
                self.video_paused = True
                self.pause_button.config(image=resumeFile)

    def stop(self):
        if self.playing_video:
            self.media_player.stop()
            self.playing_video = False
            self.play_video("output" + str(self.Count.get_VideoCount() + 1) + ".mp4")
        self.time_label.config(text="00:00:00 / " + self.get_duration_str())

    def set_video_position(self, value):
        if self.playing_video and self.is_update == False:
            total_duration = self.media_player.get_length()
            position = int((float(value) / 100) * total_duration)
            self.media_player.set_time(position)
        self.is_update = False

    
    def update_video_progress(self):
        self.progress_percentage = 0
        if self.playing_video:
            total_duration = self.media_player.get_length()
            current_time = self.media_player.get_time()
            self.progress_percentage = (current_time / total_duration) * 100 if total_duration != 0 else 0
            self.is_update = True
            self.progress_bar.set(self.progress_percentage)
            current_time_str = str(timedelta(milliseconds=current_time))[:-3]
            total_duration_str = str(timedelta(milliseconds=total_duration))[:-3]
            self.time_label.config(text=f"{current_time_str}/{total_duration_str}")
        print(self.progress_percentage)
        if self.progress_percentage == self.media_player.get_length() or (self.temp > 0 and self.temp==self.progress_percentage and self.video_paused == False):
            self.playing_video = False
            self.play_video("output" + str(self.Count.get_VideoCount() + 1) + ".mp4")
        try:
            videoNumber = self.e.get(0)
            if "output" in videoNumber:
                self.playing_video = False
                self.play_video(videoNumber + ".mp4")
        except queue.Empty:
            pass
        finally:
            self.temp = self.progress_percentage
            self.after(500, self.update_video_progress)

    def on_value_change(self, value):
        super().set(value) # 값이 변경될 때마다 호출되지만 아무 일도 하지 않음

class VideoProgressBar(tk.Scale):
    def __init__(self, master, command, is_update, **kwargs):
        kwargs["showvalue"] = False
        super().__init__(
            master,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            length=800,
            command=command,
            **kwargs,
        )
        self.is_update = is_update
        self.command = command 
        self.bind("<Button-1>", self.on_click)
    def on_click(self, event):
        if self.cget("state") == tk.NORMAL:
            value = (event.x / self.winfo_width()) * 100
            self.set(value)
            self.command(value)