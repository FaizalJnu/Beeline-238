import os
import pandas as pd
from pathlib import Path
import numpy as np

def generateInputs(RunnerObj):
    '''
    Function to generate desired inputs for NGSEM.
    If the folder/files under RunnerObj.datadir exist, 
    this function will not do anything.
    '''
    if not RunnerObj.inputDir.joinpath("NGSEM").exists():
        print("Input folder for NGSEM does not exist, creating input folder...")
        RunnerObj.inputDir.joinpath("NGSEM").mkdir(exist_ok = False)
        
    if not RunnerObj.inputDir.joinpath("NGSEM/ExpressionData.csv").exists():
        ExpressionData = pd.read_csv(RunnerObj.inputDir.joinpath(RunnerObj.exprData),
                                     header = 0, index_col = 0)
        
        newExpressionData = ExpressionData.copy()
        
        # Write .csv file
        newExpressionData.to_csv(RunnerObj.inputDir.joinpath("NGSEM/ExpressionData.csv"),
                             sep = ',', header  = True, index = True)
    
def run(RunnerObj):
    '''
    Function to run NGSEM algorithm
    '''
    inputPath = "data" + str(RunnerObj.inputDir).split(str(Path.cwd()))[1] + \
                    "/NGSEM/ExpressionData.csv"
    
    nk = RunnerObj.params["nk"]
    miter = RunnerObj.params["miter"]
    error = RunnerObj.params["error"]
    cores = RunnerObj.params["cores"]

    # make output dirs if they do not exist:
    outDir = "outputs/"+str(RunnerObj.inputDir).split("inputs/")[1]+"/NGSEM/"
    os.makedirs(outDir, exist_ok = True)
    
    outPath = "data/" +  str(outDir) + 'outFile.txt'
    cmdToRun = ' '.join([
        f'docker run --rm -v {Path.cwd()}:/ng-sem/data/ ngsem:base /bin/sh -c',
        f'"time -v -o data/{outDir}time.txt Rscript runNGSEM.R {inputPath} {outPath} {nk} {miter} {error} {cores}"'
    ])

    print(cmdToRun)
    os.system(cmdToRun)



def parseOutput(RunnerObj):
    '''
    Function to parse outputs from NGSEM.
    '''
    # Quit if output directory does not exist
    outDir = "outputs/"+str(RunnerObj.inputDir).split("inputs" + os.sep)[1]+"/NGSEM/"
    if not Path(outDir+'outFile.txt').exists():
        print(outDir+'outFile.txt'+'does not exist, skipping...')
        return
        
    # Read output
    OutDF = pd.read_csv(outDir+'outFile.txt', sep = '\t', header = 0)
    # edges with significant p-value
    #part1 = OutDF.loc[OutDF['pValue'] <= float(RunnerObj.params['pVal'])]
    #part1 = part1.assign(absCorVal = part1['corVal'].abs())
    # edges without significant p-value
    #part2 = OutDF.loc[OutDF['pValue'] > float(RunnerObj.params['pVal'])]
    
    outFile = open(outDir + 'rankedEdges.csv','w')
    outFile.write('Gene1'+'\t'+'Gene2'+'\t'+'EdgeWeight'+'\n')

    for idx, row in OutDF.sort_values('weight', ascending = False).iterrows():
        outFile.write('\t'.join([row['Gene1'],row['Gene2'],str(row['weight'])])+'\n')
    
    # for idx, row in part2.iterrows():
    #     outFile.write('\t'.join([row['Gene1'],row['Gene2'],str(0)])+'\n')
    outFile.close()
    
