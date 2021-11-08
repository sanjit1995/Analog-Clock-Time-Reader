## Analog Clock Time Reader

1) For better results please download images from https://toytheater.com/clock/
2) Image file to be provided in the run() function.
   E.g. run("../data/123.jpg")
3) The run() returns time detected (String).


Explanation :

1) The sample image is first resized to a general shape (600, 540). It is then converted to grayscale for further operations.
2) A 3X3 kernel is used to dilate the image. The purpose of dilation is to sharpen the hands of clock and blur out the second hand of the clock (if present).
3) Median Blur is done to remove the noise out and to remove irrelevant circles if any.
4) A black background mask is created for later purposes.
5) This only detects the clocks which are circular in shape. It is done by using Hough Circle Transform.
6) The parameters of Hough Circle Transform are selected in such a way as to select the biggest circle.
7) A white circle of same radius and center is drawn on the black background. The extracted clock then overlaps the white part.
8) The clock is now in a black background. Contours are used to extract the circle inscribed in the biggest quadrilateral possible.
9) Canny edge detection is used to determine the edges.
10) Probabilistic Hough Line Transform is performed on the canny image to detect lines which are the hands of the clock. It returns the co-ordinates of both the ends of a line.
11) The lines which are of the same lengths are deleted as it could be both the edges of a hand.
12) In the end only the hands with longest and shortest distance are selected as the Minute Hand and Hour Hand respectively.
13) The co-ordinates of the ends the lines are used to calculate the angles. The default origin given by the Hough Transform is located on the top-left corner of any image.
14) Thus, the X-axis runs from origin towards the right and Y-axis runs from origin towards bottom.
15) For the purpose of this project, the origin is chosen to be somewhere in the middle of the project(we'll call this makeshift origin 'O' and the plane as makeshift co-ordinate plane). This provides us with unique angles for different orientations.
16) So, the origin is shifted and the co-ordinate plane is rotated as well. Adjustments are made to the angles calculated.
17) Angles are calculated between the two ends of the line by using trigonometric tan() inverse function. The order in which co-ordinates returned are used for this very purpose.
18) The order of the co-ordinates returned by the function are can be visualized as if we are walking along the X-axis.
19) The co-ordinate which is close to our makeshift origin(O) is used to determine which quadrant on the makeshift plane it belongs to.
    E.g. Suppose, the centre of the clock is at (25, 25).
         When the minute-hand is at 2 the co-ordinates are [(24, 28), (45, 13)]. Thus, point 1 is closer to the origin than point 2.
         In the original plane, this line will lie on the 4th Quadrant but in our makeshift plane it should lie on the 1st Quadrant.
         Thus, the angle needs to be modified accordingly.

         When the minute-hand is at 8 the co-ordinates are [(5, 41), (24, 28)]. Thus, point 2 is closer to the origin than point 1.
         In the original plane, this line will lie on the 4th Quadrant but in our makeshift plane it should lie on the 3rd Quadrant.
         Thus, the angle needs to be modified accordingly.
20) The slope is also used to visualize more specific scenarios and the angles are calculated.
21) In special cases where the Minute-Hand and the Hour-Hand coincide, the Hour-Hand might not get detected at all. Thus, the same hand is taken to be Hour-Hand and Minute-Hand.
22) The angles are then used to determine the Hour-Hand position and the Minute-Hand position in the clock.
23) The time is then returned.

References:

1) https://www.cs.bgu.ac.il/~ben-shahar/Teaching/Computational-Vision/StudentProjects/ICBV151/ICBV-2015-1-ChemiShumacher/Report.pdf
2) https://docs.opencv.org/2.4/modules/imgproc/doc/imgproc.html
