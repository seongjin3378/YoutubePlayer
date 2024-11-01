import queue
import threading
import tkinter as tk
from tkinter import PhotoImage
import os
from VideoPlayer import YoutubePlayer
from VideoPlayList import VideoPlayList
import glob

# 현재 작업 디렉토리 가져오기
current_dir = os.getcwd()  # 현재 디렉토리
ffmpeg_bin_path = os.path.join(current_dir, "ffmpeg-6.1-full_build", "bin")

# ffmpeg_bin_path 확인
print(ffmpeg_bin_path)

# 환경 변수에 추가
os.environ["PATH"] += os.pathsep + ffmpeg_bin_path


class CountClass:
    def __init__(self):
        self.count = 0
        self.VideoNumber = 0
        self.lock = threading.Lock()

    def increase_count(self):
        with self.lock:
            self.count += 1
            return self.count

    def decrease_count(self):
        with self.lock:
            if self.count > 0:
                self.count -= 1
            return self.count

    def get_count(self):
        with self.lock:
            return self.count

    def set_count(self, count):
        with self.lock:
            self.count = count
            
    def set_VideoCount(self, Video):
        last_char = Video[-5]  # 마지막 글자를 추출
        VideoCount = int(last_char) 
        self.VideoNumber = VideoCount

    def set_VideoNumber(self, VideoNumber):
        self.VideoNumber = VideoNumber

    def get_VideoCount(self):
        return self.VideoNumber


class FileDropApp:
    def __init__(self, master):
        self.master = master
        self.q = queue.Queue()
        self.w = queue.Queue()
        self.e = queue.Queue()
        self.new_playlist_window = None
        self.Count = CountClass()

        # 비디오 플레이어와 플레이리스트를 생성하는 스레드 시작
        self.videoPlayerThread = threading.Thread(target=self.create_video_player, args=(self.q, self.w, self.e, self.Count), daemon=True)
        self.videoPlayListThread = threading.Thread(target=self.create_video_playlist, args=(self.q, self.w, self.e, self.Count), daemon=True)

        self.videoPlayerThread.start()
        self.videoPlayListThread.start()

    def remove_file(self, remove_file=True):
        for file in glob.glob("output*.mp4"):
            os.remove(file)          

    def create_video_player(self, q, w, e, Count):
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'YoutubeFile.png')
        icon_image = PhotoImage(file=icon_path)
        new_video_player = YoutubePlayer(self.master, q, w, e, Count)
        new_video_player.iconphoto(False, icon_image)

        def on_closing():
            new_video_player.media_player.stop()
            new_video_player.destroy()
            if self.new_playlist_window:
                self.new_playlist_window.destroy()
            self.remove_file()
            self.master.quit()  # 강제 종료
        new_video_player.protocol("WM_DELETE_WINDOW", on_closing)

    def create_video_playlist(self, q, w, e, Count):       
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'YoutubeFile.png')
        icon_image = PhotoImage(file=icon_path)
        self.new_playlist_window = VideoPlayList(self.master, q, w, e, Count)
        self.new_playlist_window.iconphoto(False, icon_image)


if __name__ == "__main__":
    root = tk.Tk()  # TkinterDnD를 사용하여 루트 창 생성
    root.geometry("500x520+1000+400")
    root.withdraw()  # 창을 숨깁니다
    app = FileDropApp(root)  # FileDropApp 인스턴스를 생성하여 스레드를 시작합니다
    root.mainloop()