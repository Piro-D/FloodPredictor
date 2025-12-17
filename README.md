====================================================================================================
Project Initilization (Very Important)

1. Create a Virtual Environment
Create a new virtual enviroment in the project directory, run [python -m venv .venv] in the terminal
    
2. Virtual Environment Activation
Activate the new virtual enviroment by running [.\.venv\Scripts\Activate] in the terminal

3. Install Required Dependencies
Install all required python packages, by running [pip install -r requirements.txt] in the terminal

4. Install the Live Server Extension (If not already installed)
Install the live server extension in VScode if it isnt already installed.
Link : https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer

5. Train the AI Model
Train the model by running this command in the terminal [python -u .\src\Backend\train.py] 

Note:
Run each command inside the [], in order.
The third step may take a while


======================================================================================================

To test the front end
1. Run Api service.py
2. Go to index.html
3. Click the Go Live button on the bottom right

Note: The "Go Live" will only appear if you have already installed the Live Server Extension in VScode


======================================================================================================
Core Files & Modules

- flood_Pipeline.py is the main module for the flood prediction. You can call it by calling this function ["predict_flood_for_kelurahan(kelurahan)"]

- api_service deals with the connection between the front end and the back end

- bmkg_fetcher handles the communication between the program and the opensource BMKG API

- predict.py is used for testing by inserting manual values to the model

- preprocess.py is used to process inputs so it can be read by the model

- runPipeline,py is also used for testing, but this time we just need to insert the kelurahan name. (You can see various kelurahan name in AreaCodes.csv)

- train.py is the main file that builds the XGBoost model. It uses the flood_training_data_kelurahan_use.csv as training data

Note: You can see the accuracy of the model by running train.py
Note: To run these files just follow this format [python -u .\src\Backend\{filename}]


======================================================================================================
Pipeline of this program:

1. User selects a kelurahan
2. Kelurahan is translated to it's corresponding ADM4 code
3. The ADM4 code is then used to call the BMKG API to receive forecast data on that kelurahan
4. The forecast data is then fed to the model that has been trained on historical flood data
5. The model returns the flood probability of that kelurahan in various time stamps.


======================================================================================================
