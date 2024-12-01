from arena import *
from dotenv import load_dotenv

load_dotenv()

scene = Scene(host="arenaxr.org", namespace=os.getenv("NAMESPACE"), scene=os.getenv("SCENE_NAME"))


def make_display_card(string):
    def prompt_handler(_scene, evt, _msg):
        nonlocal string
        if evt.type == "buttonClick":
            if evt.data.buttonName == "OK":
                print(f"Remove prompt {string}")
                scene.delete_object(scene.get_persisted_obj("display_prompt"))       
    try:
        # print("Trying to update object")
        display_prompt = scene.get_persisted_obj("display_prompt")
        display_prompt.data.title = string
        # display_prompt.evt_handler = prompt_handler
        scene.update_object(display_prompt)
        print("Obj updated")
    except:
        # print("Object not found")
        display_prompt = Prompt(
            object_id="display_prompt",
            title=string,
            description="This is a prompt with a description.",
            buttons=["OK"],
            position=Position(0, 2, -3),     # TODO: Relative to parent
            persist=True,
            look_at="#my-camera",
            evt_handler=prompt_handler,
        )
        display_prompt.data.textinput = None
        scene.add_object(display_prompt)
        print("New prompt obj added")
    


@scene.run_once
def make_tex_input_iso():
    def evt_handler(scene, evt, msg):
        if evt.type == "textinput":
            # display_name = scene.all_objects[evt.data.writer].displayName
            # print(f"{display_name}'s favorite food is: {evt.data.text}!")
            print(f"Text input: {evt.data.text}!")
            make_display_card(evt.data.text)    
    try:
        my_iso = scene.get_persisted_obj("my_iso")
        my_iso.evt_handler = evt_handler
        scene.update_object(my_iso)
    except:
        my_iso = Icosahedron(
            object_id="my_iso",
            position=(0,2,-5),
            color=(100,200,100),
            scale=(0.5,0.5,0.5),
            clickable=True,
            persist=True,
            textinput=TextInput(
                on="mouseup",
                title="Add a label here",
                # label="Please let us know below:",
                placeholder="Start typing..."
            ),
            evt_handler=evt_handler,
        )

        scene.add_object(my_iso)

scene.run_tasks()
