import { compileScript } from 'vue/compiler-sfc'
import {
  generateSensorRelations,
  generatePositionEdges,
  generateTypeSimilarity,
} from '@/utils/ILP'
import { cloneDeep, flatten } from 'lodash'
import { getSmoothHull } from '@/utils/getSmoothHull'

export const fetchLayout = async (
  sensorRelations: [number, number][],
  positionRelations: [number, number][],
  nSensors: number,
  nPositions: number
) => {
  const context = {
    sensor_relations: sensorRelations,
    position_relations: positionRelations,
    number_of_positions: nPositions,
    number_of_sensors: nSensors,
  }
  console.log(context)
  const response = await fetch('http://127.0.0.1:5000/ilp', {
    method: 'POST',
    // headers: {
    //   'Content-Type': 'application/json;charset=utf-8'
    // },
    body: JSON.stringify(context),
  })

  const ret = await response.json()
  console.log(ret)
}

export const fetchLayoutGreedy = (
  component: MyComponent,
  mapping: { [pid: number]: number },
  groupsByType: [string[], string[], string[]],
  weights: { [aspect: string]: number }
) => {
  console.log('generating layout')

  const componentSensors = component.validSensors
  const sensorRelationsGroups = generateSensorRelations(
    component.sensorGroups,
    componentSensors
  )
  const positionRelations = generatePositionEdges(component.sensorPositions, component.d)
  const typeSimilarity = generateTypeSimilarity(componentSensors, groupsByType)

  // refine mapping
  let gain = 0.01
  let iter = 0
  const positionKeys = Object.keys(mapping)
  while (gain > 0 && iter < 300) {
    gain = 0
    const curValue = evaluateValue(mapping, positionRelations, sensorRelationsGroups, typeSimilarity, weights, 0)
    let swap_i = -1
    let swap_j = -1
    for (let i = 0; i < positionKeys.length; i++) {
      for (let j = i + 1; j < positionKeys.length; j++) {
        const ki = parseInt(positionKeys[i])
        const kj = parseInt(positionKeys[j])
        const tempMapping = cloneDeep(mapping)
        // swap i j
        const temp = tempMapping[ki]
        tempMapping[ki] = tempMapping[kj]
        tempMapping[kj] = temp
        const msg = 0
        const tempValue = evaluateValue(tempMapping, positionRelations, sensorRelationsGroups, typeSimilarity, weights, msg)
        const tempGain = tempValue - curValue
        if (gain < tempGain) {
          swap_i = ki
          swap_j = kj
          gain = tempGain
        }
      }
    }
    if (swap_i > -1 && swap_j > -1) {
      const temp = mapping[swap_i]
      mapping[swap_i] = mapping[swap_j]
      mapping[swap_j] = temp
      console.log('gain:', gain, swap_i, swap_j, iter)
    }
    iter += 1
  }
  const finalValue = evaluateValue(mapping, positionRelations, sensorRelationsGroups, typeSimilarity, weights, 0)
  return { mapping, finalValue }
}

export const getLinks = (
  mapping: { [pid: number]: number },
  component: MyComponent,
  aspect: string
) => {
  const componentSensors = component.validSensors
  const sensorRelationsGroups = generateSensorRelations(
    component.sensorGroups,
    componentSensors
  )
  const positionRelations = generatePositionEdges(component.sensorPositions, component.d)
  const srDict: { [key: string]: boolean } = {}
  for (const sensorRelationsGroup of sensorRelationsGroups) {
    if (sensorRelationsGroup.aspect === aspect) {
      for (const sr of sensorRelationsGroup.relations) {
        const key1 = `${sr[0]}+${sr[1]}`
        const key2 = `${sr[1]}+${sr[0]}`
        srDict[key1] = true
        srDict[key2] = true
      }
    }
  }
  const links: [number, number][] = []
  for (const pr of positionRelations) {
    const pid1 = pr[0]
    const pid2 = pr[1]
    if (pid1 in mapping && pid2 in mapping) {
      const sid1 = mapping[pid1]
      const sid2 = mapping[pid2]

      if (`${sid1}+${sid2}` in srDict) {
        links.push([pid1, pid2])
      } else if (`${sid2}+${sid1}` in srDict) {
        links.push([pid1, pid2])
      }
    }
  }
  return links
}

