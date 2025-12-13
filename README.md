How to initialize this project
1. create a new virtual enviroment, run [python -m venv .venv]
    
2. activate the new virtual enviroment, run [.\.venv\Scripts\Activate]

3. Install required dependencies [pip install -r requirements.txt]

4. train the model by inserting this into the terminal [python -u .\src\Backend\train.py] 


Explanation of each folder
- flood_Pipeline.py is the main pipeline for the flood prediction. You can call it by calling this in a python file ["predict_flood_for_kelurahan(kelurahan)"]
- api_service deals with the connection between the front end and the back end
- bmkg_fetcher handles the communication between the program and the opensource BMKG API
- predict.py is used for testing by inserting manual values to the model
- preprocess.py is used to process inputs so it can be read by the model
- runPipeline,py is also used for testing, but this time we just need to insert the kelurahan name. (You can see various kelurahan name in AreaCodes.csv)
- train.py is the main file that creates the model. It uses the flood_training_data_kelurahan_use.csv as training data

Note: You can see the accuracy of the model by running train.py


Pipeline of this program:
1. User selects a kelurahan
2. Kelurahan is translated to it's corresponding ADM4 code
3. The ADM4 code is then used to call the BMKG API to receive forecast data on that kelurahan
4. The forecast data is then fed to the model that has been trained on historical flood data
5. The model returns the flood probability of that kelurahan in various time stamps.


To test the front end
1. Run Api service.py
2. Go to index.html
3. Click the Go Live button on the bottom right
