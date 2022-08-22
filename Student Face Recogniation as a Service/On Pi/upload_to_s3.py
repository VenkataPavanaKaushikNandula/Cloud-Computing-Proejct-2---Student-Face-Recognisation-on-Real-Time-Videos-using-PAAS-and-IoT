import json
import boto3
import io
import time
import argparse
import cv2
import threading

class UploadVideo():
    def __init__(self):
        self.aws_region = "us-east-one"
        self.s3_input_bucket_name = "cse546group27inputvideobucket"
        self.video_path = "/home/pi/videos/"
        self.sqs_service = boto3.resource("sqs")
        self.timeline_dict = dict()
        self.sqs_response_queue_name = "response-queue"

    def video_upload(self, total_number = 600):
        boto3_session = boto3.Session()
        s3 = boto3_session.client("s3")
        number = 1
        time.sleep(3)
        t1 = threading.Thread(target=self.fetch_result_from_sqs, args=(total_number,))
        t1.start()
        while number <= total_number:
            # file_name = "video" + str(number) + ".h264"
            file_name = str(number) + ".h264"
            path_of_video_file = self.video_path + file_name
            # path_of_video_file = self.extract_frames(file_name)
            # print("Video Name :", path_of_video_file)
            self.upload_video_to_s3(s3, path_of_video_file, path_of_video_file.split("/")[-1])
            # print(number)
            self.timeline_dict[str(number)] = time.time()
            # print(file_name, time.time())
            # print("upload success")
            number += 1
            # time.sleep(0.5)
        t1.join()
        print("Number: ", number)
        return

    def upload_video_to_s3(self, s3_client, file, file_name):
        # s3_client.upload_fileobj(file, self.s3_input_bucket_name, str(file_name))
        # with open(file) as f:
        files = io.open(file, "rb", buffering = 0)
        s3_client.upload_fileobj(io.BytesIO(files.read()), self.s3_input_bucket_name, file_name)
        # print("Video uploaded to S3")
        return
    
    def fetch_result_from_sqs(self, number):
        time.sleep(2)
        queue = self.sqs_service.get_queue_by_name(QueueName=self.sqs_response_queue_name)
        i = 1
        while i <= number:
            processed_time = time.time()
            messages = queue.receive_messages(MaxNumberOfMessages=1, WaitTimeSeconds=20)
            if messages:
                for m in messages:
                    content = json.loads(m.body)
                    m.delete()
                    pic = list(content.keys())[0]
                    picture_name = pic.split('.')[0]
                    # print("Pic: ", pic)
                    # print("Picture Name: ", picture_name)
                    # print("content: ", list(content.keys())[0])
                    print(f"The person {picture_name} recognized: ", content[pic])
                    print("Latency: ",processed_time - self.timeline_dict.get(picture_name))
                    # print("request received", processed_time)
                    # print("content", list(content.values())[0])
            i += 1    
            # time.sleep(0.5)
        return

    def extract_frames(self, file_name):
        # Read the video from specified path
        dimensions = (160, 160)
        cam = cv2.VideoCapture(self.video_path + file_name)
        ret, frame = cam.read()
        if ret:
            image_name = self.video_path + file_name.split(".")[0] + ".png"
            cv2.imwrite(image_name, frame)
            # img = cv2.imread(image_name, cv2.IMREAD_UNCHANGED)
            # resized = cv2.resize(img, (160, 160), interpolation = cv2.INTER_AREA)
            # cv2.imwrite(image_name, resized)
            # print("Width: ", resized.shape[1])
            # print("Length: ", resized.shape[0])
        cam.release()
        cv2.destroyAllWindows()
        return image_name
    def print_dict(self):
        print(self.timeline_dict)
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--number", help = "Denotes number of videos will be taken")
    args= parser.parse_args()
    # print("Argument number received: ", args.number)
    number_of_invocations = int(args.number)
    my_upload  = UploadVideo()
    # my_upload.print_dict()
    my_upload.video_upload(total_number=number_of_invocations)
    # my_upload.fetch_result_from_sqs()
    # i = 0
    # while i < number_of_invocations:
    #     my_upload.fetch_result_from_sqs()