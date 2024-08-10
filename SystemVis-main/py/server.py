from flask import Flask, request
from flask_cors import cross_origin
import pulp
import json
import cv2
import base64
from sklearn.cluster import KMeans, DBSCAN, HDBSCAN, SpectralClustering
import math


from inspect import Parameter
from pyomo.environ import *
import numpy as np
from sys import getsizeof

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
  
  
@app.route("/locateComponentArray", methods=["POST"])
@cross_origin(supports_credentials=True)
def locateComponentArray():
  # img = cv2.imread('Group 24.png', 0)
  data = json.loads(request.data) # 将json字符串转为dict
  background_uri = data['background_uri'] # srs
  template_uri = data['template_uri'] # srs
  n_array =  data['nArray']
  x = data['x']
  y = data['y']
  
  
  background_img = data_uri_to_cv2_img(background_uri)
  pawn_white_template = data_uri_to_cv2_img(template_uri)
  
  # Piece templates:
  background_img_rgb = cv2.cvtColor(background_img,cv2.COLOR_BGR2RGB)
  background_img_gray = cv2.cvtColor(background_img_rgb,cv2.COLOR_BGR2GRAY)

  pawn_white_template_rgb = cv2.cvtColor(pawn_white_template,cv2.COLOR_BGR2RGB)
  pawn_white_template_gray = cv2.cvtColor(pawn_white_template_rgb, cv2.COLOR_BGR2GRAY)

  # w_pawn_white, h_pawn_white = pawn_white_template.shape[::-1]
  res_pawn_white = cv2.matchTemplate(background_img_gray,pawn_white_template_gray,cv2.TM_CCOEFF_NORMED)


  threshhold = 0.6
  loc = np.where(res_pawn_white >= threshhold)

  matching_results = []
  for pt in zip(*loc[::-1]):
    matching_results.append([int(pt[0]), int(pt[1])])
    # cv2.rectangle(background_img_rgb,pt,(pt[0]+w_pawn_white, pt[1]+h_pawn_white),(0,255,255),1)
    
  # hdb = HDBSCAN()
  # hdb_result = hdb.fit(matching_results)
  # clustering_result = SpectralClustering(n_clusters=5, assign_labels='discretize', random_state=0).fit(matching_results)
  clustering_result = DBSCAN(eps=50, min_samples=2).fit(matching_results)
  
  clusters = [[], [], [], [], [], [], [], [], []]
  for i in range(len(matching_results)):
    if clustering_result.labels_[i] >= 0:
      clusters[clustering_result.labels_[i]].append(matching_results[i])
    # print(matching_results[i], clustering_result.labels_[i])
  ret_tmp = []
  for cluster in clusters:
    if len(cluster) > 0:
      means = list(np.mean(cluster, axis=0))
      d = math.sqrt((means[0] - x) * (means[0] - x) + (means[1] - y) * (means[1] - y))
      if (d > 50):
        ret_tmp.append(means)
  
  ret_tmp = np.sort(ret_tmp, axis=0)
  ret = []
  for p in ret_tmp:
    ret.append([int(p[0]), int(p[1])])
    
  return {
    'matching_results': ret
  }

def data_uri_to_cv2_img(uri):
  encoded_data = uri.split(',')[1]
  nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
  # old (python 2 version):
  # nparr = np.fromstring(encoded_data.decode('base64'), np.uint8)

  img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
  return img

# data_uri = "data:image/jpeg;base64,/9j/4AAQ..."
# img = data_uri_to_cv2_img(data_uri)


# 通过methods设置POST请求
@app.route('/ilp', methods=["POST"])
@cross_origin(supports_credentials=True)
def json_request():

  # 接收处理json数据请求
  data = json.loads(request.data) # 将json字符串转为dict
  srs = data['sensor_relations'] # srs
  prs = data['position_relations'] # prs
  nos = data['number_of_sensors'] # nos
  nop = data['number_of_positions'] # nop
  nosr = len(srs)
  nopr = len(prs)
  
  if nos != nop:
    print("\n ERROR \n")

  print(srs, prs, nos)
  
  nVar = nos * nop + nosr * nopr
  varDict = []
  varDictReversed = {}
  vi = 0
  for i in range(nos):
    for j in range(nop):
      # vi 相当于 把第i个传感器放到第j个位置上
      varDict.append('x_' + str(i) + '_' + str(j))
      varDictReversed['x_' + str(i) + '_' + str(j)] = vi
      vi += 1
  for i in range(nosr):
    for j in range(nopr):
      sr = srs[i]
      pr = prs[j]
      # vi 相当于 把第sr[0]个传感器放到第pr[0]个位置上且把第sr[1]个传感器放到第pr[1]个位置上
      varDict.append('m_' + str(sr[0]) + '_' + str(pr[0]) + '_' + str(sr[1]) + '_' + str(pr[1]))
      varDictReversed['m_' + str(sr[0]) + '_' + str(pr[0]) + '_' + str(sr[1]) + '_' + str(pr[1])] = vi
      vi += 1
  costs = [0 for i in range(nos * nop)] + [1 for i in range(nosr * nopr)]
  print(nVar, len(costs), vi)
  
  
  model = pulp.LpProblem("Maximize gain", pulp.LpMaximize)
  Vars = pulp.LpVariable.dicts("var",
                              (varIndex for varIndex in range(nVar)),
                              cat='Binary')
  # Objective Function
  model += (
    pulp.lpSum([costs[j]*Vars[j] for j in range(nVar)])
  )
  
  # Constraints
  # mat for 1 sensor 1 position
  for si in range(nos): # for each sensor
    print('72', si, nos)
    A = [0 for i in range(nVar)]
    for i in range(nos):
      A[i + si * nop] = 1
    # print(A)
    model += pulp.lpSum([A[j]*Vars[j] for j in range(nVar)]) == 1
  for pi in range(nop): # for each sensor
    print('79', pi, nop)
    A = [0 for i in range(nVar)]
    for i in range(nop):
      A[i + pi * nos] = 1
    # print(A)
    model += pulp.lpSum([A[j]*Vars[j] for j in range(nVar)]) == 1
  
  # mat for m
  for i in range(nosr * nopr):
    print('88', i, nosr * nopr)
    vi = i + nos * nop
    var_key = varDict[vi]
    if var_key[0] != 'm':
      print("\n ERROR \n")
    keys = var_key.split('_')
    sa = int(keys[1])
    pi = int(keys[2])
    xi1 = varDictReversed['x_' + str(sa) + '_' + str(pi)]
    sb = int(keys[3])
    pj = int(keys[4])
    xi2 = varDictReversed['x_' + str(sb) + '_' + str(pj)]
    
    A = [0 for i in range(nVar)]
    A[vi] = -2 # for m
    A[xi1] = 1
    A[xi2] = 1
    model += pulp.lpSum([A[j]*Vars[j] for j in range(nVar)]) >= 0
  
  solver = pulp.getSolver('PULP_CBC_CMD', timeLimit=120)
  print('solving')
  model.solve(solver)
  print('solved')
  ret = [int(Vars[j].varValue) for j in range(nVar)]
  
  return {
      "result": ret
  }

if __name__ == '__main__':
    app.run(debug=True)