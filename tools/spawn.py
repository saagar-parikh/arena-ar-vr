from arena import *
from dotenv import load_dotenv

load_dotenv()

scene = Scene(host="arenaxr.org", namespace=os.getenv("NAMESPACE"), scene=os.getenv("SCENE_NAME"))


class Furniture:
    def __init__(self, obj_id, name, img_path, obj_path, description):
        self.obj_id = obj_id
        self.name = name
        self.img_path = img_path
        self.obj_path = obj_path
        self.description = description
        self.count = 0

furniture = {}
furniture["Table 1"] = Furniture(obj_id="table-1", name="Table 1", 
                                 img_path="/store/users/saagardp/img.jpg", 
                                 obj_path="/store/users/saagardp/lab1.glb",
                                 description="Table 1 description placeholder")
furniture["Table 2"] = Furniture(obj_id="table-2", name="Table 2", 
                                 img_path="/store/users/saagardp/img.jpg", 
                                 obj_path="/store/users/aadeshkd/table2.gltf",
                                 description="Table 2 description placeholder")
furniture["Table 3"] = Furniture(obj_id="table-3", name="Table 3", 
                                 img_path="/store/users/saagardp/img.jpg", 
                                 obj_path="/store/users/aadeshkd/table3.gltf",
                                 description="Table 3 description placeholder")

def make_display_card(obj_name):
    obj = furniture[obj_name]
    # try:
    #     card = scene.get_persisted_obj(f"{obj.obj_id}-card")
    # except:
    card = Card(
        object_id=f"{obj.obj_id}-card",
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

def spawn_obj(obj_name):
    obj = furniture[obj_name]
    obj_count = obj.count


    scene_obj = GLTF(
        object_id=f"{obj.obj_id}-{obj.count}",
        parent="main",
        position=Position(12.5, 1, -2),
        # dynamic_body=True,
        clickable=True,
        url=obj.obj_path,
    )
    scene.add_object(scene_obj)
    print(f"Object added: {obj.obj_id}-{obj.count}")

    def del_button_handler(scene, evt, msg):
        if evt.type == "mousedown":
            scene.delete_object(scene_obj)
            print(f"Object deleted: {obj.obj_id}-{obj_count}")

    # Delete button
    del_button = Box(
        object_id=f"{obj.obj_id}-{obj.count}-del",
        parent=f"{obj.obj_id}-{obj.count}",
        position=Position(0.1, 0.1, 0.1),
        height=0.1,
        width=0.1,
        depth=0.1,
        clickable=True,
        evt_handler=del_button_handler,
    )
    obj.count += 1

    scene.add_object(del_button)


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