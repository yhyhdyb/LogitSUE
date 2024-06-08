# 原Network.py函数
import math
import time
import os
import numpy as np

class PyNode:
    """
    节点

    Attributes:
        - id: 节点的编号，从零开始编号;
        - position_x: 节点的X坐标;
        - position_y: 节点的Y坐标;
        - origin_id: 节点对应的起点编号，-1表示不是起点;
        - incoming_link: 进入节点的路段编号集合;
        - outgoing_link: 离开节点的路段编号集合;

        - global_id: 全局所有网络中唯一的id
        - is_od: 在不在OD对中
        - lon 经度
        - lat 纬度
        - binary_ways: 是否只能通向两个节点
    """
    def __init__(self) -> None:
        self.id = 0 # 节点的编号，从0开始编号
        self.position_x = 0.0 # 节点的X坐标
        self.position_y = 0.0 # 节点的Y坐标
        self.origin_id = -1 # 节点对应的起点编号，-1表示不是起点
        self.incoming_link = [] # 进入节点的路段编号集合
        self.outgoing_link = [] # 离开节点的路段编号集合

        # 经纬度
        self.lon = 0 # 经度
        self.lat = 0 # 纬度

        # 全局id
        self.global_id = -1
        self.is_od = False
        self.binary_ways = True

class PyLink:
    """
    路段
    
    Attributes:
        - id: 路段的编号，从零开始编号
        - p_in_node: 路段的起节点
        - p_out_node: 路段的终节点
        - free_flow_travel_time: 自由流走行时间
        - travel_time: 走行时间
        - capacity: 路段通行能力
        - alpha: BPR函数参数，一般取0.15
        - power: BPR函数参数，一般取4.0
        - od_demand_satisfied: 满足的od对的需求，一个数组，包含对以各个节点为o以及d点所满足的总demand
        - global_id: 全局所有网络中唯一的id
    """
    def __init__(self) -> None:
        self.id = 0 # 路段的编号，从零开始编号
        self.p_in_node = None # 路段的起节点
        self.p_out_node = None # 路段的终节点
        self.free_flow_travel_time = 0.0 # 自由流走行时间
        self.travel_time = 0.0 # 走行时间
        self.capacity = 0.0 # 路段通行能力
        self.alpha = 0.15 # BPR函数参数，一般取0.15
        self.power = 4.0 # BPR函数参数，一般取4.0

        self.global_id = -1
        self.od_demand_satisfied = []

class PyODPairs:
    """
    OD对

    - Attributes:
        - id: 节点的编号，从零开始编号
        - p_od_node: OD对起点和终点的列表[O,D]
        - od_demand: OD需求
        - m_n_od_path: OD对之间的路径数量
        - p_od_path: OD对之间的路径集合
        - choice_prob: OD对之间所有路径被选择的概率
    """
    def __init__(self):
        self.id = 0 # 节点的编号，从零开始编号
        self.p_od_node = [] # OD对起点和终点的列表[O,D]
        self.od_demand = 0.0 # OD需求
        self.m_n_od_path = 0 # OD对之间的路径数量
        self.p_od_path = [] # OD对之间的路径集合
        self.choice_prob = [] # OD对之间所有路径被选择的概率

class PyPath:
    """
    路径

    Attributes:
        - id: 路径的编号，从零开始编号
        - link_in_path: 路径里的路段集合
        - path_flow: 路径流量
        - cost_of_path: 路径费用
        - od_pair_id: 所属od对的id
    """
    def __init__(self):
        self.id = 0 # 路径的编号，从零开始编号
        self.link_in_path = [] # 路径里的路段集合
        self.path_flow = 0.0 # 路径流量
        self.cost_of_path = 0.0 # 路径费用
        self.od_pair_id = -1

