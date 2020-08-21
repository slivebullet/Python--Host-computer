import matplotlib.pyplot as plt
import matplotlib.animation as ma
from matplotlib.pyplot import MultipleLocator

# 动态绘制波形的时候 分辨率比例 当CSV数据足够大的时候 可以保证绘图速度和分辨率
gl_resolution = 97
gl_board = 300


def operate_file(file_path):
    """
    文件读取CSV函数 一列时间 一列函数值
    :param file_path:   文件路径： 1.当前路径下面的文件名  2. 文件路径
    :return:      返回两个列表 分别装着两列数据
    """
    filename = file_path
    datas_files = []   # 从文件当中提取数据，原始列表
    x_data = []     # 时间轴数据列表
    y_data = []     # 幅度值数据列表
    with open(filename) as file_object:
        lines = file_object.readlines()

    # 读取的是字符串形式，datas为列表，里面的元素是列表
    for line in lines:
        datas_files.append(list(line.strip().split(',')))

    file_count = 1
    for data_file in datas_files:
        if file_count == 1:         # 跳过CSV文件第一行的名称，从第二行读入正式的数据
            file_count += 1
            continue
        x_data.append(float(data_file[1]))
        y_data.append(float(data_file[2]))

    return x_data, y_data


class DrawWave(object):
    def __init__(self, file_path, y_max=2, y_min=-2, x_tick=1, y_tick=1, zero_flag=False):
        """
        画图的初始化基础性的操作
        :param zero_flag:   零点触发使能标志位 为TRUE则确定为 零点触发绘制波形 默认值为不需要：FLASE
        :param file_path:   读取源文件的文件名路径
        :param y_max:       Y轴范围 MANX
        :param y_min:              MIN
        :param x_tick:      X轴单步增长刻度值
        :param y_tick:      Y轴单步增长刻度值
        """
        # 文件操作函数，移植的时候要注意 模块名直接的移植变化!!!!
        self.x_data, self.y_data = operate_file(file_path)

        self.i_count = 0
        self.time_x = 0
        self.amplitude_y = 0
        self.x = []
        self.y = []

        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.fig.set_label('动态波形绘制')
        self.ax.set_title('Signal', fontsize=20)
        self.ax.set_xlabel('Time/ s', fontsize=14, loc='right')  # 横纵坐标标签
        self.ax.set_ylabel('Amplitude/ V', fontsize=14, loc='top')
        self.ax.set_ylim(y_min, y_max)  # 垂直坐标范围
        self.ax.tick_params(labelsize=10)  # 精度值字体大小
        self.ax.grid(linestyle=':')  # 网格线

        # 设置坐标轴的刻度值 单步增长值！！！！
        x_major_locator = MultipleLocator(x_tick)
        y_major_locator = MultipleLocator(y_tick)
        self.ax.xaxis.set_major_locator(x_major_locator)
        self.ax.yaxis.set_major_locator(y_major_locator)

        # 判断是否需要 零点触发
        if zero_flag:
            # 需要零点触发
            for data in self.y_data:
                if data >= 0:
                    # 把列表当中第一个数值符合零触发条件的索引序号 赋值给data_num
                    data_num = self.y_data.index(data)
                    self.ax.set_xlim(left=self.x_data[data_num])       # X轴坐标起始绘制的值

                    # ...
                    self.x_data = self.x_data[data_num:]
                    self.y_data = self.y_data[data_num:]
                    break   # 退出索引查找
            else:
                # 当for遍历完还没有找到大于零点的触发条件
                self.ax.set_xlim(left=self.x_data[0])
        else:
            # 不需要零点触发 False 则
            self.ax.set_xlim(left=self.x_data[0])       # X轴坐标起始绘制的值

        # 创建一个plot空对象（只是没有数据，仍然是一个完整的图像）
        self.picture = plt.plot([], [], c="orangered")[0]  # 有很多个元素，此处取一个处理
        self.picture.set_data([], [])  # 设置数据，此处给的空数据，以便于之后将生成器的数据传入

    def update(self, data):

        # 追加数据
        self.x.append(self.time_x)
        self.y.append(self.amplitude_y)
        # 移动坐标轴位置，以便持续观察数据
        # 获取当前坐标轴的最小值与最大值，即坐标系的左右边界
        x_min, x_max = self.ax.get_xlim()
        if self.time_x >= x_max:
            # 平移坐标轴：将最小值变为当前位置减去窗口宽度，最大值变为当前值
            self.ax.set_xlim(self.time_x - (x_max - x_min), self.time_x)
            # 坐标系起点终点都改变了，需要重新画一个画布
            self.ax.figure.canvas.draw()

        # 修改数据
        self.picture.set_data(self.x, self.y)

    # 生成器函数
    def generator(self):
        global gl_resolution, gl_board

        while True:
            self.time_x = self.x_data[self.i_count]
            self.amplitude_y = self.y_data[self.i_count]

            yield self.time_x, self.amplitude_y

            """
            利用分辨率比例进行绘制速率和分辨率恰到好处的图
            如果读取的数据过于冗长，则进行间隔采样绘图 不然会降低绘制图速度 
            gl_board 以内按照CSV采样最佳 速度可以保证 300以上需要除以分辨率 来保证速度和采样精度
            """

            if len(self.x_data) > gl_board:
                resolution = int(len(self.x_data) / gl_resolution)
            else:
                resolution = 1

            self.i_count += resolution

            if self.i_count >= len(self.x_data):
                # 执行完此处，把程序跳出绘制图像 直接进入后面的程序
                return

    # 生成绘制波形动画！！！！
    def draw_wave(self):
        """
        生成动画
        """
        anim = ma.FuncAnimation(self.fig, self.update, self.generator(), interval=20, repeat=False)
        plt.show()


if __name__ == '__main__':
    myfigure = DrawWave(file_path='**')
    myfigure.draw_wave()

    print("执行到这里")
