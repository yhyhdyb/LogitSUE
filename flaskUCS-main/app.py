from Network import PyNetwork
from flask import Flask, jsonify, request, render_template, send_file
from flask_cors import CORS
import copy

app = Flask(__name__)
CORS(app)


def _get_links(network_idx: int):
    """
    private 获取路段信息
    """
    tmpNetwork = network
    if network_idx >= 0 and network_idx < len(network_layers):
        tmpNetwork = network_layers[network_idx]
    
    links = []
    link_idx = 0
    for link in tmpNetwork.m_link:
        links.append({
            'ID': link.id,
            'pInNode': link.p_in_node.id,
            'pOutNode': link.p_out_node.id,
            'freeFlowTravelTime': link.free_flow_travel_time,
            'travelTime': link.travel_time,
            'flow': tmpNetwork.links_flow[link_idx],
            'capacity': link.capacity,
            'globalId': link.global_id,
            'originDemand': link.od_demand_satisfied
        })
        link_idx += 1
    return links

def _get_nodes(network_idx: int):
    """
    private 获取特定网络节点信息
    """
    tmpNetwork = network
    if network_idx >= 0 and network_idx < len(network_layers):
        tmpNetwork = network_layers[network_idx]

    nodes = []
    for node in tmpNetwork.m_node:
        nodes.append({
            'id': node.id,
            'PositionX': node.position_x,
            'PositionY': node.position_y,
            'lon': node.lon,
            'lat': node.lat,
            'OriginID': node.origin_id,
            'IncomingLink': node.incoming_link,
            'OutgoingLink': node.outgoing_link,
            'globalId': node.global_id,
            'isOd': node.is_od
        })
    return nodes

def _global_info_set(network_idx: int):
    """
    设置全局的网络信息（共有的节点/路段信息）
    """
    tmpNetwork = network
    if network_idx >= 0 and network_idx < len(network_layers):
        tmpNetwork = network_layers[network_idx]

    # 节点信息
    for i in range(tmpNetwork.m_n_node):
        if tmpNetwork.m_node[i].global_id == -1:
            now_node_info = [tmpNetwork.m_node[i].lat, tmpNetwork.m_node[i].lon]
            try:
                now_global_idx = nodes_global_info.index(now_node_info)
            except ValueError as e:
                # 找不到
                now_global_idx = len(nodes_global_info)
                nodes_global_info.append(now_node_info)
                tmpNetwork.m_node[i].global_id = now_global_idx
    
    # 还差路段信息s
    # global_links_flow_scope
    for i in range(tmpNetwork.m_n_link):
        if tmpNetwork.m_link[i].global_id == -1:
            now_link_info = [tmpNetwork.m_link[i].p_in_node.global_id,
                             tmpNetwork.m_link[i].p_out_node.global_id]
            try:
                now_global_idx = links_global_info.index(now_link_info)
            except ValueError as e:
                # 找不到
                now_global_idx = len(links_global_info)
                links_global_info.append(now_link_info)
                tmpNetwork.m_link[i].global_id = now_global_idx

