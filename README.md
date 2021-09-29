# Secure Image Retrieval and Sharing in Social Media Applications

### What is this repository for? ###
This is Academic research project for the course Advance Database Systems(CS8712). We have implemented the research paper(https://ieeexplore.ieee.org/document/9064563).

#### Quick summary
In this work, we implement a proposed work on social media image sharing, searching, and retrieval by ensuring the privacy of the images. We ensure the image privacy by encrypting images in the user end. We encrypt the image with a symmetric secret key before uploading the image to any hosting server. To alleviate key management overhead and to avoid the one-one key sharing we use secret key sharing where only users owning similar images can search and decrypt images independently. We generate image profile vectors to implement an equality search to enable the image search for users. We extract visual features from images and then apply Locality Sensitive Hashing (LSH) to create image profile vectors.  Moreover, the novelty in our work is, we successfully implement the image indexing and profile vector generation in a single iteration of LSH, whereas authors in used a redundant iteration. The benefit of our improvement is two-fold
1. We avoid running a redundant iteration of LHS that consequently help us saving processing cost.
2. Our new implementation of image indexing is free of any insertion loop effect that was present in the prior work’s cuckoo hashing indexing method.


*Status - Completed*


### How do I get set up? ###

* Summary of set up
* Configuration

## Summary of set up 

We need Node in order to run our front-end.

You can install the latest one for your platform from here - https://nodejs.org/en/download/

After installing node, before running the project, we will install all the necessary dependencies

```bash 
cd client
npm install
```
After the dependencies installation is done, we can start our front-end application with the below command
```bash
npm run start
```
This will start the development server on port `3000`. You can verify by visiting the url http://localhost:3000 in your browser.

You should be able to see the "Similar Image Search" page.

If you try uploading an image and retrieve similar images for it, it will not work as we have only started the frontend. You can verify this by opening the network panel and see that upload requests are failing.

As we are not running any server that listens to the frontend requests, this is expected.

Now that we have run our front-end, we will setup a webserver which listens to our frontend requests, handles them, pocesses them and returns necessary response.

As the backend is in completely python, we will install some required packages.

But before installation, to avoid version conflict with already existing libraries in your system, we will create a virtual-environment to install packages

```bash
python3 -m venv myenv
source myenv/bin/activate
```
Now that we have created virtual environment, we will install all the required packages.

Note: All these packages will be installed in your virtual-environment. So, make sure you activate the virtual-environment every time you are working on this project by running this command from root folder.
```bash
source myenv/bin/activate
```

Make sure you are in root folder where the requirements.txt file is there and run
```
pip install -r requirements.txt
```
This will install all the necessary packages. Below are the list of packages we are using and why we are using.

- Flask - Web-server and handling front-end requests
- flask-cors - For Avoiding CORS issue. Learn more about why this is required https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
- OpenCV - For Feature Extraction
- Nearpy - Getting Nearest Neighbours
- Scipy - For performing LSH on feature vectors
- Redis - Storage
- Pycryptodome - Python package of low-level cryptographic primitives.
- binascii — Convert between binary and ASCII

Now that we have installed the packages. we will run the web-server, so that we can handle the requests that are coming from front-end
```
cd web-server
python app.py
```

This will start the web-server. You can verify this by visiting http://localhost:5000/status. You should see the text "Service is up and running!"

Now, if you try uploading the image from front-end, even though the image is uploaded succesfully, the image that we see in frontend is broken. That is because, the image which has been uploaded and saved in the folder called 'cloud-server/images' in root folder is not accessible to the front-end. In order to do that we will have to start a static web-server which hosts these images.

Note: Make sure you are in root folder.
```bash
npm i -g serve
serve cloud-server/images -p 5001
```
Now if you visit http://localhost:5001, you can see all the images that you have uploaded.

Now, try uploading the image again, you will be able to see the image that you have uploaded.

Note:Make sure redis is installed and running.

## Configuration
There are some attributes defined in `Setup.py` file
```
self.evaluate = False
self.do_indexing = False
#NOTE: do not make the sharing_threshold grater than 20
self.sharing_threshold = 20     # threshold value for secret sharing, m
self.num_pieces = 120           # pieces number must be equal
                                # to no of extracted features number, n
# self.num_features = 10        # pieces number must be equal
self.num_features = 120         # pieces number must be equal
                                # to no of extracted features number, n
self.num_hashtable = 120
self.num_tables = 32
self.descriptor_hash_size = 8
self.inp_dimensions = 32        # this is the column count of each feature descriptors
self.engine_dimension = 32      # this is the dimension required to instantiate an Nearpy engine
self.lhash_name = 'test-image-retrieval'
```

If you want to view the evaluation report, you can set the `self.evaluate` to `True` before running the project.
