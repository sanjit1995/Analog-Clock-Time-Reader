import cv2 as cv
import numpy as np
import math

def nothing(x):
    pass


def hough_transform():
    # Choose an image
    filename = 'data/19.jpg'

    # Loads an image
    img = cv.imread(cv.samples.findFile(filename), cv.IMREAD_COLOR)
    img = cv.resize(img, (600, 540))
    cv.imshow("Original Image", img)

    # Check if image is loaded fine
    if img is None:
        print('Error opening image!')
        print('Usage: hough_circle.py [image_name -- default ' + filename + '] \n')
        return -1

    # Convert it to gray_img
    gray_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    kernel = np.ones((3, 3), np.uint8)
    gray_img = cv.dilate(gray_img, kernel, iterations=1)

    # Reduce the noise to avoid false circle detection
    gray_img = cv.medianBlur(gray_img, 5)
    # cv.imshow("blurred", gray_img)

    # define a mask which is basically a black filled image of the same size as that of the image
    # used to create a background for the clock
    height, width = gray_img.shape
    mask = np.zeros((height, width), np.uint8)

    # create Hough-Circles, make sure that only the biggest circle is selected
    rows = gray_img.shape[0]
    circles = cv.HoughCircles(gray_img, cv.HOUGH_GRADIENT, 1, rows / 8,
                               param1=100, param2=50,
                               minRadius=200, maxRadius=275)

    # draw circle outlines
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            # find the radius and center of the circle found
            center = (i[0], i[1])
            radius = i[2]

            # Draw on mask a white filled circle
            cv.circle(mask, center, radius, (255, 255, 255), -1)

            # do a bitwise_and which will only make the
            masked_data = cv.bitwise_and(gray_img, gray_img, mask=mask)

            # Apply Threshold
            _, thresh = cv.threshold(mask, 1, 255, cv.THRESH_BINARY)

            # Find Contour
            cnt = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)[0]

            # get co-ordinates (contours)
            x, y, w, h = cv.boundingRect(cnt[0])

            # Crop masked_data
            crop_img = masked_data[y:y + h, x:x + w]

    # display images
    # cv.imshow('original image', img)
    # cv.imshow("cropped clock image", crop_img)
    # cv.waitKey(0)

    return crop_img