def _update_global_links_info():
    """
    通过路段信息更新全局的路网信息
    """
    global_links_val_scope['fftt'] = [[float('inf'), -1, 0]
                                            for i in range(len(links_global_info))]
    global_links_val_scope['travelTime'] = [[float('inf'), -1, 0]
                                            for i in range(len(links_global_info))]
    global_links_val_scope['speed'] = [[float('inf'), -1, 0]
                                            for i in range(len(links_global_info))]
    global_links_val_scope['flow'] = [[float('inf'), -1, 0]
                                      for i in range(len(links_global_info))]
    global_links_val_scope['capacity'] = [[float('inf'), -1, 0]
                                            for i in range(len(links_global_info))]
    global_links_val_scope['flowRatio'] = [[float('inf'), -1, 0]
                                       for i in range(len(links_global_info))]
    
    global_links_num = [0 for _ in range(len(links_global_info))]
    
    # 遍历每个路网的信息
    for network_idx in range(-1, len(network_layers)):
        tmpNetwork = network
        if network_idx >= 0 and network_idx < len(network_layers):
            tmpNetwork = network_layers[network_idx]
        
        for i in range(tmpNetwork.m_n_link):
            global_link_id = tmpNetwork.m_link[i].global_id
            global_links_num[global_link_id] += 1
    
    # 讲数量为0的道路设置默认值
    for i in range(len(global_links_num)):
        if global_links_num[i] == 0:
            global_links_val_scope['fftt'][i] = [0,0,0]
            global_links_val_scope['travelTime'][i] = [0,0,0]
            global_links_val_scope['speed'][i] = [0,0,0]
            global_links_val_scope['flow'][i] = [0,0,0]
            global_links_val_scope['capacity'][i] = [0,0,0]
            global_links_val_scope['flowRatio'][i] = [0,0,0]

    for network_idx in range(-1, len(network_layers)):
        tmpNetwork = network
        if network_idx >= 0 and network_idx < len(network_layers):
            tmpNetwork = network_layers[network_idx]
        
        for i in range(tmpNetwork.m_n_link):
            global_link_id = tmpNetwork.m_link[i].global_id
            # print(f'global_link_id: {global_link_id}')
            now_link = tmpNetwork.m_link[i]

            # 整理全局的路段信息
            # fftt
            fftt_info = global_links_val_scope['fftt'][global_link_id]
            if now_link.free_flow_travel_time < fftt_info[0]:
                fftt_info[0] = now_link.free_flow_travel_time
            if now_link.free_flow_travel_time > fftt_info[1]:
                fftt_info[1] = now_link.free_flow_travel_time
            fftt_info[2] += now_link.free_flow_travel_time / \
                global_links_num[global_link_id]

            # travel time
            tt_info = global_links_val_scope['travelTime'][global_link_id]
            if now_link.travel_time < tt_info[0]:
                tt_info[0] = now_link.travel_time
            if now_link.travel_time > tt_info[1]:
                tt_info[1] = now_link.travel_time
            tt_info[2] += now_link.travel_time/global_links_num[global_link_id]
            
            # speed
            speed_info = global_links_val_scope['speed'][global_link_id]
            now_speed = now_link.free_flow_travel_time / now_link.travel_time
            if now_speed < speed_info[0]:
                speed_info[0] = now_speed
            if now_speed > speed_info[1]:
                speed_info[1] = now_speed
            speed_info[2] += now_speed / global_links_num[global_link_id]

            # flow
            flow_info = global_links_val_scope['flow'][global_link_id]
            if tmpNetwork.links_flow[i] < flow_info[0]:
                flow_info[0] = tmpNetwork.links_flow[i]
            if tmpNetwork.links_flow[i] > flow_info[1]:
                flow_info[1] = tmpNetwork.links_flow[i]
            flow_info[2] += tmpNetwork.links_flow[i] / \
                global_links_num[global_link_id]

            # capacity
            c_info = global_links_val_scope['capacity'][global_link_id]
            if now_link.capacity < c_info[0]:
                c_info[0] = now_link.capacity
            if now_link.capacity > c_info[1]:
                c_info[1] = now_link.capacity
            c_info[2] += now_link.capacity/global_links_num[global_link_id]

            # flow_ratio
            fr_info = global_links_val_scope['flowRatio'][global_link_id]
            now_fr = tmpNetwork.links_flow[i]/now_link.capacity
            if now_fr < fr_info[0]:
                fr_info[0] = now_fr
            if now_fr > fr_info[1]:
                fr_info[1] = now_fr
            fr_info[2] += now_fr/global_links_num[global_link_id]

    return

