# 
import runpy
import platform
import tkinter as tk
from tkinter import filedialog
import pickle
from PIL import Image
import os
import shutil
from os import listdir
from os.path import isfile, join
from exif import Image
import PIL.ExifTags
from appscript import *
if platform.system() == "Darwin":
    from tkmacosx import Button
if platform.system() == "Windows" or platform.system() == "Linux":
    from tkinter import Button
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
root.title('PhotoSorter')
root.geometry("500x210")
root.configure(background='#FFFFD7', bg="#FFFFD7")

# Create a button to open the choose image popup
def open_image():
    rewrite_textbox("processing, please wait")
    if singlesortingmode.get() == "AI":
        filename = {filedialog.askopenfilename(title="Choose Image")}
        store_data(filename)
        runpy.run_module("working model")
        print(get_data())
        rewrite_textbox("this image belongs to " + get_data())
    elif singlesortingmode.get() == "metadata":
        filename = filedialog.askopenfilename(title="Choose Image")
        print(filename)
        perform = True
        try:
            img = PIL.Image.open(filename)
            print(img.getexif())
            img.getexif()
        except PIL.UnidentifiedImageError:
            rewrite_textbox("could not open image")
            perform = False
        except AttributeError:
            rewrite_textbox("could not open image")
            perform = False
        if perform and img.getexif() is not None:
            exif = {
                PIL.ExifTags.TAGS[tag]: v
                for tag, v in img.getexif().items()
                if tag in PIL.ExifTags.TAGS
            }
            print(exif.get("GPSInfo"))
            perform = True
            gpsinfo = {}
            if exif.get("GPSInfo") is not None:
                try:
                    gpsinfo = str(float(str(exif.get("GPSInfo").get(2))[1:-1].split(", ")[0]) + float(
                        str(exif.get("GPSInfo").get(2))[1:-1].split(", ")[1]) * 100 / 6000 + float(
                        str(exif.get("GPSInfo").get(2))[1:-1].split(", ")[2]) * 100 / 360000) + " " + str(
                        float(str(exif.get("GPSInfo").get(4))[1:-1].split(", ")[0]) + float(
                            str(exif.get("GPSInfo").get(4))[1:-1].split(", ")[1]) * 100 / 6000 + float(
                            str(exif.get("GPSInfo").get(4))[1:-1].split(", ")[2]) * 100 / 360000)
                except ValueError:
                    rewrite_textbox("no GPS info")
                    perform = False
                except AttributeError:
                    rewrite_textbox("no GPS info")
                    perform = False
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
        else:
            rewrite_textbox("could not get metadata")


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
            os.mkdir(directory + "/text")
            os.mkdir(directory + "/street")
            os.mkdir(directory + "/nature")
        # Get all files in the directory
        files = [f for f in listdir(directory) if isfile(join(directory, f))]
        # Filter out only the image files
        images = [f for f in files if f.lower().endswith(".jpg") or f.lower().endswith(".png") or f.lower().endswith(
            ".gif") or f.lower().endswith(".nef") or f.lower().endswith(".arw")]
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
                elif item == "portraits_dataset":
                    os.rename(image[i], "/".join(image[i].split("/")[:-1]) + "/" + "portraits/" +
                              image[i].split("/")[-1].split("\\")[-1])
                elif item == "fruits_dataset":
                    os.rename(image[i], "/".join(image[i].split("/")[:-1]) + "/" + "fruits/" +
                              image[i].split("/")[-1].split("\\")[-1])
                elif item == "text_dataset":
                    os.rename(image[i], "/".join(image[i].split("/")[:-1]) + "/" + "text/" +
                              image[i].split("/")[-1].split("\\")[-1])
                elif item == "street_dataset":
                    os.rename(image[i], "/".join(image[i].split("/")[:-1]) + "/" + "street/" +
                              image[i].split("/")[-1].split("\\")[-1])
                elif item == "nature_dataset":
                    os.rename(image[i], "/".join(image[i].split("/")[:-1]) + "/" + "nature/" +
                              image[i].split("/")[-1].split("\\")[-1])
                i += 1

        listimages = []
        for imager in image_paths:
            perform = True
            try:
                tryim = PIL.Image.open(imager)
            except PIL.UnidentifiedImageError:
                perform = False
            if perform:
                if enabled.get() == 1:
                    shutil.copy2(imager, directory + "/copy " + os.path.basename(imager))
                    listimages.append(directory + "/copy " + os.path.basename(imager))
                else:
                    listimages.append(imager)
            else:
                if not os.path.exists(directory + "/" + "unsorted"):
                    os.mkdir(directory + "/" + "unsorted")
                if enabled.get() == 1:
                    shutil.copy2(imager, directory + "/copy " + os.path.basename(imager))
                    os.rename(directory + "/copy " + os.path.basename(imager), directory + "/" + "unsorted" + "/copy " + os.path.basename(imager))
                else:
                    os.rename(imager, directory + "/" + "unsorted" + "/" + os.path.basename(imager))
        handle_image(listimages)

    elif multisortingmode.get() == "GPS":
        print(multisortingmode.get())
        directory = filedialog.askdirectory(title="Choose Directory")
        # Get all files in the directory
        files = [f for f in listdir(directory) if isfile(join(directory, f))]
        # Filter out only the image files
        images = [f for f in files if
                  f.lower().endswith(".jpg") or f.lower().endswith(".jpeg") or f.lower().endswith(
                      ".png") or f.lower().endswith(".gif") or f.lower().endswith(".nef") or f.lower().endswith(".arw")]
        image_paths = [os.path.join(directory, image) for image in images]
        # Get the EXIF data from each image
        gpsinfo = {}
        for image in image_paths:
            perform = True
            try:
                img = PIL.Image.open(image)
                img._getexif()
            except AttributeError:
                perform = False
            except PIL.UnidentifiedImageError:
                perform = False
            if perform:
                if img._getexif() != None:
                    exif_data = {
                        PIL.ExifTags.TAGS[k]: v
                        for k, v in img._getexif().items()
                        if k in PIL.ExifTags.TAGS
                    }
                    exif = exif_data
                    if exif_data.get('GPSInfo') != None:
                        try:
                            gpsinfo = str(float(str(exif.get("GPSInfo").get(2))[1:-1].split(", ")[0]) + float(
                                str(exif.get("GPSInfo").get(2))[1:-1].split(", ")[1]) * 100 / 6000 + float(
                                str(exif.get("GPSInfo").get(2))[1:-1].split(", ")[2]) * 100 / 360000) + " " + str(
                                float(str(exif.get("GPSInfo").get(4))[1:-1].split(", ")[0]) + float(
                                    str(exif.get("GPSInfo").get(4))[1:-1].split(", ")[1]) * 100 / 6000 + float(
                                    str(exif.get("GPSInfo").get(4))[1:-1].split(", ")[2]) * 100 / 360000)
                        except ValueError:
                            rewrite_textbox("no GPS info")
                            perform = False
                        # create sorting folders
                        if perform:
                            if not os.path.exists(directory + "/" + gpsinfo):
                                os.mkdir(directory + "/" + gpsinfo)
                            if enabled.get() == 1:
                                shutil.copy2(image, directory + "/copy " + os.path.basename(image))
                                os.rename(directory + "/copy " + os.path.basename(image), directory + "/" + gpsinfo + "/" + os.path.basename(image))
                            else:
                                os.rename(image, directory + "/" + gpsinfo + "/" + os.path.basename(image))
                    else:
                        if not os.path.exists(directory + "/" + "unsorted"):
                            os.mkdir(directory + "/" + "unsorted")
                        if enabled.get() == 1:
                            shutil.copy2(image, directory + "/copy " + os.path.basename(image))
                            os.rename(directory + "/copy " + os.path.basename(image),
                                      directory + "/" + "unsorted" + "/copy " + os.path.basename(image))
                        else:
                            os.rename(image, directory + "/" + "unsorted" + "/" + os.path.basename(image))
            else:
                if not os.path.exists(directory + "/" + "unsorted"):
                    os.mkdir(directory + "/" + "unsorted")
                if enabled.get() == 1:
                    shutil.copy2(image, directory + "/copy " + os.path.basename(image))
                    os.rename(directory + "/copy " + os.path.basename(image), directory + "/" + "unsorted" + "/copy " + os.path.basename(image))
                else:
                    os.rename(image, directory + "/" + "unsorted" + "/" + os.path.basename(image))


    elif multisortingmode.get() == "Device":
        directory = filedialog.askdirectory(title="Choose Directory")
        # Get all files in the directory
        files = [f for f in listdir(directory) if isfile(join(directory, f))]
        # Filter out only the image files
        images = [f for f in files if
                  f.lower().endswith(".jpg") or f.lower().endswith(".jpeg") or f.lower().endswith(
                      ".png") or f.lower().endswith(".gif") or f.lower().endswith(".nef") or f.lower().endswith(".arw")]
        image_paths = [os.path.join(directory, image) for image in images]
        # Get the EXIF data from each image
        for image in image_paths:
            print(enabled.get())
            perform = True
            try:
                img = PIL.Image.open(image)
                img._getexif()
            except AttributeError: perform = False
            except PIL.UnidentifiedImageError: perform = False
            except FileNotFoundError: perform = False
            if perform:
                if img._getexif() != None:
                    exif_data = {
                        PIL.ExifTags.TAGS[k]: v
                        for k, v in img._getexif().items()
                        if k in PIL.ExifTags.TAGS
                    }
                    print(exif_data)
                    modelinfo = exif_data.get("Model")
                    if not os.path.exists(directory + "/" + modelinfo):
                        os.mkdir(directory + "/" + modelinfo)
                    if enabled.get() == 1:
                        shutil.copy2(image, directory + "/copy " + os.path.basename(image))
                        os.rename(directory + "/copy " + os.path.basename(image), directory + "/" + modelinfo + "/copy " + os.path.basename(image))
                    else:
                        os.rename(image, directory + "/" + modelinfo + "/" + os.path.basename(image))
            else:
                if not os.path.exists(directory + "/" + "unsorted"):
                    os.mkdir(directory + "/" + "unsorted")
                if enabled.get() == 1:
                    shutil.copy2(image, directory + "/copy " + os.path.basename(image))
                    os.rename(directory + "/copy " + os.path.basename(image),
                              directory + "/" + "unsorted" + "/copy " + os.path.basename(image))
                else:
                    os.rename(image, directory + "/" + "unsorted" + "/" + os.path.basename(image))

    elif multisortingmode.get() == "Date":
        directory = filedialog.askdirectory(title="Choose Directory")
        # Get all files in the directory
        files = [f for f in listdir(directory) if isfile(join(directory, f))]
        # Filter out only the image files
        images = [f for f in files if
                  f.lower().endswith(".jpg") or f.lower().endswith(".jpeg") or f.lower().endswith(
                      ".png") or f.lower().endswith(".gif") or f.lower().endswith(".nef") or f.lower().endswith(".arw")]
        image_paths = [os.path.join(directory, image) for image in images]
        # Get the EXIF data from each image
        for image in image_paths:
            perform = True
            try:
                img = PIL.Image.open(image)
            except PIL.UnidentifiedImageError:
                perform = False
            if perform == True:
                if img._getexif() != None:
                    exif_data = {
                    PIL.ExifTags.TAGS[k]: v
                    for k, v in img._getexif().items()
                    if k in PIL.ExifTags.TAGS
                }
                if exif_data.get('DateTime') != None:
                    dateinfo = exif_data.get("DateTime").split(" ")[0]
                    if not os.path.exists(directory + "/" + dateinfo):
                        os.mkdir(directory + "/" + dateinfo)
                    if enabled.get() == 1:
                        shutil.copy2(image, directory + "/copy " + os.path.basename(image))
                        os.rename(directory + "/copy " + os.path.basename(image), directory + "/" + dateinfo + "/copy " + os.path.basename(image))
                    else:
                        os.rename(image, directory + "/" + dateinfo + "/" + os.path.basename(image))
            else:
                if not os.path.exists(directory + "/" + "unsorted"):
                    os.mkdir(directory + "/" + "unsorted")
                if enabled.get() == 1:
                    shutil.copy2(image, directory + "/copy " + os.path.basename(image))
                    os.rename(directory + "/copy " + os.path.basename(image),
                              directory + "/" + "unsorted" + "/copy " + os.path.basename(image))
                else:
                    os.rename(image, directory + "/" + "unsorted" + "/" + os.path.basename(image))


    elif multisortingmode.get() == "extension":
        directory = filedialog.askdirectory(title="Choose Directory")
        # Get all files in the directory
        images = [f for f in listdir(directory) if isfile(join(directory, f))]
        # Filter out only the image files
        image_paths = [os.path.join(directory, image) for image in images]
        # Get the EXIF data from each image
        for image in image_paths:
            print(image)
            image = str(image)
            if enabled.get() == 0:
              if os.path.basename(image) != ".DS_Store":
                if not os.path.exists(directory + "/" + image[image.index(".")+1:]):
                    os.mkdir(directory + "/" + image[image.index(".")+1:])
                    os.rename(image, directory + "/" + image[image.index(".") + 1:] + "/" + os.path.basename(image))
            else:
                if not os.path.exists(directory + "/" + image[image.index(".")+1:]):
                    os.mkdir(directory + "/" + image[image.index(".")+1:])
                shutil.copy2(image, directory + "/copy " + os.path.basename(image))
                os.rename(directory + "/copy " + os.path.basename(image), directory + "/" + image[image.index(".") + 1:] + "/copy " + os.path.basename(image))

    rewrite_textbox("Done!")

