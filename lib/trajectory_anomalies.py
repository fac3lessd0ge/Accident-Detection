from math import pi

def trajectory_anomalies(angles):
    # trajectory anomaly detection

    trajecanomalies = {}

    theta_low = -pi/4
    theta_high = pi/4

    for pair, items in angles.items():
        betamax = 0
        for item in items:
            # if theta is between theta_low and theta_high
            if theta_low < item[0] < theta_high:
                if abs(item[0]) < (abs(theta_low) + abs(theta_high))/4.0:
                    beta = 0.0
                else:
                    beta = 0.1
            else:
                beta = abs(item[0])/(pi/2)
            
            betamax = beta if beta > betamax else betamax
                
        trajecanomalies[pair] = betamax

    return trajecanomalies