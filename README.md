# facesScanner
Finds all pictures with your face in dataset

## How to use it?
0. Get a key to [Azure Cognitive services - Face API](https://azure.microsoft.com/en-us/services/cognitive-services/face/).
Assign it to `subscription_key` in file `facelist.py`
1. Analyze your dataset with `analyze.py`. Path to dataset is stored in `BASEDIR`.

**Important! Now it can store no more than 1,000 faces.**

2. Save your face to `input.jpg` and run `search.py`. All found pictures will be saved to a new folder
3. Use `delete.py` to erase analyzed dataset.