const evaluateValue = (
  mapping: { [pid: number]: number },
  positionRelations: [number, number, number][],
  sensorRelationsGroups: RelationsGroup[],
  typeSimilarity: TypeSimilarity,
  weights: { [aspect: string]: number },
  msg: number
) => {
  let value = 0
  const srDict: { [key: string]: number } = {}
  for (const sensorRelationsGroup of sensorRelationsGroups) {
    const weight = weights[sensorRelationsGroup.aspect]
    // console.log(sensorRelationsGroup.relations)
    for (const sr of sensorRelationsGroup.relations) {
      const key1 = `${sr[0]}+${sr[1]}`
      const key2 = `${sr[1]}+${sr[0]}`
      if (!(key1 in srDict)) {
        srDict[key1] = weight
      } else {
        srDict[key1] += weight
      }
      if (!(key2 in srDict)) {
        srDict[key2] = weight
      } else {
        srDict[key2] += weight
      }
    }
  }

  for (const pr of positionRelations) {
    const pid1 = pr[0]
    const pid2 = pr[1]
    const local_weight = pr[2]
    if (pid1 in mapping && pid2 in mapping) {
      const sid1 = mapping[pid1]
      const sid2 = mapping[pid2]

      if (`${sid1}+${sid2}` in srDict) {
        const v = srDict[`${sid1}+${sid2}`]
        value += v * local_weight
      } else if (`${sid2}+${sid1}` in srDict) {
        const v = srDict[`${sid2}+${sid1}`]
        value += v * local_weight
      }

      if (typeSimilarity.category[sid1] && typeSimilarity.category[sid2]) {
        value += weights['type'] * local_weight
      }
      if (typeSimilarity.numeric[sid1] && typeSimilarity.numeric[sid2]) {
        value += weights['type'] * local_weight
      }
      if (typeSimilarity.boolean[sid1] && typeSimilarity.boolean[sid2]) {
        value += weights['type'] * local_weight
      }
    }
  }
  return Math.floor(value * 100) / 100
}

interface LinkRevisited {
  p1: number,
  p2: number,
  visited: boolean,
  i: number
}

export const getCommmunityPaths = (
  links: [number, number][],
  component: MyComponent,
  d: number
) => {
  const linksVisited: LinkRevisited[] = links.map((l, i) => ({
    p1: l[0],
    p2: l[1],
    visited: false,
    i,
  }))
  const linkDict: { [pid: number]: number[] } = {}
  links.forEach((l, i) => {
    if (l[0] in linkDict) {
      linkDict[l[0]].push(i)
    } else {
      linkDict[l[0]] = [i]
    }
    if (l[1] in linkDict) {
      linkDict[l[1]].push(i)
    } else {
      linkDict[l[1]] = [i]
    }
  })
  const communities: number[][] = []
  for (const l of linksVisited) {
    if (!l.visited) {
      const queue: LinkRevisited[] = [l]
      const community: number[] = []
      while (queue.length > 0) {
        const l = queue.shift() as LinkRevisited
        community.push(l.p1)
        community.push(l.p2)
        l.visited = true
        for (const linkidByP1 of linkDict[l.p1]) {
          if (!linksVisited[linkidByP1].visited) { // 未访问过
            queue.push(linksVisited[linkidByP1])
          }
        }
        for (const linkidByP2 of linkDict[l.p2]) {
          if (!linksVisited[linkidByP2].visited) { // 未访问过
            queue.push(linksVisited[linkidByP2])
          }
        }
      }
      communities.push(Array.from(new Set(community)))
    }
  }
  console.log(communities)
  const paths: string[] = []
  for (const community of communities) {
    const positions = community.map(pi => {
      const position = component.sensorPositions[pi]
      return [position[0], position[1]] as [number, number]
    })
    const path = getSmoothHull(positions, 15)
    paths.push(path)
  }
  return paths
}
