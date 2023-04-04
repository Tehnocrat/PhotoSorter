import keras
import tensorflow as tf
import PIL
import numpy as np
import pickle


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

dataset = tf.keras.utils.image_dataset_from_directory(
  r"tensorflow-for-poets-2-master\tf_files",
  validation_split=0.2,
  subset="training",
  seed=123,
  image_size=(256, 256),
  batch_size=32)

class_names = dataset.class_names


predictions = []
score = []
model = keras.models.load_model('MyModel')

for item in get_data():
    test_img = tf.keras.utils.load_img(
        item, target_size=(256, 256))
    img_array = tf.keras.utils.img_to_array(test_img)
    img_array = tf.expand_dims(img_array, 0)  # Create a batch

    final = ""
    predictions.append(model.predict(img_array))
    for i in predictions:
        final += class_names[np.argmax(tf.nn.softmax(i))] + " "
store_data(final)




'''print(
    "{} "
    "{:.2f}"
    .format(class_names[np.argmax(score)], 100 * np.max(score))
)'''

#print(
#    "This image less likely belongs to {}."
#    .format(class_names[np.argmax(score)+1])
#)
#print(score)

'''store_data(
    "{} "
    "{:.2f}"
    .format(class_names[np.argmax(score)], 100 * np.max(score)))'''