@app.route('/network/del')
def del_network_layer():
    """
    删除路网图层
    """
    del_origin_idx = eval(request.args.get('originIdx'))
    child_idx = -1
    
    # tmpNetwork = PyNetwork()
    if del_origin_idx < 0 or del_origin_idx >= len(network_layers):
        return jsonify({
            "static": 0,
            "editLogs": network_edits,
            "result": f"network layer id invalid. valid range: [0, {len(network_layers)})",
        })
    else:
        # 重新设置父节点
        for i in range(len(network_father)):
            if network_father[i]-1 == del_origin_idx:
                network_father[i] = network_father[del_origin_idx]
                
                # 将父节点的更改转移到子节点上
                for j in range(len(network_edits[del_origin_idx])):
                    network_edits[i][j] = network_edits[del_origin_idx][j]

            elif network_father[i]-1 > del_origin_idx:
                network_father[i] -= 1
        network_father.pop(del_origin_idx+1)
        network_layers.pop(del_origin_idx)

        # 修改编辑统计
        network_edits.pop(del_origin_idx)

    return jsonify({
        "static": 1,
        "editLogs": network_edits,
        "result": "success"
    })

@app.route('/network/recursionDel')
def recursion_del_networks_layer():
    """
    删除路网图层
    """
    networks_to_del = eval(request.args.get('networksToDel'))
    # if not isinstance(networks_to_del, list):
    #     networks_to_del = [networks_to_del]
    try:
        iterator = iter(networks_to_del)
    except TypeError:
        networks_to_del = [networks_to_del]
    
    networks_to_del = sorted(networks_to_del)

    # tmpNetwork = PyNetwork()
    for del_origin_idx in networks_to_del[::-1]:
        # del_origin_idx -= 1
        if del_origin_idx < 0 or del_origin_idx >= len(network_layers):
            continue
        else:
            # 重新设置父节点
            for i in range(len(network_father)):
                if network_father[i]-1 == del_origin_idx:
                    network_father[i] = network_father[del_origin_idx]
                elif network_father[i]-1 > del_origin_idx:
                    network_father[i] -= 1

            network_father.pop(del_origin_idx+1)
            network_layers.pop(del_origin_idx)
            # 修改编辑统计
            network_edits.pop(del_origin_idx)


    return jsonify({
        "static": 1,
        "result": "success",
        "father_arr": network_father
    })

@app.route('/network/info/all')
def get_all_networks_info():
    """
    获取所有网络的基本信息
    """
    networks_info = []
    networks_info.append({
        "id": 0,
        "title": network.title,
        "desc": network.desc,
        "father": network_father[0]
    })
    network_idx = 0
    for tmp_network in network_layers:
        network_idx += 1
        networks_info.append({
            "id": network_idx,
            "title": tmp_network.title,
            "desc": tmp_network.desc,
            "father": network_father[network_idx]
        })
    return jsonify(networks_info)

def _get_network_data(network_idx: int):
    """
    获取特定网络的所有数据
    """
    tmpNetwork = network
    editLog = []
    if network_idx >= 0 and network_idx < len(network_layers):
        tmpNetwork = network_layers[network_idx]
        editLog = network_edits[network_idx]
    else: network_idx = -1

    network_data = {
        "id": network_idx+1,
        "title": tmpNetwork.title,
        "desc": tmpNetwork.desc,
        "father": network_father[network_idx+1],
        "links": _get_links(network_idx),
        "nodes": _get_nodes(network_idx),
        "editLog": editLog,
        "globalNodes": nodes_global_info,
        "globalLinks": links_global_info,
        "globalLinksInfo": global_links_val_scope,
        "avgFlow": tmpNetwork.avg_flow,
        "avgSpeed": tmpNetwork.avg_speed,
        "costSum": tmpNetwork.cost_sum
    }
    return network_data


