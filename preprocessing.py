import cv2
import numpy as np


# In[1]:
# Image Processing

def thresh(img, thresh=(0, 255)):
    binary = np.zeros_like(img)
    binary[(img > thresh[0]) & (img <= thresh[1])] = 1
    return binary

def colorthresh(img):
    r_channel = img[:, :, 2]
    r_thresh = thresh(r_channel, thresh=(200, 255))
    hls = cv2.cvtColor(img, cv2.COLOR_RGB2HLS)
    s_channel = hls[:, :, 2]
    s_thresh = thresh(s_channel, thresh=(160, 255))
    color_combined = np.zeros_like(s_thresh)
    color_combined[((r_thresh == 1) | (s_thresh == 1))] = 1
    return color_combined
    # return s_thresh

def abs_sobel_thresh(img, orient='x', thresh_min=0, thresh_max=255):
    img = cv2.cvtColor(img, cv2.COLOR_RGB2HLS)
    img = img[:, :, 2]
    if orient == 'x':
        sobel = cv2.Sobel(img, cv2.CV_64F, 1, 0, 7)
    else:
        sobel = cv2.Sobel(img, cv2.CV_64F, 0, 1, 7)
    abs_sobel = np.absolute(sobel)
    scaled_sobel = np.uint8(255 * abs_sobel / np.max(abs_sobel))
    sbinary = np.zeros_like(scaled_sobel)
    sbinary[(scaled_sobel >= thresh_min) & (scaled_sobel <= thresh_max)] = 1
    return sbinary


def mag_thresh(img, kernel=7, mag_thresh=(40, 255)):
    img = cv2.cvtColor(img, cv2.COLOR_RGB2HLS)
    img = img[:, :, 2]
    sobelx = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=kernel)
    sobely = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=kernel)
    gradmag = np.sqrt(sobelx ** 2 + sobely ** 2)
    scale_factor = np.max(gradmag) / 255
    gradmag = (gradmag / scale_factor).astype(np.uint8)
    binary_output = np.zeros_like(gradmag)
    binary_output[(gradmag >= mag_thresh[0]) & (gradmag <= mag_thresh[1])] = 1
    return binary_output


def dir_threshold(img, kernel=7, thresh=(0.65, 1.05)):
    img = cv2.cvtColor(img, cv2.COLOR_RGB2HLS)
    img = img[:, :, 2]
    sobelx = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=kernel)
    sobely = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=kernel)
    absgraddir = np.arctan2(np.absolute(sobely), np.absolute(sobelx))
    binary_output = np.zeros_like(absgraddir)
    binary_output[(absgraddir >= thresh[0]) & (absgraddir <= thresh[1])] = 1
    return binary_output


def gradthresh(img):
    img = cv2.GaussianBlur(img, (5, 5), 0)
    gradx = abs_sobel_thresh(img, orient='x', thresh_min=10, thresh_max=255)
    grady = abs_sobel_thresh(img, orient='y', thresh_min=60, thresh_max=255)

    mag_binary = mag_thresh(img)
    dir_binary = dir_threshold(img)

    grad_combined = np.zeros_like(dir_binary)
    grad_combined[((gradx == 1) & (grady == 1)) | ((mag_binary == 1) & (dir_binary == 1))] = 1

    return grad_combined


def combinethresh(grad_thresh, color_thresh):
    combined_color_grad = np.zeros_like(grad_thresh)
    combined_color_grad[(grad_thresh == 1) | (color_thresh == 1)] = 1
    return combined_color_grad


def region_of_interest(img, vertices):
    mask = np.zeros_like(img)
    ignore_mask_color = 255
    cv2.fillPoly(mask, vertices, ignore_mask_color)
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image


def warp_image(img, src, dst, img_size):
    M = cv2.getPerspectiveTransform(src, dst)
    Minv = cv2.getPerspectiveTransform(dst, src)
    warped = cv2.warpPerspective(img, M, img_size, flags=cv2.INTER_LINEAR)

    return warped, M, Minv
