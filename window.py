import runpy
import tkinter as tk
from tkinter import filedialog
import pickle
import shutil
from PIL import Image

import os
from os import listdir
from os.path import isfile, join

sort_mode = "default"


def store_data(data):
    # Serialize the data
    data = data
    serialized_data = pickle.dumps(data)
    # Write the serialized data to a file
    with open("data.pickle", "wb") as f:
        f.write(serialized_data)

def get_data():
    # Read the serialized data from the file
    with open("data.pickle", "rb") as f:
        serialized_data = f.read()
    # Deserialize the data
    data = pickle.loads(serialized_data)
    return data




# Create the main window
root = tk.Tk()

root.geometry("500x200")

# Create a button to open the choose image popup
def open_image():
  if sort_mode == "default":
    filename = {filedialog.askopenfilename(title="Choose Image")}
    store_data(filename)
    runpy.run_module("working model")
    # Create text widget and specify size.
    T = tk.Text(root, height=10, width=52)
    # Create a label
    l = tk.Label(root, text=get_data())
    l.config(font=("Courier", 10))
    l.pack(expand=1)
  elif sort_mode == "metadata":
    filename = filedialog.askopenfilename(title="Choose Image")
    img = Image.open(filename)
    dateTaken = img.getexif()[34853] #TODO-TODO-TODO-TODO-TODO-TODO-TODO-TODO-TODO-TODO-TODO-TODO-TODO-TODO-TODO-TODO-
    print(dateTaken)







btn_image = tk.Button(root, text="Choose Image", command=open_image)
btn_image.pack()


# Create a button to open the documents directory
def open_documents():

    # Ask the user to choose a directory
    directory = filedialog.askdirectory(title="Choose Directory")

    #create sorting folders
    if not os.path.exists(directory + "/landscape"):
        os.mkdir(directory + "/landscape")
        os.mkdir(directory + "/portraits")
        os.mkdir(directory + "/fruits")

    # Get all files in the directory
    files = [f for f in listdir(directory) if isfile(join(directory, f))]

    # Filter out only the image files
    images = [f for f in files if f.endswith(".jpg") or f.endswith(".png") or f.endswith(".gif")]

    image_paths = [os.path.join(directory, image) for image in images]

    # Handle the images with a function
    def handle_image(image):

        store_data(image)
        runpy.run_module("working model")
        i = 0
        for item in get_data().split(" "):
            if item == "landscape_datset":
                os.rename(image[i], "/".join(image[i].split("/")[:-1]) + "/" + image[i].split("/")[-1].split("\\")[0] + "/landscape\\" +
                        image[i].split("/")[-1].split("\\")[-1])
            elif item == "Portraits_dataset":
                    os.rename(image[i], "/".join(image[i].split("/")[:-1]) + "/" + image[i].split("/")[-1].split("\\")[0] + "/portraits\\" +
                          image[i].split("/")[-1].split("\\")[-1])
            elif item == "fruits_dataset":
                    os.rename(image[i], "/".join(image[i].split("/")[:-1]) + "/" + image[i].split("/")[-1].split("\\")[0] + "/fruits\\" +
                          image[i].split("/")[-1].split("\\")[-1])
            i+=1

    listimages = []
    for imager in image_paths:

        listimages.append(imager)
    handle_image(listimages)



btn_documents = tk.Button(root, text="Open Documents Directory", command=open_documents)
btn_documents.pack()

def change_sort_mode():
    global sort_mode
    if sort_mode == "default":
        sort_mode = "metadata"
    elif sort_mode == "metadata":
        sort_mode = "default"
    text_box.delete('1.0', '100.0')
    text_box.insert('1.0', sort_mode)

# Create a simple button
btn_simple = tk.Button(root, text="Simple Button", command=change_sort_mode)
btn_simple.pack()




text_box = tk.Text(root)
text_box.height = 3  # set the height of text box to 5 lines
text_box.insert('1.0', sort_mode)
text_box.pack()

# Run the main loop
root.mainloop()