@app.route('/data/global/all')
def get_global_info():
    """
    获取全局信息
    """
    # 计算所有网络平均flow与平均traveltime的取值范围
    avg_flows =  [network.avg_flow] + [now_network.avg_flow for now_network in network_layers]
    avg_speeds = [network.avg_speed] + \
        [now_network.avg_speed for now_network in network_layers]
    costs_sum = [network.cost_sum] + \
        [now_network.cost_sum for now_network in network_layers]
    diff_avg_flow = [avg_flows[i]-avg_flows[network_father[i]]
                     for i in range(1, len(network_father))]
    diff_avg_speed = [avg_speeds[i]-avg_speeds[network_father[i]]
                      for i in range(1, len(network_father))]
    diff_cost_sum = [costs_sum[i]-costs_sum[network_father[i]]
                      for i in range(1, len(network_father))]

    min_avg_flow = min(avg_flows)
    max_avg_flow = max(avg_flows)
    all_avg_flow = sum(avg_flows) / len(avg_flows)
    min_avg_speed = min(avg_speeds)
    max_avg_speed = max(avg_speeds)
    all_avg_speed = sum(avg_speeds) / len(avg_speeds)
    min_cost_sum = min(costs_sum)
    max_cost_sum = max(costs_sum)
    avg_cost_sum = sum(costs_sum) / len(costs_sum)

    if len(network_father) > 1:
        min_diff_avg_flow = min(diff_avg_flow)
        max_diff_avg_flow = max(diff_avg_flow)
        min_diff_avg_speed = min(diff_avg_speed)
        max_diff_avg_speed = max(diff_avg_speed)
        min_diff_cost_sum = min(diff_cost_sum)
        max_diff_cost_sum = max(diff_cost_sum)
    else:
        min_diff_avg_flow = 0
        max_diff_avg_flow = 0
        min_diff_avg_speed = 0
        max_diff_avg_speed = 0
        min_diff_cost_sum = 0
        max_diff_cost_sum = 0

    # link的排序依据
    # link_sort_basis = [global_links_val_scope["speed"][i][1] -
    #                    global_links_val_scope["speed"][i][0] for i in range(len(links_global_info))]
    # sorted_list = sorted(link_sort_basis)
    # linkSortedIdx = []
    # sorted_idxs_stat = [[] for x in link_sort_basis]
    # for i in range(len(link_sort_basis)):
    #     sorted_idx = sorted_list.index(link_sort_basis[i])
    #     sorted_idxs_stat[sorted_idx].append(i)
    # for sorted_idx_stat in sorted_idxs_stat:
    #     linkSortedIdx.extend(sorted_idx_stat)

    # 展示所有信息
    network_data = {
        "minAvgFlow": min_avg_flow,
        "maxAvgFlow": max_avg_flow,
        "allAvgFlow": all_avg_flow,

        "minAvgSpeed": min_avg_speed,
        "maxAvgSpeed": max_avg_speed,
        "allAvgSpeed": all_avg_speed,

        "minCostsSum": min_cost_sum,
        "maxCostsSum": max_cost_sum,
        "avgCostsSum": avg_cost_sum,

        "minDiffAvgFlow": min_diff_avg_flow,
        "maxDiffAvgFlow": max_diff_avg_flow,
        "minDiffAvgSpeed": min_diff_avg_speed,
        "maxDiffAvgSpeed": max_diff_avg_speed,
        "minDiffCostSum": min_diff_cost_sum,
        "maxDiffCostSum": max_diff_cost_sum,

        "nodesPos": nodes_global_info,
        "linksPos": links_global_info,
        "globalLinksInfo": global_links_val_scope,
        # "linkSortedIdx": linkSortedIdx,
        # "nodesPos": 
    }
    return network_data

@app.route('/data/all')
def get_all_networks_data():
    """
    获取所有网络的数据
    """
    network_num = len(network_layers)
    networks_data = []
    for i in range(-1, network_num):
        networks_data.append(_get_network_data(network_idx=i))
    return networks_data


