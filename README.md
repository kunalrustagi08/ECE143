This is a public clone on my ECE 143 project. I would like to thank [Justin](https://github.com/jvolheim), [Deevanshu](https://github.com/DeevanshuGoyal), [Viraj](https://github.com/viraj-shah18) and [Udit](https://github.com/uiyengar322) for working on this project.


# Performance analysis of the competing 12 teams in the ICC T20 WC 2022

## File Structure<a name='file'></a>
```
ECE-143
├─ README.md                   -- Readme
├─ DataProcessing              -- code for processing 3200+ files to single database
├─ DataVisualization           -- code for plotting graphs
├─ Raw Data                    -- Data folder with over 3200 csv files
├─ ECE_143_ppt.pdf             -- Pdf of the group presentation
├─ requirements.txt            -- required libaries for plotting data
```


## Requirements<a name='require'></a>
To install all the required modules, run the following command
```
pip install -r requirements.txt
```


## Running code
Data Processing code needs to be run from the root folder as 
```
python ./DataProcessing/pre_process_data.py #(For Mac and Linux)
python .\DataProcessing\pre_process_data.py #(For windows)
```

For visualization, plots are created using different .py files in DataVisualization folder. All the plots are saved in plots folder of DataVisualization folder and also added to jupyter notebook. 
