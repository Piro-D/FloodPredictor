How to initialize this project
1. create a new virtual enviroment, run [python -m venv .venv]
    
2. activate the new virtual enviroment, run [.\.venv\Scripts\Activate]

3. Install required dependencies [pip install -r requirements.txt]

4. train the model by inserting this into the terminal [python -u "c:\Users\Jason\Desktop\floodPredictor_M\src\Backend\train.py"] 

flood_pipeline is the primary file used to predict
you can call it like this ["predict_flood_for_kelurahan(kelurahan)"]

predict.py is used to test with manually inputed values

To test with values given from an API, use runPipeline.py

preprocess.py is used to handle the values so it can be read by other files

The rest are util files with functions realted to the BMKG API

