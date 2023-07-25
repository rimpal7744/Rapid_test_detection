from paddleocr import PaddleOCR
import numpy as np
import cv2
import easyocr
from line_extraction import detecting_line
ocr = PaddleOCR(use_angle_cls=True, lang='en',enable_mkldnn=True)
#getting closest label from line coordinates
def closest(lst, K):
    new_list=[]
    for l in lst:
        value=l-K
        if (value)<-50:
            value=value-1000
        new_list.append(abs(value))
    minpos = new_list.index(min(new_list))
    return lst[minpos]

def get_labels(image,coordinates):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    alpha = 1  # Contrast control (1.0-3.0)
    beta = 0  #0 Brightness control (0-100)
    adjusted = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    reader = easyocr.Reader(['en'])  # this needs to run only once to load the model into memory
    result = reader.readtext(adjusted,text_threshold=0.5,batch_size=5)
    actual_list=[]
    for r in result:
        actual_list.append(r[0][2][1])
    mydict={}
    data_points=['C','T','G','M','PV','PF','PAN','1','2','6','8']
    closest_number_list=[]
    for coordinate in coordinates:
        number=closest(actual_list,coordinate)
        closest_number_list.append(number)
    all_keys=[]
    for r in result:
        key_value = r[1]
        if key_value == '6':
            key_value = 'G'
        if key_value=='8' or '8' in key_value:
            key_value='M'
        if key_value=='UF':
            key_value='Pf'
        #mark labels yes or no based on condition checking with closest number list
        if r[0][2][1] in closest_number_list:
            if key_value.upper() in data_points:
                mydict[key_value]="YES"
                all_keys.append(key_value)
        elif r[0][2][1] not in closest_number_list:
            if key_value.upper() in data_points:
                mydict[key_value]='NO'
                all_keys.append(key_value)
    if len(all_keys)==2 and ('C' in all_keys) and ('2' in all_keys):
        mydict['1']='NO'
    if len(all_keys)==1:
        mydict={}

    return mydict

#main function to extract ROI and labels
def main(file):
    image=cv2.imread(file)
    pix = np.array(image)
    result = ocr.ocr(pix, cls=True)
    result = result[0]
    #Getting region of interest
    for r in result:
        if r[1][0]=='Q-Line' or r[1][0]=='Q-line':
            x1=r[0][0][0]
            y1=r[0][0][1]
            x2=r[0][2][0]
            y2=r[0][2][1]

    roi=image[int(y1)+450:int(y2)+1250,int(x1):int(x2)]
    roi2=image[int(y1)+450:int(y2)+1250,int(x1):int(x2)+500]
    # Method for detecting lines in ROI
    coordinates=detecting_line(roi)
    # Extracting and Matching labels from ROI
    final_result=get_labels(roi2,coordinates)

    return final_result



