export const getImageDimensions: (file: string) => Promise<{ w: number, h: number }> = (file: string) => {
  return new Promise(function (resolved, rejected) {
    const i = new Image()
    i.onload = function () {
      resolved({ w: i.width, h: i.height })
    };
    i.src = file
  })
}