from picamera import PiCamera
import time
import os
import subprocess
import cv2


class Frames():
    def __init__(self):
        self.time_to_execute = 300

        self.dict_for_time = dict()
        

    def record_video(self):
        camera = PiCamera()
        time.sleep(2)
        print("invoking...")
        cmd = f"/home/pi/raspberry/upload_to_s3.py"
        subprocess.Popen(["python", cmd, f"-n {self.time_to_execute*2}"])
        print("invoked...")
        # os.system(cmd)
        start_time = time.time()
        # camera.resolution = (1280, 720)
        camera.resolution = (160, 160)
        camera.vflip = False
        camera.contrast = 10
        executed_time = 0
        video_number = 1
        print("starting to record")
        while executed_time < self.time_to_execute:
            # video_name = "video" + str(video_number) + ".h264"
            video_name = str(video_number) + ".h264"
            file_name = "/home/pi/videos/" + video_name
            self.dict_for_time[video_name] = time.time()
            # print("Start recording...")
            camera.start_preview()
            camera.start_recording(file_name)
            camera.wait_recording(0.5)
            camera.stop_recording()
            camera.stop_preview()
            # print("Done.")
            executed_time += 0.5
            video_number += 1
        print("Total time taken: ", time.time() - start_time)
    

    

if __name__ == "__main__":
    my_frames = Frames()
    my_frames.record_video()

