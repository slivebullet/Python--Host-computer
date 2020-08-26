import sys
import pandas as pd
import multiprocessing
import DrawWaveForm
from DrawWaveForm import DrawWave
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sip
from PyQt5.QtWidgets import *
from MainGUIWindows import MainGUIWindows  # 导入界面文件
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from Dialog_LFM_CSV import Ui_Dialog_CSV
from Dialog_LFM_NoneData import Ui_Dialog_Nonedata
from Dialog_WARNNING_FILE import Ui_Dialog_file
from PyQt5 import QtWidgets, QtCore
import numpy as np
import matplotlib
import matplotlib.pyplot as plt


matplotlib.use("Qt5Agg")  # 声明使用QT5


# 创建一个Figure类 继承画布类！！
class MyFigure(FigureCanvas):
    def __init__(self, width=5, height=4, dpi=100):
        # 字体显示 中文
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 这两行需要手动设置

        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super(MyFigure, self).__init__(self.fig)


class DrawSpreum(MainGUIWindows):
    def __init__(self, file_path):
        """
        从读取的CSV文件当中 获取文件路径
        :param file_path:
        """

        self.image2_spreum = MyFigure(5, 4, 100)
        self.image2_spreum_layout = QGridLayout(myWin.groupBox)
        self.toolbar2_layout = QGridLayout(myWin.groupBox_2)
        self.toolbar2 = NavigationToolbar(self.image2_spreum, myWin.groupBox_2)

        self.x_data, self.y_data = DrawWaveForm.operate_file(file_path)

    def draw_fft_amplitude(self):
        axes2 = self.image2_spreum.fig.add_subplot(111)

        # ----------------------- 绘制频谱图  ----------------
        fnum = len(self.y_data)

        x = np.fft.fft(self.y_data)
        y = np.fft.fftshift(abs(x))

        axis_xf = np.linspace(-fnum / 2, fnum / 2 - 1, num=fnum)
        axes2.plot(axis_xf, y)

        axes2.set_title('频谱图', fontproperties='SimHei')

        self.image2_spreum_layout.addWidget(self.image2_spreum)

        self.toolbar2_layout.addWidget(self.toolbar2)

    @staticmethod   # 清除绘制在 UI 界面上面的画布 ！！！！！
    def clean_spreum(image2_spreum, image2_spreum_layout, toolbar2_layout, toolbar2):
        sip.delete(image2_spreum)
        sip.delete(image2_spreum_layout)
        sip.delete(toolbar2_layout)
        sip.delete(toolbar2)


# 构建一个LFM信号绘制图类
class DrawLfm(MainGUIWindows):
    def __init__(self):
        self.image1_lfm = MyFigure(3, 3, 100)
        self.image1_lfm_layout = QGridLayout(myWin.groupBox)
        self.toolbar1_layout = QGridLayout(myWin.groupBox_2)
        self.toolbar1 = NavigationToolbar(self.image1_lfm, myWin.groupBox_2)

        self.LFM_T = 5
        self.LFM_BW = 100
        self.LFM_K = self.LFM_BW / self.LFM_T
        self.LFM_Fs = 5000
        self.LFM_Ts = 1 / self.LFM_Fs  # 采样时间间隔
        self.LFM_N = self.LFM_T / self.LFM_Ts  # 采样点个数

    # 绘制LFM 信号函数
    def lfm_timedraw(self):
        global x_lfm_data, y_lfm_data

        # ------------------------------绘制LFM时域信号------------------------------

        axes1 = self.image1_lfm.fig.add_subplot(211)

        t1 = np.linspace(0, self.LFM_T, int(self.LFM_N))
        x_lfm_data = t1

        time_ticks = np.arange(0, 6, 0.5)
        axes1.set_xticks(time_ticks)
        st_lfm = 2 * np.cos(np.pi * self.LFM_K * np.power(t1, 2))
        y_lfm_data = st_lfm

        axes1.plot(t1, st_lfm)
        axes1.set_title('LFM signal in time domain')
        axes1.set_xlabel('Time(s)')
        axes1.set_ylabel('Amplitude(W)')

        # # -----------------绘制LFM频域信号 ---------------------------
        axes2 = self.image1_lfm.fig.add_subplot(212)

        t2 = np.linspace(-self.LFM_T / 2, self.LFM_T / 2, int(self.LFM_N))

        # 设置X坐标轴的范围
        axes2.set_xlim((-150, 150))

        freq = np.linspace(-self.LFM_Fs / 2, self.LFM_Fs / 2, int(self.LFM_N))
        st_complex = np.exp(1j * np.pi * self.LFM_K * np.power(t2, 2))
        sf_complex = np.fft.fftshift(np.fft.fft(st_complex))
        axes2.plot(freq, abs(sf_complex))

        axes2.set_xlabel('Frequency(Hz)')
        axes2.set_ylabel('Amplitude(W)')
        axes2.set_title('Spectrum amplitude of complex LFM signal')

        # 在UI 界面上添加一个画布

        self.image1_lfm_layout.addWidget(self.image1_lfm)

        # 调节两个子图的位置
        self.image1_lfm.fig.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=0.48)

        self.toolbar1_layout.addWidget(self.toolbar1)

    @staticmethod      # 清除画布
    def clean_lfm(image1_lfm, image1_lfm_layout, toolbar1, toolbar1_layout):
        sip.delete(image1_lfm)
        sip.delete(image1_lfm_layout)
        sip.delete(toolbar1)
        sip.delete(toolbar1_layout)


