This folder is for storing the downloaded datasets locally.
Actual datasets are downloaded via Hugging Faces's `datasets.load_dataset` api. 
Storing the dataset locally will ensure the following:
- Only downloading and cleansing the dataset once
- Having it stored locally for quicker start times