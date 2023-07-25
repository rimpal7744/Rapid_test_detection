import cv2
import numpy as np

# returns direction of gradient
# 1 if positive, -1 if negative, 0 if flat
def getDirection(one, two):
    dx = two - one
    if dx == 0:
        return 0
    if dx > 0:
        return 1
    return -1


# detects and returns peaks and valleys
def mountainClimber(vals, minClimb):
    # init trackers
    last_valley = vals[0]
    last_peak = vals[0]
    last_val = vals[0]
    last_dir = getDirection(vals[0], vals[1])

    # get climbing
    peak_valley = []  # index, height, climb (positive for peaks, negative for valleys)
    for a in range(1, len(vals)):
        # get current direction
        sign = getDirection(last_val, vals[a])
        last_val = vals[a]

        # if not equal, check gradient
        if sign != 0:
            if sign != last_dir:
                # change in gradient, record peak or valley
                # peak
                if last_dir > 0:
                    last_peak = vals[a]
                    climb = last_peak - last_valley
                    climb = round(climb, 2)
                    peak_valley.append([a, vals[a], climb])
                else:
                    # valley
                    last_valley = vals[a]
                    climb = last_valley - last_peak
                    climb = round(climb, 2)
                    peak_valley.append([a, vals[a], climb])

                # change direction
                last_dir = sign

    # filter out very small climbs
    filtered_pv = []
    for dot in peak_valley:
        if abs(dot[2]) > minClimb:
            filtered_pv.append(dot)
    return filtered_pv


# run an mean filter over the graph values
def meanFilter(vals, size):
    fil = []
    filtered_vals = []
    for val in vals:
        fil.append(val)
        # check if full
        if len(fil) >= size:
            # pop front
            fil = fil[1:]
            filtered_vals.append(sum(fil) / size)
    return filtered_vals


# averages each row (also gets graph values while we're here)
def smushRows(img):
    vals = []
    h, w = img.shape[:2]
    for y in range(h):
        ave = np.average(img[y, :])
        img[y, :] = ave
        vals.append(ave)
    return vals


# linear reframe [min1, max1] -> [min2, max2]
def reframe(img, min1, max1, min2, max2):
    copy = img.astype(np.float32)
    copy -= min1
    copy /= (max1 - min1)
    copy *= (max2 - min2)
    copy += min2
    return copy.astype(np.uint8)


def detecting_line(image):
    all_y=[]
    # load image
    img=image
    # resize
    scale = 2
    h, w = img.shape[:2]
    h = int(h * scale)
    w = int(w * scale)
    img = cv2.resize(img, (w, h))

    # lab colorspace
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    # stretch contrast
    low = 120
    high = np.max(a)
    # if high<160:
    #     high=170
    # low = np.array([0,50,50])
    # high = np.array([10,255,255])
    a = reframe(a, low, high, 0, 255)

    # smush and get graph values
    vals = smushRows(a)

    # filter and round values
    mean_filter_size = 20
    filtered_vals = meanFilter(vals, mean_filter_size)
    for ind in range(len(filtered_vals)):
        filtered_vals[ind] = round(filtered_vals[ind], 2)
    # get peaks and valleys
    pv = mountainClimber(filtered_vals, 8)

    # pull x and y values
    pv_x = [ind[0] for ind in pv]
    pv_y = [ind[1] for ind in pv]

    # find big peaks
    big_peaks = []
    for dot in pv:
        if dot[2] > 20:  # climb filter size
            big_peaks.append(dot)
    print(big_peaks)


    # Getting Y axis of detected lines
    h, w = img.shape[:2]
    for dot in big_peaks:
        y = int(dot[0] + mean_filter_size / 2.0)  # adjust for mean filter cutting
        all_y.append(y/2)
        cv2.line(img, (367, y), (w, y), (100, 200, 0), 2)

    return all_y