# 构建一个信号类 控制上位机当中的信号与槽
class MyMainForm(QMainWindow, MainGUIWindows):
    def __init__(self):
        super(MyMainForm, self).__init__()
        self.setupUi(self)

        # 初试文件选择名设置
        self.path_way = 'NO path way'

        # X,Y轴等画图基本要求变量
        self.x_ticks = 1
        self.y_ticks = 1
        self.Yvalue_min = -2
        self.Yvalue_max = 2

        # 选择清除哪一个画布 选择变量 初始值的意思为画布一片空白 无需清除
        self.choice_string = 'clean nothing'

        self.enable_button_lfm = False
        self.enable_button_spreum = False

        self.flag_clean_lfm = False
        self.flag_clean_spreum = False

        # 存储LFM信号 变量画布值，用于删除画布用的存储变量
        self.lfm_aalast = None
        self.lfm_bblast = None
        self.lfm_cclast = None
        self.lfm_ddlast = None

        # 存储LFM信号 变量画布值，用于删除画布用的存储变量
        self.spreum_aalast = None
        self.spreum_bblast = None
        self.spreum_cclast = None
        self.spreum_ddlast = None

        # 零点触发标志位 FLASE 为不触发 TRUE为按下按钮 绘制波形的时候 进行零点触发
        self.flag_zerotrick = False

        self.pushButton.clicked.connect(self.showlfm)
        self.actionCSV.triggered.connect(self.savecsv)
        self.pushButton_2.clicked.connect(self.drawwave)
        self.pushButton_3.clicked.connect(self.drawspreum)
        self.pushButton_4.clicked.connect(self.clean_canvas)

        self.Time.valueChanged.connect(self.drawticks)
        self.AMPLITUDE.valueChanged.connect(self.drawticks)
        self.Y_MIN.valueChanged.connect(self.drawticks)
        self.Y_MAX.valueChanged.connect(self.drawticks)

        self.action.triggered.connect(self.readfile)

        self.radioButton_2.toggled.connect(self.zero_trick)

    # 点击"LFM信号"按钮 显示LFM生成信号
    def showlfm(self):

        """
        条件判断功能： 适当地让按键在某些情况下失能
        条件1： 已经绘制了该图 重复按下会产生重复的类 则无法进行删除之前的故意需要添加一个新的标志位
        条件2： 当使用的时候跳过规定步骤，试图直接不清楚就画 那么使该按键失能！！！！不然又会创建一个新的类无法有效删除
        """
        if self.enable_button_lfm or self.choice_string == 'clean spreum':
            return

        paint = DrawLfm()

        aa_lfm = paint.image1_lfm
        bb_lfm = paint.image1_lfm_layout
        cc_lfm = paint.toolbar1
        dd_lfm = paint.toolbar1_layout

        if self.flag_clean_lfm:
            # 需要进行清理，但是由于之前赋值的原因，导致图像已经改变，故需要之前画的类的信息
            aa_lfm = self.lfm_aalast
            bb_lfm = self.lfm_bblast
            cc_lfm = self.lfm_cclast
            dd_lfm = self.lfm_ddlast
        else:
            # 不需要进行清理，画好了一幅展现的波形图,存储这一幅paint的对象
            self.lfm_aalast = aa_lfm
            self.lfm_bblast = bb_lfm
            self.lfm_cclast = cc_lfm
            self.lfm_ddlast = dd_lfm

            paint.lfm_timedraw()
            self.enable_button_lfm = True

            self.choice_string = 'clean lfm'

        if self.flag_clean_lfm:
            # 需要清理了 那么进行清理之前的画布
            paint.clean_lfm(aa_lfm, bb_lfm, cc_lfm, dd_lfm)
            self.flag_clean_lfm = False

    # 保存LFM的CSV文件 信号槽函数
    def savecsv(self):
        file_csv = pd.DataFrame({'x_time': x_lfm_data, 'y_amplitude': y_lfm_data})
        file_csv.to_csv('LFM Singal.csv')

        # 如果画布上面没有东西，则提示先绘制LFM信号才能 保存为CSV文件
        if self.choice_string == 'clean nothing':
            lfm_dialog3 = QDialog()
            lfm_dialog4 = Ui_Dialog_Nonedata()
            lfm_dialog4.setupUi(lfm_dialog3)
            lfm_dialog3.exec_()

            # 直接退出保存程序，进入主UI
            return

        # 调出子窗口，提示保存成功
        lfm_dialog1 = QDialog()
        lfm_dialog2 = Ui_Dialog_CSV()
        lfm_dialog2.setupUi(lfm_dialog1)
        lfm_dialog1.exec_()

    # 动态动画绘制波形
    def drawwave(self):
        # 检测是否选择了本地文件，若无则弹出"请选择本地文件！！！！"
        if self.path_way == 'NO path way' or len(self.path_way) == 0:
            file_dialog1 = QDialog()
            file_dialog2 = Ui_Dialog_file()
            file_dialog2.setupUi(file_dialog1)
            file_dialog1.exec_()
            # 返回主程序，不执行下面的动态绘制程序！！
            return
        mywaveform = DrawWave(self.path_way, x_tick=self.x_ticks, y_tick=self.y_ticks,
                              y_max=self.Yvalue_max, y_min=self.Yvalue_min, zero_flag=self.flag_zerotrick)

        # 添加一个新的进程，专门用来动画的绘制
        p1_porcess = multiprocessing.Process(target=mywaveform.draw_wave)

        # 守护主进程，主进程一旦结束，子进程也进行结束
        p1_porcess.daemon = True
        p1_porcess.start()

    # SpinBox 调节数组相应读取函数
    def drawticks(self):
        self.x_ticks = self.Time.value()
        self.y_ticks = self.AMPLITUDE.value()
        self.Yvalue_min = self.Y_MIN.value()
        self.Yvalue_max = self.Y_MAX.value()

    # 读取本地文件函数
    def readfile(self):
        get_filename_path, ok = QFileDialog.getOpenFileName(self,
                                                            "选取单个文件",
                                                            "C:/",
                                                            "All Files (*);;Text Files (*.txt)")
        self.path_way = str(get_filename_path)

    # 零点触发 使能按钮
    def zero_trick(self):
        self.flag_zerotrick = self.radioButton_2.isChecked()

    # 频谱图的绘制
    def drawspreum(self):
        if self.path_way == 'NO path way' or len(self.path_way) == 0:
            file_dialog1 = QDialog()
            file_dialog2 = Ui_Dialog_file()
            file_dialog2.setupUi(file_dialog1)
            file_dialog1.exec_()
            # 返回主程序，不执行下面的动态绘制程序！！
            return

        """
        条件判断功能： 适当地让按键在某些情况下失能
        条件1： 已经绘制了该图 重复按下会产生重复的类 则无法进行删除之前的故意需要添加一个新的标志位
        条件2： 当使用的时候跳过规定步骤，试图直接不清楚就画 那么使该按键失能！！！！不然又会创建一个新的类无法有效删除
        """
        if self.enable_button_spreum or self.choice_string == 'clean lfm':
            return

        image_spreum = DrawSpreum(self.path_way)

        aa_spreum = image_spreum.image2_spreum
        bb_spreum = image_spreum.image2_spreum_layout
        cc_spreum = image_spreum.toolbar2
        dd_spreum = image_spreum.toolbar2_layout

        if self.flag_clean_spreum:
            # 需要进行清理，但是由于之前赋值的原因，导致图像已经改变，故需要之前画的类的信息
            aa_spreum = self.spreum_aalast
            bb_spreum = self.spreum_bblast
            cc_spreum = self.spreum_cclast
            dd_spreum = self.spreum_ddlast
        else:
            # 不需要进行清理，画好了一幅展现的波形图,存储这一幅image_spreum的对象
            self.spreum_aalast = aa_spreum
            self.spreum_bblast = bb_spreum
            self.spreum_cclast = cc_spreum
            self.spreum_ddlast = dd_spreum

            image_spreum.draw_fft_amplitude()

            self.enable_button_spreum = True

            # 告诉清除按钮的时候 选择该清除哪个
            self.choice_string = 'clean spreum'

        if self.flag_clean_spreum:
            # 需要清理了 那么进行清理之前的画布
            image_spreum.clean_spreum(aa_spreum, bb_spreum, cc_spreum, dd_spreum)
            self.flag_clean_spreum = False

    def clean_canvas(self):

        # 当没有画布画的时候 按钮失能 立即返回
        if self.choice_string == 'clean nothing':
            return

        if self.choice_string == 'clean lfm':
            self.flag_clean_lfm = True
            self.enable_button_lfm = False

            myWin.showlfm()

            # 清除完 将选择变量设置为 干净的画布状态
            self.choice_string = 'clean nothing'

        elif self.choice_string == 'clean spreum':
            self.flag_clean_spreum = True
            self.enable_button_spreum = False

            myWin.drawspreum()

            # 清除完 将选择变量设置为 干净的画布状态
            self.choice_string = 'clean nothing'

        else:   # 正常情况下 不会执行这个条件 如果执行 则提示错误地方 方便后期软件维护！！！！

            # 后期维护的错误窗口代码提示！！！！
            print("BUG !!!!!!")


if __name__ == '__main__':
    # --------------------全局变量 定义区-------------------------------------------------

    # 存储LFM时域变量的两个列表，并且写入到CSV文件
    x_lfm_data = []
    y_lfm_data = []

    # -------------------------------------------------------------------------------

    # spawn进程启动兼容WINDOWS 和MAC OS 等各种操作系统 为此采用 spawn派生一个新的进程
    multiprocessing.set_start_method('spawn')

    app = QApplication(sys.argv)
    myWin = MyMainForm()
    myWin.show()

    sys.exit(app.exec_())