f_top = tk.Frame(root, bg="#FFFFD7")
f_top.configure(background='#FFFFD7')
f_bot = tk.Frame(root, bg="#FFFFD7")
f_bot.configure(background='#FFFFD7')

btn_image = Button(f_top, text="Choose Single Image", command=open_image, borderless=1)

singlesortingmode = tk.StringVar(root)
singlesortingmode.set("Choise for single sort")  # default value
w = tk.OptionMenu(f_top, singlesortingmode, "Metadata", "AI")
w.configure(background='#FFFFD7')

btn_documents = Button(f_bot, text="Open Documents Directory", command=open_documents, borderless=1)

# create the drop-down list
multisortingmode = tk.StringVar(root)
multisortingmode.set("Choise for multiple sort")  # default value
w2 = tk.OptionMenu(f_bot, multisortingmode, "GPS", "Device", "Date", "Extension", "AI")
w2.configure(background='#FFFFD7')

f_top.pack(fill="x")
f_bot.pack(fill="x")
btn_image.pack(side="left")
w.pack(side="right")
btn_documents.pack(side="left")
w2.pack(side="right")

# Create a simple button
def nfefe():
    if platform.system() == "Darwin":
        file_to_show = directory
        app("Finder").open(mactypes.Alias(file_to_show).alias)
        '''app(u'/System/Library/CoreServices/Finder.app').startup_disk.folders[u'Applications'].application_files[
            u'iTunes.app']'''

button = Button(root, text="Open Folder with sorted images", command=nfefe, borderless=1)
button.pack()

enabled = tk.IntVar()
enabled_checkbutton = tk.Checkbutton(text="Create copies of sorted images?", variable=enabled, bg="#FFFFD7")
enabled_checkbutton.pack()

text_box = tk.Text(root, bg="#F0F0E0")
text_box.height = 10
text_box.insert('1.0', sort_mode)
text_box.pack()

# Run the main loop
root.mainloop()