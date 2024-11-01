import ffmpeg
import yt_dlp
class YoutubeDownloader:
    def __init__(self, q, w, Count):
        self.q = q
        self.w = w
        self.Count = Count
    def extract_streaming_url(self, youtube_url, format_option, filename):
        def my_hook(d):
            if d['status'] == 'downloading':
                download_progress = d['_percent_str']
                self.q.put(download_progress)
            elif d['status'] == 'finished':
                self.q.put("finished")

        # 스트리밍 추출을 위한 설정
        ydl_opts = {
            'format': format_option,
            'noplaylist': True,
            'outtmpl': f'./{filename}',  # 다운로드 파일의 경로 및 이름 설정
            'progress_hooks': [my_hook], 
        }

        # 스트리밍 URL 추출
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
            # 먼저 URL이 유효한지 검사합니다.
                if not youtube_url:
                    raise ValueError("URL이 유효하지 않습니다.")
                info_dict = ydl.extract_info(youtube_url, download=True)
                filename = ydl.prepare_filename(info_dict)  # 다운로드된 파일의 경로 가져오기
            except Exception:
                pass
        return filename  # 다운로드된 파일의 경로 반환

    def download_and_merge(self, url):
        self.Count.increase_count()
        self.w.put("CreateList")
        video_file = self.extract_streaming_url(url, "bv", "output0.mp4")
        audio_file = self.extract_streaming_url(url, "bestaudio[ext=m4a]", "output0.m4a")
        output_file = f"output{self.Count.get_count()}.mp4"
        # 비디오와 오디오 병합
        try:
            ffmpeg.output(ffmpeg.input(video_file), ffmpeg.input(audio_file), output_file, vcodec='copy', acodec='copy').run(capture_stdout=True, capture_stderr=True)
        except ffmpeg.Error as e:
            return