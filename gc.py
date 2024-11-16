# Untitled - By: lixian - Tue Nov 12 2024

import sensor       # 导入 OpenMV 摄像头模块
import time         # 导入时间模块
import math         # 导入数学模块，用于角度转换等
import image
import ustruct
from pyb import UART
from pyb import LED


#——————————————————————————变量——————————————————————————#
threshold_index = 2                 # 选择颜色跟踪阈值的索引（0为红色，1为绿色，2为蓝色）

thresholds = [
    (31, 61, 16, 82, -28, 65),      # 红色的阈值范围
    (47, 90, -21, -70, 46, -17),    # 绿色的阈值范围
    (50, 85, 11, -39, -66, -15),    # 蓝色的阈值范围
]                                   # 阈值列表，用于色块跟踪的颜色设定

color           = 0
center_point    = 0
Xx              = 0
Xy              = 0


uart = UART(3, 115200, timeout_char=200)


led_red     = LED(1)
led_green   = LED(2)
led_blue    = LED(3)
led_ir      = LED(4)

#——————————————————————————函数——————————————————————————#


def main():
    openmv_init()
    led_init()
    while(True):
        color_track()
        translate_date()

        #print(color)
    return


def color_track():                      #颜色追踪
    global color,Xx,Xy
    img = sensor.snapshot()             # 捕获一帧图像
    for blob in img.find_blobs(
        thresholds,                     #追踪全部颜色
#        [thresholds[threshold_index]],  # 根据当前阈值进行色块跟踪
        pixels_threshold = 900,         # 仅返回大于600个像素的色块
        area_threshold   = 900,         # 仅返回大于600平方像素的色块
        merge=False,                    # 合并重叠的色块
    ):
        img.draw_rectangle(blob.rect())  # 绘制色块的矩形框
        img.draw_cross(blob.cx(), blob.cy())  # 绘制色块中心的十字线标记
        #print(blob.code(),blob.cx(),blob.cy())
        color = color_judge(blob.code())
        Xx    = blob.cx()
        Xy    = blob.cy()
        #print(color)


def translate_date():
    c1 = color
    c2 = check_position(Xx, Xy)
    uasrt_translate_five_uchar(c1,c2,0,0,0)



def openmv_init():                          # 初始化openmv模块
    sensor.reset()                          # 重置传感器
    sensor.set_pixformat(sensor.RGB565)     # 设置传感器的像素格式为RGB565
    sensor.set_framesize(sensor.QVGA)       # 设置分辨率为QVGA（320x240）
    sensor.skip_frames(time=2000)           # 等待2000毫秒，确保摄像头初始化完成
    sensor.set_auto_gain(False)             # 关闭自动增益功能，必须关闭以进行颜色跟踪
    sensor.set_auto_whitebal(False)         # 关闭自动白平衡，必须关闭以进行颜色跟踪
    return


def uasrt_translate_five_uchar(c1,c2,c3,c4,c5):         #发送五个无符号字符数据（unsigned char）
    global uart;
    data = ustruct.pack("<BBBBBBBB",        #使用了 ustruct.pack() 函数将这些数据打包为二进制格式。使用 "<BBBBBBBB" 作为格式字符串来指定要打包的数据的类型和顺序：
                   0xA5,
                   0xA6,
                   c1,
                   c2,
                   c3,
                   c4,
                   c5,
                   0x5B
                   )
    uart.write(data);                       #uart.write(data) 将打包好的二进制数据帧写入 UART 发送缓冲区，从而将数据通过串口发送出去
    print(data)                             #通过 print(data) 打印发送的数据到串行终端，方便调试和确认发送的内容。


def check_position(x, y):
    global center_point,Xx,Xy
    if 0 <= x <= 400 and 0 <= y <= 320:  # 检查输入是否在合法范围内
        if 180 <= x <= 220 and 140 <= y <= 180:
            center_point    = 1
            Xx              = 0
            Xy              = 0
            return
        elif x <= 180 or x >= 220:
            center_point    = 0
            Xx = (x-200)/10
        elif y <= 140 or y >= 180:
            center_point    = 0
            Xy = (y-160)/10
        else:
            center_point    = 0
    return


def color_judge(mycolor):
    if mycolor == 1:
        return 1
    elif mycolor == 4:
        return 2
    elif mycolor == 2:
        return 3
    else:
        print("other")
        return 0


def led_init():
    led_red.on()
    led_green.on()
    led_blue.on()



#——————————————————————————程序——————————————————————————#


if __name__ == "__main__":
    main()