@app.route('/data/duplicate')
def duplicate_networks_data():
    """
    获取网络的数据，并将网络返回
    """
    copy_origin_idx = eval(request.args.get('originIdx'))
    # 设置父节点
    network_father.append(copy_origin_idx+1)

    tmpNetwork = PyNetwork()
    if copy_origin_idx < 0 or copy_origin_idx >= len(network_layers):
        tmpNetwork = copy.deepcopy(network)
        network_father[-1] = 0
    else:
        tmpNetwork = copy.deepcopy(network_layers[copy_origin_idx])

    tmpNetwork.title += ' copy'
    network_layers.append(tmpNetwork)

    # 编辑树
    if copy_origin_idx >= 0 and copy_origin_idx < len(network_layers):
        network_edits.append(copy.deepcopy(network_edits[copy_origin_idx]))
        for network_edit_info in network_edits[-1]:
            network_edit_info['edit_on_this'] = False
    else:
        network_edits.append([])

    _global_info_set(len(network_layers)-1)
    return jsonify(_get_network_data(network_idx=len(network_father)-2))


@app.route('/data/newLink')
def new_network_link():
    """
    添加一条路段
    """
    network_idx = eval(request.args.get('networkIdx'))
    start_pt_id = eval(request.args.get('startPtId'))
    end_pt_id = eval(request.args.get('endPtId'))
    capacity = eval(request.args.get('capacity'))
    free_flow_travel_time = eval(request.args.get('freeFlowTravelTime'))
    i_capacity = eval(request.args.get('iCapacity'))
    i_free_flow_travel_time = eval(request.args.get('iFreeFlowTravelTime'))
    i_exist = request.args.get('iExist') == 'true'
    

    tmp_network = network
    if network_idx >= 0 and network_idx < len(network_layers):
        tmp_network = network_layers[network_idx]

    link_id1, new_edits1 = tmp_network.add_link(start_pt_id, end_pt_id, capacity, free_flow_travel_time, False)
    if i_exist:
        link_id2, new_edits2 = tmp_network.add_link(end_pt_id, start_pt_id, i_capacity, i_free_flow_travel_time)
        new_edits1 = list(set(new_edits1).union(new_edits2))
    else:
        tmp_network.compute_path_bfs()
        
    tmp_network.LogitSUE()

    # 修改编辑树
    for new_edit_type in new_edits1:
        network_edits[network_idx].append(
            {"edit_type": new_edit_type, "edit_on_this": True})

    _global_info_set(network_idx)
    _update_global_links_info()
    return jsonify(_get_network_data(network_idx))

@app.route('/data/delLink')
def del_network_link():
    """
    删除一条路段
    """
    network_idx = eval(request.args.get('networkIdx'))
    links_to_del = eval(request.args.get('linksIdx'))

    tmp_network = network
    if network_idx >= 0 and network_idx < len(network_layers):
        tmp_network = network_layers[network_idx]

    if type(links_to_del) == int:
        tmp_network.del_link([links_to_del])
    else:
        tmp_network.del_link(links_to_del)
    tmp_network.LogitSUE()

    # 修改编辑树
    network_edits[network_idx].append({"edit_type": 6, "edit_on_this": True})

    _update_global_links_info()
    return jsonify(_get_network_data(network_idx))


@app.route('/data/newNode')
def new_network_node():
    """
    添加一个节点
    """
    network_idx = eval(request.args.get('networkIdx'))
    node_lat = eval(request.args.get('nodeLat'))
    node_lng = eval(request.args.get('nodeLng'))
    former_link_a_id = eval(request.args.get('formerLinkA'))
    linka_fftt = eval(request.args.get('aFFTT'))
    former_link_b_id = eval(request.args.get('formerLinkB'))
    linkb_fftt = eval(request.args.get('bFFTT'))

    tmp_network = network
    if network_idx >= 0 and network_idx < len(network_layers):
        tmp_network = network_layers[network_idx]

    add_node_res = tmp_network.add_node(node_lat, node_lng, former_link_a_id,
                         linka_fftt, former_link_b_id, linkb_fftt)

    former_cost = tmp_network.cost_sum
    tmp_network.LogitSUE()
    if not add_node_res:
        tmp_network.cost_sum = former_cost

    # 修改编辑树
    network_edits[network_idx].append({"edit_type": 3, "edit_on_this": True})

    _global_info_set(network_idx)
    _update_global_links_info()
    return jsonify(_get_network_data(network_idx))


