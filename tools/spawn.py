from arena import *
from dotenv import load_dotenv
import os
import numpy as np
import time
from enum import Enum

load_dotenv()

scene = Scene(host="arenaxr.org", namespace=os.getenv("NAMESPACE"), scene=os.getenv("SCENE_NAME"))


class FurnitureType:
    def __init__(self, type_id, name, img_path, obj_path, description):
        self.type_id = type_id
        self.name = name
        self.img_path = img_path
        self.obj_path = obj_path
        self.description = description
        self.count = 0

class GrabObject:
    def __init__(self, obj_id, obj_type, arena_obj=None):
        self.obj_id = obj_id
        self.arena_obj = arena_obj
        self.obj_type = obj_type
        self.grabbing = False
        self.grabber = None
        self.child_pose_relative_to_parent = None
        self.orig_scale = (1, 1, 1)
        self.grabbed_scale = (1.1, 1.1, 1.1)

    def box_click(self, scene, evt, msg):

        if evt.type == "mousedown":
            clicker = scene.users[evt.object_id]
            handRight = clicker.hands.get("handRight", None)
            # handLeft = clicker.hands.get("handLeft", None)

            if not self.grabbing:
                print("grabbed")

                if handRight is not None:
                    self.grabber = handRight

                    self.grabbing = True
                    hand_pose = pose_matrix(self.grabber.data.position, self.grabber.data.rotation)
                    # print(self.arena_obj.data.position, self.arena_obj.data.rotation)
                    child_pose = pose_matrix(self.arena_obj.data.position, self.arena_obj.data.rotation)
                    self.child_pose_relative_to_parent = get_relative_pose_to_parent(hand_pose, child_pose)

        elif evt.type == "mouseup":
            if self.grabbing:
                print("released")
                self.grabbing = False
                self.arena_obj.update_attributes(scale=self.orig_scale)
                scene.update_object(self.arena_obj)


def pose_matrix(position, rotation):
    position = np.array((position.x, position.y, position.z))
    rotation = np.array((rotation.x, rotation.y, rotation.z, rotation.w))
    scale = np.array((1, 1, 1))

    rotation_matrix = np.eye(4)
    rotation_matrix[:3,:3] = Utils.quat_to_matrix3(rotation)

    scale_matrix = np.diag([scale[0], scale[1], scale[2], 1])

    translation_matrix = np.eye(4)
    translation_matrix[:3, 3] = [position[0], position[1], position[2]]

    pose_matrix = translation_matrix @ rotation_matrix @ scale_matrix

    return pose_matrix

def get_relative_pose_to_parent(parent_pose, child_pose_world):
    parent_pose_inverse = np.linalg.inv(parent_pose)
    relative_pose = parent_pose_inverse @ child_pose_world
    return relative_pose

def get_world_pose_when_parented(parent_pose, child_pose_relative_to_parent):
    world_pose = parent_pose @ child_pose_relative_to_parent
    return world_pose

furnitureType = {}
furnitureType["Table 1"] = FurnitureType(type_id="table-1", name="Table 1", 
                                 img_path="/store/users/saagardp/img.jpg", 
                                 obj_path="/store/users/saagardp/lab1.glb",
                                 description="Table 1 description placeholder")
furnitureType["Table 2"] = FurnitureType(type_id="table-2", name="Table 2", 
                                 img_path="/store/users/saagardp/img.jpg", 
                                 obj_path="/store/users/aadeshkd/table2.gltf",
                                 description="Table 2 description placeholder")
furnitureType["Table 3"] = FurnitureType(type_id="table-3", name="Table 3", 
                                 img_path="/store/users/saagardp/img.jpg", 
                                 obj_path="/store/users/aadeshkd/table3.gltf",
                                 description="Table 3 description placeholder")

furniture = {}

