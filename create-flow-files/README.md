# Create Average Flow Files

This program is used to create flow files from the converted simulation results files (.vtp or .vtu) created by the **svpost** program or using the SimVascular **SV Simulation** plugin **Convert Results** options. It reproduces the code SimVascular uses to create the flow files when the **Calculate Flows** option is enabled.

The program creates the following files:

    all_results-pressures.txt - Pressure for each face with time steps
    all_results-flows.txt - Flowrate for each face with time steps
    all_results-averages.txt - The average, maximum, minimum values of presure, flowrate for each face
    all_results-averages-from_cm-to-mmHg-L_per_min.txt - Same info as in all_results-averages.txt, but pressure is in mmHg, flowrate is L/min.
    
## Buildin the Program ##
The program is built using CMake:

    cd build
    cmake ..
    make

This creates an executable named **create-flow-files**.

## Program Options ##

The program takes the following options:

    --mesh-directory: The directory where the mesh surface files (.vtp) are located.,
    --output-directory: The directory to write the average flow files to.
    --results-directory: The directory of the converted simulation results.
    --single-file: Simulation results have been converted to a single .vtu file. (yes/no) 
    --skip-walls: Skip calculating averages for walls. (yes/no) 
    --units: Units (cm, mm)


## Example ##

create-flow-files --mesh-directory $HOME/SimVascular/CylinderProject/Simulations/steady/mesh-complete/mesh-surfaces  --output-directory $HOME/software/ktbolt/cardiovascular/create-flow-files/test  --results-directory  $HOME/SimVascular/CylinderProject/Simulations/steady/4-procs_case/steady-converted-results  --single-file no --skip-walls yes  --units cm