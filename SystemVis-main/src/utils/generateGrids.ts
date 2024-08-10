import { cloneDeep } from "lodash"

export function generatePoints(
  left: number,
  top: number,
  width: number,
  height: number,
  d: number
) {
  const points: [number, number, number][] = []
  let pid = 0
  for (let y = top - d / 2; y < top + height - d / 2; y += d) {
    for (let x = left - d / 2; x < left + width - d / 2; x += d) {
      points.push([x, y, pid])
      pid += 1
    }
  }
  return points
}

export function inside(point: [number, number], vs: [number, number][]) {
  const x = point[0],
    y = point[1]

  let inside = false
  for (let i = 0, j = vs.length - 1; i < vs.length; j = i++) {
    const xi = vs[i][0],
      yi = vs[i][1]
    const xj = vs[j][0],
      yj = vs[j][1]

    const intersect = yi > y != yj > y && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi
    if (intersect) inside = !inside
  }

  return inside
}

export function obtainIdealPoints(
  component: MyComponent
) {
  const width = component.graphicalFeature.componentWidth
  const height = component.graphicalFeature.componentHeight
  const shapeRefined = component.shapeRefined as [number, number][]
  const nSensor = component.nSensor

  const center = [width / 2, height / 2]
  // S = 0.5×|(x1y2-x2y1)+(x2y3-y2x3)+(x3y4-y3x4) + ...... + (xny1-ynx1)|
  const pointsForArea = cloneDeep([...shapeRefined, shapeRefined[0]])
  let s = 0
  for (let i = 0; i < pointsForArea.length - 1; i++) {
    const p0 = pointsForArea[i]
    const p1 = pointsForArea[i + 1]
    s += (p0[0] * p1[1] - p0[1] * p1[0])
  }
  s = Math.abs(s) / 2
  const initialD = Math.sqrt(s / nSensor) * 1.3

  for (let d = initialD; d > 0; d -= 1) {
    let flag = false
    const shapeOuter = cloneDeep(shapeRefined)
    const shape = cloneDeep(shapeRefined)
    shapeOuter.forEach((p, i) => {
      const nextp = i === shapeOuter.length - 1 ? shapeRefined[0] : shapeRefined[i + 1]
      const cp = [center[0] - p[0], center[1] - p[1]]
      const pnp = [nextp[0] - p[0], nextp[1] - p[1]]

      const dot = cp[0] * pnp[0] + cp[1] * pnp[1]
      const det = cp[0] * pnp[1] - cp[1] * pnp[0]
      const angleRadians = Math.atan2(det, dot)

      // const angleRadians = Math.atan2(cp[1] - pnp[1], cp[0] - pnp[0]);
      const sin = Math.abs(Math.sin(angleRadians))
      const shift = d * 0.4 / sin

      const p_to_c = Math.sqrt((p[0] - center[0]) * (p[0] - center[0]) + (p[1] - center[1]) * (p[1] - center[1]))
      const ratio = shift / p_to_c
      if (ratio > 1) {
        flag = true
      }
      p[0] -= ratio * (center[0] - p[0])
      p[1] -= ratio * (center[1] - p[1])

      // shapeOuter[i][0] -= ratio * (center[0] - p[0])
      // shapeOuter[i][1] -= ratio * (center[1] - p[1])
    })
    if (flag) {
      continue
    }

    // for (let shiftX = 0; shiftX < d; shiftX += Math.floor(d / 10)) {
    //   for (let shiftY = 0; shiftY < d; shiftY += Math.floor(d / 10)) {
    const points1 = generatePoints(0, 0, width, height, d)
    let count = 0
    for (const point of points1) {
      if (inside([point[0], point[1]], shape)) {
        count += 1
      }
    }

    let newCount = 0
    let netCountAll = 0
    if (count >= nSensor) {
      // const points = generatePoints(left, top, width, height, d)
      const validPoints: [number, number, number][] = []
      const allpoints: [number, number, number][] = []
      points1.forEach((point) => {
        if (inside([point[0], point[1]], shapeOuter)) {
          allpoints.push([point[0], point[1], netCountAll])
          if (inside([point[0], point[1]], shape) && newCount < nSensor) {
            validPoints.push([point[0], point[1], netCountAll])
            newCount += 1
          }
          netCountAll += 1
        }
      })
      return { points: allpoints, validPoints, d }
    }
  }
  return { points: [], validPoints: [], d: 0 }
}


export function obtainIdealPointsForCircle(
  component: MyComponent
) {
  const width = component.graphicalFeature.componentWidth
  const height = component.graphicalFeature.componentHeight
  const shapeRefined = component.shapeRefined as ShapeForCircle
  const nSensor = component.nSensor

  const s = 3.14159 * shapeRefined.r * shapeRefined.r
  const initialD = Math.sqrt(s / nSensor) * 2

  console.log(shapeRefined.cx, shapeRefined.cy, shapeRefined.r)
  for (let d = initialD; d > 0; d -= 1) {
    const points = generatePoints(0, 0, width, height, d)
    console.log(points)
    let count = 0
    const validPoints: [number, number, number][] = []
    for (const point of points) {
      const xToCenter = point[0] - shapeRefined.cx
      const yToCenter = point[1] - shapeRefined.cy
      const dToCenter = Math.sqrt(xToCenter ** 2 + yToCenter ** 2)
      // console.log(dToCenter)
      if (dToCenter < shapeRefined.r && count < nSensor) {
        count += 1
        validPoints.push(point)
      }
    }
    console.log(count, d, nSensor)
    // console.log('count', count, "d", d, 'shiftX', shiftX, 'shiftY', shiftY)
    if (count >= nSensor) {
      return { points, validPoints, d }
    }
  }
  return { points: [], validPoints: [], d: 0 }
}
