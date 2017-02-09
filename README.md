# KnowEnG's Clustering Evaluation Pipeline
This is the Knowledge Engine for Genomics (KnowEnG), an NIH BD2K Center of Excellence, Clustering Evaluation Pipeline.

This pipeline **evaluates** the clustering result of KnowEnG's Samples Clustering Pipeline.

There are two evaluation methods:

| **Method**                                      | **Trait Type**                          |
| ------------------------------------------------ | ------------------------------------- |
| one-way ANOVA(f_oneway)                               | Continuous                                | 
| one-way chi square test(chisquare)                                     | Categorical          |


* * * 
## How to run this pipeline with Our data
* * * 
###1. Clone the Clustering_Evaluation Repo
```
 git clone https://github.com/KnowEnG-Research/Clustering_Evaluation.git
```
 
###2. Install the following (Ubuntu or Linux)
  ```
 apt-get install -y python3-pip
 apt-get install -y libblas-dev liblapack-dev libatlas-base-dev gfortran
 pip3 install numpy==1.11.1
 pip3 install pandas==0.18.1
 pip3 install scipy==0.18.0
 pip3 install scikit-learn==0.17.1
 apt-get install -y libfreetype6-dev libxft-dev
 pip3 install matplotlib==1.4.2
 pip3 install pyyaml
 pip3 install knpackage
```

###3. Change directory to Clustering_Evaluation

```
cd Clustering_Evaluation
```

###4. Change directory to test

```
cd test
```
 
###5. Create a local directory "run_dir" and place all the run files in it
```
make env_setup
```

###6. Select and run a gene set characterization option:
 
 * Run clustering evaluation</br>
  ```
  make run_cluster_eval
  ```


* * * 
## How to run this pipeline with Your data
* * * 

__***Follow steps 1-3 above then do the following:***__

### * Create your run directory

 ```
 mkdir run_directory
 ```

### * Change directory to the run_directory

 ```
 cd run_directory
 ```

### * Create your results directory

 ```
 mkdir results_directory
 ```
 
### * Create run_paramters file (YAML Format)
 ``` 
 Look for examples of run_parameters in the Clustering_Evaluation/data/run_files template_run_parameters.yml
 ```

### * Run the Clustering Evaluation Pipeline:

  * Update PYTHONPATH enviroment variable
   ``` 
   export PYTHONPATH='./src':$PYTHONPATH    
   ```
   
  * Run
   ```
  python3 ../src/clustering_eval.py -run_directory ./ -run_file BENCHMARK_1_cluster_eval.yml
   ```

* * * 
## Description of "run_parameters" file
* * * 

| **Key**                   | **Value** | **Comments** |
| ------------------------- | --------- | ------------ |
| phenotype_data_full_path | directory+phenotype_data_name| Path and file name of user supplied phenotype data |
| results_directory | directory | Directory to save the output files |
| threshold | 10 | Maximum number of traits for categorical phenotype |

phenotype_data_name = phenotype_data.tsv

* * * 
## Description of Output files saved in results directory
* * * 

* The clustering evaluation output file has the name **clustering_evaluation_result_{timestamp}.tsv**.</br>

 |  |**Trait_length_after_dropna**|**measure**|**chi/fval**|**pval**|
 | :--------------------: |:--------------------:|:--------------------:|:--------------------:|:--------------------:|
 | **sample 1**|int(more than threshold)|f_oneway|float|float|
 |...|...|...|...|...|
 | **sample m**| int(less than threshold)|chisquare|float|float|
