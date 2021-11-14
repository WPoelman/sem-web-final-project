# sem_web_final_project
Final project for the course Semantic Webtechnology (LIX002M05), 2021-2022.

## Project description
This project enables the generation of Wikipedia infobox content in Dutch, based on English Wikipedia infoboxes. It consists of several subparts: the extraction of data, the creation of mappings and the final prediction process. All code used for the writing of _Final Project Report: Aligning Wikipedia Infoboxes_ is present: the results are fully reproducible.

## Usage
1. (Optionally) create a virtual environment (the system was created on python 3.7+)
2. Run `pip install -r requirements.txt`
   1. If you get a `curl` related error on Debian based systems, try installing the following:
    `sudo apt install libcurl4-openssl-dev libssl-dev`
3. To evaluate our test set with the provided mappings, run: `python generate.py -ts=data/test/test_titles.txt`

## Full process
To do the training data, mappings and evaluation from scratch. Run the following:
1. `python create_infobox_dict.py` to create a dataset of infoboxes
2. `python extract_mappings.py` to learn mappings from the created training dataset
3. `python generate_infoboxes.py -ts=data/test/test_titles.txt` to evaluate some infoboxes with the learned mappings

```
usage: create_infobox_dict.py [-h] [-t TITLES_FILE] [-w MAX_WORKERS]

optional arguments:
  -h, --help            show this help message and exit
  -t TITLES_FILE, --titles_file TITLES_FILE
                        Input txt file containing book titles on each line.
  -w MAX_WORKERS, --max_workers MAX_WORKERS
                        Max concurrent workers used to fetch the infoboxes.
```

```
usage: extract_mappings.py [-h] [-e EN_PATH] [-n NL_PATH] [-t THRESHOLD]
                           [-top_10]

optional arguments:
  -h, --help            show this help message and exit
  -e EN_PATH, --en_path EN_PATH
                        Path to cleaned English infoboxes train set
  -n NL_PATH, --nl_path NL_PATH
                        Path to cleaned Dutch infoboxes train set
  -t THRESHOLD, --threshold THRESHOLD
                        Levenshtein similarity ratio threshold for infobox
                        values, bigger or equal to the threshold counts as a
                        match)
  -top_10, --top_10     Print top 10 mappings
```

```
usage: generate_infoboxes.py [-h] [-t TITLE] [-ts TITLES] [-m MAPPER] 
                             [-w MAX_WORKERS] [-v] [-e]

optional arguments:
  -h, --help            show this help message and exit
  -t TITLE, --title TITLE
                        Title of the English wikipedia page (default: 'The
                        Very Hungry Caterpillar')
  -ts TITLES, --titles TITLES
                        List of titles to evaluate
  -m MAPPER, --mapper MAPPER
                        Path to a trained mapper object.
  -w MAX_WORKERS, --max_workers MAX_WORKERS
                        Max concurrent workers used to create the infoboxes.
  -v, --verbose         Show the output of the boxes as they are created
  -e, --expand          Next to newly generated infboxes, also try to expand
                        existing infoboxes
```