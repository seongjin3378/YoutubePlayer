from tkinter import Tk, Toplevel, Button, Listbox, END, Frame, Label, ttk
import tkinter as tk
import queue
import re
import time
def do_nothing():
    pass

class VideoPlayList(Toplevel):
    def __init__(self, parent, q, w, e, Count):
        super().__init__(parent)
        self.geometry('300x700+1520+200') # 창 크기 설정
        self.resizable(False, False)
        self.title("PlayList")
        self.protocol("WM_DELETE_WINDOW", do_nothing) 
        self.q = q
        self.w = w
        self.e = e
        self.parent = parent
        # 재생목록에 노래 추가
        self.progress_var = None
        self.loading_bar = None
        self.frames = {} 
        self.after(100, self.check_message)
        self.Count = Count

    def check_message(self):
        try:
            Message = self.w.get(0)
            print(Message)
            print(self.Count.get_count())
            if "FailedLoad" == Message:
                self.delete_video_list("output" + str(self.Count.get_count()))
                self.after(100, self.check_message)
                self.Count.decrease_count() 
            elif "CreateList" == Message:    
                print(Message)
                self.create_video_list("output"+str(self.Count.get_count()))
                self.Count.increase_count
                self.after(100, self.check_message)
            else:
                self.after(100, self.check_message)
                
        except queue.Empty:
            self.after(100, self.check_message)
        except Exception as e:  # 모든 예외를 잡기 위한 구문
            print(f'check_message에서 예외가 발생했습니다: {e}')

       
    def check_queue(self):
        try:
            progress = self.q.get(0)
            if progress == "finished":
                self.w.put("finshed")
                return
            progress = re.sub(r'\x1b\[[0-9;]*m', '', progress)
            progress_float = float(progress.replace("%", ""))
            self.progress_var.set(progress_float)
            self.after(100, self.check_queue)
        except queue.Empty:
            pass
        finally:
            self.after(100, self.check_queue)

    def create_video_list(self, video):
        frame = Frame(self)
        frame.pack(fill='x')

        # 노래 제목 레이블 생성
        Label(frame, text=video).pack(side='left')
        # 재생 버튼 생성
        Button(frame, text="재생", command=lambda video=video: self.play_song(video)).pack(side='right')

            # 로딩 바 추가
        self.progress_var = tk.DoubleVar() 
        self.loading_bar = ttk.Progressbar(frame, length=100, mode='determinate', variable=self.progress_var)
        self.loading_bar.pack(fill='both', expand=True) # 로딩 바가 콤보박스를 꽉 채우도록 설정
        self.frames[video] = frame
        self.after(100, self.check_queue)
        
    def delete_video_list(self, video):
        # 딕셔너리에서 frame을 가져옴
        frame = self.frames.get(video)

        # frame이 존재하면 삭제
        if frame is not None:
            frame.destroy()
            del self.frames[video]  # 딕셔너리에서도 삭제
    def play_song(self, song):
        self.e.put(song)