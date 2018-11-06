import cv2
import numpy as np
class Scenograph:
    '''
     This module is work at scenopragh:
        init
            Input:
                    depth         Distance from perspective to background wall                  type    int/float
                    width         The width of  background wall                                 type    int/float
                    VPtoleft      Distance from Vanishing point to background wall's lefe line  type    int/float
                    size          Picture size                                                  type    tuple (int,int)     default=(1920,1080)
                    dpieverymeter How much DPI everymerter in the background                    type    int                 default=50
                    heigh         Background height                                             type    int                 default=3
                    HL            Height of the horizon                                         type    float/int           default=1.2
                    outsize       Picture size of output                                        type    tuple (int,int)     default=(960,540)
        To draw Scenograph
            Input:
                    name          Picture name                                                  type    str
    '''
    def __init__(self,depth,width,VPtoleft,size=(1920,1080),dpieverymeter=50,heigh=3,HL=1.2,outsize=(960,540)):
        self.depth=depth
        self.width=width
        self.dpievermeter=dpieverymeter
        self.VPtoleft=VPtoleft
        self.heigh=heigh
        self.HL=HL
        self.size=size
        self.outsize=outsize
        self.vpx=int(self.size[0]/2)
        self.vpy=int(self.size[1]/2)
        self.vp=(self.vpx,self.vpy)
        self.left=int(self.vpx-self.VPtoleft*self.dpievermeter)
        self.right=int(self.vpx+(self.width-self.VPtoleft)*self.dpievermeter)
        self.top=int(self.vpy-(self.heigh-self.HL)*self.dpievermeter)
        self.bottom=int(self.vpy+self.HL*self.dpievermeter)
        self.lefttop=(self.left,self.top)
        self.rightbottom=(self.right,self.bottom)
        self.leftbottom=(self.left,self.bottom)
        self.righttop=(self.right,self.top)
        #初始化画薄
        self.canvas = np.zeros((self.size[1],self.size[0], 3), dtype="uint8")
        self.canvas[:] = [255, 255, 255]
    # function of two point in line    return k ,b
    def lineequation(self,point1,point2):
        if point2[0]-point1[0]==0:
            return None,point1[0]
        else:
            k=(point2[1]-point1[1])/(point2[0]-point1[0])
            b=point2[1]-k*point2[0]
            return k,b
    # function of find a Border junction point return x0,y0
    def findborderpoint(self,k,b,type):
        y0=b #纵轴截距
        x0=-b/k #横轴截距
        if type=='lefttop':
            if y0>0 and x0<0:
                return 0,int(y0)
            elif x0>0 and y0 <0:
                return int(x0),0
            else:
                return 0,0
        elif type=='leftbottom':
            y0=b
            x0=(self.size[1]-b)/k
            if y0<self.size[1] :
                return  0,int(y0)
            elif y0>self.size[1]:
                return int(x0),self.size[1]
            else:
                return 0,self.size[1]
        elif type=='righttop':
            y0=k*self.size[0]+b

            if x0<self.size[0]:
                return int(x0),0
            elif x0>self.size[0]:
                return self.size[0],int(y0)
            else:
                return self.size[0],0
        elif type=='rightbottom':
            y0=k*self.size[0]+b
            x0=(self.size[1]-b)/k
            if y0>self.size[1]:
                return self.size[1],int(y0)
            elif y0<self.size[1]:
                return int(x0),self.size[1]
            else:
                return self.size[0],self.size[1]
    #function of Two line intersecting return x0,y0
    def findintersection(self, k1, b1, k2, b2):
        if k1!=k2:
            x0 = (b2 - b1) / (k1 - k2)
            y0 = k1 * x0 + b1
            return int(x0), int(y0)
        else:
            return None
    #function of show scenopragh    show image in new windows
    def scenoshow(self,name):

        black = [0,0,0]
        #绘制后地面和灭点
        cv2.rectangle(self.canvas,self.lefttop,self.rightbottom,black)
        cv2.circle(self.canvas, (int(self.vpx), int(self.vpy)),2, (0,0,255))
        #确定并绘制四面交接线
        k1,b1=self.lineequation(self.lefttop,self.vp)
        pox,poy=self.findborderpoint(k1,b1,'lefttop')
        cv2.line(self.canvas,self.lefttop,(pox,poy),black)
        k2, b2 = self.lineequation(self.righttop, self.vp)
        pox, poy = self.findborderpoint(k2, b2, 'righttop')
        cv2.line(self.canvas, self.righttop, (pox, poy), black)
        k3, b3 = self.lineequation(self.leftbottom, self.vp)
        poxz, poyz = self.findborderpoint(k3, b3, 'leftbottom')
        cv2.line(self.canvas, self.leftbottom, (poxz, poyz), black)
        k4, b4 = self.lineequation(self.rightbottom, self.vp)
        pox, poy = self.findborderpoint(k4, b4, 'rightbottom')
        cv2.line(self.canvas, self.rightbottom, (pox, poy), black)

        nx=self.left-self.depth*self.dpievermeter
        ny=self.bottom
        k,b = self.lineequation((nx,ny),(poxz,poyz))
        #根据反距法确定辅助点
        self.ax=int((self.vpy-b)/k)
        self.ay=self.vpy
        #存放方格线边点的列表
        listz=[]
        #绘制辅助线确立单位坐标大小
        for i in range(1,int(self.depth)+1):
            nx=self.left-i*self.dpievermeter
            ny=self.bottom
            k,b=self.lineequation((nx,ny),(self.ax,self.ay))
            x1,y1=self.findintersection(k,b,k3,b3)
            listz.append((x1,y1))
            cv2.line(self.canvas,(self.ax,self.ay),(x1,y1),(255,0,0),2)
        #绘制四面的横条方格线
        for z in listz[-int(self.depth):]:
            xn=int((z[1]-b4)/k4)
            cv2.line(self.canvas,(z[0],z[1]),(xn,z[1]),(0,255,0),2)
            listz.append((xn,z[1]))
        for l in listz[-int(self.depth):]:
            yn=int(l[0]*k2+b2)
            cv2.line(self.canvas,(l[0],l[1]),(l[0],yn),(0,0,255),2)
            listz.append((l[0],yn))
        for z in listz[-int(self.depth):]:
            xn=int((z[1]-b1)/k1)
            cv2.line(self.canvas,(z[0],z[1]),(xn,z[1]),(155,155,155),2)
            listz.append((xn,z[1]))
        for l in listz[-int(self.depth):]:
            yn=int(l[0]*k3+b3)
            cv2.line(self.canvas,(l[0],l[1]),(l[0],yn),(200,200,200),2)
        #绘制竖条方格线
        for levelwidth in range(1,int(self.width)):
                x=int(self.left+levelwidth*self.dpievermeter)
                k,b=self.lineequation((x,self.bottom),self.vp)
                if k!=None:
                    x1=int((self.size[1]-b)/k)
                    cv2.line(self.canvas,(x,self.bottom),(x1,self.size[1]),(0,255,0),2)
                else:
                    cv2.line(self.canvas,(x,self.bottom),(x,self.size[1]),(0,255,0),2)


                k,b=self.lineequation((x,self.top),self.vp)
                if  k!=None:
                    x1=-int(b/k)
                    cv2.line(self.canvas,(x,self.top),(x1,0),(155,155,155),2)
                else:
                    cv2.line(self.canvas,(x,self.top),(x,0),(155,155,155),2)
        for levelheigh in range(1,int(self.heigh)):
            y= int(self.bottom-levelheigh*self.dpievermeter)
            k,b = self.lineequation((self.left,y),self.vp)
            y1=int(b)
            cv2.line(self.canvas,(self.left,y),(0,y1),(200,200,200),2)

            k,b = self.lineequation((self.right,y),self.vp)
            y1=int(self.size[0]*k+b)
            cv2.line(self.canvas,(self.right,y),(self.size[0],y1),(0,0,255),2)
        self.canvas=cv2.resize(self.canvas,self.outsize,interpolation=cv2.INTER_CUBIC)
        cv2.imshow(name,self.canvas)
        cv2.waitKey(0)
    #function of Deconstruction
    def __del__(self):
        self.canvas[:]=[255,255,255]
if __name__ == '__main__':
    sc1=Scenograph(5.2,5.2,2,size=(1920,1080),dpieverymeter=100,heigh=3,HL=1.2,outsize=(960,540))
    sc1.scenoshow('SCENOGRAPH')