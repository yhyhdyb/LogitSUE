import matplotlib.pyplot as plt
from Network import PyNetwork


network = PyNetwork()
network.read_node("data/Node_SiouxFalls.txt")
network.read_link("data/Link_SiouxFalls.txt")
network.read_od_pairs("data/ODPairs_SiouxFalls.txt")
network.read_path("data/Path_SiouxFalls.txt")


# 定义点的坐标
points = []
for node in network.m_node:
    points.append((node.lat, node.lon))

# 绘制矢量图
fig, ax = plt.subplots()
for i, point in enumerate(points):
    ax.plot(point[0], point[1], 'ro')  # 绘制红色圆点
    ax.text(point[0], point[1], 'n'+str(network.m_node[i].id+1), ha='left', va='top')  # 在点上标记序号

# 绘制边
for link in network.m_link:
    start_node = link.p_in_node.id
    end_node = link.p_out_node.id
    ax.plot([points[start_node][0], points[end_node][0]], [points[start_node][1], points[end_node][1]], 'b-')  # 绘制蓝色直线
    ha = 'left'
    va = 'top'
    if start_node < end_node:
        ha = 'right'
    # ax.text((points[start_node][0]+points[end_node][0])/2,
    #         (points[start_node][1]+points[end_node][1])/2,
    #         'l'+str(link.id+1)+'  ', ha=ha, va=va)  # 在点上标记序号
# 连接点的边
# for i in range(len(points)-1):
#     ax.plot([points[i][0], points[i+1][0]], [points[i][1], points[i+1][1]], 'b-')  # 绘制蓝色直线

plt.xlabel('X')
plt.ylabel('Y')
plt.title('Vector Graph')
plt.grid(True)
plt.show()