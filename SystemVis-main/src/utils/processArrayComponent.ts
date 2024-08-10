import { getImageDimensions } from './getImageDimensions'
import { callTemplateMatching } from './callTemplateMatching'
export const processArrayComponent = async (component: MyComponent, backgroundImageUrl: string) => {
  const { leftTopX, leftTopY, componentWidth, componentHeight } = component.graphicalFeature

  const clippedCanvas = document.createElement('canvas');
  const context = clippedCanvas.getContext("2d") as CanvasRenderingContext2D;
  const backgroundDiv = document.getElementById('background-image') as HTMLElement
  const rect = backgroundDiv.getBoundingClientRect()
  const divWidth = rect.width
  const divHeight = rect.height

  const sourceImage = new Image();
  sourceImage.src = backgroundImageUrl;
  const dimensions = await getImageDimensions(backgroundImageUrl)
  const ratio = Math.max(dimensions.w / divWidth, dimensions.h / divHeight)

  console.log(ratio)
  const menuHeight = 50
  const x = leftTopX * ratio
  const y = (leftTopY - menuHeight) * ratio
  const width = componentWidth * ratio
  const height = componentHeight * ratio

  // Set canvas dimensions to match the clipped region
  clippedCanvas.width = width;
  clippedCanvas.height = height;

  // Clip and draw the portion of the image onto the canvas
  context.drawImage(sourceImage, x, y, width, height, 0, 0, width, height);

  // Convert the clipped portion to base64
  const clippedBase64 = clippedCanvas.toDataURL("image/png");

  // Log the base64 representation (you can use it as needed)
  const response = await callTemplateMatching(clippedBase64, backgroundImageUrl, component.nArray, x, y)
  for (const p of response.matching_results) {
    p[0] = p[0] / ratio
    p[1] = p[1] / ratio + menuHeight
  }
  component.arrayMatchingResults = response.matching_results as [number, number][]
}

