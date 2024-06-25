from math import pi

def angle_anomalies(angles): 
    changeanomalies = {}

    for pair, items in angles.items():
        angle_diffs = []
        max_diff = 0
        for i in range(1, len(items)):
            diff = items[i][0] - items[i-1][0]
            if diff > pi/2:
                diff -= pi
            if abs(diff) > max_diff:
                max_diff = abs(diff)
            
        # decide gamma
        if max_diff < 0.1:
            gamma = 0
        elif max_diff < 0.2:
            gamma = 0.1
        elif max_diff < 0.3:
            gamma = 0.2
        elif max_diff < 0.4:
            gamma = 0.3
        elif max_diff < 0.5:
            gamma = 0.5
        elif max_diff < 0.6:
            gamma = 0.7
        elif max_diff < 0.7:
            gamma = 0.8
        elif max_diff < 0.8:
            gamma = 0.9
        else:
            gamma = 1

        changeanomalies[pair] = gamma

    return changeanomalies