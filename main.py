import cv2
import numpy as np
from ultralytics import YOLO
import torch
import csv
import os
from datetime import datetime

# detection function
def detection(model, frame):

    # resizing the frame
    h, w, _ = np.shape(frame)
    new_h, new_w = int(h / 2), int(w / 2)
    frame = cv2.resize(frame, (new_w, new_h))

    tracking = ['person'] # class to detect

    class_list = model.names # list of classes

    items = [item[1] for item in class_list.items()] # items in class_list

    # Defining colors
    color_green = (0,255,0)
    color_yellow = (0,255,255)
    color_red = (0,0,255)
    color_pink = (255, 0, 255)

    # Defining work stations
    station_cordinates = {

    "station_1": {'x1': 148, 'x2': 267,
                  'y1': 47, 'y2': 95},
    
    "station_2": {'x1': 388, 'x2': 518,
                  'y1': 8, 'y2': 77},

    "station_3": {'x1': 638, 'x2': 750,
                  'y1': 23, 'y2': 114},
    
    "station_4": {'x1': 859, 'x2': 912,
                  'y1': 86, 'y2': 193},
    
    "station_5": {'x1': 715, 'x2': 909,
                  'y1': 289, 'y2': 509},

    "station_6": {'x1': 10, 'x2': 180,
                  'y1': 310, 'y2': 510}
                  }


    # performing detection
    results = model.track(frame, persist=True)
    
    # if there are detections
    if results[0].boxes.data is not None:
        boxes = results[0].boxes.xyxy.cpu().numpy().astype(np.int32).tolist() # bounding box coordinates
        classes = results[0].boxes.cls.cpu().numpy().astype(np.int32).tolist() # classes
        confidence = results[0].boxes.conf.cpu().tolist() # confidence values
        working_stations = [] # occupied station information

        for box, cls, conf in zip(boxes, classes, confidence):
            x0, y0, x1, y1 = map(int, box) # coordinates of each detected bbox
            label = items[cls] # detected object label name
            conf = round(conf, 2) # rounding the conf value

            # if label and conf conditions are met
            if conf >= 0.8 and label in tracking:
                status = "IDLE" # Assuming initial working station status as idle

                # iterating through station cordinated dictionary
                for station_name, coord in station_cordinates.items():
                    
                    # work station coordinates
                    sx1, sy1 = coord['x1'], coord['y1']  
                    sx2, sy2 = coord['x2'], coord['y2']

                    # Checking if detection is inside any station
                    if sx1 <= x0 and sy1 <= y0 and sx2 >= x1 and sy2 >= y1:
                        status = "WORKING" # toggling the status 
                        working_stations.append(station_name) # capturing occupied station data for logging

                # Draw person box and status
                cv2.rectangle(frame, (x0, y0), (x1, y1), color_green if status == "WORKING" else color_red , 1) # green bbox if "working" otherwise red
                
                cv2.putText(frame, status, (x0, y0 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                            color_green if status == "WORKING" else color_yellow, 2) # green text if "working" otherwise yellow

        # Draw all stations and station name
        for stations, coordinate in station_cordinates.items():
            cv2.rectangle(frame, 
                          (coordinate['x1'], coordinate['y1']),
                          (coordinate['x2'], coordinate['y2']), 
                          color_pink, 
                          2)
            
            cv2.putText(frame, f"{stations}",
                        (coordinate['x1'], coordinate['y1'] - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        color_pink, 2)
            
    return frame, boxes, working_stations

def append_to_csv(filename, fieldnames, data):
    # Check if the file exists to determine whether to write the header
    file_exists = os.path.isfile(filename)

    with open(filename, mode='a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write header if file is new
        if not file_exists:
            writer.writeheader()

        # Write the data row
        writer.writerow(data)

def station_status(station_name, detections):

    if station_name in detections:
        return "Working"
    
    else:
        return "Idle"
    
def main(model_path:str, 
         video_path: str, 
         csv_save_path: str):

    device = 'cuda' if torch.cuda.is_available() else 'cpu' # Device agnostic code

    model_path = model_path # model path
    video_path = video_path # video path
    csv_folder = csv_save_path # logging file path

    model = YOLO(model_path).to(device) # defining model

    cap = cv2.VideoCapture(video_path) # capturing feed

    # define logger file name and path
    file_count = len(os.listdir(csv_folder)) + 1
    csv_filename = f"logger_{file_count}.csv"
    csv_path = os.path.join(csv_folder, csv_filename)

    serial_num_count = 1 # Keeping track of serial numbers

    run = True # run condition

    logger_tracker = 0 # tracking logging file operation

    while run:

        ret, frame = cap.read() # readin frame

        # running inference
        if ret:
            frame, boxes, stations = detection(model,frame)
            detections = len(boxes)
            
            # for the scope of the video keeping the detections uniform
            if detections > 6:
                detections = 6
            
            working_stations = len(stations) # number of station people working on
            
            idle_stations = detections - working_stations # number of idle stations
            
            dt = datetime.now() # timestamps

            # defining field name for logger file
            field_names = ['S.No.', 
                        'Timestamp', 
                        'Detections', 
                        'Working stations', 
                        'Idle stations', 
                        'Station 1',  
                        'Station 2',  
                        'Station 3',  
                        'Station 4',  
                        'Station 5',  
                        'Station 6']

            # logginf every 60 frames
            if logger_tracker % 60 == 0:

                append_to_csv(csv_path, field_names, {'S.No.': serial_num_count, 
                                                    'Timestamp': dt, 
                                                    'Detections': detections, 
                                                    'Working stations': working_stations, 
                                                    'Idle stations': idle_stations, 
                                                    'Station 1': station_status('station_1', stations), 
                                                    'Station 2': station_status('station_2', stations), 
                                                    'Station 3': station_status('station_3', stations), 
                                                    'Station 4': station_status('station_4', stations), 
                                                    'Station 5': station_status('station_5', stations), 
                                                    'Station 6': station_status('station_6', stations)
                                                    })
                
                serial_num_count += 1

        k = cv2.waitKey(1)

        # press 'q' to quit or end stream once video feedends
        if k == ord('q') or not ret:
            run = False
            break

        cv2.imshow('frame', frame) # displaying frame

        logger_tracker += 1 # tracking logger file

    cap.release()
    cv2.destroyAllWindows()

# function path parameters requested to user
model = input("Enter model path: ")
video = input("Enter video path: ")
csv_path = input("Enter path for logger file: ")

# running function
main(model, video, csv_path)
