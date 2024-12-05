from arena import *
from dotenv import load_dotenv
from utils import *
import os

load_dotenv()

scene = Scene(host="arenaxr.org", namespace=os.getenv("NAMESPACE"), scene=os.getenv("SCENE_NAME"))
prompt = None
my_iso=None

def noop_handler(_scene, _evt, _msg):
    """A no-operation handler that does nothing."""
    print("No operation handler triggered. Exiting all ongoing events.")

def click(scene, evt, msg):
    if evt.type == "mousedown":
        # print("Click!")
        start = evt.data.originPosition
        end = evt.data.targetPosition
        start.y=start.y-.1
        # start.x=start.x-.1
        # start.z=start.z-.1
        line = ThickLine(path=(start,end), color=(255,0,0), lineWidth=5, ttl=1)
        scene.add_object(line)
        ball = Sphere(
            position=end,
            scale = (0.06,0.06,0.06),
            color=(255,0,0),
            ttl=1)
        scene.add_object(ball)
        

def make_display_card(string):
    def prompt_handler(_scene, evt, _msg):
        nonlocal string
        if evt.type == "buttonClick":
            if evt.data.buttonName == "OK":
                print(f"Remove prompt {string}")
                scene.delete_object(scene.get_persisted_obj("display_prompt"))       
    try:
        display_prompt = scene.get_persisted_obj("display_prompt")
        display_prompt.data.title = string
        scene.update_object(display_prompt)
        print("Obj updated")
    except:
        # print("Object not found")
        display_prompt = Prompt(
            object_id="display_prompt",
            title="Label",
            description=string,
            buttons=["OK"],
            position=Position(0, 0, 0.5),     # TODO: Relative to parent
            look_at="#my-camera",
            evt_handler=prompt_handler,
            parent="my_iso",
        )
        display_prompt.data.textinput = None
        scene.add_object(display_prompt)
        print("New prompt obj added")
    

main_pos, main_rot = get_main_pos_rotation(scene)
print(main_pos, main_rot)

furnitureType = {}
furnitureType["Table 1"] = FurnitureType(type_id="table-1", name="Table 1", 
                                 img_path="/store/users/saagardp/table1.jpg", 
                                 obj_path="/store/users/saagardp/table1.obj",
                                 mtl_path="/store/users/saagardp/table1.mtl",
                                 scale=0.01,
                                 description="Add a touch of rustic elegance to your home with this beautifully crafted wooden table. Featuring a distressed wooden surface and sturdy black legs, this table combines durability with vintage charm. Perfect for both dining and decorative purposes, its timeless design fits seamlessly into modern, farmhouse, or industrial decor. A statement piece for any room, designed to bring warmth and character to your space.",
                                 desc_title="Rustic Charm Wooden Table",                                 
                                 )
furnitureType["Table 2"] = FurnitureType(type_id="table-2", name="Table 2", 
                                 img_path="/store/users/saagardp/table2.jpg", 
                                 obj_path="/store/users/saagardp/table2.obj",
                                 mtl_path="/store/users/saagardp/table2.mtl",
                                 description="Elevate your living room with this contemporary coffee table, blending sleek functionality with bold design. Its smooth, dark wood finish and contrasting white drawers create a striking minimalist aesthetic. Featuring ample storage space and an open shelf for easy access to books or decor, this table is perfect for modern homes. The clean lines and subtle curves make it an ideal centerpiece, bringing sophistication and practicality to any space.",
                                 desc_title="Sleek Modern Coffee Table",
                                 )
furnitureType["Table 3"] = FurnitureType(type_id="table-3", name="Table 3", 
                                 img_path="/store/users/saagardp/table3.jpg", 
                                 obj_path="/store/users/saagardp/table3.obj",
                                 mtl_path="/store/users/saagardp/table3.mtl",
                                 scale=0.03,
                                 description="Bring timeless elegance to your space with this stunning mid-century modern sideboard. Crafted from rich wood with a natural finish, it features clean lines and tapered legs that exude classic sophistication. With spacious drawers, open shelves, and a closed cabinet, it offers versatile storage for your living or dining area. Perfect for showcasing decor or keeping essentials organized, this piece combines style and functionality in perfect harmony.",
                                 desc_title="Mid-Century Modern Sideboard",
                                 )

furniture = {}

