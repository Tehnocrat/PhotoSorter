import runpy
import tkinter as tk
from tkinter import filedialog
import pickle
from PIL import Image
import os
from os import listdir
from os.path import isfile, join
from exif import Image
import PIL.ExifTags
from appscript import *

sort_mode = "default"


def rewrite_textbox(newtext):
    text_box.delete('1.0', '100.0')
    text_box.insert('1.0', newtext)


def decimal_coords(coords, ref):
    decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
    if ref == "S" or ref == 'W':
        decimal_degrees = -decimal_degrees
    return decimal_degrees


def image_coordinates(image_path):
    coords = []
    with open(image_path, 'rb') as src:
        img = Image(src)
    if img.has_exif:
        try:
            coords = (decimal_coords(img.gps_latitude,
                                     img.gps_latitude_ref),
                      decimal_coords(img.gps_longitude,
                                     img.gps_longitude_ref))
        except AttributeError:
            print('No Coordinates')
    else:
        print('The Image has no EXIF information')

    return {"imageTakenTime": img.datetime_original, "geolocation_lat": coords[0], "geolocation_lng": coords[1]}


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
    rewrite_textbox("processing, please wait")
    if singlesortingmode.get() == "AI":
        filename = {filedialog.askopenfilename(title="Choose Image")}
        store_data(filename)
        runpy.run_module("working model")
        # Create text widget and specify size.
        # T = tk.Text(root, height=10, width=52)
        # Create a label
        print(get_data())
        rewrite_textbox("this image belongs to " + get_data())
        # l = tk.Label(root, text=get_data())
        # l.config(font=("Courier", 10))
        # l.pack(expand=1)
    elif singlesortingmode.get() == "metadata":
        filename = filedialog.askopenfilename(title="Choose Image")
        # img = Image.open(filename)
        print(filename)
        img = PIL.Image.open(filename)
        if img._getexif != None:
            exif = {
                PIL.ExifTags.TAGS[k]: v
                for k, v in img._getexif().items()
                if k in PIL.ExifTags.TAGS
            }
            if exif.get("GPSInfo") != None:
                gpsinfo = str(float(str(exif.get("GPSInfo").get(2))[1:-1].split(", ")[0]) + float(
                    str(exif.get("GPSInfo").get(2))[1:-1].split(", ")[1]) * 100 / 6000 + float(
                    str(exif.get("GPSInfo").get(2))[1:-1].split(", ")[2]) * 100 / 360000) + " " + str(
                    float(str(exif.get("GPSInfo").get(4))[1:-1].split(", ")[0]) + float(
                        str(exif.get("GPSInfo").get(4))[1:-1].split(", ")[1]) * 100 / 6000 + float(
                        str(exif.get("GPSInfo").get(4))[1:-1].split(", ")[2]) * 100 / 360000)

            perform = True
            try:
                exif.get("GPSInfo").get(2)
            except AttributeError:
                perform = False
                rewrite_textbox("no gps information")
            finally:
                if perform:
                    rewrite_textbox(gpsinfo)

            perform = True
            try:
                exif.get("Model")
            except AttributeError:
                perform = False
                rewrite_textbox(text_box.get('1.0', '100.0') + "no model information")
            finally:
                if perform:
                    rewrite_textbox(text_box.get('1.0', '100.0') + "\n" + str(exif.get("Model")))

            perform = True
            try:
                exif.get("DateTime")
            except AttributeError:
                perform = False
                rewrite_textbox(text_box.get('1.0', '100.0') + "\n" + "no datetime information")
            finally:
                if perform:
                    rewrite_textbox(text_box.get('1.0', '100.0') + "\n" + str(exif.get("DateTime")))
        else: print("No exif Data")



btn_image = tk.Button(root, text="Choose Image", command=open_image)
btn_image.pack()


