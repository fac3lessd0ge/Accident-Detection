import cv2
from ultralytics import YOLO

from utils import *
from lib.centroid_predict import centroid_predict
from lib.process_video import process_video

from lib.angle_anomalies import angle_anomalies
from lib.trajectory_anomalies import trajectory_anomalies
from lib.acceleration_anomalies import acceleration_anomalies


vehicle_detector_weight_path = './weights/car_detector_best.pt'
accident_detector_weight_path = './weights/accident_detector.pt'

accident_detector = YOLO(accident_detector_weight_path)
classificator_for_centroid = YOLO(vehicle_detector_weight_path)

def run(path_to_video, frame_count):

    lower_confidence = 0.4
    upper_confidence = 0.7

    ensemble_value = 0.3

    overlaps, accelerations, angles, collision_frames = process_video(path_to_video, frame_count, classificator_for_centroid)
    

    acceleration_anomalies_values = acceleration_anomalies(overlaps, accelerations)
    angle_anomalies_values = angle_anomalies(angles)
    trajectory_anomalies_values = trajectory_anomalies(angles)

    prediction_values = [[(1, 3), 0.6350612471810022]] #centroid_predict(acceleration_anomalies_values, trajectory_anomalies_values, angle_anomalies_values) #[[(0, 3), 0.5]] [[(1, 3), 0.6750612471810022]] #
    for prediction in prediction_values:
        print("Предсказание первого метода", prediction)
        if prediction[1] >= lower_confidence and prediction[1] <= upper_confidence:
            second_predictions = detect(f"{path_to_video}{get_middle_element(collision_frames[prediction[0]])}.jpg", accident_detector)
            print("Первый метод не уверен", prediction[1], second_predictions)
            if (len(second_predictions)):
                increase_value = 0
                for second_prediction in second_predictions:
                    if second_prediction[4] > increase_value: increase_value = second_prediction[4]
                prediction[1] += increase_value * ensemble_value
    

    print("Final Predictions:", prediction_values)
    
    # do a bit of cleanup
    cv2.destroyAllWindows()