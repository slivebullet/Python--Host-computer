import matplotlib.pyplot as plt

"""
 读取数据 其中需要改变的量为 filename = ''  文件名
 读取后的数据，时域波形存储在 x_data 和 y_data 列表里面
"""
# -------------------------------读取文件 ---------------------------------------
filename = 'SIN(X)  零点触发测试文件.csv'

datas_files = []  # 从文件当中提取数据，原始列表
x_data = []  # 时间轴数据列表
y_data = []  # 幅度值数据列表
with open(filename) as file_object:
    lines = file_object.readlines()

# 读取的是字符串形式，datas为列表，里面的元素是列表
for line in lines:
    datas_files.append(list(line.strip().split(',')))

file_count = 1
for data_file in datas_files:
    if file_count == 1:  # 跳过CSV文件第一行的名称，从第二行读入正式的数据
        file_count += 1
        continue
    x_data.append(float(data_file[1]))
    y_data.append(float(data_file[2]))
# ----------------------------------------------------------------------------------------
for data in y_data:
    if data >= 0:
        num = y_data.index(data)
        print(x_data[num])
        break
else:
    print('不符合零触发条件')

# plt.plot(x_data, y_data)
# plt.show()
