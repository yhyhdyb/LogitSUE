<script setup lang="ts"></script>
<template>
  <div class="main_bar">
    <div class="title_column">
      <div class="logo_box">
        <img src="/static/logo.svg" alt="" srcset="/static/logo.svg" height="40" />
      </div>
      <div class="title_title">TraSculptor</div>
    </div>
  </div>
</template>

<style scoped>
.main_bar {
  width: 100%;
  height: 100%;
  background-color: #dfdfdf;

  display: flex;
  flex-direction: row;
  align-items: center;
  /* box-shadow: 0px 0px 2px rgba(255,255,255,0.2); */
  box-shadow: 0px 5px 5px rgba(255, 255, 255, 0.2);
}

.title_column {
  padding: 5px 10px;
  height: 40px;

  display: flex;
  flex-direction: row;
  align-items: center;
}

.title_column * {
  margin-left: 2px;
  margin-right: 2px;
}

.title_column .logo_box {
  height: 30px;
}

.title_column .logo_box img {
  height: 30px;
}
.title_column .title_title {
  color: black;
}
</style>