def spawn_obj(obj_name):
    obj = furnitureType[obj_name]
    obj_count = obj.count
    object_id = f"{obj.type_id}-{obj.count}"

    grabObj = GrabObject(obj_id=object_id, obj_type=obj, main_pos=main_pos, main_rot=main_rot)
    scene_obj = ObjModel(
        object_id=object_id,
        parent="main",
        position=Position(-2, -1, 1), # TODO: Relative to button panel
        rotation=(0, 0, 0, 0),
        scale=(obj.scale, obj.scale, obj.scale),
        # dynamic_body=True,
        clickable=True,
        obj=obj.obj_path,
        mtl=obj.mtl_path,
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
        height=0.1/obj.scale,
        width=0.1/obj.scale,
        depth=0.1/obj.scale,
        clickable=True,
        evt_handler=del_button_handler,
    )
    obj.count += 1

    scene.add_object(del_button)

def make_view_card(obj_name):
    obj = furnitureType[obj_name]
    # try:
    #     card = scene.get_persisted_obj(f"{obj.type_id}-card")
    # except:
    card = Card(
        object_id=f"{obj.type_id}-card",
        title=obj.desc_title,
        body=obj.description,
        bodyAlign="left",
        imgDirection="left",
        img=obj.img_path,
        imgSize="contain",
        closeButton=True,
        parent="button-panel",
        position=Position(0, 0, 0.5)
    )
    scene.add_object(card)

@scene.run_forever(interval_ms=10)
def move_box():
    global furniture
    for id, obj in furniture.items():
        if obj.grabber is not None and obj.child_pose_relative_to_parent is not None and obj.grabbing:
            hand_pose = pose_matrix(obj.grabber.data.position, obj.grabber.data.rotation)
            new_pose_abs = get_world_pose_when_parented(hand_pose, obj.child_pose_relative_to_parent)
            new_pose = get_relative_pose_to_parent(pose_matrix(main_pos, main_rot), new_pose_abs)

            new_position = (new_pose[0,3], new_pose[1,3], new_pose[2,3])
            new_rotation = Utils.matrix3_to_quat(new_pose[:3,:3])
            new_rotation = (new_rotation[3], new_rotation[0], new_rotation[1], new_rotation[2])

            obj.arena_obj.update_attributes(position=new_position, scale=obj.grabbed_scale)#, rotation=new_rotation)
            scene.update_object(obj.arena_obj)
            print("object position updated to", new_position)

