import numpy as np
import cv2


def extrapolate_sudoku(sudoku_image, model_name):
    '''Given a sudoku image and a neural network model, return the sudoku array extracted from the image'''
    # import an already trained model
    from tensorflow.keras.models import load_model
    model = load_model(model_name)

    # open a sudoku image
    image = cv2.imread(sudoku_image, 0)

    # resize the image    
    img_height = image.shape[0]
    img_width = image.shape[1]
    
    if img_height > img_width:
        image = cv2.resize(image, (800, 1000))
    elif img_height < img_width:
        image = cv2.resize(image, (1000, 800))
    else:
        image = cv2.resize(image, (800, 800))

    # manipulate the image so that the digits are recognizable
    blur = cv2.GaussianBlur(image, (13, 13), 0)

    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 7, 2)

    kernel = np.ones((3,3), np.uint8)
    erosion = cv2.erode(thresh, kernel)
    dilatation = cv2.dilate(erosion, kernel)

    invert = cv2.bitwise_not(dilatation)

    # find the largest square contour's coordinates
    contours, hierarchy = cv2.findContours(invert, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_sorted = sorted(contours, key=cv2.contourArea, reverse=True)

    largest_rect_coord = []
    for c in contours_sorted:
        perimeter = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.01 * perimeter, True)
        if len(approx) == 4:
            largest_rect_coord = approx
            cv2.drawContours(image, [approx], 0, (0, 255, 0), 3)
            break

    # return empty sudoku if no contours are found
    if len(largest_rect_coord) == 0 or largest_rect_coord == []:
        empty_sudoku = np.zeros((9, 9), np.int8)
        return empty_sudoku

    largest_rect_coord = largest_rect_coord.reshape(4,2)

    # sort the coordinates
    sum_coord = largest_rect_coord.sum(1)
    diff_coord = np.diff(largest_rect_coord, axis=1)

    pt_A = largest_rect_coord[np.argmin(sum_coord)]
    pt_B = largest_rect_coord[np.argmax(diff_coord)]
    pt_C = largest_rect_coord[np.argmax(sum_coord)]
    pt_D = largest_rect_coord[np.argmin(diff_coord)]

    # calculate L2 norm to find the maximum sides
    width_AD = np.sqrt(((pt_A[0] - pt_D[0]) ** 2) + ((pt_A[1] - pt_D[1]) ** 2))
    width_BC = np.sqrt(((pt_B[0] - pt_C[0]) ** 2) + ((pt_B[1] - pt_C[1]) ** 2))
    maxWidth = max(int(width_AD), int(width_BC))

    height_AB = np.sqrt(((pt_A[0] - pt_B[0]) ** 2) + ((pt_A[1] - pt_B[1]) ** 2))
    height_CD = np.sqrt(((pt_C[0] - pt_D[0]) ** 2) + ((pt_C[1] - pt_D[1]) ** 2))
    maxHeight = max(int(height_AB), int(height_CD))

    input_pts = np.float32([pt_A, pt_B, pt_C, pt_D])
    output_pts = np.float32([[0, 0],
                            [0, maxHeight - 1],
                            [maxWidth - 1, maxHeight - 1],
                            [maxWidth - 1, 0]])

    # warp the image and obtain a square
    transf = cv2.getPerspectiveTransform(input_pts, output_pts)
    warp = cv2.warpPerspective(invert, transf, (maxWidth, maxHeight), flags=cv2.INTER_LINEAR)
    grid = cv2.resize(warp, (252, 252))

    # slice the image of the grid to obtain each cell separately
    cell = np.zeros([9, 9, 28, 28])

    for i in range(9):
        for j in range(9):
            cell[i][j] = grid[0+28*i:28+28*i, 0+28*j:28+28*j]


    # define the sudoku grid array where the recognized digits will be placed
    sudoku_grid = np.zeros((9, 9), np.int8)

    for i in range(9):
        for j in range(9):
            im = cell[i][j]

            # make images binary for contour
            im = cv2.convertScaleAbs(im)

            # find digit contours
            num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(im)

            digit_contour = []    
            for k in range(0, labels.max() + 1):
                im_mask = cv2.compare(labels, k, cv2.CMP_EQ)
                
                cell_contours, hierarchy = cv2.findContours(im_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for c in cell_contours:
                    for pt in c:
                        if np.math.sqrt((pt[0][0] - 14)**2 + (pt[0][1] - 14)**2) < 6: # change the values 6 and 8 if a number is not detected
                            if len(c) > 0 and len(c) <8:
                                continue
                            else:
                                digit_contour = c
                                break
            # check if there is a digit
            if len(digit_contour) == 0 or digit_contour == []:
                sudoku_grid[i][j] = 0
                continue

            # bounding rectangle of the digit
            x, y, w, h = cv2.boundingRect(digit_contour)

            # define a mask to make it all black, except the digit
            mask = np.zeros_like(im)
            mask[y:y + h, x:x + w] = 1

            # clean image with the mask applied
            clean_im = cv2.bitwise_and(im, im, mask=mask)
            
            # image just of the digit
            digit_image = clean_im[y:y + h, x:x + w].copy()

            # before predicting the digit, check if there are at least 5 white pixels in the digit image, otherwise is considered noise
            pixel_threshold = 5
            pixel_count = 0
            for m in range(digit_image.shape[0]):
                for n in range(digit_image.shape[1]):
                    if digit_image[m][n] == 255:
                        pixel_count += 1
            if pixel_count < pixel_threshold:
                sudoku_grid[i][j] = 0
                continue
      
            # define a mnist-like image
            mnist_image = np.zeros((28, 28), np.float)

            # put the digit in the center of the image
            mean_row = int((28 - digit_image.shape[0]) / 2)
            mean_col = int((28 - digit_image.shape[1]) / 2)
            mnist_image[mean_row:mean_row + digit_image.shape[0], mean_col:mean_col + digit_image.shape[1]] = digit_image

            # add dimension to obtain the right shape for the model (1, 28, 28, 1)
            mnist_image = np.expand_dims(mnist_image, axis=0)
            mnist_image = np.expand_dims(mnist_image, axis=3)

            # predict the digit using the model
            digit_prediction = model.predict(mnist_image)
            cell_value = np.argmax(digit_prediction, axis=1)

            # assign the prediction to the sudoku cell
            sudoku_grid[i][j] = cell_value


    return sudoku_grid
