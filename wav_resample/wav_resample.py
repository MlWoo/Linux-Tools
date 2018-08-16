import librosa
import glob
import os


orig_sr = 22050
tar_sr = 16000



def get_files(path, extension='.wav'):
    filenames = []
    for filename in glob.iglob(f'{path}/**/*{extension}', recursive=True):
        filenames += [filename]
    return filenames


file_path = "/home/lynn/dataset/LJSpeech-1.1/wavs/LJ001-0001.wav"
out_file_path= "/home/lynn/J001-0001.wav"

y, sr = librosa.load(file_path, sr=orig_sr)
y_16k = librosa.resample(y, orig_sr, tar_sr)

librosa.output.write_wav(out_file_path, y_16k, tar_sr)

