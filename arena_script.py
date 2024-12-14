from arena import *
import time

# Set your ARENA credentials and parameters
HOST = "arenaxr.org"  
NAMESPACE = "aadeshkd"    # Replace with your namespace
SCENE = "tempscene"            # Replace with your scene name

# Initialize ARENA connection
scene = Scene(
    host=HOST,
    scene=SCENE
)

# Create a function to define and add objects to the scene
@scene.run_once
def create_objects():
    # Create a cube
    cube = Box(
        object_id="cube",
        persist=True,
        position=(0, 1.5, -3),
        scale=(1, 1, 1),
        color=(255, 0, 0)  # Red color
    )
    scene.add_object(cube)

    # Create a sphere
    sphere = Sphere(
        object_id="sphere",
        persist=True,
        position=(1.5, 1.5, -3),
        scale=(0.5, 0.5, 0.5),
        color=(0, 255, 0)  # Green color
    )
    scene.add_object(sphere)

    # Create a plane as the ground
    ground = Plane(
        object_id="ground",
        persist=True,
        position=(0, 0, -3),
        rotation=(0, 0, 0),
        scale=(10, 10, 1),
        color=(200, 200, 200)  # Light gray color
    )
    scene.add_object(ground)

    # Create a 3D object from a GLTF model
    model = ObjModel(
        object_id="textured_output",
        persist=True,
        obj="store/users/aadeshkd/textured_output.obj",
        position=(0, 2, 0),
        rotation=(0,90,0),
        mtl="store/users/aadeshkd/textured_output.mtl"
    )
    print("Adding model to the scene...")
    scene.add_object(model)
    print(f"Model {model.object_id} added.")

# Call the function to create objects in the scene
# create_objects()

scene.run_tasks()
# scene.run_forever(interval_ms=100)
# Keep the script running to maintain connection with ARENA
# try:
print("Scene is live. Press Ctrl+C to exit.")
#     while True:
#         time.sleep(5)
# except KeyboardInterrupt:
#     print("Disconnecting...")
# finally:
#     arena.close()
