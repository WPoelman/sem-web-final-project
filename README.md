# sem_web_final_project
Final project for the course Semantic Webtechnology (LIX002M05), 2021-2022.

## Project description
This project enables the generation of Wikipedia infobox content in Dutch, based on English Wikipedia infoboxes. It consists of several subparts: the extraction of data, the creation of mappings and the final prediction process. All code used for the writing of _Final Project Report: Aligning Wikipedia Infoboxes_ is present: the results are fully reproducible.

## Usage
1. Run `pip install -r requirements.txt`
   1. If you get a `curl` related error on Debian based systems, try installing the following:
    `sudo apt install libcurl4-openssl-dev libssl-dev`
2. Run the script you want, all runnable scripts can show a `usage` message by using the `--help` flag. 
3. The 'correct' order to do all steps is the following:
   1. `python create_infobox_dict.py` to create a dataset of infoboxes
   2. `python extract_mappings.py` to learn mappings from the created training dataset
   3. `python demo.py -ts=data/test/test_titles.txt` to create some infoboxes with the learned mappings