def line_transform(crop_img):
    # use canny edge detection to get the edges
    canny_img = cv.Canny(crop_img, 75, 150)
    cdst = cv.cvtColor(canny_img, cv.COLOR_GRAY2BGR)

    # Probabilistic Line Transform
    linesP_img = cv.HoughLinesP(canny_img, 1, np.pi / 180, 50, None, 70, 5)

    # Draw the lines
    if linesP_img is not None:
        k1 = 0
        for i in linesP_img:
            l = i[0]
            length = math.sqrt(abs((l[2]-l[0])**2 + (l[3]-l[1])**2))
            k2 = k1
            for j in linesP_img[k1:]:
                l1 = j[0]
                comparison = l1 == l
                equal_arrays = comparison.all()
                if equal_arrays:
                    k2 += 1
                    continue
                else:
                    length_1 = math.sqrt(abs((l1[2] - l1[0])**2 + (l1[3] - l1[1])**2))
                    if abs(length_1 - length) < 10:
                        # Delete the lines which are of same length, which could be two lines of the same hand of the clock
                        if length > length_1:
                            linesP_img = np.delete(linesP_img, k2, 0)
                            k2 -= 1
                        else:
                            linesP_img = np.delete(linesP_img, k1, 0)
                            k1 -= 1
                            break
                k2 += 1
            k1 += 1

    # Find the maximum and minimum lengths of the hands present
    if len(linesP_img) is not None:
        max_length = 0
        minute_hand = []
        min_length = math.sqrt(abs((linesP_img[0][0][2] - linesP_img[0][0][0]) ** 2 + (linesP_img[0][0][3] - linesP_img[0][0][1]) ** 2))
        hour_hand = []
        for i in range(0, len(linesP_img)):
            l2 = linesP_img[i][0]
            p1_2 = (l2[0], l2[1])
            p2_2 = (l2[2], l2[3])
            length_1 = math.sqrt(abs((l2[2] - l2[0]) ** 2 + (l2[3] - l2[1]) ** 2))
            if length_1 > max_length:
                max_length = length_1
                minute_hand = l2
            if length_1 < min_length:
                min_length = length_1
                hour_hand = l2

    # Save only the hands of the clock with minimum and maximum lengths as minute_hand and hour_hand
    linesP_img_final = [minute_hand, hour_hand]

    angles = []
    print(linesP_img_final)

    # If the clock has 2 detected separate lines for the two hands
    if len(linesP_img_final) == 2 and len(linesP_img_final[0]) > 0 and len(linesP_img_final[1]) > 0:
        for i in range(0, len(linesP_img_final)):
            l3 = linesP_img_final[i]
            p1_3 = (l3[0], l3[1])
            p2_3 = (l3[2], l3[3])
            dy = l3[3] - l3[1]
            dx = l3[2] - l3[0]
            angle1 = angle = 0
            if dy == 0 and dx < 0:
                angle = 0
            if dy == 0 and dx > 0:
                angle = 180
            if dy > 0 and dx == 0:
                angle = -90
            if dy < 0 and dx == 0:
                angle = 90
            if dy != 0 and dx != 0:
                angle1 = math.degrees(math.atan(dy / dx))
            if (abs((cdst.shape[0]/2) - l3[0]) < abs((cdst.shape[0]/2) - l3[2])) or (abs((cdst.shape[1]/2) - l3[1]) < abs((cdst.shape[1]/2) - l3[3])):
                angle = -angle1
            else:
                if dy > 0:
                    angle = 180 - angle1
                if dy < 0:
                    angle = -180 - angle1
            angles.append(angle)
            cv.line(cdst, p1_3, p2_3, (0, 100, 200), 2, cv.LINE_AA)
    else:
        print("Image detection error, please check parameters")
        l3 = linesP_img_final[0]
        p1_3 = (l3[0], l3[1])
        p2_3 = (l3[2], l3[3])
        dy = l3[3] - l3[1]
        dx = l3[2] - l3[0]
        angle1 = 0
        if dy == 0 and dx < 0:
            angle1 = 0
        if dy == 0 and dx > 0:
            angle1 = 180
        if dy > 0 and dx == 0:
            angle1 = -90
        if dy < 0 and dx == 0:
            angle1 = 90
        if dy != 0 and dx != 0:
            angle1 = math.degrees(math.atan(dy / dx))
        hour_angle = -angle1
        if dy > 0:
            minute_angle = 180 - angle1
        if dy < 0:
            minute_angle = -180 - angle1
        angles = [hour_angle, minute_angle]
        print(angles)
        cv.line(cdst, p1_3, p2_3, (0, 100, 200), 2, cv.LINE_AA)

    cv.imshow("Detected Lines (in red) - Probabilistic Line Transform", cdst)
    return angles

def getTime(angles):
    minute_angle = angles[0]
    hour_angle = angles[1]
    minutes_temp = 0
    hours = ""
    if 0 <= minute_angle <= 90:
        minutes_temp = round(15 - ((1/6) * minute_angle))
    if 90 < minute_angle <= 180:
        minutes_temp = round(60 - ((1/6) * (minute_angle - 90)))
    if -180 < minute_angle < -90:
        minutes_temp = round(30 + ((1 / 6) * ((-1 * minute_angle) - 90)))
    if -90 <= minute_angle < 0:
        minutes_temp = round(15 + ((1 / 6) * (-1 * minute_angle)))

    minutes = str(minutes_temp)
    if minutes_temp < 10:
        minutes = "0" + minutes

    # Define the hours based on the range of the angle created by the hour_hand
    if 0 < hour_angle <= 30:
        hours = "02"
    if 30 < hour_angle <= 60:
        hours = "01"
    if 60 < hour_angle <= 90:
        hours = "12"
    if 90 < hour_angle <= 120:
        hours = "11"
    if 120 < hour_angle <= 150:
        hours = "10"
    if 150 < hour_angle <= 180:
        hours = "09"
    if -180 < hour_angle <= -150:
        hours = "08"
    if -150 < hour_angle <= -120:
        hours = "07"
    if -120 < hour_angle <= -90:
        hours = "06"
    if -90 < hour_angle <= -60:
        hours = "05"
    if -60 < hour_angle <= -29:
        hours = "04"
    if -29 < hour_angle <= 0:
        hours = "03"

    # Print the time
    print("Time : " + hours + ":" + minutes)
    cv.waitKey(0)

if __name__ == "__main__":
    crop_img = hough_transform()
    angles = line_transform(crop_img)
    getTime(angles)