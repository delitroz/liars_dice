import cv2

from skimage.color import label2rgb

from src.camera_utils import select_camera
from src.ip import *

if __name__ == "__main__":

    camera = 0
    # camera = select_camera()
    # cv2.destroyAllWindows()   # Necessary otherwise the window for camera selection don't go away

    cap = cv2.VideoCapture(camera)

    while(True):

        ret, frame = cap.read()

        gray = rgb2gray_uint8(frame)

        norm = normalize_uint8(gray)

        bin = otsu_uint8(norm)

        cleared = clear_border(bin)

        label_image = label(cleared)

        # # Drastically reduces framerate
        # image_label_overlay = label2rgb(
        #     label_image, image=frame, bg_label=0
        # )
        # cv2.imshow("Labels", image_label_overlay)

        obj_lst = []
        for region in regionprops(label_image):
            if region.area >= 100:
                obj_lst.append(
                    Dice(
                        in_img=frame,
                        center=region.centroid,
                        bbox=region.bbox,
                        value=None,
                    )
                )

        overlay = dices_bboxes_overlay(frame, obj_lst)

        # Display everything on a big image
        gray_disp = np.stack([gray, ] * 3, axis=2)
        cleared_disp = np.stack([cleared, ] * 3, axis=2)
        norm_disp = np.stack([norm, ] * 3, axis=2)
        bin_disp = np.stack([bin, ] * 3, axis=2)

        row1 = np.concatenate([frame, gray_disp, norm_disp], axis=1)
        row2 = np.concatenate([bin_disp, cleared_disp, overlay], axis=1)
        display = np.concatenate([row1, row2], axis=0)
        cv2.imshow("", display)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()