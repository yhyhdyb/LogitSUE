import { defineStore } from 'pinia'
import axios from 'axios'

interface tsNode {
  lat: number
  lon: number
  id: number
}

interface tsLink {
  pInNode: number
  pOutNode: number
  id: number
  freeFlowTravelTime: number
  travelTime: number
  flow: number
  capacity: number
  speed: number
}

interface tsNetwork {
  title: string
  desc: string
  id: number
  father: number
  nodes: tsNode[]
  links: tsLink[]
}


export const useNetworksData = defineStore('networksInfo', {
  state: () => ({
    networksInfoArr: [] as tsNetwork[],
    networkShow: [] as boolean[],
    networksFatherIdx: [] as number[],
    now_showing_network: -1
  }),
  getters: {
    // 计算属性
  },
  actions: {
    req_links_to_links(req_links: tsLink[]) {
      // 将request的links列表转换为前端格式
      const res_links = new Array<tsLink>()
      for (let i = 0; i < req_links.length; i++) {
        res_links.push({
          id: req_links[i].id,
          pInNode: req_links[i].pInNode,
          pOutNode: req_links[i].pOutNode,
          freeFlowTravelTime: req_links[i].freeFlowTravelTime,
          travelTime: req_links[i].travelTime,
          flow: req_links[i].flow,
          capacity: req_links[i].capacity,
          speed: req_links[i].travelTime / req_links[i].freeFlowTravelTime
        })
      }
      return res_links
    },
    req_nodes_to_nodes(req_nodes: tsNode[]) {
      // 将request的nodes列表转换为前端格式
      const res_nodes = new Array<tsNode>()
      for (let i = 0; i < req_nodes.length; i++) {
        res_nodes.push({
          id: req_nodes[i].id,
          lat: req_nodes[i].lat,
          lon: req_nodes[i].lon
        })
      }
      return res_nodes
    },
    async networksInitialization() {
      // 初始化所有数据
      this.networksInfoArr = new Array()
      this.networkShow = new Array()
      this.networksFatherIdx = new Array()
      this.now_showing_network = -1
      try {
        const response = await axios.get('http://localhost:8081/data/all')
        const req_get_networks = new Array<tsNetwork>()
        const network_data_req = response.data as tsNetwork[]
        for (let i = 0; i < network_data_req.length; i++) {
          req_get_networks.push({
            id: network_data_req[i].id,
            title: network_data_req[i].title,
            desc: network_data_req[i].desc,
            father: network_data_req[i].father,
            nodes: this.req_nodes_to_nodes(network_data_req[i].nodes),
            links: this.req_links_to_links(network_data_req[i].links)
          })
          this.networkShow.push(false)
          this.networksFatherIdx.push(network_data_req[i].father)
        }
        this.networksInfoArr = req_get_networks
      } catch (error) {
        console.log('Network Data Initialization Error: ', error)
      }
    },
    linksInfoSet(network_idx: number, req_layer_links: tsLink[]) {
      const tmp_layers_links = new Array<tsLink>()
      for (let j = 0; j < req_layer_links.length; j++) {
        // tmp_layers_links[i].push(req_layers_links)
        const now_link: tsLink = {
          id: req_layer_links[j].id,
          pInNode: req_layer_links[j].pInNode,
          pOutNode: req_layer_links[j].pOutNode,
          freeFlowTravelTime: req_layer_links[j].freeFlowTravelTime,
          travelTime: req_layer_links[j].travelTime,
          flow: req_layer_links[j].flow,
          capacity: req_layer_links[j].capacity,
          speed: req_layer_links[j].travelTime / req_layer_links[j].freeFlowTravelTime
        }
        tmp_layers_links.push(now_link)
      }
      this.networksInfoArr[network_idx].links = tmp_layers_links
    },
    async newLink(
      network_idx: number,
      start_pt_id: number,
      end_pt_id: number,
      free_flow_travel_time: number,
      capacity: number,
      i_free_flow_travel_time: number,
      i_capacity: number,
      iExist: boolean
    ) {
      try {
        const response = await axios.get('http://localhost:8081/link/new', {
          params: {
            networkIdx: network_idx - 1,
            startPtId: start_pt_id,
            endPtId: end_pt_id,
            capacity: capacity,
            freeFlowTravelTime: free_flow_travel_time,
            iCapacity: i_capacity,
            iFreeFlowTravelTime: i_free_flow_travel_time,
            iExist: iExist
          }
        })
        const req_layer_links = response.data as tsLink[]
        this.linksInfoSet(network_idx, req_layer_links)
        console.log('success!!!')
      } catch (error) {
        console.log('New Link Error', error)
      }
    },
    async resetLink(
      network_idx: number,
      link_idx: number,
      free_flow_travel_time: number,
      capacity: number
    ) {
      try {
        const response = await axios.get('http://localhost:8081/data/linkReset', {
          params: {
            networkIdx: network_idx - 1,
            capacity: capacity,
            freeFlowTravelTime: free_flow_travel_time,
            linkIdx: link_idx
          }
        })
        const req_layer_links = response.data as tsLink[]
        this.linksInfoSet(network_idx, req_layer_links)
        console.log('success!!!')
      } catch (error) {
        console.log('Reset Link Error', error)
      }
    },
    async networkDuplicate(origin_network_idx: number) {
      // 复制网络内容
      try {
        const response = await axios.get('http://localhost:8081/data/duplicate', {
          params: {
            originIdx: origin_network_idx - 1
          }
        })
        const req_duplicate_network = response.data as tsNetwork
        const network_to_add = {
          id: req_duplicate_network.id,
          title: req_duplicate_network.title,
          desc: req_duplicate_network.desc,
          father: req_duplicate_network.father,
          nodes: this.req_nodes_to_nodes(req_duplicate_network.nodes),
          links: this.req_links_to_links(req_duplicate_network.links)
        }
        this.networksInfoArr.push(network_to_add)
        this.networkShow.push(false)
        this.networksFatherIdx.push(network_to_add.father)
        return req_duplicate_network.id
      } catch (error) {
        console.log('Network Duplicated Error', error)
      }
      return -1
    },
    async networkDelete(network_idx: number) {
      try {
        const _this = this
        const response = await axios.get(
          'http://localhost:8081/network/del?originIdx=' + (network_idx - 1)
        )
        if (response.data.static == 1) {
          console.log('Network Deleted')
          _this.networksInfoArr.splice(network_idx, 1)
          _this.networkShow.splice(network_idx, 1)
          for (let i = 0; i < _this.networksInfoArr.length; i++) {
            _this.networksInfoArr[i].id = i
          }
        } else {
          console.log('Networks Delete Error', response.data.result)
        }
      } catch (error) {
        console.log('Network Delete Error, ', error)
      }
    },
    async networkRecursionDelete(network_idx: number) {
      // 迭代删除网络
      try {
        const response = await axios.get(
          'http://localhost:8081/network/recursionDel?networksToDel=' + (network_idx - 1)
        )
        if (response.data.static == 1) {
          console.log('Network Deleted')
          this.networksInfoArr.splice(network_idx, 1)
          this.networkShow.splice(network_idx, 1)
          for (let i = 0; i < this.networksInfoArr.length; i++) {
            this.networksInfoArr[i].id = i
          }
        } else {
          console.log('Networks Delete Error', response.data.result)
        }
      } catch (error) {
        console.log('Network Delete Error, ', error)
      }
    },
    async network_link_reset(
      // 修改路段信息
      network_idx: number,
      start_pt_id: number,
      link_id: number,
      free_flow_travel_time: number,
      capacity: number
    ) {
      try {
        const response = await axios.get('http://localhost:8081/data/linkReset', {
          params: {
            networkIdx: network_idx - 1,
            linkIdx: link_id,
            capacity: capacity,
            freeFlowTravelTime: free_flow_travel_time
          }
        })
        const req_layer_links = response.data as tsLink[]
        this.linksInfoSet(network_idx, req_layer_links)
      } catch (error) {
        console.log('Reset Link Error', error)
      }
    },
    getSelNetworkMapInfo(network_idx: number) {
      // 获取选中网络的节点信息
      const nodes_num = this.networksInfoArr[network_idx].nodes.length
      const sel_network_nodes_pos = new Array<number[]>()
      for (let i = 0; i < nodes_num; i++) {
        sel_network_nodes_pos.push([
          this.networksInfoArr[network_idx].nodes[i].lat,
          this.networksInfoArr[network_idx].nodes[i].lon
        ])
      }

      // 获取选中的单个网络的路段信息
      const link_num = this.networksInfoArr[network_idx].links.length
      const sel_network_links_flow = new Array<number>(link_num)
      const sel_network_links_travel_time = new Array<number>(link_num)
      const sel_network_links_speed = new Array<number>(link_num)
      const sel_network_links_pos = new Array<number[][]>()
      const nodes_in_links = new Array<number[]>()
      for (let i = 0; i < link_num; i++) {
        sel_network_links_flow[i] = this.networksInfoArr[network_idx].links[i].flow
        sel_network_links_travel_time[i] = this.networksInfoArr[network_idx].links[i].travelTime
        sel_network_links_speed[i] = this.networksInfoArr[network_idx].links[i].speed
        sel_network_links_pos.push([
          sel_network_nodes_pos[this.networksInfoArr[network_idx].links[i].pInNode],
          sel_network_nodes_pos[this.networksInfoArr[network_idx].links[i].pOutNode]
        ])
        nodes_in_links.push([
          this.networksInfoArr[network_idx].links[i].pInNode,
          this.networksInfoArr[network_idx].links[i].pOutNode
        ])
      }

      const bi_links = new Array<number[]>()
      const bi_links_flow = new Array<number>()
      const bi_links_speed = new Array<number>()
      const bi_links_node_pos = new Array<number[][]>()
      let bi_flow_scope = 0
      let bi_speed_scope = 0
      for (let i = 0; i < link_num; i++) {
        const bi_link_idx = sel_network_links_pos.indexOf([
          sel_network_links_pos[i][1],
          sel_network_links_pos[i][0]
        ])
        if (bi_link_idx != -1 && bi_link_idx > i) {
          bi_links.push([i, bi_link_idx])
          bi_links_flow.push((sel_network_links_flow[i] + sel_network_links_flow[bi_link_idx]) / 2)
          bi_links_speed.push(
            (sel_network_links_speed[i] + sel_network_links_speed[bi_link_idx]) / 2
          )
          bi_links_node_pos.push([
            sel_network_nodes_pos[this.networksInfoArr[network_idx].links[i].pInNode],
            sel_network_nodes_pos[this.networksInfoArr[network_idx].links[i].pOutNode]
          ])
        } else if (bi_link_idx == -1) {
          bi_links.push([i])
          bi_links_flow.push(sel_network_links_flow[i])
          bi_links_speed.push(sel_network_links_speed[i])
          bi_links_node_pos.push([
            sel_network_nodes_pos[this.networksInfoArr[network_idx].links[i].pInNode],
            sel_network_nodes_pos[this.networksInfoArr[network_idx].links[i].pOutNode]
          ])
        }
        if (Math.abs(bi_links_flow[bi_links_flow.length - 1]) > bi_flow_scope) {
          bi_flow_scope = Math.abs(bi_links_flow[bi_links_flow.length - 1])
        }
        if (Math.abs(bi_links_speed[bi_links_speed.length - 1]) > bi_speed_scope) {
          bi_speed_scope = Math.abs(bi_links_speed[bi_links_speed.length - 1])
        }
      }
      return {
        nodes_pos: sel_network_nodes_pos,
        links_flow: sel_network_links_flow,
        links_travel_time: sel_network_links_travel_time,
        links_speed: sel_network_links_speed,
        links_flow_scope: [
          Math.min(...sel_network_links_flow),
          Math.max(...sel_network_links_flow)
        ],
        links_speed_scope: [
          Math.min(...sel_network_links_speed),
          Math.max(...sel_network_links_speed)
        ],
        links_pos: sel_network_links_pos,
        nodes_in_links: nodes_in_links
        // 双边统计
        // bi_links: bi_links,
        // bi_links_speed: bi_links_speed,
        // bi_links_flow: bi_links_flow,
        // bi_speed_scope: bi_speed_scope,
        // bi_flow_scope: bi_flow_scope,
        // bi_links_node_pos: bi_links_node_pos
      }
    },
    getSelComparedNetworksMapInfo(network_a_idx: number, network_b_idx: number) {
      // 获取选中网络的节点信息：a是最新选中的网络
      const nodes_a_num = this.networksInfoArr[network_a_idx].nodes.length
      const nodes_b_num = this.networksInfoArr[network_b_idx].nodes.length
      const sel_network_nodes_pos = new Array<number[]>()
      const a2nodes = new Array<number>()
      const b2nodes = new Array<number>()
      const nodes2a = new Array<number>()
      const nodes2b = new Array<number>()
      for (let i = 0; i < nodes_a_num; i++) {
        const now_node_pos = [
          this.networksInfoArr[network_a_idx].nodes[i].lat,
          this.networksInfoArr[network_a_idx].nodes[i].lon
        ]
        sel_network_nodes_pos.push(now_node_pos)
        a2nodes.push(i)
        nodes2a.push(i)
        nodes2b.push(-1)
      }
      for (let i = 0; i < nodes_b_num; i++) {
        const now_node_pos = [
          this.networksInfoArr[network_b_idx].nodes[i].lat,
          this.networksInfoArr[network_b_idx].nodes[i].lon
        ]
        // const b_in_pos = sel_network_nodes_pos.indexOf(now_node_pos)
        const b_in_pos = sel_network_nodes_pos.findIndex((element) => {
          return element[0] == now_node_pos[0] && element[1] == now_node_pos[1]
        })
        if (b_in_pos == -1) {
          sel_network_nodes_pos.push(now_node_pos)
          b2nodes.push(sel_network_nodes_pos.length - 1)
          nodes2a.push(-1)
          nodes2b.push(i)
        } else {
          b2nodes.push(b_in_pos)
          nodes2b[b_in_pos] = i
        }
      }

      // 获取选中的单个网络的路段信息
      const links_a_num = this.networksInfoArr[network_a_idx].links.length
      const links_b_num = this.networksInfoArr[network_b_idx].links.length
      const sel_network_a_links_flow = new Array<number>()
      const sel_network_a_links_travel_time = new Array<number>()
      const sel_network_b_links_flow = new Array<number>()
      const sel_network_b_links_travel_time = new Array<number>()
      const sel_network_links_node_pos = new Array<number[]>()

      const a2links = new Array<number>()
      const b2links = new Array<number>()
      const links2a = new Array<number>()
      const links2b = new Array<number>()
      for (let i = 0; i < links_a_num; i++) {
        sel_network_a_links_flow.push(this.networksInfoArr[network_a_idx].links[i].flow)
        sel_network_a_links_travel_time.push(
          this.networksInfoArr[network_a_idx].links[i].travelTime
        )
        sel_network_links_node_pos.push([
          a2nodes[this.networksInfoArr[network_a_idx].links[i].pInNode],
          a2nodes[this.networksInfoArr[network_a_idx].links[i].pOutNode]
        ])

        a2links.push(i)
        links2a.push(i)
        links2b.push(-1)
      }
      for (let i = 0; i < links_b_num; i++) {
        sel_network_b_links_flow.push(this.networksInfoArr[network_b_idx].links[i].flow)
        sel_network_b_links_travel_time.push(
          this.networksInfoArr[network_b_idx].links[i].travelTime
        )

        const now_link_pos = [
          b2nodes[this.networksInfoArr[network_b_idx].links[i].pInNode],
          b2nodes[this.networksInfoArr[network_b_idx].links[i].pOutNode]
        ]
        // const link_in_arr = sel_network_links_node_pos.indexOf(now_link_pos)
        const link_in_arr = sel_network_links_node_pos.findIndex((element) => {
          return element[0] == now_link_pos[0] && element[1] == now_link_pos[1]
        })

        if (link_in_arr == -1) {
          sel_network_links_node_pos.push(now_link_pos)
          b2links.push(sel_network_links_node_pos.length - 1)
          links2b.push(i)
          links2a.push(-1)
        } else {
          b2links.push(link_in_arr)
          links2b[link_in_arr] = i
        }
      }

      const compared_links_flow = new Array<number>()
      const compared_links_travel_time = new Array<number>()
      const compared_links_speed = new Array<number>()
      const compared_links_state = new Array<boolean>()
      let max_links_flow_scope = 0
      let max_links_travel_time_scope = 0
      let max_links_speed_scope = 0
      for (let i = 0; i < sel_network_links_node_pos.length; i++) {
        const a_idx = links2a[i]
        const b_idx = links2b[i]
        if (a_idx != -1 && b_idx != -1) {
          compared_links_state.push(true)
          compared_links_flow.push(
            sel_network_a_links_flow[a_idx] - sel_network_b_links_flow[b_idx]
          )
          compared_links_travel_time.push(
            sel_network_a_links_travel_time[a_idx] - sel_network_b_links_travel_time[b_idx]
          )
          compared_links_speed.push(
            this.networksInfoArr[network_a_idx].links[a_idx].speed -
              this.networksInfoArr[network_b_idx].links[b_idx].speed
          )
        } else {
          compared_links_state.push(false)
          if (b_idx == -1 && a_idx != -1) {
            compared_links_flow.push(sel_network_a_links_flow[a_idx])
            compared_links_travel_time.push(sel_network_a_links_travel_time[a_idx])
            compared_links_speed.push(this.networksInfoArr[network_a_idx].links[a_idx].speed)
          } else if (b_idx != -1 && a_idx == -1) {
            compared_links_flow.push(-sel_network_b_links_flow[b_idx])
            compared_links_travel_time.push(-sel_network_b_links_travel_time[b_idx])
            compared_links_speed.push(-this.networksInfoArr[network_b_idx].links[b_idx].speed)
          }
        }

        if (compared_links_state[i]) {
          if (Math.abs(compared_links_flow[i]) > max_links_flow_scope)
            max_links_flow_scope = Math.abs(compared_links_flow[i])
          if (Math.abs(compared_links_speed[i]) > max_links_speed_scope)
            max_links_speed_scope = compared_links_speed[i]
          if (Math.abs(compared_links_travel_time[i]) > max_links_travel_time_scope)
            max_links_travel_time_scope = Math.abs(compared_links_travel_time[i])
        }
      }

      const links_pos = new Array<number[][]>()
      for (let i = 0; i < sel_network_links_node_pos.length; i++) {
        links_pos.push([
          sel_network_nodes_pos[sel_network_links_node_pos[i][0]],
          sel_network_nodes_pos[sel_network_links_node_pos[i][1]]
        ])
      }

      const bi_links = new Array<number[]>()
      const bi_links_speed = new Array<number>()
      const bi_links_flow = new Array<number>()
      let bi_max_speed_scope = 0
      let bi_max_flow_scope = 0
      for (let i = 0; i < sel_network_links_node_pos.length; i++) {
        const op_link_nodes = [sel_network_links_node_pos[i][1], sel_network_links_node_pos[i][0]]
        // const op_link = sel_network_links_node_pos.indexOf(op_link_nodes)
        const op_link = sel_network_links_node_pos.findIndex((element) => {
          return element[0] == op_link_nodes[0] && element[1] == op_link_nodes[1]
        })

        if (op_link != -1 && op_link > i) {
          bi_links.push([i, op_link])
          bi_links_speed.push((compared_links_speed[i] + compared_links_speed[op_link]) / 2)
          bi_links_flow.push((compared_links_speed[i] + compared_links_speed[op_link]) / 2)
        } else if (op_link == -1) {
          bi_links.push([i])
          bi_links_speed.push(compared_links_speed[i])
          bi_links_flow.push(compared_links_speed[i])
        }

        if (Math.abs(bi_links_speed[bi_links_speed.length - 1]) > bi_max_speed_scope) {
          bi_max_speed_scope = Math.abs(bi_links_speed[bi_links_speed.length - 1])
        }
        if (Math.abs(bi_links_flow[bi_links_flow.length - 1]) > bi_max_flow_scope) {
          bi_max_flow_scope = Math.abs(bi_links_flow[bi_links_flow.length - 1])
        }
      }

      // 路径坐标
      const bi_links_node_pos = new Array<number[][]>()
      for (let i = 0; i < bi_links.length; i++) {
        const now_link_idx = bi_links[i][0]
        bi_links_node_pos.push([
          sel_network_nodes_pos[sel_network_links_node_pos[now_link_idx][0]],
          sel_network_nodes_pos[sel_network_links_node_pos[now_link_idx][1]]
        ])
      }

      return {
        // 点相关
        nodes_a_num: nodes_a_num,
        nodes_b_num: nodes_b_num,
        nodes_pos: sel_network_nodes_pos,
        a2nodes: a2nodes,
        b2nodes: b2nodes,
        nodes2a: nodes2a,
        nodes2b: nodes2b,
        // 线相关
        links_a_num: links_a_num,
        links_b_num: links_b_num,
        sel_network_a_links_flow: sel_network_a_links_flow,
        sel_network_a_links_travel_time: sel_network_a_links_travel_time,
        sel_network_b_links_flow: sel_network_b_links_flow,
        sel_network_b_links_travel_time: sel_network_b_links_travel_time,
        sel_network_links_node_pos: sel_network_links_node_pos,
        a2links: a2links,
        b2links: b2links,
        links2a: links2a,
        links2b: links2b,
        links_pos: links_pos,
        // 线统计
        compared_links_flow: compared_links_flow,
        compared_links_travel_time: compared_links_travel_time,
        compared_links_speed: compared_links_speed,
        compared_links_state: compared_links_state,
        delta_flow_scope: max_links_flow_scope,
        delta_speed_scope: max_links_speed_scope,
        nodes_in_links: sel_network_links_node_pos
        // 双边统计
        // bi_links: bi_links,
        // bi_links_speed: bi_links_speed,
        // bi_links_flow: bi_links_flow,
        // bi_speed_scope: bi_max_speed_scope,
        // bi_flow_scope: bi_max_flow_scope,
        // bi_links_node_pos: bi_links_node_pos
      }
    }
  }
})
