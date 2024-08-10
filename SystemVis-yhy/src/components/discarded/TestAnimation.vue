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

    function init() {

      scene = new THREE.Scene()

      //

      camera = new THREE.PerspectiveCamera( 40, window.innerWidth / window.innerHeight, 1, 1000 );
      camera.position.set( 25, 25, 50 );
      camera.lookAt( scene.position );

      //

      const axesHelper = new THREE.AxesHelper( 10 );
      scene.add( axesHelper );

      //

      const geometry = new THREE.BoxGeometry( 5, 5, 5 );
      const material = new THREE.MeshBasicMaterial( { color: 0xffffff, transparent: true } );
      const mesh = new THREE.Mesh( geometry, material );
      scene.add( mesh );

      // create a keyframe track (i.e. a timed sequence of keyframes) for each animated property
      // Note: the keyframe track type should correspond to the type of the property being animated

      // POSITION
      const positionKF = new THREE.VectorKeyframeTrack( '.position', [ 0, 1, 2 ], [ 0, 0, 0, 30, 0, 0, 0, 0, 0 ] );

      // SCALE
      const scaleKF = new THREE.VectorKeyframeTrack( '.scale', [ 0, 1, 2 ], [ 1, 1, 1, 2, 2, 2, 1, 1, 1 ] );

      // ROTATION
      // Rotation should be performed using quaternions, using a THREE.QuaternionKeyframeTrack
      // Interpolating Euler angles (.rotation property) can be problematic and is currently not supported

      // set up rotation about x axis
      const xAxis = new THREE.Vector3( 1, 0, 0 );

      const qInitial = new THREE.Quaternion().setFromAxisAngle( xAxis, 0 );
      const qFinal = new THREE.Quaternion().setFromAxisAngle( xAxis, Math.PI );
      const quaternionKF = new THREE.QuaternionKeyframeTrack( '.quaternion', [ 0, 1, 2 ], [ qInitial.x, qInitial.y, qInitial.z, qInitial.w, qFinal.x, qFinal.y, qFinal.z, qFinal.w, qInitial.x, qInitial.y, qInitial.z, qInitial.w ] );

      // COLOR
      const colorKF = new THREE.ColorKeyframeTrack( '.material.color', [ 0, 1, 2 ], [ 1, 0, 0, 0, 1, 0, 0, 0, 1 ], THREE.InterpolateDiscrete );

      // OPACITY
      const opacityKF = new THREE.NumberKeyframeTrack( '.material.opacity', [ 0, 1, 2 ], [ 1, 0, 1 ] );

      // create an animation sequence with the tracks
      // If a negative time value is passed, the duration will be calculated from the times of the passed tracks array
      const clip = new THREE.AnimationClip( 'Action', 3, [ scaleKF, positionKF, quaternionKF, colorKF, opacityKF ] );

      // setup the THREE.AnimationMixer
      mixer = new THREE.AnimationMixer( mesh );

      // create a ClipAction and set it to play
      const clipAction = mixer.clipAction( clip );
      clipAction.play();

      //

      renderer = new THREE.WebGLRenderer( { antialias: true } );
      renderer.setPixelRatio( window.devicePixelRatio );
      renderer.setSize( window.innerWidth, window.innerHeight );
      document.body.appendChild( renderer.domElement );

      //

      stats = new Stats()
      document.body.appendChild( stats.dom );

      //

      clock = new THREE.Clock();

      //

      window.addEventListener( 'resize', onWindowResize );

      }

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





function onWindowResize() {

  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();

  renderer.setSize( window.innerWidth, window.innerHeight );

}

function animate() {

  requestAnimationFrame( animate );

  render();

}

function render() {

  const delta = clock.getDelta();

  if ( mixer ) {

    mixer.update( delta );

  }

  renderer.render( scene, camera );

  stats.update();

}