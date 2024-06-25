import cv2
from math import sqrt, acos, pi
import matplotlib.pyplot as plt

from utils import detect
from tracker.centroidtracker import CentroidTracker

def process_video(path_to_video, frame_count, classificator_for_centroid):
    # initialize our centroid tracker and frame dimensions
    centroid_tracker = CentroidTracker()

    # dictionary to keep centroid values in
    centroids_objects = {}

    norm_differences = {}
    scaled_speeds_before = {}

    accelerations = {}
    
    overlaps = {}
    angles = {}
    collision_frames = {}

    start = 1
    frames_per_second = 24.0
    frame_inc = 1
    delta_time = frame_inc/frames_per_second
    current_frame_index = start
    
    while current_frame_index < frame_count:
        
        current_frame_index += frame_inc

        iterated_objects = []

        frame = cv2.imread(f"{path_to_video}{current_frame_index:02}.jpg")
        original_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  
        resized_image = cv2.resize(original_image, (640, 640))
        detections = detect(resized_image, classificator_for_centroid)

        # Print the objects found and the confidence level
        #print_objects(detections, class_names)

        width = frame.shape[1]
        height = frame.shape[0]
        
        boxes = []
        confidences = []
        classIDs = []

        for detection in detections:
            scale_x = width / 640
            scale_y = height / 640
            confidence = float(detection[4])
            classID = int(detection[5])
            x1 = int(detection[0] * scale_x)
            y1 = int(detection[1] * scale_y)
            x2 = int(detection[2] * scale_x)
            y2 = int(detection[3] * scale_y)
            if confidence > 0.35:
                box = [x1, y1, x2, y2]
                boxes.append(box)
                confidences.append(confidence)
                classIDs.append(classID)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # update our centroid tracker using the computed set of bounding
        # box rectangles
        objects = centroid_tracker.update(boxes)
        #print(objects)

        # loop over the tracked objects
        for (objectID, centroid) in objects.items():
            # draw both the ID of the object and the centroid of the
            # object on the output frame
            text = "ID {}".format(objectID)
            
            # if the object ID is already registered, append the newest centroid value at the end of the list
            if objectID in centroids_objects:
                centroids_objects[objectID].append(centroid)
            # if the centroid is new, register it in the dictionary
            else:
                centroids_objects[objectID] = [centroid]
            
            cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)

        
        interval = 5
        thres_diff = 15.0 # for magnitude of differences
        
        for item, cents in centroids_objects.items():
            if len(cents) > interval and item in objects: # if there are at least 'interval' centroid values recorded and the object has not been deregistered from the tracker
                # difference between two points
                diff = cents[-1] - cents[-1-interval]
                mag_diff = (diff[0]**2 + diff[1]**2)**0.5
                norm_diff = (diff[0]/float(mag_diff), diff[1]/float(mag_diff)) if mag_diff != 0 else (0.0, 0.0)
                
                if mag_diff > thres_diff:
                    if item not in norm_differences:
                        norm_differences[item] = [[norm_diff, mag_diff, current_frame_index]]
                    else:
                        norm_differences[item].append([norm_diff, mag_diff, current_frame_index])

                # speed and acceleration
                gross_speed = (cents[-1] - cents[-1-interval])/(delta_time*interval)
                scaled_speed = (gross_speed[0]*((width-centroid_tracker.widthheight[item][0])/width + 1), gross_speed[1]*((height-centroid_tracker.widthheight[item][1])/height + 1))
                if item in scaled_speeds_before: # if a previous scaled speed value exists
                    acceleration = ((scaled_speed[0]**2 - scaled_speeds_before[item][0]**2)/(delta_time*interval), (scaled_speed[1]**2 - scaled_speeds_before[item][1]**2)/(delta_time*interval))
                    if item not in accelerations:
                        accelerations[item] = [[acceleration, current_frame_index]]
                    else:
                        accelerations[item].append([acceleration, current_frame_index])
                scaled_speeds_before[item] = scaled_speed
                    
        for (first_object, first_centroid) in centroids_objects.items():
            if first_object not in objects:
                continue
            iterated_objects.append(first_object)
            current_first_centroid = first_centroid[-1]
            width_height_first = centroid_tracker.widthheight[first_object]
            for (second_object, second_centroid) in centroids_objects.items():
                if second_object not in objects:
                    continue
                if second_object not in iterated_objects:
                    current_second_centroid = second_centroid[-1]
                    width_height_second = centroid_tracker.widthheight[second_object]
                    if (2*abs(current_first_centroid[0] - current_second_centroid[0]) < (width_height_first[0] + width_height_second[0])) and (2*abs(current_first_centroid[1] - current_second_centroid[1]) < (width_height_first[1] + width_height_second[1])):
                        pair = (first_object, second_object)
                        if pair in overlaps:
                            overlaps[pair].append(current_frame_index)
                            if pair in collision_frames:
                                collision_frames[pair].append(current_frame_index)
                            else:
                                collision_frames[pair] = [current_frame_index]
                        else:
                            overlaps[pair] = [current_frame_index]
                            if pair in collision_frames:
                                collision_frames[pair].append(current_frame_index)
                            else:
                                collision_frames[pair] = [current_frame_index]
                            
                        if first_object in norm_differences and second_object in norm_differences:
                            # find angle between two overlapping objects
                            ratio = norm_differences[first_object][-1][0][0] * norm_differences[second_object][-1][0][0] + norm_differences[first_object][-1][0][1] * norm_differences[second_object][-1][0][1]
                            if ratio > 1.0:
                                ratio = 1.0
                            elif ratio < -1.0:
                                ratio = -1.0
                            theta = acos(ratio)
                            if theta >= pi/2:
                                theta = theta - pi
                            # record the angle between two objects and the time
                            if pair in angles:
                                angles[pair].append([theta, current_frame_index])
                            else:
                                angles[pair] = [[theta, current_frame_index]]
                        else:
                            theta = None
        
                    # show the output frame
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

    
    return overlaps, accelerations, angles, collision_frames