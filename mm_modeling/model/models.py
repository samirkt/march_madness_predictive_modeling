import keras
from utils.globs import *
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from keras.callbacks import EarlyStopping,ModelCheckpoint
import pickle
import os

def lr(data):
    x_train, x_test, y_train, y_test = data

    # Parameters
    penalty = 'l2'
    max_iter = 9000

    model_name = get_model_name('.obj')
    output_string = "\n{0}\n***LOGISTIC REGRESSION\n{1}:\nPenalty: {2}\nMax Iterations: {3}\n".format(tourney_ref,model_name,penalty,max_iter)
    print(output_string)


    # Build model
    model = LogisticRegression(penalty=penalty,max_iter=max_iter,verbose=1)

    # Fit model
    model.fit(x_train, y_train)

    # Evaluate
    train_acc = 'Train acc: ' + str(accuracy_score(y_train, model.predict(x_train)))
    val_acc = 'Val acc: ' + str(accuracy_score(y_test, model.predict(x_test)))

    # Save model
    pickle.dump(model, open(model_name, 'wb'))
    # LOAD: loaded_model = pickle.load(open(filename, 'rb'))

    # Store results
    output_string += '\n' + train_acc + '\n' + val_acc + '\n\n'
    print(output_string)
    write_model_info(output_string)

    os.system('say \'done\'')


def rf(data):
    x_train, x_test, y_train, y_test = data

    # Parameters
    num_trees = 500
    max_depth = 8 
    max_samples = 100

    model_name = get_model_name('.obj')
    output_string = "\n{0}\n***RANDOM FOREST\n{1}:\nNum Trees: {2}\nMax Depth: {3}\n".format(tourney_ref,model_name,num_trees,max_depth)
    print(output_string)

    # Build model
    model = RandomForestClassifier(n_estimators=num_trees,max_depth=max_depth,bootstrap=True,max_samples=max_samples)


    # Fit model
    model.fit(x_train, y_train)

    # Evaluate
    train_acc = 'Train acc: ' + str(accuracy_score(y_train, model.predict(x_train)))
    val_acc = 'Val acc: ' + str(accuracy_score(y_test, model.predict(x_test)))

    # Save model
    pickle.dump(model, open(model_name, 'wb'))
    # LOAD: loaded_model = pickle.load(open(filename, 'rb'))

    # Store results
    output_string += '\n' + train_acc + '\n' + val_acc + '\n\n'
    print(output_string)
    write_model_info(output_string)

    os.system('say \'done\'')


def nn(data):
    x_train, x_test, y_train, y_test = data

    # Parameters
    batch_size = 128
    patience = 10
    epochs = 5000
    layer1 = 200
    layer2 = 200
    dropout = 0.6

    model_name = get_model_name('.h5')
    output_string = "\n{0}\n***NEURAL NET\n{1}:\nBatch size: {2}\nEpochs: {3}\nLayer1: {4}\nLayer2: {5}\nDropout: {6}\nPatience: {7}\n".format(tourney_ref,model_name,batch_size,epochs,layer1,layer2,dropout,patience)
    print(output_string)

    # Compile model
    model = build_model(len(x_train[0]),layer1,layer2,dropout)

    # Fit model
    early_stop = EarlyStopping(monitor='loss', mode='min', verbose=1, patience=patience)
    #model_save = ModelCheckpoint(model_name, monitor='val_loss', mode='min', save_best_only=True)
    model.fit(x_train,
            y_train,
            batch_size=batch_size,
            verbose=1,
            epochs=epochs,
            #steps_per_epoch=len(x_train)//batch_size,
            validation_data=(x_test,y_test),
            #validation_steps=10,
            callbacks=[early_stop])

    # Evaluate
    loss_and_metrics = model.evaluate(x_train, y_train)
    train_loss = 'Train Loss = '+str(loss_and_metrics[0])
    train_acc = 'Train Accuracy = '+str(loss_and_metrics[1])
    loss_and_metrics = model.evaluate(x_test, y_test)
    val_loss = 'Val Loss = '+str(loss_and_metrics[0])
    val_acc = 'Val Accuracy = '+str(loss_and_metrics[1])

    print(train_loss)
    print(train_acc)
    print(val_loss)
    print(val_acc)

    # Save model
    model.save(model_name)
    # LOAD: model = keras.models.load_model('path/to/location')

    # Store results
    str_list = []
    model.summary(print_fn=lambda x: str_list.append(x))
    output_string += '\n'.join(str_list)
    output_string += '\n' + train_loss + '\n' + train_acc + '\n' + val_loss + '\n' + val_acc + '\n\n'
    print(output_string)
    write_model_info(output_string)

    os.system('say \'done\'')


def build_model(num_cols,layer1,layer2,dropout):
    model = keras.Sequential()
    model.add(keras.layers.InputLayer(input_shape=(num_cols,)))
    model.add(keras.layers.Dense(layer1, input_shape=(num_cols,), activation="relu"))
    model.add(keras.layers.Dropout(dropout))
    model.add(keras.layers.Dense(layer2, activation="relu"))
    model.add(keras.layers.Dropout(dropout))
    model.add(keras.layers.Dense(1, activation="sigmoid"))

    model.compile(loss='binary_crossentropy',
            optimizer='adam',
            metrics=['accuracy'])

    return model

def write_model_info(output_string):
    with open('outputs/outputs.txt','a') as f:
        f.write(output_string + '\n\n')

def get_model_name(suff):
    # Pick model name
    model_dir = 'saved/'
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    model_list = os.listdir(model_dir)
    model_id = 0
    while True:
        model_name = 'model' + str(model_id) + suff
        if model_name in model_list:
            model_id += 1
        else:
            break

    return 'saved/' + model_name


