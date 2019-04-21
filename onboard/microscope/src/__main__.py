from rover_common import aiolcm
from rover_common.aiohelper import run_coroutines
from rover_msgs import Microscope
import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst # noqa

lcm_ = aiolcm.AsyncLCM()
pipeline = None
streaming = False


def start_pipeline():
    global pipeline

    pipeline_string = ("v4l2src device=/dev/v4l/by-id/usb-05e3_USB2.0_Digital_"
                       "Camera_USB2.0_Digital_Camera-video-index0 ! "
                       "videoscale ! videoconvert ! x264enc tune=zerolatency "
                       "bitrate=500 speed-preset=superfast ! rtph264pay ! "
                       "udpsink host=10.0.0.1 port=5002")

    if pipeline is None:
        pipeline = Gst.parse_launch(pipeline_string)

    pipeline.set_state(Gst.State.PLAYING)

    print("Playing pipeline.")


def stop_pipeline():
    global pipeline

    pipeline.set_state(Gst.State.PAUSED)

    print("Stopping pipeline.")


def camera_callback(channel, msg):
    global pipeline
    global streaming

    microscope = Microscope.decode(msg)
    if microscope.streaming == streaming:
        return
    streaming = microscope.streaming
    if streaming:
        start_pipeline()
    else:
        stop_pipeline()

def picture_callback(channel, msg):
    data = TakePicture.decode(msg)
    if index != data.index:
        return
    stop_pipeline()
    os.system( ('ffmpeg -f video4linux2 -i'
                '/dev/v4l/by-id/usb-0c45_USB_camera-video-index0'
                '-vframes 1 /home/pi/out-mic.jpg' ) )
    start_pipeline()
    os.system('scp -l 2000 /home/pi/out-mic.jpg mrover@10.0.0.1:{}.jpg'
              .format(round(time.time() * 1000)))


def main():
    Gst.init(None)

    lcm_.subscribe("/microscope", camera_callback)
    lcm_.subscribe("/take_picture", picture_callback)

    run_coroutines(lcm_.loop())
