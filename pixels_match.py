
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  8 18:27:01 2018

@author: ambs
"""
import matplotlib.pyplot as plt
import models

# import the necessary packages
import numpy as np
import imutils
import math
#import glob
import cv2
import os
from shutil import copyfile
from wand.image import Image as Img
import wand.image as wandimg
import os
import cv2
import numpy as np
import os
import imageio
#from scipy.misc import imread, imshow, imsave
from scipy.ndimage import rotate
import json
import pytesseract
from PIL import Image
import base64
import requests
import json
from collections import namedtuple
Rectangle = namedtuple('Rectangle', 'xmin ymin xmax ymax')

def area(a, b):  # returns None if rectangles don't intersect
    dx = min(a.xmax, b.xmax) - max(a.xmin, b.xmin)
    dy = min(a.ymax, b.ymax) - max(a.ymin, b.ymin)
    if (dx>=0) and (dy>=0):
        return dx*dy
def takeFirst(elem):
    return elem['x_start']
#image to base64, which is a long long text
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read())

#make api call
def image_request(image_path):
    
    url = "https://vision.googleapis.com/v1/images:annotate"
    
    querystring = {"key":"AIzaSyBB9VeUNjoOjSmn10WbO9aNxEmIHfiCewc"}
    headers = {
            'Content-Type': "application/json",
            }
    payload = '{  \"requests\":[    {      \"image\":{        \"content\":\"'+encode_image(image_path).decode('utf-8')+'"      },      \"features\":[        {          \"type\":\"TEXT_DETECTION\" }      ]    }  ]}'
    response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
                            
    return response.text
def sub_image(image, o,save_path):
    image = cv2.imread(image)

    x_center=(int(o["x"]* 7)+int(o["width"]* 7))/2
    y_center = (int(o["y"]* 7) + int(o["height"]* 7)) / 2
    center=(x_center,y_center)
    theta=int(o["rotate"])
    width=int(o["width"]* 7)
    height=int(o["height"]* 7)

    if 45 < theta <= 90:
        theta = theta - 90
        width, height = height, width

    theta *= math.pi / 180 # convert to rad
    v_x = (math.cos(theta), math.sin(theta))
    v_y = (-math.sin(theta), math.cos(theta))
    s_x = center[0] - v_x[0] * (width / 2) - v_y[0] * (height / 2)
    s_y = center[1] - v_x[1] * (width / 2) - v_y[1] * (height / 2)
    mapping = np.array([[v_x[0],v_y[0], s_x], [v_x[1],v_y[1], s_y]])

    img=cv2.warpAffine(image, mapping, (width, height), flags=cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REPLICATE)
 #   img.save(save_path)
    cv2.imwrite(save_path,img)
    return cv2.warpAffine(image, mapping, (width, height), flags=cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REPLICATE)
    #vc = cv2.VideoCapture(0)
def rotate_(path, angle):
    img = imread(path)

    rotate_img = rotate(img, -90)
    imsave(path, rotate_img)

def resizer_img(path_source,filname_source,path_destination,filname_destination ,scale):
        filname=path_source+filname_source
        print(filname)
        img_rgb = cv2.imread(filname)
        height, width =img_rgb.shape[:2]
        h_scal=int(height/scale)
        w_scal=int(width/scale)
        vvv_thumbnail = cv2.resize(img_rgb, (w_scal, h_scal), interpolation = cv2.INTER_AREA)
        filenamed=path_destination+filname_destination
        cv2.imwrite(filenamed, vvv_thumbnail)
        return filname_destination

def converter_pdf(path_source,pdffilename,path_destination,imgfilename,dpi):

    filename=os.getcwd()+"/"+path_source+pdffilename
    image_name=os.getcwd()+"/"+path_destination+imgfilename
    
    with Img(filename=filename, resolution=dpi) as img:
        img.alpha_channel = 'remove' #close alpha channel   
        img.background_color = wandimg.Color('white')
        img.compression_quality = 99
        
        img.save(filename=image_name)
    return image_name

def found_rectlogo(db,path_main,image,file_name,alpha):
    
    path=os.path.join(path_main,"template_cropped_img_200/")
    count=0
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    result = db.query(models.Template).all()
    listdir=[row.template_path for row in result]

    
#    listdir=os.listdir(path)
#    print(listdir)
    found = None
    for name in listdir:
        template_path=path+name
#    	print(template_path)
#    	template_source = cv2.imread(template_path)
        im1=Image.open(template_path)
        im2=im1.rotate(270, expand=1)
        im1=Image.open(template_path)
        im3=im1.rotate(90, expand=1)

#    	template_source = cv2.imread(template_path)
        template = np.array(im1)
        template270= np.array(im2)
        template90= np.array(im3)

        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        template = cv2.Canny(template_gray, 50, 200)
        (tH, tW) = template.shape[:2]

        (h, w) = (tH, tW)
        
        center = (w / 2, h / 2)
        
        angle90 =90
        scale = 1.0
        template_gray90 = cv2.cvtColor(template90, cv2.COLOR_BGR2GRAY)
        (tH90, tW90) = template90.shape[:2]
        

        angle270 =270
        scale = 1.0
        template_gray270 = cv2.cvtColor(template270, cv2.COLOR_BGR2GRAY)
        (tH270, tW270) = template270.shape[:2]
        
        template90 = cv2.Canny(template_gray90, 50, 200)
        template270 = cv2.Canny(template_gray270, 50, 200)

        # cv2.imshow('images', template90)

        for scale in np.linspace(0.2, 1.0,20)[::-1]:
            #print('scale  ',scale)
            resized = imutils.resize(gray, width = int(gray.shape[1] * scale))
            r = gray.shape[1] / float(resized.shape[1])
            edged = cv2.Canny(resized, 50, 200)
            if resized.shape[0] < tH or resized.shape[1] < tW:
                pass
            else:
                rotate=0
                result = cv2.matchTemplate(edged, template, cv2.TM_CCOEFF)
                (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)

                #print('maxval ===', maxVal)
                if found is None or maxVal > found[0]:
                                found = (maxVal, maxLoc, r,tH, tW,name,rotate)
                           
                            
                            

            if resized.shape[0] < tH90 or resized.shape[1] < tW90:
                pass
            else:
                result = cv2.matchTemplate(edged, template90, cv2.TM_CCOEFF)
                (_, maxVal90, _, maxLoc90) = cv2.minMaxLoc(result)
    
                #print('maxval 270==', maxVal270)
                if  found is None or  maxVal90 > found[0]:
                    rotate=2
                    found = (maxVal90, maxLoc90, r,tH90, tW90,name,rotate)
                    
                    
                    
            if resized.shape[0] < tH270 or resized.shape[1] < tW270:
                pass
            else:
                result = cv2.matchTemplate(edged, template270, cv2.TM_CCOEFF)
                (_, maxVal270, _, maxLoc270) = cv2.minMaxLoc(result)
    
                #print('maxval 270==', maxVal270)
                if  found is None or  maxVal270 > found[0]:
                    rotate=1
                    found = (maxVal270, maxLoc270, r,tH270, tW270,name,rotate)
            # print('print val max=',found[0])
            # print('print name=',found[5])
            # print('print name=',found[6])



     

#################################################################################
#
################################################################################    

    (maxVal, maxLoc, r,tH, tW,name,rotate) = found
    (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
    (endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))
    # print('max==',maxVal) 
        # draw a bounding box around the detected result and display the image
    rect=image[startY:endY,startX:endX]
#    cv2.imwrite('./rect0/{}'.format(name),rect)
#     cv2.imshow('images',rect0)
    cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)
    cv2.imwrite('./{}'.format(name),image)
    rect=image[startY:endY,startX:endX]
    path0=os.path.join(path_main,"check_convert_300/")
    rect_temp=cv2.imread(path0+file_name)
    x0=startX*alpha
    x1=endX*alpha
    y0=startY*alpha
    y1=endY*alpha
    rect0=rect_temp[y0:y1,x0:x1]
    
    # cv2.imwrite('./{}'.format(name),rect0)

    
    
    if rotate==1:
        im_pil0 = Image.fromarray(rect0)
        im_pil0=im_pil0.rotate(90, expand=1)
        rect0 = np.asarray(im_pil0)
    if rotate==2:
        im_pil0 = Image.fromarray(rect0)
        im_pil0=im_pil0.rotate(270, expand=1)
        rect0 = np.asarray(im_pil0)

# For reversing the operation:

    count=count+1    
#    cv2.waitKey(0)
#    return  image,rect,rect0,name
    return  rect0,name

def resize_folder(path_source,path_destination,scale):
    listdir=os.listdir(path_source)
#    bar = Bar('Processing', max=len(listdir))
    for name in listdir:
        if 'jpg' in name:
            resizer_img(path_source,name,path_destination,name,scale)

def get_rect(data_):
#    print(data_)
#    data_=json.loads(data_)
    
    x_start=int(data_['x'])
    y_start=int(data_['y'])
    x_end=x_start+int(data_['width'])
    y_end=y_start+int(data_['height'])
    rotate=int(data_['rotate'])
    return x_start,y_start,x_end,y_end,rotate    

def get_rect_2(data_,scale_h,scale_w):
#    print(data_)
#    data_=json.loads(data_)
    x_start=int(data_['x'])*scale_w
    y_start=int(data_['y'])*scale_w
    x_end=(x_start+int(data_['width']))*scale_h
    y_end=(y_start+int(data_['height']))*scale_h
    rotate=int(data_['rotate'])
    return x_start,y_start,x_end,y_end,rotate



def ocr_google(image):
    

        api_answer = json.loads(image_request(image))
        
        try:
            rows = api_answer['responses'][0]['textAnnotations']

        except:
            print('----Error API Google------------')
            print(api_answer)
        rwd_list=[]

        for k in range(1,len(rows)):
            rw=rows[k]
            rwd_min=rw['boundingPoly']['vertices'][0]
            rwd_max=rw['boundingPoly']['vertices'][2]
            try:
                x_min=rwd_min['x']
            except:
                x_min=0
            try:
                y_min=rwd_min['y']
            except:
                y_min=0
        
            rwd={'x_start':x_min,
                 'y_start':y_min,
                 'x_end':rwd_max['x'],
                 'y_end':rwd_max['y'],
                 'description':rw['description']
                 }
            rwd_list.append(rwd)
            takeFirst
            rwd_list.sort(key=takeFirst)
            
        return rwd_list
            
def text_field(ra_logo,rwd_list):
    description=''
    for rwd in  rwd_list:
           rb_img_process=Rectangle(rwd['x_start'],rwd['y_start'],rwd['x_end'],rwd['y_end'])
           rsl=area(ra_logo, rb_img_process)
           if rsl:
               #print (area(ra_logo, rb_img_process))
               #print(rwd['description'])
               description=description+rwd['description']+' '
    return description            
def ocr(image,path_main,psm):

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        

        kernel = np.ones((2, 2), np.uint8)
        img = cv2.dilate(gray, kernel, iterations=1)
        img = cv2.erode(img, kernel, iterations=1)
        filename = "{}.png".format(os.getpid())
        cv2.imwrite(path_main+'/'+str(filename), img)
        tessdata_dir_config = '--oem 3 --psm {} --c tessedit_char_whitelist=01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz@ß€!$%&/()=?+-.,;:<>'.format(psm)

        text = pytesseract.image_to_string(Image.open(path_main+'/'+str(filename)),lang='eng', config=tessdata_dir_config)
        return text

def get_data(db,path_main,rect0,name0,file_name,ds=0):
        profile_ocr={}
        profile_ocr['text']=[]
        profile_ocr['text'].append({}) 

        # # path_json = os.path.join(path_main, "rlogo/")
        # path_logo = os.path.join(path_main, "template_cropped_img_300/")
        # path_img = os.path.join(path_main, "template_cropped_img_300/")
        image_path=path_main+"queues_pdf_cropped/"+file_name.replace(".pdf",".jpg")
        status = cv2.imwrite(image_path,rect0)
        # print("Image written to file-system : ",status)
        
        # file_json=name0.replace('jpg','json')
        # file_json=path_json+file_json
        # file_logo=file_json.replace('json','jpg').replace('rlogo','croped_img')

        file_logo=path_main+'template_cropped_img_300/'+name0
        print(name0)
        logo= cv2.imread(file_logo)


        w0,h0=logo.shape[:2]        
        w1,h1=rect0.shape[:2]
        scale_w=(w1/w0)
        scale_h=(h1/h0)

        result = db.query(models.Template).filter(models.Template.template_path==name0).first()
        print(name0,"rrrrrrrr")

        data= result.label_json
        
        
#        with open(file_json) as datafile:
#                data = json.load(datafile)
                
        
        rwd_list=ocr_google(image_path)
        
        label=data['title']  
        x_start,y_start,x_end,y_end,rotate=get_rect_2(label,scale_h,scale_w) 
        ra_logo = Rectangle(x_start,y_start,x_end,y_end)
        title_text=text_field(ra_logo,rwd_list)
        
        
        cv2.rectangle(rect0, (int(x_start*scale_w), int(y_start*scale_h+ds)), (int(x_end*scale_w), int(y_end*scale_h)), (0, 0, 255), 2)
       
        # print('title_text=',title_text)
        # img_title=image[int(y_start*scale_h+ds):int(y_end*scale_h),int(x_start*scale_w):int(x_end*scale_w)]
        # cv2.imwrite(path_main+'/title.jpg',img_title)

        label=data['drawing_number']  
        x_start,y_start,x_end,y_end,rotate=get_rect_2(label,scale_h,scale_w) 
        ra_logo = Rectangle(x_start,y_start,x_end,y_end)
        drawingN_text=text_field(ra_logo,rwd_list)
        print('img_drawingN=',drawingN_text)
        cv2.rectangle(rect0, (int(x_start*scale_w), int(y_start*scale_h+ds)), (int(x_end*scale_w), int(y_end*scale_h)), (0, 255, 0), 2)

        # img_drawingN=image[int(y_start*scale_h+ds):int(y_end*scale_h),int(x_start*scale_w):int(x_end*scale_w)]
        # cv2.imwrite(path_main+'/drawing_number.jpg',img_drawingN)
        
        label=data['revision']
        x_start,y_start,x_end,y_end,rotate=get_rect_2(label,scale_h,scale_w) 
        ra_logo = Rectangle(x_start,y_start,x_end,y_end)
        revsion_text=text_field(ra_logo,rwd_list)
        print('revsion =',revsion_text)
        cv2.rectangle(rect0, (int(x_start*scale_w), int(y_start*scale_h+ds)), (int(x_end*scale_w), int(y_end*scale_h)), (255, 0, 0), 2)

        # img_revsion=image[int(y_start*scale_h+ds):int(y_end*scale_h),int(x_start*scale_w):int(x_end*scale_w)]
        # cv2.imwrite(path_main+'/revision.jpg',img_revsion)


        label=data['project_name']
        x_start,y_start,x_end,y_end,rotate=get_rect_2(label,scale_h,scale_w) 
        ra_logo = Rectangle(x_start,y_start,x_end,y_end)
        project_name_text=text_field(ra_logo,rwd_list)
        print('project_name =',project_name_text)
        cv2.rectangle(rect0, (int(x_start*scale_w), int(y_start*scale_h+ds)), (int(x_end*scale_w), int(y_end*scale_h)), (0, 255, 255), 2)

        # project_name=image[int(y_start*scale_h+ds):int(y_end*scale_h),int(x_start*scale_w):int(x_end*scale_w)]
        # cv2.imwrite(path_main+'/project_name.jpg',project_name)      
        
        
        
        cv2.imwrite('main.jpg',rect0)
        profile_ocr['text'][0]['Title']=title_text
        profile_ocr['text'][0]['drawingN']=drawingN_text
        profile_ocr['text'][0]['revsion']=revsion_text
        profile_ocr['text'][0]['project_name']=project_name_text

        total_data=(json.dumps(profile_ocr,indent=4,ensure_ascii=False))
        
        return total_data

def process_image(path_source,pdffilename,path_destination0):
    path_source = './static/img/check/'
    # path_destination0 = './static/img/check_convert_300/'
    path_destination1 = './static/img/check_convert_200/'
    # pdffilename = '00.pdf'
    imgfilename = pdffilename.replace('pdf', 'jpg')
    alpha = 7
    dpi = 300
    # data = process_image(path_destination1, imgfilename, alpha)
    file_name_img=path_destination1+imgfilename
    img_rgb=cv2.imread(file_name_img)
    image=img_rgb
    file_name=	imgfilename
    image,rect,rect0,name0=found_rectlogo(img_rgb,imgfilename,alpha)
    print(name0)
#    image=found_rectlogo(img_rgb,name)
    
    json_data=get_data(rect0,name0)
    print(json_data)
    return json_data


# #
# path_source='./static/img/check/'
# path_destination0='./static/img/check_convert_300/'
# path_destination1='./static/img/check_convert_200/'
#
# #    path_source='C:/Users/benna/OneDrive/Bureau/Drawapp/static/img/check/'
#
# pdffilename='00.pdf'
# #    path_destination='C:/Users/benna/OneDrive/Bureau/Drawapp/static/img/check_convert/'
# imgfilename=pdffilename.replace('pdf','jpg')
# alpha=7
# dpi=300
# filname=converter_pdf(path_source,pdffilename,path_destination0,imgfilename,dpi)
#
# resizer_img(path_destination0,imgfilename,path_destination1,imgfilename ,alpha)
# data=process_image(path_destination1,imgfilename,alpha)
# print(data)
