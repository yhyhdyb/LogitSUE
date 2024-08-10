export const generateSensorRelations = (sensorGroups: SensorGroup[], allSensors: string[]) => {
  const aspects = ['location', 'measurement']
  const relationsGroups: RelationsGroup[] = []
  aspects.forEach((aspect, i) => {
    for (const sensorGroup of sensorGroups) {
      if (sensorGroup.aspect === aspect) {
        const relationsGroup: RelationsGroup = {
          weight: 1,
          aspect,
          relations: []
        }
        for (const sensors of sensorGroup.groups) {
          for (let i = 0; i < sensors.length; i++) {
            for (let j = 0; j < sensors.length; j++) {
              if (i != j) {
                const si = sensors[i]
                const sj = sensors[j]
                const indexOfSi = allSensors.indexOf(si)
                const indexOfSj = allSensors.indexOf(sj)
                if (indexOfSi > -1 && indexOfSj > -1) {
                  relationsGroup.relations.push([allSensors.indexOf(si), allSensors.indexOf(sj)])
                }
              }
            }
          }
        }
        relationsGroups.push(relationsGroup)
      }
    }
  })

  return relationsGroups
}

export const generatePositionEdges = (points: [number, number, number][], d: number) => {
  const edges: [number, number, number][] = [] // the 3td item for weight
  for (let i = 0; i < points.length; i++) {
    for (let j = i + 1; j < points.length; j++) {
      const pi = points[i]
      const pj = points[j]
      const dx = pi[0] - pj[0]
      const dy = pi[1] - pj[1]
      const distance = Math.sqrt(dx * dx + dy * dy)
      if (distance < d * 1.1) {
        edges.push([pi[2], pj[2], 1])
      } else if (distance < d * 1.5) {
        edges.push([pi[2], pj[2], 0.5])
      }
    }
  }
  return edges
}

export const generateTypeSimilarity = (sensors: string[], batteryGroupsByType: [string[], string[], string[]]) => {
  const sensorTypeDicts: TypeSimilarity = {
    category: {},
    numeric: {},
    boolean: {}
  }
  const [categoricalSensorNames, booleanSensorNames, numericSensorNames] = batteryGroupsByType
  for (const sensorName in categoricalSensorNames) {
    sensorTypeDicts.category[sensors.indexOf(sensorName)] = true
  }
  for (const sensorName in booleanSensorNames) {
    sensorTypeDicts.category[sensors.indexOf(sensorName)] = true
  }
  for (const sensorName in numericSensorNames) {
    sensorTypeDicts.category[sensors.indexOf(sensorName)] = true
  }
  // for (const sensorName in sensors) {
  //   count += 1
  //   if (nums[sensorName] === '') {
  //     sensorTypeDicts.category[sensors.indexOf(sensorName)] = true
  //   } else {
  //     sensorTypeDicts.numeric[sensors.indexOf(sensorName)] = true
  //   }
  // }
  return sensorTypeDicts
}