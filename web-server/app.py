# app.py
from flask import Flask, request
from flask import jsonify          # import flask
from flask_cors import CORS

from services.ImageUpload import *
from services.ImageSearchAndRetrieve import *
from EvaluationPlot import *
from AccuracyLogging import *
from Setup import *
import time


setup_params = Setup()
CLOUD_SERVER_URL = 'http://localhost:5001/'

UPLOAD_FOLDER = '../cloud-server/images'
ENCRYPTED_FOLDER = '../cloud-server/encrypted'
DECRYPTED_FOLDER = '../cloud-server/decrypted'

import os

app = Flask(__name__)             # create an app instance
cors = CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ENCRYPTED_FOLDER'] = ENCRYPTED_FOLDER
app.config['DECRYPTED_FOLDER'] = DECRYPTED_FOLDER

@app.route("/status")
def get_status():
  return 'Service is up and running!'

@app.route("/fetch-similar-images") # at the end point /
def fetch_similar_images():                      # call method hello
    # This is just mock response. This route should return similar images
    return jsonify([
    {
      'address':
        "https://post.healthline.com/wp-content/uploads/2020/09/benefits-of-pineapple-1200x628-facebook-1200x628.jpg"
    },
    {
      'address':
        "https://post.healthline.com/wp-content/uploads/2020/09/benefits-of-pineapple-1200x628-facebook-1200x628.jpg"
    },
    {
      'address':
        "https://post.healthline.com/wp-content/uploads/2020/09/benefits-of-pineapple-1200x628-facebook-1200x628.jpg"
    }
  ])

@app.route("/similar", methods=['POST'])
def get_similar_images():
  if request.method == 'POST':
    if 'image' not in request.files:
      return "There's no 'image' in the the formdata."
    image = request.files['image']
    path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
    image.save(path)

    ####### Codes belong to service
    search = ImageSearchAndRetrieve()

    # return time in second
    start_time = time.time()

    res, item_found, computation_time  = search.do_process(path, image.filename, app.config['DECRYPTED_FOLDER'])

    end_time = time.time()
    total_processing_time = end_time - start_time
    print("total_processing_time for Image Search: ", total_processing_time, " sec")

    similar_images = []
    for index in range(len(res)):
        record = dict()
        record['address'] = CLOUD_SERVER_URL + "decrypted/" + res[index]
        similar_images.append(record)


    if setup_params.evaluate:
      print("\n+++++++++++++ Evaluation +++++++++++")
      print("++++++++++++++++++++++++++++++++++++")
      # uncomment below code to run evaluation
      print("computation_time ", computation_time)
      if setup_params.generate_evaluation_plot:
        plotting = EvaluationPlot()
        plotting.draw_image_search_timing(computation_time, total_processing_time)
      ########

      # keep log of accuracy
      total_search_count = int(AccuracyLogging.read_value_by_key("TOTAL_SEARCH_COUNT"))
      success_count = int(AccuracyLogging.read_value_by_key("SUCCESS_COUNT"))
      AccuracyLogging.write_value_by_key("TOTAL_SEARCH_COUNT", total_search_count + 1)

      if item_found:
          AccuracyLogging.write_value_by_key("SUCCESS_COUNT", success_count + 1)

      print("Total searches: ", total_search_count)
      print("Total success: ", success_count)
      print("Accuracy :", (success_count / total_search_count) * 100, " %")
      print("LSH (k, L) : ", setup_params.inp_dimensions, setup_params.num_hashtable)

    return jsonify({
      'status': 200,
      'similar_images': similar_images,
      'query_image_address': CLOUD_SERVER_URL + "images/" + image.filename,
    })

@app.route("/upload", methods=['POST'])
def upload_image():
  if request.method == 'POST':
    if 'image' not in request.files:
      return "There's no 'image' in the the formdata."
    image = request.files['image']
    path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
    image.save(path)

    ####### Codes belong to service
    upload = ImageUpload()

    # return time in second
    start_time = time.time()

    computation_time = upload.do_process(path, image.filename, app.config['ENCRYPTED_FOLDER'])
    end_time = time.time()

    total_processing_time = end_time - start_time
    print("total_processing_time for Image Upload: ", total_processing_time, " sec")

    if setup_params.evaluate:
      print("\n+++++++++++++ Evaluation +++++++++++")
      print("++++++++++++++++++++++++++++++++++++")
      print("computation_time ", computation_time)
      # uncomment three lines below to run evaluation

      if setup_params.generate_evaluation_plot:
        plotting = EvaluationPlot()
        plotting.draw_image_upload_timing(computation_time, total_processing_time)
        plotting.draw_image_upload_total_cost(None, None)

      # run search evalaution
      # search = ImageSearchAndRetrieve()
      # res, item_found, computation_time  = search.do_process(path, image.filename, app.config['DECRYPTED_FOLDER'])
      # # keep log of accuracy
      # total_search_count = int(AccuracyLogging.read_value_by_key("TOTAL_SEARCH_COUNT"))
      # success_count = int(AccuracyLogging.read_value_by_key("SUCCESS_COUNT"))
      #
      # AccuracyLogging.write_value_by_key("TOTAL_SEARCH_COUNT", total_search_count + 1)
      # if item_found:
      #     AccuracyLogging.write_value_by_key("SUCCESS_COUNT", success_count + 1)
      #
      # print("Total searches: ", total_search_count)
      # print("Total success: ", success_count)
      # print("Accuracy :", (success_count/total_search_count) * 100, " %" )
      # print("LSH (k, L) : ", setup_params.inp_dimensions, setup_params.num_hashtable)

    return jsonify({
      'status': 200,
      'image_address': CLOUD_SERVER_URL + image.filename
    })

if __name__ == "__main__":        # on running python app.py
    app.run()                     # run the flask app