# Untitled - By: lixian - Tue Nov 12 2024

import sensor       # 导入 OpenMV 摄像头模块
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

color           = 0                 # 识别到的颜色
catch_flag      = 0                 # 抓取标志位
control_flag    = 0                 # 小车控制标志位
Xx              = 0                 # x方向运动数据
Xy              = 0                 # y方向运动数据

x_date          = 0
y_date          = 0
last_x_date     = None
last_y_date     = None
car_is_moving   = False

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
        check_position(x_date, y_date)
        print(f"catch_flag: {catch_flag}, x_date: {x_date}, y_date: {y_date}")
        # print(f"catch_flag: {catch_flag}, Xx: {Xx}, Xy: {Xy}")  # 输出: catch_flag,Xx,Xy
        uasrt_translate_five_uchar(catch_flag,control_flag,Xx,Xy,0)
        #translate_date()

    return


def color_track():                      #颜色追踪
    global color,x_date,y_date
    x_date  = None
    y_date  = None
    color   = 0

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

        # 更新为检测到的色块数据
        color   = color_judge(blob.code())
        x_date  = blob.cx()
        y_date  = blob.cy()
        #print(color)


#def translate_date():
#    c1 = color
#    c2 = check_position(Xx, Xy)
#    uasrt_translate_five_uchar(c1,c2,0,0,0)



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
    # print(data)                             #通过 print(data) 打印发送的数据到串行终端，方便调试和确认发送的内容。


def check_position(x, y):
    global catch_flag,Xx,Xy                 # 声明需要修改的全局变量

    if x is None or y is None:              # 如果未检测到物料，重置状态
        catch_flag = 0
        Xx = 0
        Xy = 0
        return

    if 140 <= x <= 180 and 100 <= y <= 120: # 检查是否在中心区域
        catch_flag      = 1
        Xx              = 0
        Xy              = 0
        return

    catch_flag      = 0                     # 不在中心区域时重置抓取标志位

    if 140 <= x <= 180:                     # 判断 x 方向
        Xx              = 0
    elif x < 140:
        Xx              = -1
    elif x > 180:
        Xx              = 1

    if 100 <= y <= 120:                     # 判断 y 方向
        Xy              = 0
    elif y < 100:
        Xy              = 1
    elif y > 120:
        Xy              = -1

    return


# 判断转盘是否转动
def is_turning(x, y):
    global last_x_date, last_y_date
    if x is None or y is None:  # 当前帧没有物料
        return False
    if last_x_date is None or last_y_date is None:  # 初始情况，无法判断
        return False
    # 计算位置变化
    dx = abs(x - last_x_date)
    dy = abs(y - last_y_date)
    # 设定阈值，例如2像素（可调整）
    threshold = 20
    if dx > threshold or dy > threshold:
        return True  # 转盘在转动
    return False  # 转盘静止



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
