import cv2
from src.ip import detect_dices, dices_bboxes_overlay

if __name__ == "__main__":

    cap = cv2.VideoCapture(0)

    while(True):

        ret, frame = cap.read()

        obj_lst = detect_dices(frame)

        overlay = dices_bboxes_overlay(frame, obj_lst)

        cv2.imshow("processed", overlay)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()