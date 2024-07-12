# TraSculptor
请直接进入仓库下载最新的代码（不是release）
- 前端
  - [最新版本](https://github.com/akihaisland/UCS/tree/master)
- 后端
  - [最新版本](https://github.com/akihaisland/flaskUCS)

## 目录
1. [项目配置](#c_1)
2. [界面说明](#c_2)
3. [功能说明](#c_3)
    1. [展示地图](#c_3_1)
    2. [基于节点的操作](#c_3_2)
         1. [新建路段](#3_2_1)
         2. [删除节点](#3_2_2)
    3. [基于路段的操作](#c_3_3)
         1. [修改free flow travel time](#c_3_3_1)
         2. [修改capacity](#c_3_3_2)
         3. [创建节点](#c_3_3_3)
         4. [删除路段](#c_3_3_4)
    4. [其他操作](#c_3_4)
         1. [展示路段信息](#c_3_4_1)
         2. [快速选择矩阵中目标路段](#c_3_4_2)
         3. [矩阵内信息说明](#c_3_4_3)
         4. [选择需要展示的路段范围](#c_3_4_4)
         5. [对矩阵中link进行排序](#c_3_4_5)
         6. [展示经过link的需求的饼图](#c_3_4_6)

## 1. 项目配置
<span id="c_1"></span>
1. 解压压缩文件，得到前端与后端的文件夹
2. 1. 获取在前端的文件夹中执行命令，下载库
```sh
npm i
```
1. 项目运行
在后端文件夹下执行以下代码，开启后端
```sh
python app.py
```
在前端文件夹下执行以下代码，开启前端
```sh
npm run dev
```
点击前端中展示的网址，进入web界面

## 2. 界面说明
<span id="c_2"></span>
![220545a04ec06681f37a7df2c29d6db](https://github.com/akihaisland/UCS/assets/132194045/86427441-e931-4f43-829b-1dadc89dd797)

## 3. 功能介绍
<span id="c_3"></span>
### 3.1 展示地图
<span id="c_3_1"></span>
- 点击右侧工作流树状图中节点，展示该网络的信息
![show_map](https://github.com/akihaisland/UCS/assets/132194045/08868f07-1656-4894-af0d-31710a1c640c)

### 3.2 基于节点的操作
<span id="c_3_2"></span>
- 右键节点，选择新建路段的按键。

#### i. 新建路段
<span id="c_3_2_1"></span>
- 调整路段的参数，完成路段的新建
    - 按住新建道路的初始节点，不释放鼠标，并拖动到目标节点，完成端点的选择
    - 当鼠标拖动到终点后立即松开，则直接生成一条单向新道路；否则若鼠标在终点停留1秒后释放，则打开菜单，进行详细的设置，设置完成点击保存按钮即可创建新道路
    - ![2way_new_link](https://github.com/akihaisland/UCS/assets/132194045/f4bcf05c-c97b-4bba-971d-3ab7488c9fa5)


> 创建路段菜单说明
> ![rm_newlink4](https://github.com/akihaisland/UCS/assets/132194045/abb293d8-c5fb-41c8-8e76-871323a27397)
> 新版的界面：![9682417a3bf3d7e35fc58274ba3231a](https://github.com/akihaisland/UCS/assets/132194045/2c29925c-ffb4-4669-80ec-ff6388c0b678)
> 形象化的操作与后续“修改freeflowtraveltime”与修改“capacity”一致

#### ii. 删除节点
<span id="c_3_2_2"></span>
- 只能删除新建的节点
    - 右键节点删除节点

### 3.3 基于路段的操作
<span id="c_3_3"></span>
- 左键路段进行操作
> 界面说明
> ![rm_linkop](https://github.com/akihaisland/UCS/assets/132194045/4cf1aecb-045f-429b-a0a4-8b1613325883)


#### i. 修改free flow travel time
<span id="c_3_3_1"></span>
![rm_operate_link1](https://github.com/akihaisland/UCS/assets/132194045/9de7a771-8e5f-437a-8e8b-e3e9bdc5122d)
- 更形象化的操作
  - ![bf4d5b6c89319a1ddc462567ffbd673](https://github.com/akihaisland/UCS/assets/132194045/1b17987e-ee58-4ae7-b543-bb299181b9a3)

#### ii. 修改capacity
<span id="c_3_3_2"></span>
![rm_operate_link2](https://github.com/akihaisland/UCS/assets/132194045/56656d90-6bc8-432f-ba06-6269578c82a0)
- 更形象化的操作
  - ![1860c8a5e157b67644626e63e2fd3ba](https://github.com/akihaisland/UCS/assets/132194045/11bbd75d-fd67-4d87-8ffb-6faa8ca26551)


#### iii. 创建节点
<span id="c_3_3_3"></span>
> 界面说明
> ![rm_newnode1](https://github.com/akihaisland/UCS/assets/132194045/3fc02129-d38f-4d13-b72a-45b798363f34)

- 创建节点示例
    - ![rm_newnode2](https://github.com/akihaisland/UCS/assets/132194045/c166a31b-5e13-4b43-8607-87801266af5e)


#### iv. 删除路段
<span id="c_3_3_4"></span>
- 操作示例
    - ![rm_dellink1](https://github.com/akihaisland/UCS/assets/132194045/a2992790-6e6b-4ea1-a446-36f90dd287bd)
- 更快捷、形象化的操作
    - 右键道路删除路段
    - ![del_link01](https://github.com/akihaisland/UCS/assets/132194045/783fb808-6729-4adf-8fd1-9ec176183f76)


### 3.4 其他
<span id="c_3_4"></span>
#### i. 展示路段信息
<span id="c_3_4_1"></span>
- ![rm_other1](https://github.com/akihaisland/UCS/assets/132194045/4bea6ff1-e2b7-437a-aa59-73d6d0b281cb)
> 只会在控制台中展示，作为调试程序时使用

#### ii. 快速选择矩阵中目标路段
<span id="c_3_4_2"></span>
- 点击矩阵中元素，即可快速选择地图中对应link
    - ![choose_link01](https://github.com/akihaisland/UCS/assets/132194045/0a5a9666-9b4e-40b0-818e-b229b3e7d63e)

#### iii. 矩阵内信息说明
<span id="c_3_4_3"></span>
![e0c48ccedb6f2f78a67a30dc49582e0](https://github.com/akihaisland/UCS/assets/132194045/f18266b5-3ffe-4967-a4f3-e808842e1e54)
> 当某个路网上不存在该路段时，矩阵中该位置则没有内容，为空白。

#### iv. 选择需要展示的路段范围
<span id="c_3_4_4"></span>
- 通过右下角直方图调节
    - ![sel_show_links](https://github.com/akihaisland/UCS/assets/132194045/4652361f-445b-45c0-9cbd-b43288929bbb)
> - 深色柱状图为被选中展示的部分，浅色为被过滤不展示的部分
> - 拉动直方图左右两边的垂直条设置需要展示的路段的范围。其中，左右垂直条中间的部分即为被选中展示的路段，两边为被过滤的部分
> - 选择好特定的范围后，点击确定（✔）按钮实线过滤；否则，将鼠标移出直方图区域即可还原操作
> - 当需要取消某个直方图属性的限制时，点击直方图右上角的取消（❌）按钮将限制取消并更新
> - 由于矩阵部分为以其中心而非鼠标位置进行缩放，故当选择的link过多，矩阵高度过大时，直接滚轮缩放可能导致矩阵脱出
> - avg FFTT: 每个道路在各个状态下平均的fftt；tt scope：每个道路在各个状态下tt的范围；tt ratio：各个道路平均的fftt/tt；tt ratio scope：各个道路tt ratio的范围；avg capacity：各个道路平均的capacity；tf scope：哥哥道路的flow范围；tf ratio：各个道路的flow/capacity；tf ratio scope：各个道路的tf ratio范围

#### v. 排序
<span id="c_3_4_5"></span>
- 按钮的图标表示当前属性参与排序的状态
![4b2541b46b59bb2c16129a790696354](https://github.com/akihaisland/UCS/assets/132194045/2060baa4-9ca6-4c34-a4a0-86152df847a4)

#### vi. 展示经过link的需求的饼图
<span id="c_3_4_6"></span>
- 双击某一条路段可以开启该模式，点击地图外任意位置关闭模式
    - 饼图的大小与该link满足的节点的需求总量呈正相关
    - 饼图中，蓝色为以该点为o点满足的demand，粉色为以该点为d点满足的demand
![0ccdecdd3bc6d1b8fab1fb98ebcdfd5](https://github.com/akihaisland/UCS/assets/132194045/ad769a75-83c1-4d51-ad0c-f301a4e84be5)




