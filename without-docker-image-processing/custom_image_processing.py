import cv2

def processImage(folder_path,image_filename):

    image = cv2.imread(folder_path+"/"+image_filename)
    image = cv2.rectangle(image, (0,0), (30,30), (0,0,255), 3)

    cv2.imwrite(folder_path+"/processed-"+image_filename,image)

