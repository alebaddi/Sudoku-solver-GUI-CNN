import numpy as np
import sklearn
import tensorflow
import cv2


def train_and_save_model_mnist():
    '''Save a CNN model trained on a dataset given by the union of digits taken from a sudoku magazine and the MNIST handwritten digits dataset'''
    # trained with epochs=15, an accuracy of 0.9958 has been obtained

    import pickle
    # open dictionary and import the dataset
    file = open("sudoku_dataset.pkl", "rb")
    dataset = pickle.load(file)
    file.close()

    x1, y1 = dataset['data'], dataset['target']
    y1 = y1.reshape(1310,)

    # shuffle the dataset
    from sklearn.utils import shuffle
    x1, y1 = shuffle(x1, y1, random_state=0)

    # train-test splitting
    x_train_1, x_test_1, y_train_1, y_test_1 = x1[:1048], x1[1048:], y1[:1048], y1[1048:]

    from tensorflow.keras.datasets import mnist
    # download mnist data and split into train and test sets
    (x_train_2, y_train_2), (x_test_2, y_test_2) = mnist.load_data()

    x_train = np.concatenate((x_train_1, x_train_2), axis=0)
    x_test = np.concatenate((x_test_1, x_test_2), axis=0)
    y_train = np.concatenate((y_train_1, y_train_2), axis=0)
    y_test = np.concatenate((y_test_1, y_test_2), axis=0)

    x_train, y_train = shuffle(x_train, y_train, random_state=1)
    x_test, y_test = shuffle(x_train, y_train, random_state=1)


    # reshape data to fit the model
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
    model.save("model_sudoku_mnist.hdf5", overwrite=True)
