import tensorflow as tf
import keras
from sklearn.model_selection import train_test_split
from keras.callbacks import EarlyStopping,ModelCheckpoint
import pandas as pd
import numpy as np
import sys, os

def load():
    ### Set year parameters
    if len(sys.argv) == 1:  # Default year range
        start = 1993    # First season with data available
        end = 2019
    elif len(sys.argv) == 2:    # Manual year entry (single year)
        start = sys.argv[1]
        end = sys.argv[1]
    elif len(sys.argv) == 3: # Manual year entry
        start = sys.argv[1]
        end = sys.argv[2]
    else:   
        print('Error: Invalid number of arguments (%s)' % len(sys.argv))
        quit()

    try:
        sfilename = "../data/season/"+str(start)+"_to_"+str(end)+"_season_clean.csv"
        print('Loading season data from file %s' % (sfilename))
        season = pd.read_csv(sfilename)
    except:
        print('Error: Could not read file %s' % (sfilename))


    try:
        tfilename = "../data/tourney/"+str(start)+"_to_"+str(end)+"_tourney.csv"
        print('Loading tourney data from file %s' % (tfilename))
        tourney = pd.read_csv(tfilename)
    except:
        print('Error: Could not read file %s' % (tfilename))
    
    return season, tourney
    

def preprocess(season, tourney):
    season = season.loc[:, season.isnull().sum() < 0.9*len(season)]

    tourney = tourney[['Year','Round','school_seed','School','opponent_seed','Opponent','PTS','PTS.1']]

    # NOTE: IF CATEGORIZING ROUNDS, the round names are not consistent in the data. Dropping for now..
    #tourney['Round'] = pd.Categorical(tourney['Round'],ordered=True,categories=['First Four','First Round','Second Round','Regional Semifinal','Regional Final','National Semifinal','National Final'])
    #tourney['Round'] = tourney['Round'].cat.codes

    data = []
    for index, match in tourney.iterrows():
        team1 = season[(season['Year']==match['Year']) & (season['_School']==match['School'])]
        team1.drop(['_School'],axis=1,inplace=True)
        team2 = season[(season['Year']==match['Year']) & (season['_School']==match['Opponent'])]
        team2.drop(['_School'],axis=1,inplace=True)
        match1 = match[['school_seed','opponent_seed']]
        match2 = match[['opponent_seed','school_seed']]


        if match['PTS'] > match['PTS.1']:
            targ1 = 1
            targ2 = 0
        else:
            targ1 = 0
            targ2 = 1
        
        
        data_row1 = np.concatenate((team1, team2, match1, targ1), axis=None)
        data_row2 = np.concatenate((team2, team1, match2, targ2), axis=None)

        data.append(data_row1)
        data.append(data_row2)


    cols = np.concatenate((team1.columns.values, team2.columns.values, ['team1_seed','team2_seed','target']), axis=None)
    table = pd.DataFrame(columns=cols,data=data)


    return table

def missing_vals(data):
    #print_missing_percentages(data)
    data.fillna(0,inplace=True)
    print("Dataset has nans: ",data.isna().values.any())

    return data

def nn(x): 
    # Parameters
    batch_size=len(x)
    epochs = 20
    layer1 = 200
    layer2 = 200
    dropout = 0.2

    model_name = get_model_name()
    output_string = "\nNEURAL NET\n{0}:\nBatch size: {1}\nEpochs: {2}\nLayer1: {3}\nLayer2: {4}\nDropout: {5}\n".format(model_name,batch_size,epochs,layer1,layer2,dropout)
    print(output_string)

    # Get target
    y = x.pop('target')

    # Split data
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state= 0)

    # Compile model
    model = build_model(len(x.columns.values),layer1,layer2,dropout)

    # Fit model
    early_stop = EarlyStopping(monitor='loss', mode='min', verbose=1, patience=50)
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
    loss_and_metrics = model.evaluate(x_test, y_test)
    print('Loss = ',loss_and_metrics[0])
    print('Accuracy = ',loss_and_metrics[1])

    # Save model
    model.save(model_name)

    # Store results
    str_list = []
    model.summary(print_fn=lambda x: str_list.append(x))
    output_string += '\n'.join(str_list)
    write_model_info(output_string)

def build_model(num_cols,layer1,layer2,dropout):
    model = keras.Sequential()
    model.add(keras.layers.InputLayer(input_shape=(num_cols,)))
    model.add(keras.layers.Dense(layer1, activation="relu"))
    model.add(keras.layers.Dense(layer2, activation="relu"))
    model.add(keras.layers.Dropout(dropout))
    model.add(keras.layers.Dense(1, activation="sigmoid"))

    model.compile(loss='binary_crossentropy',
            optimizer='adam',
            metrics=['accuracy'])

    return model

def write_model_info(output_string):
    with open('outputs.txt','a') as f:
        f.write(output_string + '\n\n')

def get_model_name():
    # Pick model name
    model_dir = 'saved/'
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    model_list = os.listdir(model_dir)
    model_id = 0
    while True:
        model_name = 'model' + str(model_id) + '.h5'
        if model_name in model_list:
            model_id += 1
        else:
            break

    return 'saved/' + model_name

def print_missing_percentages(table):
    missing = table.isnull().sum()/len(table)*100
    for col,val in missing.items():
        print(col,val)
    
def main():
    #season, tourney = load()
    #table = preprocess(season,tourney)
    table = pd.read_csv("../data/saved_states/93to19.csv")
    table = missing_vals(table)
    nn(table)

if __name__ == "__main__":
    main()
