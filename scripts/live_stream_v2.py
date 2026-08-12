import carla
import io
import signal
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from PIL import Image

latest_frame = None
frame_condition = threading.Condition()
actors = []

client = carla.Client("127.0.0.1", 2000)
client.set_timeout(10.0)
world = client.get_world()
blueprints = world.get_blueprint_library()

# --- 车辆：复用现有车辆，避免重复生成 ---
vehicle = None
for actor in world.get_actors().filter("vehicle.*"):
    if actor.is_alive:
        vehicle = actor
        break
spawned_vehicle = False
if vehicle is None:
    vehicle_bp_list = blueprints.filter("vehicle.tesla.model3")
    if not vehicle_bp_list:
        vehicle_bp_list = blueprints.filter("vehicle.*")
    for spawn_point in world.get_map().get_spawn_points():
        vehicle = world.try_spawn_actor(vehicle_bp_list[0], spawn_point)
        if vehicle is not None:
            break
    spawned_vehicle = True
if vehicle is None:
    raise RuntimeError("无法找到或生成车辆")
actors.append(vehicle)

if spawned_vehicle:
    traffic_manager = client.get_trafficmanager(8000)
    vehicle.set_autopilot(True, traffic_manager.get_port())
    print("已生成新车辆并启用自动驾驶", flush=True)
else:
    print(f"复用现有车辆 {vehicle.id} {vehicle.type_id}", flush=True)

# --- 摄像头配置（第三人称后方视角） ---
camera_bp = blueprints.find("sensor.camera.rgb")
camera_bp.set_attribute("image_size_x", "640")
camera_bp.set_attribute("image_size_y", "360")
camera_bp.set_attribute("fov", "90")
camera_bp.set_attribute("sensor_tick", "0.1")
camera_transform = carla.Transform(
    carla.Location(x=-6.0, z=3.0),
    carla.Rotation(pitch=-10.0)
)


def on_image(image):
    global latest_frame
    img = Image.frombuffer(
        "RGBA",
        (image.width, image.height),
        bytes(image.raw_data),
        "raw",
        "BGRA",
        0,
        1,
    ).convert("RGB")
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=60)
    with frame_condition:
        latest_frame = buffer.getvalue()
        frame_condition.notify_all()


def create_camera():
    cam = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)
    cam.listen(on_image)
    actors.append(cam)
    return cam


# --- 相机：复用已正确挂载的，否则重建 ---
camera = None
for actor in world.get_actors().filter("sensor.camera.rgb"):
    if actor.is_alive:
        camera = actor
        break
if camera is not None:
    parent = camera.parent
    if parent is None or parent.id != vehicle.id:
        try:
            camera.destroy()
        except Exception:
            pass
        camera = None
        print("检测到摄像头脱离车辆，将重建", flush=True)
if camera is None:
    camera = create_camera()
    print("摄像头已创建并挂载到车辆", flush=True)
else:
    try:
        camera.listen(on_image)
    except Exception:
        pass
    print(f"复用摄像头 {camera.id}", flush=True)


def camera_ok() -> bool:
    try:
        if camera is None or not camera.is_alive:
            return False
        parent = camera.parent
        return parent is not None and parent.id == vehicle.id
    except Exception:
        return False


# --- 看门狗：相机脱离车辆则自动重建并重新挂载 ---
def camera_watchdog():
    global camera
    while True:
        threading.Event().wait(5)
        try:
            if not camera_ok():
                print("摄像头脱离车辆，重建中…", flush=True)
                try:
                    if camera is not None and camera.is_alive:
                        camera.stop()
                        camera.destroy()
                except Exception:
                    pass
                try:
                    camera = create_camera()
                    print("摄像头已重建并重新挂载", flush=True)
                except Exception as exc:
                    print(f"摄像头重建失败: {exc}", flush=True)
        except Exception:
            pass


threading.Thread(target=camera_watchdog, daemon=True).start()


class StreamHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/":
            page = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>CARLA 实时监控</title>
<style>
html,body {
    margin:0;
    width:100%;
    height:100%;
    background:#111;
    overflow:hidden;
}
body {
    display:flex;
    align-items:center;
    justify-content:center;
}
img {
    width:100vw;
    height:100vh;
    object-fit:contain;
}
</style>
</head>
<body>
<img src="/stream">
</body>
</html>
"""
            data = page.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        if self.path == "/stream":
            self.send_response(200)
            self.send_header(
                "Content-Type",
                "multipart/x-mixed-replace; boundary=frame"
            )
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            try:
                while True:
                    with frame_condition:
                        frame_condition.wait(timeout=1.0)
                        frame = latest_frame
                    if frame is None:
                        continue
                    self.wfile.write(b"--frame\r\n")
                    self.wfile.write(b"Content-Type: image/jpeg\r\n")
                    self.wfile.write(
                        f"Content-Length: {len(frame)}\r\n\r\n".encode()
                    )
                    self.wfile.write(frame)
                    self.wfile.write(b"\r\n")
            except (BrokenPipeError, ConnectionResetError):
                pass
            return

        self.send_response(404)
        self.end_headers()


server = ThreadingHTTPServer(("0.0.0.0", 8080), StreamHandler)


def cleanup(*args):
    try:
        camera.stop()
    except Exception:
        pass
    for actor in reversed(actors):
        try:
            actor.destroy()
        except Exception:
            pass
    sys.exit(0)


signal.signal(signal.SIGTERM, cleanup)
signal.signal(signal.SIGINT, cleanup)

print("CARLA 实时监控已启动", flush=True)
print("端口：8080", flush=True)
print("分辨率：640×360", flush=True)
print("帧率：约10帧/秒", flush=True)

try:
    server.serve_forever()
finally:
    cleanup()
