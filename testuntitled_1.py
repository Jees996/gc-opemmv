import sensor                   # type: ignore # 导入 OpenMV 摄像头模块
import ustruct                  # type: ignore
from pyb import UART, LED, Pin, Timer  # type: ignore

# ———————————————————————— 变量 ———————————————————————— #
threshold_index = 0  # 颜色跟踪阈值索引（0为红色，1为绿色，2为蓝色）

Goods_thresholds = [  # 物料颜色阈值
    (39, 74, 18, 82, 14, 78),   # 红色
    (57, 77, -19, -63, 27, 3),  # 绿色
    (42, 78, 12, -24, -12, -56) # 蓝色
]

color = 0
color_flag = 0
position_flag = 0
catch_flag = 0
Xx = 0
Xy = 0

uart_state = 0
uart_data = [0] * 9
color_number = [0] * 3
car_state = 1
color_change_flag = 0
color_step = 1
color_serial = 0

center_x, center_y, side_length = 70, 60, 8
x_date, y_date = 0, 0

DEBUG = True  # 开启调试模式

# ———————————————————————— 外设初始化 ———————————————————————— #
uart = UART(3, 115200, timeout_char=100)
light = Timer(2, freq=50000).channel(1, Timer.PWM, pin=Pin("P6"))

led_red, led_green, led_blue = LED(1), LED(2), LED(3)


# ———————————————————————— 主函数 ———————————————————————— #
def main():
    openmv_init()
    LED_Bord(80)

    while True:
        img_get()
        state_switching()
        check_position(x_date, y_date)
        check_color(color)
        is_catch_ok()
        uart_recieve()
        # uasrt_translate_five_uchar(1, catch_flag, Xx, Xy, 0)

        if DEBUG:
            draw_red_square(img, center_x, center_y, side_length)
            print(f"{color_number} ,{car_state}, {color_change_flag}, {color_step}")


# ———————————————————————— 状态切换 ———————————————————————— #
def state_switching():
    global x_date, y_date

    if car_state in (2, 3):  # 物料识别模式
        color_track()
    elif car_state == 1:  # 识别色环模式
        find_green_circles()
    else:
        x_date, y_date = None, None


# ———————————————————————— 目标判断 ———————————————————————— #
def check_position(x, y):
    global position_flag, Xx, Xy

    if x is None or y is None:
        position_flag, Xx, Xy = 0, 0, 0
        return

    if center_x - side_length <= x <= center_x + side_length and center_y - side_length <= y <= center_y + side_length:
        position_flag, Xx, Xy = 1, 0, 0
        return

    position_flag = 0
    Xx = 1 if x < center_x - side_length else 2 if x > center_x + side_length else 0
    Xy = 1 if y < center_y - side_length else 2 if y > center_y + side_length else 0


def check_color(mycolor):
    global color_flag
    if car_state in (1, 3):
        color_flag = 1 if mycolor == color_number[color_serial_number()] else 0
    elif car_state == 2:
        color_flag = 1
    else:
        color_flag = 0


def is_catch_ok():
    global catch_flag
    catch_flag = 1 if position_flag and color_flag else 0


def color_serial_number():
    return max(0, min(color_step - 1, 2))


def color_judge(mycolor):
    return {1: 1, 2: 2, 4: 3}.get(mycolor, 0)


# ———————————————————————— 视觉处理 ———————————————————————— #
def color_track():
    global color, x_date, y_date, img
    x_date, y_date, color = None, None, 0

    for blob in img.find_blobs(Goods_thresholds, pixels_threshold=900, area_threshold=900, merge=False):
        img.draw_rectangle(blob.rect())
        img.draw_cross(blob.cx(), blob.cy())
        color, x_date, y_date = color_judge(blob.code()), blob.cx(), blob.cy()


def find_green_circles():
    global x_date, y_date, img
    x_date, y_date = None, None

    for c in img.find_circles(threshold=2800, x_margin=50, y_margin=50, r_margin=20, r_min=5, r_max=30, r_step=1):
        img.draw_circle(c.x(), c.y(), c.r(), color=(255, 0, 0))
        img.draw_cross(c.x(), c.y())
        x_date, y_date = c.x(), c.y()


# ———————————————————————— OpenMV 初始化 ———————————————————————— #
def openmv_init():
    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QQVGA)
    sensor.skip_frames(time=2000)


def img_get():
    global img
    img = sensor.snapshot()


# ———————————————————————— 串口通信 ———————————————————————— #
def uasrt_translate_five_uchar(c1, c2, c3, c4, c5):
    data = ustruct.pack("<BBBBBBBB", 0xA5, 0xA6, c1, c2, c3, c4, c5, 0x5B)
    uart.write(data)


def uart_recieve():
    if uart.any() > 0:
        Receive_Prepare()


def Receive_Prepare():
    global uart_state, uart_data, color_number, car_state, color_change_flag, color_step

    if uart.any() >= 7:  # 确保有完整的 7 字节数据
        data = uart.read(7)  # 读取 7 字节
        if data and len(data) == 7 and data[0] == 0xdf:  # 检查帧头
            color_number[0] = int(data[1])
            color_number[1] = int(data[2])
            color_number[2] = int(data[3])
            car_state = int(data[4])
            color_change_flag = int(data[5])
            color_step = int(data[6])
        else:
            print(f"Invalid UART Data: {data}")  # 打印无效数据用于调试
    else:
        print("Waiting for UART data...")



# ———————————————————————— 外设控制 ———————————————————————— #
def LED_Bord(a):
    light.pulse_width_percent(a)


def draw_red_square(img, center_x, center_y, side_length):
    x, y = center_x - side_length // 2, center_y - side_length // 2
    img.draw_rectangle(x, y, side_length, side_length, color=(255, 0, 0), thickness=2)


if __name__ == "__main__":
    main()