class PyNetwork:
    """
    算法的主体网络

    Attributes:
        - theta: Theta
        - ita: Ita
        - gama: Gama
        - link_flow: 路段流量
        - descent_direction: 下降方向
        - max_ue_gap: UE的最大误差
        - ue_gap: UE误差
        - cpu_time: CPU Time
        - shortest_path_cost: 最短距离
        - shortest_path_parent: 最短路前继路段
        - output_path: 输出路径

        - m_node: 网络节点集合
        - node_distance_matrix: 网络节点的距离矩阵

        - m_link: 网络路段集合
        - m_path: 网络路径集合
        - m_od_pairs: 网络的OD对集合
        - m_n_node: 节点数
        - m_n_link: 路段数量
        - m_n_od_pairs: 起点数量
        - m_n_path: 路径数量

        - links_flow: 各路段流量
        - title: 路网标题
        - desc: 路网描述

        - avg_flow: 平均路段流
        - avg_speed: 平均速度（travel_time/free_flow_travel_time）
        - alg_cnt: 算法运行次数
        - cost_sum: 应对所有需求的开销
    
    定义了求解算法中的一些重要的变量：
        如模型参数、路段流量、下降方向、UE误差、与网络基本结构四个类有关的统计变量等。
    此外，还在类中构造了实现算法的函数，这些构造函数是算法的主体。
    """
    def __init__(self):
        # 算法参数设置
        # self.theta = 1.0 # Theta
        self.theta = 0.3
        self.ita = 1.5 # Ita
        self.gama = 0.01 # Gama
        self.link_flow = [] # 路段流量
        self.descent_direction = [] # 下降方向
        self.max_ue_gap = 1.0e-10 # UE的最大误差
        self.ue_gap = 0.0 # UE误差
        self.cpu_time = 0.0 # CPU Time
        self.shortest_path_cost = [] # 最短距离
        self.shortest_path_parent = [] # 最短路前继路段
        self.output_path = "./output.txt" # 输出路径

        # 四个类有关
        self.m_node = [] # 网络节点集合
        self.node_distance_matrix = np.array([]) # 网络节点的距离矩阵

        self.m_link = [] # 网络路段集合
        self.m_path = [] # 网络路径集合
        self.m_od_pairs = [] # 网络的OD对集合
        self.m_n_node = 0 # 节点数
        self.m_n_link = 0 # 路段数量
        self.m_n_od_pairs = 0 # 起点数量
        self.m_n_path = 0 # 路径数量

        self.links_flow = [] # 各路段流量
        self.title = "Network" # 标题
        self.desc = "Network Description" # 描述

        self.avg_flow = 0
        self.avg_speed = 0
        self.alg_cnt = 0
        self.cost_sum = 0

    def read_node(self, DataPath):
        """
        读取节点文件
            - DataPath: 节点文件位置

        文件格式：节点编号 X坐标 Y坐标
        """
        # 判断路径是否存在
        if not os.path.exists(DataPath):
            print(f"Node Read Error: {DataPath} does not exist!")
            return
    
        # 开始读取文件
        self.m_node = []
        self.m_n_node = 0
        with open(DataPath, 'r') as f1:
            for row in f1:
                if row == "":
                    continue
                Data = row.split('\t')
                pNode = PyNode()
                pNode.id = self.m_n_node
                pNode.position_x = float(Data[1])
                pNode.position_y = float(Data[2])
                pNode.lat = float(Data[3])
                pNode.lon = float(Data[4])
                self.m_n_node += 1
                self.m_node.append(pNode)

            # 初始化节点距离矩阵
            self.node_distance_matrix = np.full((self.m_n_node, self.m_n_node), float('inf'))
            np.fill_diagonal(self.node_distance_matrix, 0)

    def read_link(self, DataPath):
        """
        读取路段文件
            - DataPath: 路段文件位置
        
        路段文件格式: 路段入节点 路段出节点 自由流走行时间 路段通行能力
        """
        # 判断地址是否存在
        if not os.path.exists(DataPath):
            print(f"{DataPath} does not exist!")
            return
        self.m_link = []
        self.m_n_link = 0
        with open(DataPath, 'r') as f2:
            # 按行读取文件内容
            for row in f2:
                if row == "":
                    continue
                Data = row.split('\t')
                p_link = PyLink()
                p_link.id = self.m_n_link
                p_link.p_in_node = self.m_node[int(Data[0]) - 1]
                p_link.p_out_node = self.m_node[int(Data[1]) - 1]
                p_link.free_flow_travel_time = float(Data[2])
                p_link.capacity = float(Data[3])
                p_link.p_in_node.outgoing_link.append(p_link.id)
                p_link.p_out_node.incoming_link.append(p_link.id)
                self.m_n_link += 1
                self.m_link.append(p_link)

    def read_od_pairs(self, DataPath):
        """
        读取OD对文件
            - DataPath: OD对文件路径

        OD对文件格式：起点 讫点 OD需求
        """
        if not os.path.exists(DataPath):
            print(f"{DataPath} does not exist!")
            return
        self.m_od_pairs = []
        self.m_n_od_pairs = 0
        with open(DataPath, 'r') as f3:
            for row in f3:
                if row == "":
                    continue
                Data = row.split('\t')
                pOrigin = PyODPairs()
                pOrigin.id = self.m_n_od_pairs
                ONode = int(Data[0]) - 1
                pOrigin.p_od_node.append(ONode)
                DNode = int(Data[1]) - 1
                pOrigin.p_od_node.append(DNode)
                pOrigin.od_demand = float(Data[2])
                self.m_n_od_pairs += 1
                self.m_od_pairs.append(pOrigin)

                # 标记节点为OD对中
                self.m_node[ONode].is_od = True
                self.m_node[DNode].is_od = True

    def check_nodes_access(self):
        # 获取该点可达的点
        for node_id in range(self.m_n_node):
            out_links = self.m_node[node_id].outgoing_link
            in_links = self.m_node[node_id].incoming_link
            neighbor_in_nodes = [
                self.m_link[link_id].p_in_node.id for link_id in in_links]
            neighbor_out_nodes = [
                self.m_link[link_id].p_out_node.id for link_id in out_links]
            
            union_nodes_set = set(neighbor_in_nodes).union(neighbor_out_nodes)
            if len(union_nodes_set) <= 2:
                self.m_node[node_id].binary_ways = True
            else:
                self.m_node[node_id].binary_ways = False

        tmp = [node.binary_ways for node in self.m_node]
        print(tmp)


    def _dfs(self, start, end, path=[], paths=[], links_path=[], links_paths=[], path_len=0, paths_len=[], link_num=0, min_path=[100,100]):
        """
        使用dfs算法计算两点间的所有路段
        """
        # print(min_path)
        self.alg_cnt += 1
        path = path + [start]  # 将当前节点添加到路径中
        if start == end:  # 若到达目标节点，将路径添加到结果列表
            paths.append(path)
            links_paths.append(links_path)
            paths_len.append(path_len)
            # if len(links_path) < min_path[0]:
            #     min_path[0] = len(links_paths)
            if link_num < min_path[0]:
                min_path[0] = link_num
            if path_len < min_path[1]:
                min_path[1] = path_len
            # print(f"path_len: {min_path}")
        # elif len(paths) > 0 and (len(links_path) > 6+min_path[0] and path_len > 2 * min_path[1]):
        elif len(paths) > 0 and (link_num > 6+min_path[0] and path_len > 2 * min_path[1]):
        # elif len(paths) > 0 and (path_len > 5 * min_path[1]):
            # print("jianzhi")
            return paths, links_paths, paths_len
        else:
            # if len(paths) > 0:
            #     print(
            #         f"alg: {self.alg_cnt}, minlink: {min_path[0]}, links_path: {len(links_path)}")
            new_link_num = link_num
            if not self.m_node[start].binary_ways:
                new_link_num += 1
            for out_link_id in self.m_node[start].outgoing_link:
                neighbor = self.m_link[out_link_id].p_out_node.id
                if neighbor not in path:  # 避免访问已经在路径中的节点，避免形成环路
                    self._dfs(neighbor, end, path, paths,
                        links_path+[out_link_id], links_paths,
                              path_len+self.m_link[out_link_id].free_flow_travel_time,
                              paths_len, new_link_num, min_path)  # 递归探索相邻节点
        return paths, links_paths, paths_len

    def _bfs(self, start, end):
        """
        通过bfs计算任意两点之间的路段

            - start: 起始节点的node id
            - end: 终止节点的node id
        """
        end_paths_idx = []
        former_nodes_tree = [start]
        from_links_tree = [-1]
        from_idxs_in_tree = [-1]
        visited_nodes = [[start]]
        paths_len = [0]
        now_pos = 0
        min_path_len = float('inf')
        while now_pos < len(former_nodes_tree):
            # 假如当前节点为终点
            now_node_id = former_nodes_tree[now_pos]
            if now_node_id == end:
                end_paths_idx.append(now_pos)
                if paths_len[now_pos] < min_path_len:
                    min_path_len = paths_len[now_pos]
            elif len(end_paths_idx) > 0 and paths_len[now_pos] > 2*min_path_len:
                now_pos += 1
                continue
            else:
                # 遍历所有的出节点
                # now_node = self.m_node[now_node_id]
                for out_link_id in self.m_node[now_node_id].outgoing_link:
                    neighbor = self.m_link[out_link_id].p_out_node.id
                    # 避免访问已经在路径中的节点，避免形成环路
                    if neighbor not in visited_nodes[now_pos]:
                        # 更新记录的数组
                        former_nodes_tree.append(neighbor)
                        from_links_tree.append(out_link_id)
                        from_idxs_in_tree.append(now_pos)
                        visited_nodes.append(visited_nodes[now_pos] + [neighbor])
                        paths_len.append(
                            paths_len[now_pos] + self.m_link[out_link_id].free_flow_travel_time)

            now_pos += 1

        return former_nodes_tree, from_links_tree, from_idxs_in_tree, end_paths_idx, paths_len

    def compute_path_bfs(self):
        """
        通过OD对以及路段信息计算路径信息
        """
        self.m_path = []
        self.m_n_path = 0
        num_in_b = 0

        for od_pair in self.m_od_pairs:
            start_node_id = od_pair.p_od_node[0]
            end_node_id = od_pair.p_od_node[1]
            former_nodes_tree, from_links_tree, from_idxs_in_tree, end_paths_idx, paths_len =\
                self._bfs(start_node_id, end_node_id)
            # 对所有路径进行排序
            paths_len_info = [{"l": paths_len[end_pos], "p": end_pos} for end_pos in end_paths_idx]
            sorted_paths = sorted(paths_len_info, key=lambda x: x["l"])

            # 修改od对中信息
            # 初始化信息
            min_path_len = sorted_paths[0]['l']
            od_pair.p_od_path = []
            od_pair.m_n_od_path = 0

            num_in_b += len(end_paths_idx)
            if len(end_paths_idx) == 0:
                print(f"[Error] No way from node \"{start_node_id}\" to node \"{end_node_id}\"!")
            
            # 遍历创建路径path
            # print(sorted_paths[0]['l'], end=' ')
            for path_len_info_idx in range(len(sorted_paths)):
                path_len_info = sorted_paths[path_len_info_idx]

                if path_len_info['l'] > sorted_paths[path_len_info_idx-1]['l']:
                    if od_pair.m_n_od_path > 8:
                        break
                    elif od_pair.m_n_od_path >= 5 and path_len_info['l'] > 2*min_path_len:
                        break

                # 计算path中的link
                links_path = []
                now_pos = path_len_info['p']
                while from_links_tree[now_pos] != -1:
                    links_path.append(from_links_tree[now_pos])
                    now_pos = from_idxs_in_tree[now_pos]

                # 创建路径信息
                p_path = PyPath()
                p_path.id = self.m_n_path
                p_path.link_in_path = links_path

                # 在od对中记录路径的信息
                od_pair.p_od_path.append(p_path.id)
                p_path.od_pair_id = od_pair.id

                self.m_path.append(p_path)
                self.m_n_path += 1
                od_pair.m_n_od_path += 1

        print(f"path_num: {self.m_n_path}, num_in_b: {num_in_b}")


    def compute_path(self):
        """
        通过OD对以及路段信息计算路径信息
        """
        self.m_path = []
        self.m_n_path  = 0
        num_in_b = 0
        self.check_nodes_access() # 计算节点的可达性
        for od_pair in self.m_od_pairs:
            start_node_id = od_pair.p_od_node[0]
            end_node_id = od_pair.p_od_node[1]
            node_paths, node_links_paths, node_paths_len = self._dfs(
                start_node_id, end_node_id, [], [], [], [], 0, [])
            min_path_len = min(node_paths_len) # 最短的路径长度

            # 修改od对中信息
            # 初始化信息
            od_pair.p_od_path = []
            od_pair.m_n_od_path = 0
            # od_pair.m_n_od_path = len(node_links_paths)

            if len(node_links_paths) == 0:
                print("zero!!!")
            # 使用 zip() 函数将两个列表打包在一起，并根据 node_paths_len 的值进行排序
            sorted_lists = sorted(zip(node_paths_len, node_links_paths))

            # 解压缩排序后的列表
            sorted_paths_len, sorted_paths = zip(*sorted_lists)

            # 遍历创建路径path
            sort_idx = -1
            for now_path in sorted_paths:
                sort_idx += 1

                if od_pair.m_n_od_path > 5 and len(now_path)>2*len(sorted_paths[0]) and sorted_paths_len[sort_idx] > 2*sorted_paths_len[0]:
                    break

                links_path = now_path
                # 创建路径信息
                p_path = PyPath()
                p_path.id = self.m_n_path
                od_pair.p_od_path.append(p_path.id)

                # 遍历路径中路段
                p_path.link_in_path = links_path

                p_path.od_pair_id = od_pair.id
                self.m_path.append(p_path)
                self.m_n_path += 1
                od_pair.m_n_od_path += 1
                if od_pair.m_n_od_path > 8:
                    break
            
            '''
            # 使用桶获取更优的路径集
            paths_barrels = [[] for i in range(5)]
            for lst_link_id in range(len(node_links_paths)):
                barrel_idx = math.ceil(node_paths_len[lst_link_id]/min_path_len)-1
                if barrel_idx < 5:
                    paths_barrels[barrel_idx].append(lst_link_id)
                    num_in_b += 1
            
            # 遍历创建路径path
            for barrel in paths_barrels:
                # 当长度大于两倍的最短长度时，不取
                # if node_paths_len[lst_link_id] > 2*min_path_len:
                #     od_pair.m_n_od_path -= 1
                #     continue
                # if od_pair.m_n_od_path > len(node_links_paths[paths_barrels[0][0]])+2:
                if od_pair.m_n_od_path > 5:
                    break
                
                # 继续遍历桶中path
                for path_idx in barrel:
                    links_path = node_links_paths[path_idx]
                    # 创建路径信息
                    p_path = PyPath()
                    p_path.id = self.m_n_path
                    od_pair.p_od_path.append(p_path.id)

                    # 遍历路径中路段
                    p_path.link_in_path = links_path
                    # for link_id_in_path in links_path:
                    #     p_path.link_in_path.append(link_id_in_path)
                    #     if link_id_in_path >= self.m_n_link:
                    #         print(f"[ERROR] o{start_node_id}, d{end_node_id}; qiguai: {link_id_in_path} \tpath:{links_path}")

                    p_path.od_pair_id = od_pair.id
                    self.m_path.append(p_path)
                    self.m_n_path += 1
                    od_pair.m_n_od_path += 1
                    if od_pair.m_n_od_path > 8:
                        break

            # print(f"od pairs: {od_pair.m_n_od_path}")
            '''
        print(f"path_num: {self.m_n_path}, num_in_b: {num_in_b}")

    def read_path(self, DataPath):
        """
        读取路径集合
            - DataPath: 路径文件地址
        
        """
        # 判断路径是否存在
        if not os.path.exists(DataPath):
            print(f"{DataPath} does not exist!")
            return
        
        # 网络路径集合
        self.m_path = []
        # 路径数量
        self.m_n_path = 0
        
        with open(DataPath, 'r') as f4:
            p_od_pairs = PyODPairs()
            num_of_row = 1
            num_of_path = 0
            num = 0
            for row in f4:
                if row == "":
                    continue
                Data = row.split('\t')

                # 首行数据 OD对编号”、“O点”、“D点”、“OD间的路径数量”
                if num_of_row == 1:
                    od_pairsID = int(Data[0]) - 1
                    num_of_path = int(Data[3])
                    p_od_pairs = self.m_od_pairs[od_pairsID]
                    p_od_pairs.m_n_od_path = num_of_path
                    num_of_row += 1

                    # print(f"{row}", end='')
                    continue

                # OD对中的每条路径
                if num < num_of_path:
                    num += 1
                    p_path = PyPath()
                    p_path.id = self.m_n_path
                    p_od_pairs.p_od_path.append(p_path.id)
                    
                    # 所属od对的id
                    p_path.od_pair_id = od_pairsID
                    link_in_n = int(Data[0]) - 1
                    for node in range(1, len(Data)):
                        link_out_n = int(Data[node]) - 1
                        for link in range(self.m_n_link):
                            p_link = self.m_link[link]
                            if (link_in_n == p_link.p_in_node.id) and (link_out_n == p_link.p_out_node.id):
                                p_path.link_in_path.append(link)
                                break
                        link_in_n = link_out_n
                    self.m_path.append(p_path)
                    self.m_n_path += 1
                    continue
                else:
                    # OD对各条路径读取完毕，读取下一对OD对首行信息
                    num = 0
                    od_pairsID = int(Data[0]) - 1
                    num_of_path = int(Data[3])
                    p_od_pairs = self.m_od_pairs[od_pairsID]
                    p_od_pairs.m_n_od_path = num_of_path
                    
                    # print(f"{row}", end='')

    def route_choice_prob(self, od_pairs):
        """
        计算路径选择概率
        """
        p_od_pairs = self.m_od_pairs[od_pairs]
        choice_prob = []
        Sum = 0
        for path in p_od_pairs.p_od_path:
            p_path = self.m_path[path]
            LogitPara = math.exp(-self.theta * p_path.cost_of_path)
            Sum += LogitPara
            choice_prob.append(LogitPara)
            # if LogitPara == 0:
            #     print("0 nb!")

        for index in range(len(choice_prob)):
            choice_prob[index] /= Sum
        return choice_prob

    def get_ue_gap(self, link_flow):
        """
        间隙函数，获取UE的误差

        Parameters:
            - link_flow: 初始路段流量link_flow（索引对应CLink中的ID）

        Return:
            - 间隙函数值
        """
        num1 = 0
        # 计算被减项分母 + 更新路段走行时间（出行费用：TravelTime）
        for link in range(self.m_n_link):
            p_link = self.m_link[link]
            
            # 更新travel_time
            p_link.travel_time = self.BPR(p_link.free_flow_travel_time, link_flow[link], p_link.capacity)
            
            # 单一求和项的计算
            num1 += (p_link.travel_time * link_flow[link])

        num2 = 0
        self.floyd_algorithm()
        # 计算被减项分子
        for od_pairs in range(self.m_n_od_pairs):
            # 循环遍历OD对
            p_od_pairs = self.m_od_pairs[od_pairs]
            OriginNode = p_od_pairs.p_od_node[0]
            DestinationNode = p_od_pairs.p_od_node[1]
            Demand = p_od_pairs.od_demand
            # ODCost = self.get_shortest_cost(OriginNode, DestinationNode)

            # 改用弗洛伊德算法计算最短路径
            ODCost = self.node_distance_matrix[OriginNode, DestinationNode]
            num2 += (Demand * ODCost)

        # 计算间隙函数值
        UEGap = 1 - num2 / num1
        
        return UEGap

    def BPR(self, FreeFlowTravelTime, Flow, Capacity):
        """
        求解BPR函数

        Parameters:
            - FreeFlowTravelTime: 路段的自由流出行费用
            - Flow: 路段流量
            - Capacity: 通行能力
        """
        if Capacity != 0:
            BPRValue = FreeFlowTravelTime * (1 + 0.15 * (Flow / Capacity) ** 4)
        else:
            BPRValue = float('inf')
        return BPRValue

    def get_vector_norm(self, Vector):
        """
        计算向量的模长

        Parameters:
            - vector: 向量的列表
        """
        Sum = 0
        for value in Vector:
            Sum += value ** 2
        return math.sqrt(Sum)

    def get_shortest_cost(self, Start, End):
        """
        计算最短路距离

        Parameters:
            - Start: 起点的节点id
            - End: 终点的节点id

        Return:
            - 最短路径上的最短距离
        """
        startposition = 0
        endposition = 1

        ShortestPathCost = [float('inf')] * self.m_n_node # 当前最短路径
        ShortestPathParent = [-1] * self.m_n_node # 前驱节点
        checkList = [0] * self.m_n_node # 循环使用的队列
        binCheckList = [False] * self.m_n_node # 是否在队列中
        bscanStatus = [False] * self.m_n_node 

        ShortestPathCost[Start] = 0
        checkList[0] = Start

        while startposition != endposition:
            if startposition >= self.m_n_node:
                startposition = 0
            i = checkList[startposition]
            startposition += 1
            pNode = self.m_node[i]

            # 遍历每一条从节点i离开的路段
            for index in range(len(pNode.outgoing_link)):
                
                p_link = self.m_link[pNode.outgoing_link[index]]
                j = p_link.p_out_node.id # 离开路段的终结点
                value = p_link.travel_time # 离开所需时间

                if ShortestPathCost[j] > ShortestPathCost[i] + value:
                    ShortestPathCost[j] = ShortestPathCost[i] + value
                    ShortestPathParent[j] = i
                    if endposition >= self.m_n_node:
                        endposition = 0
                    checkList[endposition] = j
                    endposition += 1
                    bscanStatus[j] = True
        return ShortestPathCost[End]

    def floyd_algorithm(self):
        """
        弗洛伊德算法计算全局最优路径
        """
        d = np.copy(self.node_distance_matrix)

        # 迭代计算
        for k in range(self.m_n_node):
            d = np.minimum(d, np.add.outer(d[:, k], d[k, :]))

        self.node_distance_matrix = d

    def LogitSUE(self):
        """
        用自适应平均法求解SUE交通分配问题
        """

        # 初始化
        K = 1 # 迭代次数
        Beta = 1
        begtime = time.time()

        # 初始化每个link的od_demand_satisfied
        for link in self.m_link:
            link.od_demand_satisfied = [[0,0] for _ in self.m_node]

        # 基于自由流走行时间更新路径出行费用
        for path in self.m_path:
            path.cost_of_path = 0
            for link in path.link_in_path:
                if link >= self.m_n_link:
                    print(f"error: {link}, {self.m_n_link}")
                p_link = self.m_link[link]
                path.cost_of_path += p_link.free_flow_travel_time

        # 计算路径选择概率
        for od_pairs in range(self.m_n_od_pairs):
            p_od_pairs = self.m_od_pairs[od_pairs]
            p_od_pairs.choice_prob = self.route_choice_prob(od_pairs)

        # 计算路径流量
        for od_pairs in range(self.m_n_od_pairs):
            p_od_pairs = self.m_od_pairs[od_pairs]
            Demand = p_od_pairs.od_demand
            for path in range(p_od_pairs.m_n_od_path):
                p_path = self.m_path[p_od_pairs.p_od_path[path]]
                Prob = p_od_pairs.choice_prob[path]
                p_path.path_flow = Demand * Prob

        # 计算初始路段流量
        link_flow = [0] * self.m_n_link
        for path in range(self.m_n_path):
            p_path = self.m_path[path]
            for link in p_path.link_in_path:
                link_flow[link] += p_path.path_flow

        # 初始化下降方向DescentDirection
        DescentDirection = link_flow[:]

        NormD = self.get_vector_norm(DescentDirection)

        nowtime = time.time()
        start_time = nowtime
        CPUTime = start_time - begtime

        with open(self.output_path, 'w') as tw:
            while NormD > self.max_ue_gap:

                last_now_time = nowtime
                nowtime = time.time()
                # 根据路段流量更新路径阻抗
                for link in range(self.m_n_link):
                    p_link = self.m_link[link]
                    p_link.travel_time = self.BPR(p_link.free_flow_travel_time, link_flow[link], p_link.capacity)

                    in_node_id = p_link.p_in_node.id
                    out_node_id = p_link.p_out_node.id

                    # 初始化距离矩阵
                    if p_link.travel_time < self.node_distance_matrix[in_node_id, out_node_id]:
                        self.node_distance_matrix[in_node_id, out_node_id] = p_link.travel_time

                for path in range(self.m_n_path):
                    p_path = self.m_path[path]
                    p_path.cost_of_path = 0
                    for link in p_path.link_in_path:
                        p_link = self.m_link[link]
                        p_path.cost_of_path += p_link.travel_time

                # 计算路径选择概率
                for od_pairs in range(self.m_n_od_pairs):
                    p_od_pairs = self.m_od_pairs[od_pairs]
                    p_od_pairs.choice_prob = self.route_choice_prob(od_pairs)

                # 计算路径流量
                for od_pairs in range(self.m_n_od_pairs):
                    p_od_pairs = self.m_od_pairs[od_pairs]
                    Demand = p_od_pairs.od_demand
                    for path in range(p_od_pairs.m_n_od_path):
                        p_path = self.m_path[p_od_pairs.p_od_path[path]]
                        Prob = p_od_pairs.choice_prob[path]
                        p_path.path_flow = Demand * Prob

                # 利用公式计算可行下降方向
                new_link_flow = [0] * self.m_n_link

                for path in self.m_path:
                    for link in path.link_in_path:
                        new_link_flow[link] += path.path_flow

                DescentDirection = [link_flow[i] - new_link_flow[i] for i in range(self.m_n_link)]
                NewNormD = self.get_vector_norm(DescentDirection)

                if NewNormD >= NormD:
                    Beta += self.ita
                else:
                    Beta += self.gama

                last_NormD = NormD
                NormD = NewNormD
                Lamuda = 1 / Beta # 步长更新

                # 更新路段流量
                for link in range(self.m_n_link):
                    link_flow[link] -= Lamuda * DescentDirection[link]

                K += 1

                # if K%100 == 0:
                #     print(f"K: {K:05d}, NormD: {NormD}, max_ue_gap: {self.max_ue_gap}")
                # print()

                self.ue_gap = self.get_ue_gap(link_flow)
                
                if (last_NormD == NormD): break
                nowtime = time.time()
                CPUTime = nowtime - begtime
                tw.write(f"{K},{NormD},{CPUTime}\n")

        Z = 0
        # 计算每个link的od_demand_satisfied
        for path in self.m_path:
            p_od_pairs = self.m_od_pairs[path.od_pair_id]
            for link in path.link_in_path:
                p_link = self.m_link[link]
                p_link.od_demand_satisfied[p_od_pairs.p_od_node[0]
                                         ][0] += int(path.path_flow)
                p_link.od_demand_satisfied[p_od_pairs.p_od_node[1]
                                         ][1] += int(path.path_flow)

        # for od_pairs in range(self.m_n_od_pairs):
        #     p_od_pairs = self.m_od_pairs[od_pairs]
        #     # Demand = p_od_pairs.od_demand
        #     for path in range(p_od_pairs.m_n_od_path):
        #         p_path = self.m_path[p_od_pairs.p_od_path[path]]
        #         for link in p_path.link_in_path:
        #             p_link = self.m_link[link]
        #             p_link.od_demand_satisfied[p_od_pairs.p_od_node[0]
        #                                        ][0] += p_path.path_flow
        #             p_link.od_demand_satisfied[p_od_pairs.p_od_node[1]
        #                                        ][1] += p_path.path_flow

        # 计算路径流量
        # 输出结果
        # print("Algorithm Result")
        # print("Link:", self.m_n_link)
        # print("ID\t\tFlow\t\tCost")
        self.links_flow = link_flow # 各路段流量
        for link in range(self.m_n_link):
            p_link = self.m_link[link]
            flow = round(link_flow[link], 0)
            cost = round(p_link.travel_time, 2)
            # print(f"{link}\t\t{flow}\t\t{cost}")
            if p_link.capacity != 0:
                Z += p_link.free_flow_travel_time * (link_flow[link] + 0.03 * (link_flow[link] ** 5) / (p_link.capacity ** 4))

        print()
        SumCost = 0
        for path in self.m_path:
            flow = round(path.path_flow, 0)
            cost = round(path.cost_of_path, 2)
            O = self.m_link[path.link_in_path[0]].p_in_node.id + 1
            D = self.m_link[path.link_in_path[-1]].p_out_node.id + 1
            SumCost += path.path_flow * path.cost_of_path
        self.cost_sum = SumCost

        for link_idx in range(self.m_n_link):
            self.avg_flow += self.links_flow[link_idx]
            self.avg_speed += self.m_link[link_idx].free_flow_travel_time/self.m_link[link_idx].travel_time
        self.avg_flow /= self.m_n_link
        self.avg_speed /= self.m_n_link

        endtime = time.time()
        CPUTime = endtime - begtime
        # print()
        # print("Number of Iterations:", K)
        print("Objective Function:", Z)
        print("Total Impedance:", SumCost)
        print(f"LogitSUE End, CPUTime: {CPUTime} seconds")

    def change_link_capcity(self, link_idx: int, new_capacity: float):
        """
        修改路段的通行能力

        Parameters:
            - link_idx: 路段序号
            - new_capacity: 修改的目标值
        """
        res = self.m_link[link_idx].capacity - new_capacity
        if res == 0:
            return -1
        elif res > 0:
            res = 2
        else: res = 1

        self.m_link[link_idx].capacity = new_capacity
        return res

    def change_link_free_travel_time(self, link_idx: int, free_flow_travel_time: float):
        """
        修改路段自由流通行时间

        Parameters:
            - link_idx: 路段序号
            - free_flow_travel_time: 修改的目标值
        """
        res = self.m_link[link_idx].free_flow_travel_time - free_flow_travel_time
        self.m_link[link_idx].free_flow_travel_time = free_flow_travel_time
        if res == 0:
            return -1
        elif res > 0:
            return 7
        else: return 8
        
    def change_algorithm_parameter(self, theta: float, ita: float, gama: float, max_ue_gap: float):
        """
        修改算法的超参数

        parameters:
            - theta: Theta
            - ita: ita
            - gama: Gama
            - max_ue_gap: UE的最大误差
        """
        self.theta = theta
        self.ita = ita
        self.gama = gama
        self.max_ue_gap = max_ue_gap

    def add_link(self, start_pt_id: int, end_pt_id: int, capacity:float, free_flow_travel_time: float, recompute_paths=True):
        """
        新增一条路段
        """
        # 判断是否原本就存在这条路段
        for now_link in self.m_link:
            if now_link.p_in_node.id == start_pt_id and now_link.p_out_node.id == end_pt_id:
                new_edits = []
                if capacity > now_link.capacity:
                    now_link.capacity = capacity
                    new_edits.append(1)
                if now_link.free_flow_travel_time < free_flow_travel_time:
                    now_link.free_flow_travel_time = free_flow_travel_time
                    new_edits.append(7)
                return now_link.id, new_edits

        p_link = PyLink()
        p_link.id = self.m_n_link
        p_link.p_in_node = self.m_node[start_pt_id]
        p_link.p_out_node = self.m_node[end_pt_id]
        p_link.free_flow_travel_time = free_flow_travel_time
        p_link.capacity = capacity
        p_link.p_in_node.outgoing_link.append(p_link.id)
        p_link.p_out_node.incoming_link.append(p_link.id)
        self.m_n_link += 1
        self.m_link.append(p_link)

        # 更新path
        if recompute_paths:
            self.compute_path_bfs()
        # self.add_path_from_link(p_link.id)
        return p_link.id, [5]

    def del_link(self, links_to_del: list, recompute_paths=True):
        """
        删除已有节点
            - links_to_del: 需要删除的路段的id列表
        """
        links_to_del.sort(reverse=True)
        for link_id_to_del in links_to_del:
            if link_id_to_del >= self.m_n_link:
                continue

            link_to_del = self.m_link[link_id_to_del]
            node_a = link_to_del.p_in_node
            node_b = link_to_del.p_out_node

            # 删除节点存储的信息
            node_a.outgoing_link.remove(link_id_to_del)
            node_b.incoming_link.remove(link_id_to_del)

            # 修改id信息
            for node in self.m_node:
                for i in range(len(node.outgoing_link)):
                    if node.outgoing_link[i] > link_id_to_del:
                        node.outgoing_link[i] -= 1
                for i in range(len(node.incoming_link)):
                    if node.incoming_link[i] > link_id_to_del:
                        node.incoming_link[i] -= 1
            self.m_link.remove(self.m_link[link_id_to_del])
            for link in self.m_link:
                if link.id > link_id_to_del:
                    link.id -= 1
            self.m_n_link -= 1

        # print(self.m_n_link)
        # print(len(self.m_link))
        if recompute_paths:
            self.compute_path_bfs()

    def add_node(self, node_lat, node_lng, former_link_a_id, linka_fftt, former_link_b_id=-1, linkb_fftt=[-1,-1]):
        """
        在原始道路中新增节点
        """
        # 将节点加入网络
        pNode = PyNode()
        pNode.id = self.m_n_node
        pNode.lat = float(node_lat)
        pNode.lon = float(node_lng)
        self.m_n_node += 1
        self.m_node.append(pNode)

        # 初始化节点距离矩阵
        self.node_distance_matrix = np.full((self.m_n_node, self.m_n_node), float('inf'))
        np.fill_diagonal(self.node_distance_matrix, 0)

        # 保存老路段信息
        link_a = self.m_link[former_link_a_id]
        a_dir_capacity = link_a.capacity
        link_b = link_a
        b_dir_capacity = a_dir_capacity
        if former_link_b_id != -1:
            link_b = self.m_link[former_link_b_id]
            b_dir_capacity = link_b.capacity
        former_a_fftt = link_a.free_flow_travel_time
        former_b_fftt = link_b.free_flow_travel_time
        node_a_id = link_a.p_in_node.id
        node_b_id = link_a.p_out_node.id

        # 删除老路段
        links_to_del = []
        if former_link_b_id != -1 and former_link_a_id != former_link_b_id:
            self.del_link([former_link_a_id, former_link_b_id], False)
            links_to_del = [former_link_a_id, former_link_b_id]
        else:
            self.del_link([former_link_a_id], False)
            links_to_del = [former_link_a_id]
            
        # 新建路段
        self.add_link(node_a_id, pNode.id,
                      a_dir_capacity, linka_fftt[0], False)
        self.add_link(pNode.id, node_b_id,
                      a_dir_capacity, linka_fftt[1], False)
        if former_link_b_id != -1:
            self.add_link(node_b_id, pNode.id,
                        b_dir_capacity, linkb_fftt[0], False)
            self.add_link(pNode.id, node_a_id,
                        b_dir_capacity, linkb_fftt[1], False)
            
        # 重新设置path
        if former_link_a_id != former_link_b_id and former_a_fftt == linka_fftt[0]+linka_fftt[1]:
            links_new = [pNode.incoming_link, pNode.outgoing_link]
            for pPath in self.m_path:
                links_in_path = pPath.link_in_path
                for link_del_idx in range(len(links_to_del)):
                    if links_to_del[link_del_idx] in links_in_path:
                        link_idx_in_path = links_in_path.index(
                            links_to_del[link_del_idx])
                        pPath.link_in_path = links_in_path[:link_idx_in_path] + [
                            links_new[0][link_del_idx]+len(links_to_del), 
                            links_new[1][link_del_idx]+len(links_to_del)] + \
                            links_in_path[link_idx_in_path+1:]
                        
                # 更新path中原本link的id
                links_in_path = pPath.link_in_path
                for link_idx_in_path in range(len(links_in_path)):
                    for link_del_idx in range(len(links_to_del)):
                        if links_in_path[link_idx_in_path] > links_to_del[link_del_idx]:
                            pPath.link_in_path[link_idx_in_path] -= 1
            return False
        else:
            # 通过计算重新获取路径
            self.compute_path_bfs()
        return True

    def del_node(self, node_id):
        """
        删除节点
        - node_id: 要删除的节点的id
        """
        # 获取该点可达的点
        out_links = self.m_node[node_id].outgoing_link
        in_links = self.m_node[node_id].incoming_link
        neighbor_in_nodes = [
            self.m_link[link_id].p_in_node.id for link_id in in_links]
        neighbor_out_nodes = [
            self.m_link[link_id].p_out_node.id for link_id in out_links]
        
        # 获取起始与终点的OD对
        start_od_pairs = []
        end_od_pairs = []
        for od_pair in self.m_od_pairs:
            if od_pair.p_od_node[0] == node_id:
                start_od_pairs.append(od_pair.id)
            elif od_pair.p_od_node[1] == node_id:
                end_od_pairs.append(od_pair.id)

        # 该点有需求，不能轻易删除
        if len(start_od_pairs)>0 and len(end_od_pairs)>0:
            return False

        # 连接该节点的路段
        self.del_link(out_links+in_links, False)
        # self.del_link(in_links, False)
        print(f"links del: {len(out_links)}, {len(in_links)}, links last: {self.m_n_link}")

        # 删除该节点
        self.m_node.pop(node_id)

        # 重新计算OD对之间的路径
        self.compute_path_bfs()

        return True

    def add_path_from_link(self, from_link_id):
        """
        将link配套的path添加
        """
        # 获取link及其起始与终止点
        from_p_link = self.m_link[from_link_id]
        start_node_id = from_p_link.p_in_node
        end_node_id = from_p_link.p_out_node

        paths_to_add = []
        for origin_path in self.m_path:
            node_start_on = False
            node_end_on = False

            path_to_push = PyPath()
            path_to_push.od_pair_id = origin_path.od_pair_id
            # 搜索是否包含起始与终止路段
            for alink_in_path_idx in origin_path.link_in_path:
                alink_in_path = self.m_link[alink_in_path_idx]
                # 判断是否可以开始连接入路段
                if not node_start_on:
                    if alink_in_path.p_in_node == from_p_link.p_in_node:
                        node_start_on = True

                # 复制原始路径的途径路段，
                if not node_start_on or node_end_on:
                    path_to_push.link_in_path.append(alink_in_path_idx)

                # 判断是否可以结束路段的连接
                if node_start_on and not node_end_on:
                    if alink_in_path.p_out_node == from_p_link.p_out_node:
                        path_to_push.link_in_path.append(from_link_id)
                        node_end_on = True
            
            # 判断是否可以将路段插入原始路径中形成新路径
            if node_end_on:
                paths_to_add.append(path_to_push)
    
        # 将新路径插入原始地图
        for new_path in paths_to_add:
            new_path.id = self.m_n_path
            od_pairsID = new_path.od_pair_id

            # 添加到网络中
            self.m_od_pairs[od_pairsID].p_od_path.append(new_path.id)
            self.m_od_pairs[od_pairsID].m_n_od_path += 1
                    # p_od_pairs = self.m_od_pairs[od_pairsID]
                    # p_od_pairs.m_n_od_path = num_of_path
            self.m_path.append(new_path)

            self.m_n_path += 1

        return


# import tqdm
if __name__ == "__main__":
    # Initialize the Net
    network = PyNetwork()

    # Update the file paths to your data files
    network.read_node("data/Node_SiouxFalls.txt")
    network.read_link("data/Link_SiouxFalls.txt")
    network.read_od_pairs("data/ODPairs_SiouxFalls.txt")
    start = time.time()
    # network.compute_path()
    network.compute_path_bfs()
    # for od_pair in tqdm.tqdm(network.m_od_pairs):
    # for od_pair in network.m_od_pairs:
    #     start_node_id = od_pair.p_od_node[0]
    #     end_node_id = od_pair.p_od_node[1]
    #     network._bfs(start_node_id, end_node_id)
    end = time.time()
    print(f"compute path time: {end-start:.05f}s")

    network.add_node(43.51732391499998, -96.78675666500001, 36, [1.5, 1.5], 37, [1.5, 1.5])

    # Run the solution algorithm
    network.LogitSUE()
