export const callTemplateMatching = async (template_uri: string, background_uri: string, nArray: number, x: number, y: number) => {
  const context = {
    template_uri,
    background_uri,
    nArray,
    x,
    y
  }
  const response = await fetch('http://127.0.0.1:5000/locateComponentArray', {
    method: 'POST',
    // headers: {
    //   'Content-Type': 'application/json;charset=utf-8'
    // },
    body: JSON.stringify(context),
  })

  // const ret = await response.json()
  return response.json()
}