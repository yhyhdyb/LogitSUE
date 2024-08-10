<template>
  <div class="demo"></div>
</template>

<script lang="ts">
import * as THREE from "three";
import { defineComponent, onMounted } from "vue";
export default defineComponent({
  name: "demo-dd",
  props: {},
  setup() {
    let scene: THREE.Scene | null = null;
    let camera: THREE.PerspectiveCamera | null = null;
    let renderer: THREE.WebGLRenderer | null = null;
    let ambientLight: THREE.AmbientLight | null = null;
    let mesh: THREE.Mesh | null = null;

    const setCamera = () => {
    // 第二参数就是 长度和宽度比 默认采用浏览器  返回以像素为单位的窗口的内部宽度和高度
      camera = new THREE.PerspectiveCamera(
        75,
        window.innerWidth / window.innerHeight,
        0.1,
        1000
      );
      camera.position.z = 5;
    }

        // 设置渲染器
    const setRenderer = () =>  {
      renderer = new THREE.WebGLRenderer();
      // 设置画布的大小
      renderer.setSize(window.innerWidth, window.innerHeight);
      //这里 其实就是canvas 画布  renderer.domElement
      document.body.appendChild(renderer.domElement);
    }

    // 设置环境光
    const setLight = () => {
      if (scene) {
        ambientLight = new THREE.AmbientLight(0xffffff); // 环境光
        scene.add(ambientLight);
      }
    }

      // 创建网格模型
    const setCube = () => {
      if (scene) {
        const geometry = new THREE.BoxGeometry(); //创建一个立方体几何对象Geometry
        // const material = new THREE.MeshBasicMaterial({ color: 0xff3200 }); //材质对象Material
        const texture = new THREE.TextureLoader().load(
          "src/assets/bus-1m.png"
        ); //首先，获取到纹理
        const material = new THREE.MeshBasicMaterial({ map: texture }); //然后创建一个phong材质来处理着色，并传递给纹理映射
        mesh = new THREE.Mesh(geometry, material); //网格模型对象Mesh
        scene.add(mesh); //网格模型添加到场景中
        render();
      }
    }

    // 渲染
    const render = () => {
      if (renderer && scene && camera) {
        renderer.render(scene, camera);
      }
    }

    // 动画
    const animate = () => {
      if (mesh) {
        requestAnimationFrame(animate.bind(this));
        mesh.rotation.x += 0.01;
        mesh.rotation.y += 0.01;
        render();
      }
    }


    onMounted(() => {
      // new ThreeJs();
      scene = new THREE.Scene();
      setCamera();
      setRenderer();
      setCube();
      animate();
    });

    return {
      scene,
      camera,
      renderer,
      ambientLight,
      mesh
    }
  },
});
</script>
<style scoped lang="scss"></style>
