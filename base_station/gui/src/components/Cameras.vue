<template>
  <div class="wrap">
    <div class="box header">
      <h3>Cameras</h3>
      <div class="spacer"></div>
      <div class="comms">
        <ul id="vitals">
          <li v-for="connection, i in connections" :key="i"><CommIndicator v-bind:connected="connection" v-bind:name="'Pi'+(i+1)"/></li>
        </ul>
        </div>
    </div>

    <div class="servos">
      <span>Servos pan: {{servosData.pan.toFixed(2)}}, Servos tilt: {{servosData.tilt.toFixed(2)}}</span>
    </div>

    <div class="video">
      <Checkbox v-bind:name="'Microscope'" v-on:toggle="toggleMicroscope()" ref="microscope"/>
      <Checkbox v-bind:name="'Dual Stream'" v-on:toggle="toggleDualStream()" ref="dualstream"/>
      <Video v-bind:pi_index="pi_index_1" v-bind:dual_stream="dual_stream" v-on:pi_index="setPiIndex($event, 1)"/>
      <Video v-show="dual_stream" v-bind:pi_index="pi_index_2" v-bind:dual_stream="dual_stream" v-on:pi_index="setPiIndex($event, 2)"/>
    </div>
  </div>
</template>


<style>
  .wrap {
    display: grid;
    grid-gap: 10px;
    grid-template-columns: 1fr;
    grid-template-rows: 60px 20px;
    grid-template-areas: "header" "servos";

    font-family: sans-serif;
    height: 100%;
  }

  .box {
    border-radius: 5px;
    padding: 10px;
    border: 1px solid black;
  }

  img {
    border: none;
    border-radius: 0px;
  }

  .servos {
    grid-area: servos;
    margin: auto;
  }

  .header {
    grid-area: header;
    display: flex;
    align-items: center;
  }

  .header h1 {
    margin-left: 5px;
  }

  .spacer {
    flex-grow: 0.8;
  }

  .comms {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
  }

  .comms * {
    margin-top: 2px;
    margin-bottom: 2px;
    display: flex;
  }

  ul#vitals li {
    display: inline;
    padding: 0px 10px 0px 0px;
  }
</style>

<script>
  import CommIndicator from './CommIndicator.vue'
  import Video from './Video.vue'
  import Checkbox from "./Checkbox.vue"


  let interval;

  export default {
    data() {
      return {
        dual_stream: false,
        pi_index_1: -1,
        pi_index_2: -1,
        microscope_streaming: false
      }
    },

    beforeDestroy: function () {
      window.clearInterval(interval);
    },

    created: function () {
      const JOYSTICK_CONFIG = {
        'down_left_button': 6,
        'up_left_button': 7,
        'down_middle_button': 8,
        'up_middle_button': 9,
        'down_right_button': 10,
        'up_right_button': 11
      }

      const CAMERA_NUM = {
        'down_left_button': 1,
        'up_left_button': 2,
        'down_middle_button': 3,
        'up_middle_button': 4,
        'down_right_button': 5,
        'up_right_button': 6
      }

      window.addEventListener('keydown', (e) => {
        const activeElement = document.activeElement;
        const inputs = ['input', 'select', 'textarea'];

        //Prevent camera change if inside text area
        if (activeElement && inputs.indexOf(activeElement.tagName.toLowerCase()) !== -1) {
            return;
        }

        if(e.keyCode>=49 && e.keyCode<=54)  //keys 1 to 6
          this.pi_index_1 = e.keyCode-48
      })

      // Change PI index based on joystick button
      interval = window.setInterval(() => {
        const gamepads = navigator.getGamepads()
        for (let i = 0; i < 2; i++) {
          const gamepad = gamepads[i]
          if (gamepad) {
            if (gamepad.id.includes('Logitech')) {
              if (gamepad.buttons[JOYSTICK_CONFIG['down_left_button']]['pressed']) {
                this.pi_index_1 = CAMERA_NUM['down_left_button']
              } else if (gamepad.buttons[JOYSTICK_CONFIG['up_left_button']]['pressed']) {
                this.pi_index_1 = CAMERA_NUM['up_left_button']
              } else if (gamepad.buttons[JOYSTICK_CONFIG['down_middle_button']]['pressed']) {
                this.pi_index_1 = CAMERA_NUM['down_middle_button']
              } else if (gamepad.buttons[JOYSTICK_CONFIG['up_middle_button']]['pressed']) {
                this.pi_index_1 = CAMERA_NUM['up_middle_button']
              } else if (gamepad.buttons[JOYSTICK_CONFIG['down_right_button']]['pressed']) {
                this.pi_index_1 = CAMERA_NUM['down_right_button']
              } else if (gamepad.buttons[JOYSTICK_CONFIG['up_right_button']]['pressed']) {
                this.pi_index_1 = CAMERA_NUM['up_right_button']
              }
            }
          }
        }
        this.$parent.publish('/pi_camera', {type: "PiCamera", active_index_1: this.pi_index_1, active_index_2: this.pi_index_2, dual_stream: this.dual_stream})
        this.$parent.publish('/microscope', {type: "Microscope", streaming: this.microscope_streaming})
      }, 250)
    },

    props: {
      connections: {
        type: Array,
        required: true
      },

      servosData: {
        type: Object,
        required: true
      }
    },

    methods: {
      setPiIndex: function (new_index, stream) {
        if (stream === 1 && new_index !== this.pi_index_2) {
          this.pi_index_1 = new_index
        } else if (stream === 2 && new_index !== this.pi_index_1) {
          this.pi_index_2 = new_index
        }
      },

      toggleMicroscope: function () {
        this.microscope_streaming = !this.microscope_streaming
        if (this.dual_stream) {
          this.$refs.dualstream.toggle()
          this.dual_stream = !this.dual_stream
          this.pi_index_1 = -1
          this.pi_index_2 = -1
        }
      },

      toggleDualStream: function () {
        this.dual_stream = !this.dual_stream
        if (this.microscope_streaming) {
          this.$refs.microscope.toggle()
          this.microscope_streaming = !this.microscope_streaming
        }
        if (!this.dual_stream) {
          this.pi_index_2 = -1
        }
      }
    },

    components: {
      CommIndicator,
      Video,
      Checkbox
    }
  }
</script>
