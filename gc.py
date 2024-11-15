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
    (62, 82, -76, -3, -36, 16),     # 绿色的阈值范围
    (26, 83, -57, 48, -79, -24),    # 蓝色的阈值范围
]                                   # 阈值列表，用于色块跟踪的颜色设定

set_color = 0
color     = 0

#——————————————————————————函数——————————————————————————#


def main():
    openmv_init();
    uart = UART(3, 115200, timeout_char=200)
    clock = time.clock()
    while(True):
    #    clock.tick()
        color_track()
    #    print(clock.fps())
    return


def color_track():                      #颜色追踪
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
        print(blob.code(),blob.cx(),blob.cy())
#        color_judge(blob.code())


def openmv_init():                          # 初始化openmv模块
    sensor.reset()                          # 重置传感器
    sensor.set_pixformat(sensor.RGB565)     # 设置传感器的像素格式为RGB565
    sensor.set_framesize(sensor.QVGA)       # 设置分辨率为QVGA（320x240）
    sensor.skip_frames(time=2000)           # 等待2000毫秒，确保摄像头初始化完成
    sensor.set_auto_gain(False)             # 关闭自动增益功能，必须关闭以进行颜色跟踪
    sensor.set_auto_whitebal(False)         # 关闭自动白平衡，必须关闭以进行颜色跟踪
    uart = UART(3, 115200, timeout_char=200)# 初始化串口
    return




def color_judge(mycolor):
    if mycolor == 1:
        uart.write("红色")
        #print("红色")
        return 1
    elif mycolor == 4:
        uart.write("蓝色")
        #print("蓝色")
        return 2
    elif mycolor == 2:
        uart.write("绿色")
        #print("绿色")
        return 3
    else:
        print("多颜色混合或未识别到颜色")
        return 0





#——————————————————————————程序——————————————————————————#


if __name__ == "__main__":
    main()
