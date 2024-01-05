import numpy as np
import cv2

from skimage.color import rgb2gray
from skimage.filters import threshold_otsu
from skimage.segmentation import clear_border
from skimage.measure import label, regionprops


def rgb2gray_uint8(img):
    """Converts RGB image to 8bit grayscale

    Args:
        img (ndarray): RGB image

    Returns:
        ndarray: grayscale image
    """

    gray = rgb2gray(img)
    gray = (gray * 255).astype(np.uint8)

    return gray

def normalize_uint8(img):
    """Normalizes an image and return as 8bit.

    Args:
        img (ndarray): Input image

    Returns:
        ndarray: Normalized image
    """

    im = np.copy(img).astype(np.float32)
    norm_im = (img - np.min(im)) / (np.max(im) - np.min(im))
    norm_im = (norm_im * 255).astype(np.uint8)

    return norm_im


def otsu_uint8(img):
    """Applies Otsu's thresholding to an image. Returns a
    binary image encoded in 8bit with values [0, 255].

    Args:
        img (ndarray): Input image

    Returns:
        ndarray: Binarized image
    """
    t = threshold_otsu(img)
    retval = np.zeros_like(img).astype(np.uint8)
    retval[img > t] = 255
    return retval


def invert_uint8(img):
    """Inverts binary image encoded in 8bit with values [0, 255].

    Args:
        img (ndarray): Input image

    Returns:
        ndarray: Inverted image
    """
    retval = np.zeros_like(img)
    retval[img == 0] = 255
    return retval


class Dice():

    def __init__(self, in_img, center, bbox, value=None):
        """Constructor for the Dice class

        Args:
            in_img (ndarray): Input image
            center (tupple(int)): Center coordinates (x,y)
            bbox (tupple(int)): Bounding box coordinates (top, left, bottom, right)
            value (int, optional): Value of the dice. Defaults to None.
        """

        self.center = center
        self.bbox = bbox
        self.bbox_color = [0, 0, 255]

        self.img = in_img[
            self.bbox[0]:self.bbox[2],
            self.bbox[1]:self.bbox[3]
        ]

        if value is not None:
            self.value = value
        else:
            gray = rgb2gray_uint8(self.img)
            norm = normalize_uint8(gray)
            bin = otsu_uint8(norm)
            inv = invert_uint8(bin)
            cleared = clear_border(inv)
            label_image = label(cleared)

            self.value = len(np.unique(label_image)) - 1

    
    def get_bbox_mask(self, in_img):
        """Returns a mask of the dice's bounding box

        Args:
            in_img (ndarray): input image

        Returns:
            ndarray: mask
        """

        mask = np.zeros_like(in_img, dtype=np.uint8)
        mask[self.bbox[0]:self.bbox[2], self.bbox[1]] = self.bbox_color
        mask[self.bbox[0]:self.bbox[2], self.bbox[3]] = self.bbox_color
        mask[self.bbox[0], self.bbox[1]:self.bbox[3]] = self.bbox_color
        mask[self.bbox[2], self.bbox[1]:self.bbox[3]] = self.bbox_color

        return mask


def detect_dices(frame):
    """Dice detection pipeline.

    Args:
        frame (ndarray): Current frame

    Returns:
        lst[Dice]: list of Dices found on the frame
    """
    gray = rgb2gray_uint8(frame)
    norm = normalize_uint8(gray)
    bin = otsu_uint8(norm)
    cleared = clear_border(bin)
    label_image = label(cleared)

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

    return obj_lst


def dices_bboxes_overlay(frame, obj_lst):
    """Generates an overaly displaying the bounding box and value of
    each dice detected on the current frame.

    Args:
        frame (ndarray): Current frame
        obj_lst (list[Dice]): List of dices detected on the frame

    Returns:
        ndarray: Ouput image
    """
    if len(obj_lst) == 0:
        overlayed = frame.copy()
    else:
        for i, obj in enumerate(obj_lst):
            if i == 0:
                overlayed = cv2.addWeighted(
                    src1=frame,
                    alpha=1,
                    src2=obj.get_bbox_mask(frame),
                    beta=0.5,
                    gamma=0
                )
            else:
                overlayed = cv2.addWeighted(
                    src1=overlayed,
                    alpha=1,
                    src2=obj.get_bbox_mask(frame),
                    beta=0.5,
                    gamma=0
                )
            
            cv2.putText(
                img=overlayed,
                text=str(obj.value),
                org=(obj.bbox[1], obj.bbox[0]-10),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.75,
                color=(0,0,255),
                thickness=1,
                bottomLeftOrigin=False,
            )

    return overlayed