# Create a button to open the documents directory
directory = ""
def open_documents():
    global directory
    rewrite_textbox("processing... please wait")
    if multisortingmode.get() == "AI":
    # Ask the user to choose a directory
        directory = filedialog.askdirectory(title="Choose Directory")

    # create sorting folders
        if not os.path.exists(directory + "/landscape"):
            os.mkdir(directory + "/landscape")
            os.mkdir(directory + "/portraits")
            os.mkdir(directory + "/fruits")
    # Get all files in the directory
        files = [f for f in listdir(directory) if isfile(join(directory, f))]
    # Filter out only the image files
        images = [f for f in files if f.lower().endswith(".jpg") or f.lower().endswith(".png") or f.lower().endswith(".gif") or f.lower().endswith(".nef")]
        image_paths = [os.path.join(directory, image) for image in images]
    # Handle the images with a function
        def handle_image(image):
            store_data(image)
            runpy.run_module("working model")
            i = 0
            for item in get_data().split(" "):
                '''image[i].split("/")[-1].split("")[0]'''
                if item == "landscape_datset":
                    os.rename(image[i], "/".join(image[i].split("/")[:-1]) + "/landscape/" +
                            image[i].split("/")[-1].split("\\")[-1])
                elif item == "Portraits_dataset":
                    os.rename(image[i], "/".join(image[i].split("/")[:-1]) + "/" + "portraits/" +
                            image[i].split("/")[-1].split("\\")[-1])
                elif item == "fruits_dataset":
                    os.rename(image[i], "/".join(image[i].split("/")[:-1]) + "/" +  "fruits/" +
                            image[i].split("/")[-1].split("\\")[-1])
                i += 1

        listimages = []
        for imager in image_paths:
            listimages.append(imager)
        handle_image(listimages)

    elif multisortingmode.get() == "GPS":
        print(multisortingmode.get())
        directory = filedialog.askdirectory(title="Choose Directory")
        # Get all files in the directory
        files = [f for f in listdir(directory) if isfile(join(directory, f))]
        # Filter out only the image files
        images = [f for f in files if
                  f.lower().endswith(".jpg") or f.lower().endswith(".jpeg") or f.lower().endswith(".png") or f.lower().endswith(".gif")  or f.lower().endswith(".nef")]
        image_paths = [os.path.join(directory, image) for image in images]
        # Get the EXIF data from each image
        exif_data = {}
        for image in image_paths:
            img = PIL.Image.open(image)
            if img._getexif() != None:
                exif_data = {
                    PIL.ExifTags.TAGS[k]: v
                    for k, v in img._getexif().items()
                    if k in PIL.ExifTags.TAGS
                }
            exif = exif_data
            print(exif_data)
            if exif_data.get('GPSInfo') != None:
                gpsinfo = str(float(str(exif.get("GPSInfo").get(2))[1:-1].split(", ")[0]) + float( #TODO-TODO-TODO
                    str(exif.get("GPSInfo").get(2))[1:-1].split(", ")[1]) * 100 / 6000 + float(
                    str(exif.get("GPSInfo").get(2))[1:-1].split(", ")[2]) * 100 / 360000) + " " + str(
                    float(str(exif.get("GPSInfo").get(4))[1:-1].split(", ")[0]) + float(
                        str(exif.get("GPSInfo").get(4))[1:-1].split(", ")[1]) * 100 / 6000 + float(
                        str(exif.get("GPSInfo").get(4))[1:-1].split(", ")[2]) * 100 / 360000)
            # create sorting folders
                if not os.path.exists(directory + "/" + gpsinfo):
                    os.mkdir(directory + "/" + gpsinfo)
                os.rename(image, directory + "/" + gpsinfo + "/" + os.path.basename(image))
 # todo сделать по красоте
    elif multisortingmode.get() == "Device":
        directory = filedialog.askdirectory(title="Choose Directory")
        # Get all files in the directory
        files = [f for f in listdir(directory) if isfile(join(directory, f))]
        # Filter out only the image files
        images = [f for f in files if
                  f.lower().endswith(".jpg") or f.lower().endswith(".jpeg") or f.lower().endswith(".png") or f.lower().endswith(".gif") or  f.lower().endswith(".nef")]
        image_paths = [os.path.join(directory, image) for image in images]
        # Get the EXIF data from each image
        for image in image_paths:
            img = PIL.Image.open(image)
            exif_data = {}
            if img._getexif() != None:
                exif_data = {
                    PIL.ExifTags.TAGS[k]: v
                    for k, v in img._getexif().items()
                    if k in PIL.ExifTags.TAGS
                }
                print(exif_data)
                if exif_data.get('Model') != None:
                    modelinfo = exif_data.get("Model")
                    if not os.path.exists(directory + "/" + modelinfo):
                        os.mkdir(directory + "/" + modelinfo)
                    os.rename(image, directory + "/" + modelinfo + "/" + os.path.basename(image))

    elif multisortingmode.get() == "Date":
        directory = filedialog.askdirectory(title="Choose Directory")
        # Get all files in the directory
        files = [f for f in listdir(directory) if isfile(join(directory, f))]
        # Filter out only the image files
        images = [f for f in files if
                  f.lower().endswith(".jpg") or f.lower().endswith(".jpeg") or f.lower().endswith(".png") or f.lower().endswith(".gif") or f.lower().endswith(".nef")]
        image_paths = [os.path.join(directory, image) for image in images]
        # Get the EXIF data from each image
        for image in image_paths:
            img = PIL.Image.open(image)
            exif_data = {}
            if img._getexif() != None:
                exif_data = {
                    PIL.ExifTags.TAGS[k]: v
                    for k, v in img._getexif().items()
                    if k in PIL.ExifTags.TAGS
                }
                print(exif_data)
                if exif_data.get('DateTime') != None:
                    dateinfo = exif_data.get("DateTime").split(" ")[0]
                    if not os.path.exists(directory + "/" + dateinfo):
                        os.mkdir(directory + "/" + dateinfo)
                    os.rename(image, directory + "/" + dateinfo + "/" + os.path.basename(image))
    rewrite_textbox("Done!")
# TODO fix slashes instead of double dots


btn_documents = tk.Button(root, text="Open Documents Directory", command=open_documents)
btn_documents.pack()


# create the drop-down list
multisortingmode = tk.StringVar(root)
multisortingmode.set("Choise for multiple sort")  # default value
w = tk.OptionMenu(root, multisortingmode, "GPS", "Device", "Date", "AI")
w.pack()

singlesortingmode = tk.StringVar(root)
singlesortingmode.set("Choise for single sort")  # default value
w = tk.OptionMenu(root, singlesortingmode, "metadata", "AI")
w.pack()

# Create a simple button
def nfefe():
    file_to_show = directory
    app("Finder").open(mactypes.Alias(file_to_show).alias)
    '''app(u'/System/Library/CoreServices/Finder.app').startup_disk.folders[u'Applications'].application_files[
        u'iTunes.app']'''

button = tk.Button(root, text="Open Folder with sorted images", command=nfefe)
button.pack()


text_box = tk.Text(root)
text_box.height = 3  # set the height of text box to 5 lines
text_box.insert('1.0', sort_mode)
text_box.pack()

# Run the main loop
root.mainloop()