@scene.run_once
def setup_scene():
    global my_iso
    target_reset = scene.get_persisted_obj("target")
    target_reset.update_attributes(textinput=None)
    # Update the object in the scene
    scene.update_object(target_reset)

    def make_tex_input_iso():
        global my_iso
        def evt_handler(scene, evt, msg):
            global my_iso
            if evt.type == "textinput":
                # display_name = scene.all_objects[evt.data.writer].displayName
                # print(f"{display_name}'s favorite food is: {evt.data.text}!")
                print(f"Text input: {evt.data.text}!")
                make_display_card(evt.data.text)    
        try:
            my_iso = scene.get_persisted_obj("my_iso")

            my_iso.evt_handler = evt_handler
            # my_iso.update_attributes(
            #     textinput=TextInput(
            #         on="mouseup",
            #         title="Enter your text",
            #         placeholder="Type something..."
            #     ),
            #     evt_handler=evt_handler
            # )
            scene.update_object(my_iso)
        except:
            print("Obj does not exist")
            my_iso = Image(
                object_id="my_iso",
                url="store/users/aadeshkd/img_text.jpg",
                position=(1,0,0.5),
                # color=(100,200,100),
                scale=(0.5,0.5,0.5),
                clickable=True,
                textinput=TextInput(
                    on="mouseup",
                    title="Say Something...",
                    # label="Please let us know below:",
                    placeholder="Start typing..."
                ),
                evt_handler=evt_handler,
                look_at="#my-camera",
                parent="button-panel",
            )

            # my_iso = PcdModel(
            #     object_id="my_iso",
            #     url="store/users/aadeshkd/target.pcd",
            #     position=(1,0,0.5),
            #     # color=(100,200,100),
            #     scale=(0.5,0.5,0.5),
            #     clickable=True,
            #     textinput=TextInput(
            #         on="mouseup",
            #         title="Say Something...",
            #         # label="Please let us know below:",
            #         placeholder="Start typing..."
            #     ),
            #     evt_handler=evt_handler,
            # )

            scene.add_object(my_iso)




    hello_card = Card(
        object_id="main_display",
        title="Ar-Vr Interaction",
        body="This platform is designed to simplify and host multi-user collaborations.",
        bodyAlign="center",
        position=Position(0.7, 0.5, -0.5),
        widthScale=0.25,
        parent="main",
        look_at="#my-camera"
    )
    scene.add_object(hello_card)

    # Add a popup prompt with single button

    def prompt_handler(_scene, evt, _msg):
        if evt.type == "buttonClick":
            if evt.data.buttonName == "OK":
                print("OK clicked!")
                scene.delete_object(prompt)

    # Add a button panel, with two sets of buttons

    first_buttonset = [Button(name="LASER"), Button(name="TEXT"), Button("FURNITURE"), Button("HOME")]
    second_buttonset = [Button(name="Home")] + [Button(name=s) for s in furnitureType.keys()]
    third_buttonset = [Button(name="Back"), Button(name="View"), Button(name="Add")]
    obj_name = None
    def button_handler(_scene, evt, _msg):
        global prompt
        global my_iso
        global obj_name
        if evt.type == "buttonClick":
            print(f"{evt.data.buttonName} clicked!")
            if evt.data.buttonName in ["TABLE", "TABLE1", "TABLE2"]: # Compawdre buttonName
                print(f"{evt.data.buttonName} clicked!")
                print(f"{evt.data.buttonIndex} clicked!")
            elif evt.data.buttonName == "LASER":  # Show prompt
                objs = scene.get_persisted_objs()
                for obj_id,obj in objs.items():
                    if obj_id in furniture.keys():
                        continue
                    # obj.update_attributes(clickable=True)
                    try:
                        if obj.clickable:
                            obj.update_attributes(evt_handler=click)
                            scene.update_object(obj)
                            print("Clickable: ", obj_id)
                    except AttributeError:
                        print("Skipped: ", obj_id)
                        pass
            elif evt.data.buttonName == "TEXT":
                make_tex_input_iso()
            elif evt.data.buttonName == "FURNITURE":  # switch to second button set
                print("Furniture button clicked!")
                button_panel.update_attributes(buttons=second_buttonset, title="Choose a table you want to add")
                scene.update_object(button_panel)
            elif evt.data.buttonName == "HOME":  # Reset to Home state
                print("Home button clicked!")
                # Restore initial button set
                button_panel.update_attributes(buttons=first_buttonset, title="Interaction Modes")
                scene.update_object(button_panel)
                print("Exiting all ongoing events.")
                objs = scene.get_persisted_objs()
                for obj_id, obj in objs.items():
                    if obj_id in furniture.keys():
                        continue
                    try:
                        obj.update_attributes(evt_handler=noop_handler)
                        scene.update_object(obj)
                        print(f"Event handler reset for object: {obj_id}")
                        
                    except AttributeError:
                        print(f"Skipped: {obj_id}")
                print(my_iso)
              
                if my_iso:
                    try:
                        # print("Removing text")
                        # my_iso = scene.get_persisted_obj("target")
                        # my_iso.update_attributes(textinput=None)
                        # # Update the object in the scene
                        # scene.update_object(my_iso)
                        scene.delete_object(my_iso)
                        my_iso = None  # Reset the variable
                        print("Deleted my_iso.")
                    except Exception as e:
                        print(f"Failed to delete my_iso: {e}")
            elif evt.data.buttonName == "Home":      
                button_panel.update_attributes(buttons=first_buttonset, title="Interaction Modes")
                scene.update_object(button_panel)
            elif evt.data.buttonName in furnitureType.keys():
                scene.update_object(button_panel, buttons=third_buttonset, 
                                    title=f"{evt.data.buttonName}")
                obj_name = evt.data.buttonName
            elif evt.data.buttonName == "Back":
                scene.update_object(button_panel, buttons=second_buttonset, 
                                    title="Choose a table you want to add")
            elif evt.data.buttonName == "View":
                make_view_card(obj_name)
            elif evt.data.buttonName == "Add":
                spawn_obj(obj_name)
            

    button_panel = ButtonPanel(
        object_id="button-panel",
        title="Interaction Modes",
        buttons=first_buttonset,
        vertical=True,
        font="Roboto-Mono",
        position=Position(-2, 0.5, 0),
        ###4, 0.5, -4.5
        parent="main",
        evt_handler=button_handler,
        look_at="#my-camera",
    )
    scene.add_object(button_panel)
    print("Obj added")

scene.run_tasks()

#    position=Position(1.5, 0.5, 0.5),