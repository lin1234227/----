
# coding: utf-8



from pyforest import *
import cv2
from PIL import Image
import math
from multiprocessing import Process, Lock
import datetime
import time


# In[2]:


lock = Lock() 
NA_index = []
# In[3]:

# def count_time(func):
#     def wrapper(*args, **kw):
#         local_time = time.time()
#         func(*args, **kw)
#         print('current Function [%s] run time is %.2f' % (func.__name__ ,time.time() - local_time))
#     return wrapper


# @count_time
def rotate_bound(array, angle):
    # 获取图像的尺寸
    # 旋转中心
    (h, w) = array.shape[:2]
    (cx, cy) = (w / 2, h / 2)
    # # 设置旋转矩阵
    M = cv2.getRotationMatrix2D((cx, cy), angle, 1.0)
    return cv2.warpAffine(array, M, (w, h))


# In[4]:

# @count_time
def trans_matrix(tmppath):
    with open(tmppath) as f:
        t = f.readlines()
        temp = t[0].strip().split(' ')
        array = []
        ans = []
        for index,val in enumerate(temp):#320*240
            ans.append(float(val))
            if (index+1)%320==0:
                array.append(ans)
                ans = []
    # print(np.array(array).shape)
    return np.array(array)


# In[5]:

# @count_time
def get_txt_data(txtpath):
    dict1 = {}
    filename = re.sub('.txt','',txtpath.split('/')[-1])
    with open(txtpath) as f:
        t = f.read().split(' ')
        dict1['filename'] = filename
        dict1['a4'] = float(t[2].split(':')[1])
        dict1['height'] = float(t[5].split(':')[1])
        dict1['meantmp'] = float(t[6].split(':')[1])
        dict1['maxtmp'] = float(t[7].split(':')[1])
        dict1['hot_spot_nums'] = int(t[8].split(':')[1])
        dict1['tmp_integral'] = int(t[9].split(':')[1])
    return dict1


# In[6]:

# @count_time
# def fill_NA(x,y,r,array,value):
#     height = array.shape[0]
#     width = array.shape[1]
#     for i in range(width):
#         for j in range(height):
#             if (i - x) ** 2 + (j - y) ** 2 > r**2:
#                 array[j][i] = value
#     return array
def fill_NA(x,y,r,array,value):
    global NA_index
    if len(NA_index)==0:
        rows = array.shape[0]
        cols = array.shape[1]
        for i in range(rows):
            for j in range(cols):
                if (j - x) ** 2 + (i - y) ** 2 > r**2:
                    NA_index.append([i,j])
                    array[i][j] = value
    else:
        for i in NA_index:
            array[i[0],i[1]] = value
    return array


# In[7]:

# @count_time
def split_data(array,r,c):
    #以分4份为例
    dict1 = {}
    rows = array.shape[0] #height 高度
    cols = array.shape[1] #width 宽度
    step_r = rows//r
    step_c = cols//c
    for i in range(r):
        for j in range(c):
            dict1[str(i)+'_'+str(j)]=array[i*step_r:(i+1)*step_r,j*step_c:(j+1)*step_c].mean()
    return dict1


# In[8]:


# E:\data\1207\4
def get_temperature(filepath):
    df = pd.DataFrame()
    # global lock
    tmppath1 = filepath + '/tmp'
    txtpath = filepath+'/txt'
    print(len(os.listdir(tmppath1)))
    for index,filename in enumerate(os.listdir(tmppath1)):
        if index%100==0:
            print('finished {}'.format(index))
        M = trans_matrix(tmppath1+'/'+filename)

        dict1 = get_txt_data(txtpath+'/'+re.sub('.tmp','.txt',filename))
        M = cv2.copyMakeBorder(M[:185,10:310], 135, 0, 0, 0,cv2.BORDER_CONSTANT,value=dict1['meantmp'])#补充上边界

        M = fill_NA(148, 167, 130,M,dict1['meantmp'])

        M = M[167-130:167+130,148-130:148+130]
        angle = dict1['a4']*180/math.pi

        M = rotate_bound(M,-angle)
        print(M.shape)
    #     dict2 = split_data(M,5,5)
    #     dict_merge = dict1.copy()
    #     dict_merge.update(dict2)
    #
    #     df = df.append(dict_merge,ignore_index=True)
    #
    # # lock.acquire()
    # print('-------------'+filepath+'在写入............................')
    # print('{}一共有多少行{}'.format(filepath,len(df)))
    # df.to_csv('./export_data/negative_direction/fillNA-mean/5-5/my_data.csv', mode='a')
    # print('-------------'+filepath+'写入完成!!!!!!!!!!!!!!!!!!!!!!!!!!')

    # lock.release()
        
    return None


        

    


# In[9]:


if __name__ == '__main__':
    processes = []
    path = 'E:/data'
    for i in os.listdir(path):
        for j in os.listdir(path+'/'+i):
            get_temperature(path+'/'+i+'/'+j)
    #         p = Process(target=get_temperature, args=(path+'/'+i+'/'+j,))
    #         processes.append(p)
    #         p.start()
    # print('all in all {} process'.format(len(processes)))
    #
    # for t in processes:
    #     t.join()

