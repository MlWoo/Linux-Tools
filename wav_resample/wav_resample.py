import librosa
import glob
import os
from tqdm import tqdm

orig_sr = 22050
tar_sr = 16000

file_path = '' # file path contain .wav files   example: "/data/dataset/LJSpeech-1.1/wavs"
out_file_path= '' 

if not os.path.exists(out_file_path):
    os.makedirs(out_file_path)

def get_files(path, extension='.wav'):
    filenames = []
    for filename in glob.iglob(f'{path}/**/*{extension}', recursive=True):
        filenames += [filename]
    return filenames

def path_transfer(filename, out_file_path):
    _,tail = os.path.split(filename)
    out_filename = os.path.join(out_file_path, tail)
    return out_filename

def wav_generate(filename, out_filename, orig_sr=orig_sr, tar_sr=tar_sr):
    y, sr = librosa.load(filename, sr=orig_sr)
    y = librosa.resample(y, orig_sr, tar_sr)
    librosa.output.write_wav(out_filename, y, tar_sr)
    
filenames = get_files(file_path)

for filename in tqdm(filenames):
    out_filename = path_transfer(filename, out_file_path)
    wav_generate(filename, out_filename)