@app.route('/data/delNode')



def del_network_node():
    """
    删除一个节点
    """
    network_idx = eval(request.args.get('networkIdx'))
    node_to_del = eval(request.args.get('nodeIdx'))

    tmp_network = network
    if network_idx >= 0 and network_idx < len(network_layers):
        tmp_network = network_layers[network_idx]

    res = tmp_network.del_node(node_to_del)
    if res:
        tmp_network.LogitSUE()

        # 修改编辑树
        network_edits[network_idx].append({"edit_type": 4, "edit_on_this": True})

        _update_global_links_info()
    return jsonify(_get_network_data(network_idx))


@app.route('/data/linkReset')
def reset_network_link():
    """
    修改路段属性
    """
    network_idx = eval(request.args.get('networkIdx'))
    link_idx = eval(request.args.get('linkIdx'))
    new_free_flow_travel_time = eval(request.args.get('freeFlowTravelTime'))
    new_capacity = eval(request.args.get('capacity'))

    tmp_network = network
    if network_idx >= 0 and network_idx < len(network_layers):
        tmp_network = network_layers[network_idx]
    
    # 修改编辑树
    res1 = tmp_network.change_link_free_travel_time(link_idx, new_free_flow_travel_time)
    if res1 >= 1:
        network_edits[network_idx].append(
            {"edit_type": res1, "edit_on_this": True})
        print(f"res: {res1}")
    
    res2 = tmp_network.change_link_capcity(link_idx, new_capacity)
    if res2 >= 1:
        network_edits[network_idx].append(
            {"edit_type": res2, "edit_on_this": True})
        print(f"res: {res2}")
    
    if res1 >= 1 or res2 >= 1:
        tmp_network.LogitSUE()
    _update_global_links_info()
    return jsonify(_get_network_data(network_idx))


@app.route('/network/switchPos')
def switch_network_layer_pos():
    """
    修改网络的编号
    """
    network_idx = eval(request.args.get('networkIdx'))
    target_network_idx = eval(request.args.get('targetNetworkIdx'))

    if network_idx < 0 or target_network_idx < 0:
        return jsonify({
            "static": 0,
            "fatherArr": network_father,
            "editLogs": network_edits
        })

    # 修改父节点，以免其出现在父节点之前
    while network_father[network_idx+1]-1 >= target_network_idx:
        network_father[network_idx +
                       1] = network_father[network_father[network_idx+1]]
        
    # 修改编辑日志
    now_fa_idx = network_father[network_idx+1] - 1
    for i in range(len(network_edits[now_fa_idx]), len(network_edits[network_idx])):
        network_edits[network_idx]['edit_on_this'] = True
    
    # 修改位置
    network_to_switch = network_layers.pop(network_idx)
    network_layers.insert(target_network_idx, network_to_switch)
    
    return jsonify({
        "static": 1,
        "fatherArr": network_father,
        "editLogs": network_edits
    })



if __name__ == '__main__':
    network_layers = []
    network_father = [-1]

    # 全局的节点与路段信息
    nodes_global_info = []
    links_global_info = []
    global_links_val_scope = {"fftt": [], "travelTime": [], "speed":[], "capacity": [], "flow": [], "flowRatio": []}

    # edit_type 1提高capacity 2降低capacity 3新建节点 4删除节点 5新建路段 6删除路段 7降低freeflowtraveltime 8提高fftt
    # edit_on_this 是否在本网络上修改
    network_edits = []

    # Initialize the Net 
    network = PyNetwork()

    # Update the file paths to your data files
    network.read_node("data/Node_SiouxFalls.txt")
    network.read_link("data/Link_SiouxFalls.txt")
    network.read_od_pairs("data/ODPairs_SiouxFalls.txt")
    # network.read_path("data/Path_SiouxFalls.txt")
    network.compute_path_bfs()

    # Run the solution algorithm
    network.LogitSUE()
    _global_info_set(-1)
    _update_global_links_info()

    # Run backend
    app.run(debug=True,port=8081)
