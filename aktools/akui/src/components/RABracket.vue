<template>
  <div class="RABracket">
    <div style="display: flex; height: auto">
      <div style="width: 20%">
        <div><button type="button" v-on:click="calibrate">Calibrate</button></div>
        <div><button type="button" v-on:click="reset">Reset</button></div>
      </div>
      <div style="width: 20%">
        <div><h4>ROLL</h4></div>
        <div><h4>{{roll}}</h4></div>
      </div>
      <div style="width: 20%;">
        <div><h4>ROLL2MINS</h4></div>
        <div><h4>{{roll2mins}}</h4></div>
      </div>
      <div style="width: 20%">
        <div><h4>ROLL2HOURS</h4></div>
        <div><h4>{{roll2hours}}</h4></div>
      </div>
      <div style="width: 20%">
        <div><h4>ROLLOFFSET</h4></div>
        <div><h4>{{rolloffset}}</h4></div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RABracket',
  props: {
  },
  data() {
    return{
        websocket: null,
        server: "ws://"+window.location.host+"/ws/",
        //server: "ws://"+"astroberry:8000"+"/ws/",
        roll: 0,
        roll2mins: 0,
        roll2hours: 0,
        rolloffset: 0
    }
  },
  beforeUnmount() {
    this.websocket.close()
  },
  mounted() {
    this.openws()
  },
  methods: {
    calibrate: function() {
        console.log("CALIBRATE")
      let resp = {"calibrate": true}
      if (this.websocket != null){
        this.websocket.send(JSON.stringify(resp));
      }
    },
    reset: function() {
        console.log("RESET")
      let resp = {"reset": true}
      if (this.websocket != null){
        this.websocket.send(JSON.stringify(resp));
      }
    },
    openws: function() {
      let myself=this
      if (myself.websocket != null) {
        myself.websocket.close()
      }
      try {
           console.log(window.location)
          myself.websocket = new WebSocket(myself.server);
          myself.websocket.onopen = function(openEvent) {
              console.log("WebSocket OPEN: " + JSON.stringify(openEvent, null, 4));
              myself.status="OPEN"
              myself.error=""
          };
          myself.websocket.onclose = function (closeEvent) {
              console.log("WebSocket CLOSE: " + JSON.stringify(closeEvent, null, 4));
              myself.status="CLOSED"
          };
          myself.websocket.onerror = function (errorEvent) {
              console.log("WebSocket ERROR: " + JSON.stringify(errorEvent, null, 4));
              myself.error=JSON.stringify(errorEvent, null, 4)
          };
          myself.websocket.onmessage = function (messageEvent) {
              var wsMsg = messageEvent.data;
              var msg = JSON.parse(wsMsg)
              console.log(msg)
              myself.roll=msg["data"]["roll"]
              myself.roll2mins=msg["data"]["rolltomins"]
              myself.roll2hours=msg["data"]["rolltohours"]
              myself.rolloffset=msg["data"]["rolloffset"]
          };
      } catch (exception) {
          console.log("ERROR",exception);
      }
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h4 {
  margin: 0px 0 0;
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
