//@ts-nocheck
import { line, curveCatmullRomClosed, polygonHull } from "d3"

// interface Point {

// }


export function getSmoothHull(rawPoints: Point[], hullPadding) {
  const points = getHullPoints(rawPoints) as Point[]
  const pointCount = points.length

  // Handle special cases
  if (!points || pointCount < 1) return ""
  if (pointCount === 1) return createOnePointHull(points[0], hullPadding)
  if (pointCount === 2) return createTwoPointHull(points as [Point, Point], hullPadding)

  return createPolyHull(points, hullPadding)
}

function getHullPoints(points: Point[]) {
  return points.length < 3 ? points : polygonHull(points)
}

function createOnePointHull(point: Point, hullPadding: number) {
  const [x, y] = point
  const p1 = [x, y - hullPadding];
  const p2 = [x, y + hullPadding];

  return `
		M ${p1}
		A ${[hullPadding, hullPadding, '0,0,0', p2].join(',')}
		A ${[hullPadding, hullPadding, '0,0,0', p1].join(',')}
	`.trim()
}

function createTwoPointHull([p1, p2]: [Point, Point], hullPadding: number) {
  console.log(p1, p2)
  const vector = createVector(p1, p2, hullPadding / 3);
  console.log('vector:', vector)

  console.log('hullPadding', hullPadding)
  const tangentHalfLength = hullPadding / 12
  const controlDelta = scaleVector(
    [-vector[1], vector[0]],
    tangentHalfLength,
  )
  const inverseControlDelta = scaleVector(controlDelta, -1)

  const endPoints: [Point, Point] = [
    sumVectors(p1, scaleVector(vector, -1)),
    sumVectors(p2, vector),
  ]
  const controlPoints = [
    sumVectors(endPoints[0], inverseControlDelta),
    sumVectors(endPoints[1], inverseControlDelta),
    sumVectors(endPoints[0], controlDelta),
  ]
  console.log('controlDelta:', controlDelta)
  console.log('inverseControlDelta:', inverseControlDelta)
  console.log('endPoints:', endPoints)
  console.log('controlPoints:', controlPoints)

  return `
		M ${endPoints[0]}
		C ${[controlPoints[0], controlPoints[1], endPoints[1]].join(',')}
		S ${[controlPoints[2], endPoints[0]].join(',')}
		Z
	`.trim()
}

function createVector([x1, y1]: Point, [x2, y2]: Point, length = 1) {
  const [x, y] = [x2 - x1, y2 - y1]
  const magnitude = getMagnitude([x, y], length)
  const vector = scaleVector([x, y], magnitude)

  return scaleVector(
    vector,
    length,
  )
}

function scaleVector([x, y]: Point, scale: number) {
  return [scale * x, scale * y] as Point
}

function sumVectors([x1, y1]: Point, [x2, y2]: Point) {
  return [x1 + x2, y1 + y2] as Point
}

function getMagnitude([x, y]: Point, length: number) {
  return length / Math.sqrt(x ** 2 + y ** 2)
}

function createPolyHull(points: Point[], hullPadding: number) {
  const hullPoints = points
    .map(addVectorToPoint)
    .map(expandPoint(hullPadding))

  const hullCurve = createHullCurve()
  return hullCurve(hullPoints)
}

function addVectorToPoint(point: Point, index: number, points: Point[]) {
  const nextPoint = points[(index + 1) % points.length] // Returns original point at end

  return {
    p: point,
    v: createVector(point, nextPoint)
  }
}

function expandPoint(hullPadding: number) {
  return (point: VectorPoint, index: number, points: VectorPoint[]) => {
    const previousIndex = (index > 0) ? (index - 1) : (points.length - 1)
    const previousPoint = points[previousIndex]

    const hullVector = sumVectors(
      previousPoint.v,
      scaleVector(point.v, -1),
    )

    return {
      ...point,
      p: sumVectors(
        point.p,
        scaleVector(hullVector, hullPadding)
      ),
    }
  }
}

function createHullCurve() {
  return line()
    .curve(curveCatmullRomClosed.alpha(0.3))
    .x(({ p }) => p[0])
    .y(({ p }) => p[1])
}