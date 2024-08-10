import csv
import json
import math
types = []

# with open('src/assets/M15.csv') as f:
with open('src/assets/sample_data_resample_1T.csv') as f:
  f_csv = csv.reader(f)
  headers = next(f_csv)
  # print(headers)
  valueDicts = []
  for h in headers:
    valueDicts.append({})
  
  for row in f_csv:
    for index in range(len(row)):
      cell = row[index]
      valueDicts[index][str(cell)] = 1
  
  for index in range(len(valueDicts)):
    valueDict = valueDicts[index]
    # print(len(valueDict.keys()), headers[index])
    if len(valueDict.keys()) == 2 and (float(list(valueDict.keys())[0]) + float(list(valueDict.keys())[1]) == 1):
      types.append({
        'name': headers[index],
        'type': 'boolen'
      })
      # boolean
    elif len(valueDict.keys()) == 1 and float(list(valueDict.keys())[0]) == 0:
      types.append({
        'name': headers[index],
        'type': 'boolean'
      })
      # boolean
    elif len(valueDict.keys()) < 10:
      types.append({
        'name': headers[index],
        'type': 'categorical'
      })
      # cate
    else:
      types.append({
        'name': headers[index],
        'type': 'numeric'
      })
      #numerci

print('\n')
  
# with open('src/assets/M13.csv') as f:
with open('src/assets/sample_data_resample_1T.csv') as f:
  f_csv = csv.reader(f)
  headers = next(f_csv)

  rangeDicts = []
  for headerIndex in range(len(headers)):
    h = headers[headerIndex]
    rangeDicts.append({
      'type': types[headerIndex]['type'],
      'max': float('-inf'),
      'min': float('inf')
    })
    
  for row in f_csv:
    for headerIndex in range(len(row)):
      if types[headerIndex]['type'] == 'numeric':
        cell = float(row[headerIndex])
        h = headers[headerIndex]
        if (h == '第EE层风门开度反馈' and cell > 0.6):
          print(cell)
        if cell < rangeDicts[headerIndex]['min']:
          rangeDicts[headerIndex]['min'] = cell
        if cell > rangeDicts[headerIndex]['max']:
          rangeDicts[headerIndex]['max'] = cell
  
  output = ''
  categoricalSensors = []
  booleanSensors = []
  numericSensors = []
  for headerIndex in range(len(rangeDicts)):
    range = rangeDicts[headerIndex]
    header = headers[headerIndex]
    if range['type'] == 'numeric':
      numericSensors.append(header)
      output += ('\'' + header + '\': \'n,' + str(range['min']) + ',' + str(range['max']) + '\',\n')
    elif range['type'] == 'boolean':
      booleanSensors.append(header)
      output += ('\'' + header + '\': \'b\'' + ',\n')
    else:
      categoricalSensors.append(header)
      output += ('\'' + header + '\': \'c\'' + ',\n')
      
  # print(output)
  
  # print(categoricalSensors)
  # print(booleanSensors)
  # print(numericSensors)
    