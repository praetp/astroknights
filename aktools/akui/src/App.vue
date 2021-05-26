<template>
  <RABracket/>
  <PolarCam/>
</template>

<script>
import RABracket from './components/RABracket.vue'
import PolarCam from './components/PolarCam.vue'

export default {
  name: 'App',
  components: {
    RABracket,
    PolarCam
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}
</style>
