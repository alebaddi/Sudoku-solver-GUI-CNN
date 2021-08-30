import numpy as np
import sklearn
import tensorflow
import cv2


def train_and_save_model():
    '''Save a CNN model trained on a dataset composed of digits taken from a sudoku magazine'''
    # trained with epochs=15, an accuracy of 0.9990 has been obtained

    import pickle
    # open dictionary and import the dataset
    file = open("sudoku_dataset.pkl", "rb")
    dataset = pickle.load(file)
    file.close()

    x, y = dataset['data'], dataset['target']
    y = y.reshape(1310,)

    # shuffle the dataset
    from sklearn.utils import shuffle
    x, y = shuffle(x, y, random_state=0)

    # train-test splitting
    x_train, x_test, y_train, y_test = x[:1048], x[1048:], y[:1048], y[1048:]

    # reshape data to fit model
    x_train = x_train.reshape(x_train.shape[0], 28, 28, 1)
    x_test = x_test.reshape(x_test.shape[0], 28, 28, 1)

    # normalize the train/test dataset
    x_train, x_test = x_train.astype('float32') / 255.0, x_test.astype('float32') / 255.0

    from tensorflow.keras.utils import to_categorical
    # one-hot encode target column
    y_train_OHE = to_categorical(y_train)
    y_test_OHE = to_categorical(y_test)


    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import MaxPool2D, Conv2D, Flatten, Dense

    # create the model
    model = Sequential()

    # add model layers
    model.add(Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=(28,28,1)))
    model.add(Conv2D(32, (3, 3), activation='relu'))
    model.add(MaxPool2D())

    model.add(Conv2D(16, (3, 3), activation='relu', padding='SAME'))
    model.add(Conv2D(64, (5, 5), activation='relu', padding='SAME'))
    model.add(Conv2D(32, (1, 1), activation='relu', padding='SAME'))
    model.add(MaxPool2D())

    model.add(Conv2D(8, (3, 3), activation='relu', padding='SAME'))
    model.add(Conv2D(32, (5, 5), activation='relu', padding='SAME'))
    model.add(Conv2D(16, (1, 1), activation='relu', padding='SAME'))
    model.add(Flatten())

    model.add(Dense(400, activation='relu'))
    model.add(Dense(10, activation='softmax'))

    # compile the model using accuracy to measure model performance
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    # train the model
    model.fit(x_train, y_train_OHE, validation_data=(x_test, y_test_OHE), epochs=15)

    # save the model
    model.save("model_sudoku.hdf5", overwrite=True)
