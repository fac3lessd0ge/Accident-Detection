def detect(image_path, model):
    # Выполнение детекции объектов на изображении
    results = model.predict(image_path, device="0")

    # Получение массива векторов с результатами детекции
    detections = []
    for result in results:
        for detection in result.boxes.data.tolist():
            #if(detection[5] == 2):
                x1, y1, x2, y2 = detection[:4]
                confidence = detection[4]
                class_id = int(detection[5])
                detections.append([x1, y1, x2, y2, confidence, class_id])

    return detections

def get_middle_element(arr):
    if not arr:
        return None
    
    length = len(arr)
    mid = length // 2
    
    if length % 2 == 0:
        return (arr[mid - 1] + arr[mid]) // 2
    else:
        return arr[mid]