<template>
  <div class="PolarCamera">
    <div style="display: flex, width: 100%, height: 100%">
        <img :src="server" style="width: auto, height=100%">
    </div>
  </div>
</template>

<script>
export default {
  name: 'PolarCamera',
  props: {
  },
  data() {
    return{
        server: "http://"+window.location.host+"/stream.mjpg"
        //server: "http://astroberry:8001/stream.mjpg"
    }
  },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>
