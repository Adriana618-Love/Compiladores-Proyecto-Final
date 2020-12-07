from moviepy.editor import VideoFileClip
string = "videos/video.mp4"

video = VideoFileClip(string)
d = {
    'h': video,
}
d['h'].write_videofile("videos/latvideo.mp4")