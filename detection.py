# -*- coding: utf-8 -*-
from ultralytics import YOLO
import cv2
import math
import os
from tqdm import tqdm
from datetime import datetime

def detection_position(video_path, result_path):
    cap = cv2.VideoCapture(video_path)
    fps = 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    model = YOLO("./YOLO-PretrainedModels/yolov8m.pt")
    classnames = {0: 'person'}
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    filename = video_path.split('/')[-1]
    start_name = filename
    filename = filename.split('mp4')[0].strip('.') +'_'+ str(datetime.now().year)+'-'+str(datetime.now().month)+'-'+str(datetime.now().day)+' ' +str(datetime.now().hour)+':'+str(datetime.now().minute)+':'+str(datetime.now().second)+'.mp4'
    name = filename
    filename = "rez"+filename
    old = filename
    output_path = os.path.join(result_path,filename)
    output_video = cv2.VideoWriter(os.path.join(output_path), fourcc, fps, (640, 360))
    name = name.strip('rez')
    filename = name
    log_filename = os.path.splitext(filename)[0] + "_log.txt"
    full_log_filename = os.path.splitext(filename)[0] + "_log_full.txt"
    log_file_path = os.path.join(result_path, log_filename) 
    full_log_file_path = os.path.join(result_path, full_log_filename)

    with open(log_file_path, "w") as log_file:
        buf_size = 600
        buf = []
        status = ''

        for _ in tqdm(range(total_frames)):
            success, img = cap.read()
            img = cv2.resize(img, (640, 360))

            if not success or cv2.waitKey(1) == 27:
                break

            results = model(img, stream=True)

            is_person_detected = False
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                    w, h = x2 - x1, y2 - y1
                    w, h = int(w), int(h)

                    conf = math.ceil((box.conf[0] * 100)) / 100
                    cls = int(box.cls[0])

                    if cls in classnames and classnames[cls] == "person":
                        is_person_detected = True
                        if w > h:
                            color = (0, 0, 255)
                            status_text = 'FALL'
                        else:
                            color = (0, 255, 0)
                            status_text = 'OK'

                        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
                        text_y = max(0, y1 - 10)

                        cv2.putText(img, f'{status_text}', (max(0, x1), text_y),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

                        buf.append(status_text)
                        if len(buf) > buf_size:
                            buf.pop(0)

            output_video.write(img)

            # Логика обработки событий
            if is_person_detected:
                buf.append(status_text)
                if buf[-10:].count('OK') == 10 and status != 'Человек встал' and (status == 'Человек долго находится без движения' or status == 'Человек упал'):
                    status = 'Человек встал'
                    log_line = f"{cap.get(cv2.CAP_PROP_POS_MSEC) / 1000:.2f} - Человек встал\n"
                    log_file.write(log_line)
                elif status != 'Человек встал' and buf[-300:].count(
                        'FALL') / 300 >= 0.75:
                    status = 'Человек долго находится без движения'
                    log_line = f"{cap.get(cv2.CAP_PROP_POS_MSEC) / 1000:.2f} - Человек долго находится без движения\n"
                    log_file.write(log_line)
                elif buf[-10:].count('FALL') >= 5 and status != 'Человек долго находится без движения':
                    status = 'Человек упал'
                    log_line = f"{cap.get(cv2.CAP_PROP_POS_MSEC) / 1000:.2f} - Человек упал\n"
                    log_file.write(log_line)
    with open(full_log_file_path, "w") as full_log_file:
        with open(log_file_path, "r") as log_file:
            full_log_file.writelines(log_file.readlines())
# Обработка лога и добавление интервалов
    with open(log_file_path, "r") as log_file:
        lines = log_file.readlines()

    if lines:
        # Создание списка для новых строк с интервалами
        new_lines = []
        current_line = lines[0].strip()
        start_time = float(current_line.split(" - ")[0])

        for line in lines[1:]:
            line = line.strip()
            time = float(line.split(" - ")[0])

            if line.split(" - ")[1] != current_line.split(" - ")[1]:
                new_lines.append(f"{start_time:.2f}-{time:.2f} - {current_line.split(' - ')[1]}\n")
                start_time = time
                current_line = line

        # Добавление последней строки
        new_lines.append(f"{start_time:.2f}-{time:.2f} - {current_line.split(' - ')[1]}\n")

        # Перезапись файла лога
        with open(log_file_path, "w") as log_file:
            log_file.writelines(new_lines)  

    output_video.release()
    cap.release()
    cv2.destroyAllWindows()
    old = '\''+old+'\''

    os.system("ffmpeg -i "+os.path.join(result_path, old)+" -vcodec libx264 -f mp4 "+os.path.join(result_path, '\''+name+'\''))
    os.system("rm " + os.path.join(result_path, old))
    return name

