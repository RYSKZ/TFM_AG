import keras
import librosa
import os
import cv2
import numpy as np
from keras.models import model_from_json
from keras.preprocessing import image
from config import EXAMPLES_PATH
from config import MODEL_DIR_PATH

class audioPredictions:

    def __init__(self, file):

        self.file = file
        self.path = MODEL_DIR_PATH + 'audioModel.h5'
        self.loaded_model = keras.models.load_model(self.path)

    def make_predictions(self):

        data, sampling_rate = librosa.load(self.file)
        mfccs = np.mean(librosa.feature.mfcc(y=data, sr=sampling_rate, n_mfcc=40).T, axis=0)
        x = np.expand_dims(mfccs, axis=1)
        x = np.expand_dims(x, axis=0)
        predictions = self.loaded_model.predict_classes(x)
        #print("Audio emotion prediction is", " ", self.convert_class_to_emotion(predictions))
        return self.convert_class_to_emotion(predictions)

    @staticmethod
    def convert_class_to_emotion(pred):

        label_conversion = {'0': 'neutral',
                            '1': 'neutral',
                            '2': 'happy',
                            '3': 'sad',
                            '4': 'angry',
                            '5': 'fear',
                            '6': 'disgust',
                            '7': 'surprise'}

        for key, value in label_conversion.items():
            if int(key) == pred:
                label = value
        return label

if __name__ == '__main__':
    # load model
    model = model_from_json(open("vidModel.json", "r").read())
    # load weights
    model.load_weights('vidModelWeights.h5')
    face_haar_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    cap = cv2.VideoCapture("test.avi")
    chunks = os.listdir("./audioChunks/")
    i=0
    for chunk in chunks:
      live_prediction = audioPredictions(file="./audioChunks/" + chunk)

      ret, test_img = cap.read()  # captures frame and returns boolean value and captured image
      if not ret:
          continue
      gray_img = cv2.cvtColor(test_img, cv2.COLOR_BGR2GRAY)

      faces_detected = face_haar_cascade.detectMultiScale(gray_img, 1.32, 5)
      visual_prediction = ""
      for (x, y, w, h) in faces_detected:
        cv2.rectangle(test_img, (x, y), (x + w, y + h), (255, 0, 0), thickness=7)
        roi_gray = gray_img[y:y + w, x:x + h]  # cropping region of interest i.e. face area from  image
        roi_gray = cv2.resize(roi_gray, (48, 48))
        img_pixels = image.img_to_array(roi_gray)
        img_pixels = np.expand_dims(img_pixels, axis=0)
        img_pixels /= 255

        predictions = model.predict(img_pixels)

        # find max indexed array
        max_index = np.argmax(predictions[0])

        emotions = ('angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral')
        visual_prediction = emotions[max_index]
      audio_prediction = live_prediction.make_predictions()
      print("Visual emotion prediction at second " + str(i) +" is :" + visual_prediction)
      print("Visual emotion prediction at second " + str(i) +" is :" + audio_prediction)
      if visual_prediction ==  audio_prediction:
        print("Multimodal emotion prediction at second " + str(i) +" is :" + audio_prediction)
      else:
        print("The singles modalities predictions do not match")
      #cv2.putText(test_img, predicted_emotion, (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
      i=i+1
      #resized_img = cv2.resize(test_img, (1000, 700))
      #cv2.imshow('Emotion analysis ',resized_img)


    #if cv2.waitKey(10) == ord('q'):#wait until 'q' key is pressed
    #break

    cap.release()
    cv2.destroyAllWindows