def spawn_obj(obj_name):
    obj = furnitureType[obj_name]
    obj_count = obj.count
    object_id = f"{obj.type_id}-{obj.count}"

    grabObj = GrabObject(obj_id=object_id, obj_type=obj)

    scene_obj = GLTF(
        object_id=object_id,
        # parent="main",
        # position=Position(12.5, 1, -2),
        # rotation=(0, 0, 0, 0),
        position=Position(5.25, 2.327, -12.23),
        rotation=(0, -0.445, 0, -0.896),
        # dynamic_body=True,
        clickable=True,
        url=obj.obj_path,
        evt_handler=grabObj.box_click,
    )
    grabObj.arena_obj = scene_obj
    scene.add_object(scene_obj)
    print(f"Object added: {obj.type_id}-{obj.count}")

    furniture[object_id] = grabObj

    def del_button_handler(scene, evt, msg):
        if evt.type == "mousedown":
            scene.delete_object(scene_obj)
            del furniture[object_id]
            print(f"Object deleted: {obj.type_id}-{obj_count}")

    # Delete button
    del_button = Box(
        object_id=f"{object_id}-del",
        parent=object_id,
        position=Position(0.1, 0.1, 0.1),
        height=0.1,
        width=0.1,
        depth=0.1,
        clickable=True,
        evt_handler=del_button_handler,
    )
    obj.count += 1

    scene.add_object(del_button)

def make_display_card(obj_name):
    obj = furnitureType[obj_name]
    # try:
    #     card = scene.get_persisted_obj(f"{obj.type_id}-card")
    # except:
    card = Card(
        object_id=f"{obj.type_id}-card",
        title=obj_name,
        body=obj.description,
        bodyAlign="left",
        imgDirection="left",
        img=obj.img_path,
        imgSize="contain",
        closeButton=True,
        parent="spawn-panel",
        position=Position(0, 0, 0.5)
    )
    scene.add_object(card)

@scene.run_forever(interval_ms=10)
def move_box():
    global furniture
    for id, obj in furniture.items():
        if obj.grabber is not None and obj.child_pose_relative_to_parent is not None and obj.grabbing:
            hand_pose = pose_matrix(obj.grabber.data.position, obj.grabber.data.rotation)
            new_pose = get_world_pose_when_parented(hand_pose, obj.child_pose_relative_to_parent)

            new_position = (new_pose[0,3], new_pose[1,3], new_pose[2,3])
            new_rotation = Utils.matrix3_to_quat(new_pose[:3,:3])
            new_rotation = (new_rotation[3], new_rotation[0], new_rotation[1], new_rotation[2])

            obj.arena_obj.update_attributes(position=new_position, scale=obj.grabbed_scale)#, rotation=new_rotation)
            scene.update_object(obj.arena_obj)
            print("object position updated to", new_position)

@scene.run_once()
def setup():

    obj_name = None
    def button_handler(scene, evt, msg):
        global obj_name
        if evt.type == "buttonClick":
            print(f"Button clicked: {evt.data.buttonName}")
            if evt.data.buttonName in ["Table 1", "Table 2", "Table 3"]:
                scene.update_object(button_panel, buttons=second_buttonset, 
                                    title=f"{evt.data.buttonName}")
                obj_name = evt.data.buttonName
            elif evt.data.buttonName == "Back":
                scene.update_object(button_panel, buttons=first_buttonset, 
                                    title="Choose a table you want to add")
            elif evt.data.buttonName == "View":
                make_display_card(obj_name)
            elif evt.data.buttonName == "Add":
                spawn_obj(obj_name)

    first_buttonset = [Button(name="Table 1"), Button(name="Table 2"), Button(name="Table 3")]
    second_buttonset = [Button(name="Back"), Button(name="View"), Button(name="Add")]

    button_panel = ButtonPanel(
        object_id="spawn-panel",
        title="Choose a table you want to add",
        buttons=first_buttonset,
        vertical=True,
        font="Roboto-Mono",
        position=Position(12, 0.5, -2.5),
        rotation=Rotation(0, -45, 0),
        parent="main",
        evt_handler=button_handler,
    )
    scene.add_object(button_panel)

scene.run_tasks()