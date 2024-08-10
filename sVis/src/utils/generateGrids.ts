export function generatePoints(
  left: number,
  top: number,
  width: number,
  height: number,
  d: number
) {
  const points: [number, number][] = []
  for (let y = top - 1.5 * d; y < top + height + 1.5 * d; y += d) {
    for (let x = left - 1.5 * d; x < left + width + 1.5 * d; x += d) {
      points.push([x, y])
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
  left: number,
  top: number,
  width: number,
  height: number,
  shape: [number, number][],
  nSensor: number
) {
  console.log('left', left, 'top', top, 'width', width, 'height', height)
  console.log('shape', shape)
  // return { points: [], d: 0 }
  for (let d = 50; d > 0; d -= 1) {

    for (let shiftX = 0; shiftX < d; shiftX += Math.floor(d / 10)) {
      for (let shiftY = 0; shiftY < d; shiftY += Math.floor(d / 10)) {
        const points = generatePoints(left - shiftX, top - shiftY, width, height, d)
        let count = 0
        // console.log('points', points)
        const validPoints: [number, number][] = []
        console.log('debug2', points, shape)
        for (const point of points) {
          if (inside(point, shape)) {
            count += 1
            validPoints.push(point)
          }
        }
        console.log('count', count, "d", d, 'shiftX', shiftX, 'shiftY', shiftY)
        if (count > nSensor) {
          console.log('debug', d, nSensor, shiftX, shiftY)
          return { points: validPoints, d }
        }
      }
    }
  }
  return { points: [], d: 0 }
}
