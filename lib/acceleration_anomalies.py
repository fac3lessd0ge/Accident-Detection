def acceleration_anomalies(overlaps, accelerations):
    # acceleration anomaly detection

    # amounts to go back and forward to from the point of contact
    frames_before = 6
    frames_after = 6

    acceleration_anomalies = {}

    for pair, indexes in overlaps.items():
        # for each overlapping moment of a pair
        alphamax = 0
        for frameIdx in indexes:
            # check if there are at least 15 acceleration values before the overlapping condition for both objects
            first_acceleration_before = []
            second_acceleration_before = []
            
            first_acceleration_after = []
            second_acceleration_after = []
            
            for values in accelerations[pair[0]]:
                first_acceleration_before += [values] if values[1] < frameIdx else []
                first_acceleration_after += [values] if values[1] > frameIdx else []

            for values in accelerations[pair[1]]:
                second_acceleration_before += [values] if values[1] < frameIdx else []
                second_acceleration_after += [values] if values[1] > frameIdx else [] 

            if len(first_acceleration_before) >= frames_before and len(second_acceleration_before) >= frames_before and len(first_acceleration_after) >= frames_after and len(second_acceleration_after) >= frames_after:
                average_first_acceleration_before = 0.0
                for acceleration_value in first_acceleration_before[-frames_before:]:
                    average_first_acceleration_before += (acceleration_value[0][0]**2 + acceleration_value[0][1]**2)**0.5
                average_first_acceleration_before /= float(frames_before)
                
                average_second_acceleration_before = 0.0
                for acceleration_value in second_acceleration_before[-frames_before:]:
                    average_second_acceleration_before += (acceleration_value[0][0]**2 + acceleration_value[0][1]**2)**0.5
                average_second_acceleration_before /= float(frames_before)

                max_first_acceleration_after = 0.0
                for acceleration_value in first_acceleration_after[0:frames_after]:
                    magnitude = (acceleration_value[0][0]**2 + acceleration_value[0][1]**2)**0.5
                    max_first_acceleration_after = magnitude if magnitude > max_first_acceleration_after else max_first_acceleration_after
                
                max_second_acceleration_after = 0.0
                for acceleration_value in second_acceleration_after[0:frames_after]:
                    magnitude = (acceleration_value[0][0]**2 + acceleration_value[0][1]**2)**0.5
                    max_second_acceleration_after = magnitude if magnitude > max_second_acceleration_after else max_second_acceleration_after
                    
                first_acceleration_difference = max_first_acceleration_after - average_first_acceleration_before
                second_acceleration_difference = max_second_acceleration_after - average_second_acceleration_before
                
                acc_anomaly_score = first_acceleration_difference + second_acceleration_difference
                
                # determine alpha
                if abs(acc_anomaly_score) < 100:
                    alpha = 0
                elif abs(acc_anomaly_score) < 500:
                    alpha = 0.2
                elif abs(acc_anomaly_score) < 750:
                    alpha = 0.4
                elif abs(acc_anomaly_score) < 900:
                    alpha = 0.6
                elif abs(acc_anomaly_score) < 1200:
                    alpha = 0.8
                elif abs(acc_anomaly_score) < 1500:
                    alpha = 0.9
                else:
                    alpha = 1
                    
                alphamax = alpha if alpha > alphamax else alphamax
            
                #print(pair, frameIdx, obj1accdiff, obj2accdiff)
                
        acceleration_anomalies[pair] = alphamax
                    
    return acceleration_anomalies            