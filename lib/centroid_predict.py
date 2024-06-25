def centroid_predict(acceleration_anomalies, trajectory_anomalies, angle_anomalies):
    alpha_weight = 0.2
    beta_weight = 0.35
    gamma_weight = 0.45

    results = []

    for pair in acceleration_anomalies:
        if pair in trajectory_anomalies and pair in angle_anomalies:
            final_score = alpha_weight*acceleration_anomalies[pair] + beta_weight*trajectory_anomalies[pair] + gamma_weight*angle_anomalies[pair]
            results.append([pair, final_score])

    return results
