import { flatten } from "lodash"
export const orderingPoints = (component: MyComponent) => {
  const positionRows: PositionInfo[][] = []
  let y = component.sensorValidPositions[0][1]
  let positionRow: PositionInfo[] = []
  component.sensorValidPositions.forEach(p => {
    if (p[1] === y) {
      positionRow.push({
        x: p[0],
        y: p[1],
        pid: p[2]
      })
    } else {
      y = p[1]
      const n_row = positionRows.length
      positionRows.push(positionRow.sort((a, b) => {
        if (n_row % 2 === 0) {
          return a.x - b.x
        } else {
          return b.x - a.x
        }
      }))
      positionRow = [{
        x: p[0],
        y: p[1],
        pid: p[2]
      }]
    }
  })
  if (positionRow.length > 0) {
    const n_row = positionRows.length
    positionRows.push(positionRow.sort((a, b) => {
      if (n_row % 2 === 0) {
        return a.x - b.x
      } else {
        return b.x - a.x
      }
    }))
  }
  return flatten(positionRows)
}
