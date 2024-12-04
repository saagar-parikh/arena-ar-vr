from arena import *
from dotenv import load_dotenv

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
            title=string,
            description="This is a prompt with a description.",
            buttons=["OK"],
            position=Position(0, 0, -0.5),     # TODO: Relative to parent
            look_at="#my-camera",
            evt_handler=prompt_handler,
            parent="my_iso",
        )
        display_prompt.data.textinput = None
        scene.add_object(display_prompt)
        print("New prompt obj added")
    

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
    second_buttonset = [Button("TABLE"), Button("BACK")]
    third_buttonset = [Button("TABLE1"), Button("TABLE2"), Button("BACK")]

    def button_handler(_scene, evt, _msg):
        global prompt
        global my_iso
        if evt.type == "buttonClick":
            print(f"{evt.data.buttonName} clicked!")
            if evt.data.buttonName in ["TABLE", "TABLE1", "TABLE2"]: # Compawdre buttonName
                print(f"{evt.data.buttonName} clicked!")
                print(f"{evt.data.buttonIndex} clicked!")
            elif evt.data.buttonName == "LASER":  # Show prompt
                objs = scene.get_persisted_objs()
                for obj_id,obj in objs.items():
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
                print("Hello")
                scene.update_object(button_panel, buttons=second_buttonset)
            elif evt.data.buttonName == "HOME":  # Reset to Home state
                print("Home button clicked!")
                # Restore initial button set
                scene.update_object(button_panel, buttons=first_buttonset)
                print("Exiting all ongoing events.")
                objs = scene.get_persisted_objs()
                for obj_id, obj in objs.items():
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
            elif evt.data.buttonIndex == 1:      # compare buttonIndex, switch 1st set
                scene.update_object(button_panel, buttons=first_buttonset)

    button_panel = ButtonPanel(
        object_id="button-panel",
        title="Interaction Modes",
        buttons=first_buttonset,
        vertical=True,
        font="Roboto-Mono",
        position=Position(4, 0.5, -4.5),
        parent="main",
        evt_handler=button_handler,
        look_at="#my-camera",
    )
    scene.add_object(button_panel)
    print("Obj added")

scene.run_tasks()

#    position=Position(1.5, 0.5, 0.5),