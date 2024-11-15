# Untitled - By: lixian - Tue Nov 12 2024

import sensor       # 导入 OpenMV 摄像头模块
import time         # 导入时间模块
import math         # 导入数学模块，用于角度转换等
import image
from pyb import UART


#——————————————————————————变量——————————————————————————#
threshold_index = 2                 # 选择颜色跟踪阈值的索引（0为红色，1为绿色，2为蓝色）

thresholds = [
    (31, 61, 16, 82, -28, 65),      # 红色的阈值范围
    (55, 86, -31, -86, 50, -9),     # 绿色的阈值范围
    (54, 80, 11, -33, -52, 127),    # 蓝色的阈值范围
]                                   # 阈值列表，用于色块跟踪的颜色设定

color = 0

uart = UART(3, 115200, timeout_char=200)
#——————————————————————————函数——————————————————————————#


def main():
    openmv_init();
    clock = time.clock()
    while(True):
        color_track()
        translate_date()
    return


def color_track():                      #颜色追踪
    global color
    img = sensor.snapshot()             # 捕获一帧图像
    for blob in img.find_blobs(
        thresholds,                     #追踪全部颜色
#        [thresholds[threshold_index]],  # 根据当前阈值进行色块跟踪
        pixels_threshold = 600,         # 仅返回大于600个像素的色块
        area_threshold   = 600,         # 仅返回大于600平方像素的色块
        merge=False,                     # 合并重叠的色块
    ):
        img.draw_rectangle(blob.rect())  # 绘制色块的矩形框
        img.draw_cross(blob.cx(), blob.cy())  # 绘制色块中心的十字线标记
        #print(blob.code(),blob.cx(),blob.cy())
        color = color_judge(blob.code())
        print(color)



def openmv_init():                          # 初始化openmv模块
    sensor.reset()                          # 重置传感器
    sensor.set_pixformat(sensor.RGB565)     # 设置传感器的像素格式为RGB565
    sensor.set_framesize(sensor.QVGA)       # 设置分辨率为QVGA（320x240）
    sensor.skip_frames(time=2000)           # 等待2000毫秒，确保摄像头初始化完成
    sensor.set_auto_gain(False)             # 关闭自动增益功能，必须关闭以进行颜色跟踪
    sensor.set_auto_whitebal(False)         # 关闭自动白平衡，必须关闭以进行颜色跟踪
    return


def translate_date():
    uart.write(f"{color}\r\n")
    time.sleep_ms(10)
    return


def color_judge(mycolor):
    if mycolor == 1:
        return 1
    elif mycolor == 4:
        return 2
    elif mycolor == 2:
        return 3
    else:
        return 0





#——————————————————————————程序——————————————————————————#


if __name__ == "__main__":
    main()
