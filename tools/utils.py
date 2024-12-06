from arena import *
import numpy as np

class FurnitureType:
    def __init__(self, type_id, name, img_path, obj_path, description, mtl_path=None, scale=1, desc_title="Title"):
        self.type_id = type_id
        self.name = name
        self.img_path = img_path
        self.obj_path = obj_path
        self.mtl_path = mtl_path
        self.description = description
        self.desc_title = desc_title
        self.scale = scale
        self.count = 0

class GrabObject:
    def __init__(self, obj_id, obj_type, main_pos, main_rot, orig_scale=(1, 1, 1), grabbed_scale=(1.1, 1.1, 1.1), arena_obj=None):
        self.obj_id = obj_id
        self.arena_obj = arena_obj
        self.obj_type = obj_type
        self.main_pos = main_pos
        self.main_rot = main_rot
        self.grabbing = False
        self.grabber = None
        self.child_pose_relative_to_parent = None
        self.orig_scale = orig_scale
        self.grabbed_scale = grabbed_scale

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
                    child_pose_relative_to_main = pose_matrix(self.arena_obj.data.position, self.arena_obj.data.rotation)
                    child_pose = get_world_pose_when_parented(pose_matrix(self.main_pos, self.main_rot), child_pose_relative_to_main)
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

def get_main_pos_rotation(scene):
    try:
        main = scene.get_persisted_obj("main")
        pos = main.data.position
        rotation = main.data.rotation
    except:
        pos = (0, 0, 0)
        rotation = (0, 0, 0, 0)
    return pos, rotation