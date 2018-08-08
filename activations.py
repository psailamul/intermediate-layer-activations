from keras.applications.resnet50 import ResNet50
from keras.models import Model
from keras.preprocessing.image import img_to_array, load_img
import os
from tqdm import tqdm
from keras import backend as K
import pickle
from keras.preprocessing.image import ImageDataGenerator
import shutil

def resnet(op_from_layers=[79]):
    model = ResNet50(include_top=True, weights='imagenet', input_tensor=None, input_shape=None)
    output_layers = [model.layers[i].output for i in op_from_layers]
    model_req = Model(input=model.input, output=output_layers)
    return model_req

def prediction_with_flow(model,main_dir, batch_size, h, w):
    pred={}
    test_datagen = ImageDataGenerator()
    for i in tqdm(os.listdir(main_dir)):
        cwd = os.path.join(main_dir,i)
        if(os.path.isdir(cwd)):
            generator = test_datagen.flow_from_directory(
                    os.path.join(main_dir,i),
                    target_size = (h, w),
                    batch_size = batch_size)
            number_of_images = len(generator.filenames)
            probabilities = model.predict_generator(generator,steps=(number_of_images/batch_size)+1)
            pred.update({i.split("_")[0]:probabilities})
    return pred

def dump_pickle(reults):
    with open("results.p", 'wb') as pfile:
        pickle.dump(results, pfile, protocol=pickle.HIGHEST_PROTOCOL)
        
def put_dir_into_dir(directory):
    fnames = os.listdir(directory)
    for i in fnames:
        os.makedirs(os.path.join(directory,i+'_'))
        shutil.move(os.path.join(directory,i),os.path.join(directory,i+'_'))

def main():
    import argparse
    parser = argparse.ArgumentParser(description="  python blah blah  ")
    parser.add_argument('--dir',
                            type=str,
                            help="""full path to directory where the video is stored""")

    parser.add_argument('--batch_size',
                            type=int,
                            help="""batch_size of data""")
    parser.add_argument('--input_height',
                            type=int,
                            help="""height of input to the model""")

    parser.add_argument('--input_width',
                            type=int,
                            help="""width of input to the model""")
    parser.add_argument('--output_layers', nargs='+', type=int)


    args=parser.parse_args()

    directory = args.dir
    batch_size = args.batch_size
    height = args.input_height
    width = args.input_width
    output_from_layers = args.output_layers
    model = resnet(output_from_layers)
    put_dir_into_dir(directory)
    results = prediction_with_flow(model, directory, batch_size, height, width)
    dump_pickle(results)

if __name__=="__main__":
    main()
