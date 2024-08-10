import type { sensorData } from '../interface/coal/sensorData'

function readCSVByLine(filePath: string, interval: number, sensorNames: string[]) {
  fetch(filePath)
    .then((response) => response.text())
    .then((contents) => {
      const rows = contents.split('\n')

      let index = 1
      function processLine() {
        if (index < rows.length) {
          // console.log(rows[index])
          let columns: string[] | null = rows[index].split(',')
          // 处理每行数据
          let data: sensorData | null = {} as sensorData
          for (let i = 0; i < columns.length; i++) {
            // console.log('sensorNames',i,':',sensorNames[i])
            // console.log('columns',i,':',columns[i])
            const propertyName = sensorNames[i]
            const propertyValue = columns[i]
            data[propertyName as keyof sensorData] = propertyValue
          }
          console.log(data)
          self.postMessage(data)
          index++
          setTimeout(processLine, interval) // 设置时间间隔
          // 释放资源

          data = null
          columns = null
        } else {
          // 文件读取完成
          self.postMessage('文件读取完成')
        }
      }

      processLine()
    })
    .catch((error) => {
      console.error('发生错误:', error)
      self.postMessage({ error: error.message })
    })
}

self.onmessage = function (event) {
  const { filePath, interval, serializedSensorNames } = event.data
  const sensorNames = JSON.parse(serializedSensorNames)

  readCSVByLine(filePath, interval, sensorNames)
}
