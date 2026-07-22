# PERT and Monte Carlo Project Scheduling

Python implementation of the PERT method and Monte Carlo simulation for project scheduling, critical path analysis, deadline probability estimation, and uncertainty assessment.

This repository contains the source code developed as part of a Bachelor's Thesis in Aerospace Engineering. The project combines a deterministic PERT analysis with a Monte Carlo simulation to study the effect of activity-duration uncertainty on the total project duration and the critical path.

---

## Project overview

The project is divided into two main analyses:

### Deterministic PERT analysis

The deterministic program:

- Reads the activities and precedence relationships from an Excel file.
- Validates the consistency of the input data.
- Calculates the expected duration and variance of each activity.
- Constructs the Activity-on-Node network.
- Performs the forward and backward passes.
- Calculates early and late start and finish times.
- Determines the activity margins.
- Identifies the critical activities.
- Estimates the probability of meeting a target deadline.
- Generates a graphical representation of the network.

### Monte Carlo simulation

The Monte Carlo program extends the deterministic PERT analysis by considering activity durations as random variables.

For each simulation:

1. A possible duration is generated for every activity using a beta-PERT distribution.
2. The complete PERT network is solved again.
3. The total project duration is stored.
4. The critical activities and critical path are recorded.

After repeating this process a specified number of times, the program calculates statistical indicators such as:

- Mean project duration.
- Standard deviation.
- Minimum and maximum duration.
- Duration percentiles.
- Probability of meeting the target deadline.
- Criticality frequency of each activity.
- Frequency of occurrence of each critical path.

---

## Repository contents

```text
PERT-and-Monte-Carlo-Project-Scheduling/
│
├── PERT.py
├── MONTE-CARLO.py
├── Caso_Estudio.xlsx
└── README.md
```

### Files

- `PERT.py`: deterministic implementation of the PERT method.
- `MONTE-CARLO.py`: Monte Carlo simulation applied to the PERT network.
- `Caso_Estudio.xlsx`: input file containing the activities, precedence relationships and time estimates.
- `README.md`: instructions for installing and running the project.

---

## Requirements

The programs require Python 3 and the following Python libraries:

```bash
pip install pandas numpy matplotlib scipy tqdm openpyxl graphviz
```

The Graphviz application must also be installed on the computer because the Python `graphviz` package requires the Graphviz executable to generate the Activity-on-Node diagrams.

After installing Graphviz, verify the installation with:

```bash
dot -V
```

If the command is not recognised, Graphviz may need to be added to the system `PATH`.

---

## Input file

The file `Caso_Estudio.xlsx` must be located in the same directory as the Python scripts.

Each row of the Excel file represents one project activity.

The input table must contain the following columns:

| Column | Description |
|---|---|
| `ID` | Unique activity identifier |
| `Predecesoras` | Direct predecessor activities |
| `To` | Optimistic duration |
| `Tmp` | Most likely duration |
| `Tp` | Pessimistic duration |

Example:

| ID | Predecesoras | To | Tmp | Tp |
|---|---|---:|---:|---:|
| A | - | 1 | 2 | 3 |
| B | A | 3 | 4 | 5 |
| C | B | 3 | 5 | 7 |
| G | D,F | 2 | 3 | 4 |

### Predecessor format

- Activities without predecessors must contain an empty cell or a hyphen (`-`).
- When an activity has several predecessors, their identifiers must be separated by commas.
- Every predecessor identifier must correspond to an activity included in the table.
- Activity identifiers must not be duplicated.
- The temporal estimates must satisfy:

```text
To ≤ Tmp ≤ Tp
```

---

## PERT calculations

The expected duration of each activity is calculated as:

```text
te = (To + 4·Tmp + Tp) / 6
```

The activity variance is calculated as:

```text
Var = ((Tp - To) / 6)²
```

The program then performs:

1. Topological ordering of the activities.
2. Forward pass to calculate `ES` and `EF`.
3. Backward pass to calculate `LS` and `LF`.
4. Margin calculation.
5. Identification of critical activities.
6. Calculation of the total expected project duration.
7. Approximate deadline-compliance analysis.

---

## Running the deterministic PERT analysis

Open a terminal in the repository directory and run:

```bash
python PERT.py
```

On some systems, the command may be:

```bash
python3 PERT.py
```

The target project deadline is defined in the script using the variable:

```python
plazo_objetivo = 64
```

Modify this value before executing the program if a different deadline must be analysed.

### Deterministic results

The program provides:

- Expected duration of every activity.
- Activity variance.
- Predecessor and successor lists.
- Early start and early finish times.
- Late start and late finish times.
- Total margin.
- Expected project duration.
- Critical activities.
- Approximate project variance and standard deviation.
- Approximate probability of meeting the target deadline.
- Activity-on-Node network diagram.

---

## Running the Monte Carlo simulation

Open a terminal in the repository directory and run:

```bash
python MONTE-CARLO.py
```

On some systems, the command may be:

```bash
python3 MONTE-CARLO.py
```

Before running the program, define the target deadline and the number of simulations:

```python
plazo_objetivo = 64
N = 20000
```

Where:

- `plazo_objetivo` is the deadline to be analysed.
- `N` is the total number of Monte Carlo simulations.

A larger value of `N` generally produces more stable statistical results, although it also increases the execution time.

---

## Beta-PERT duration generation

In the Monte Carlo simulation, the duration of each activity is generated using a beta-PERT distribution defined by:

- Optimistic duration: `To`
- Most likely duration: `Tmp`
- Pessimistic duration: `Tp`

The implementation uses the parameter:

```python
lambda = 4
```

The generated duration always remains between the optimistic and pessimistic estimates, with greater probability assigned to values close to the most likely duration.

For activities where:

```text
To = Tmp = Tp
```

the duration is considered deterministic and remains constant in every simulation.

---

## Monte Carlo procedure

For each simulation `k = 1, 2, ..., N`, the program performs the following operations:

```text
Generate one duration for every activity
                    ↓
Solve the complete PERT network
                    ↓
Calculate the total project duration
                    ↓
Identify the critical activities
                    ↓
Store the results
```

The structure of the precedence network remains constant throughout the simulation. Only the activity durations change between scenarios.

---

## Monte Carlo results

After completing all simulations, the program calculates:

- Mean simulated project duration.
- Standard deviation.
- Minimum and maximum duration.
- Percentiles `P5`, `P50`, `P80`, `P90` and `P95`.
- Empirical probability of meeting the target deadline.
- Number and percentage of simulations in which each activity is critical.
- Number and percentage of appearances of each critical path.
- Simulated distribution of the total project duration.

The empirical probability of meeting the deadline is obtained as:

```text
Number of simulations completed before the deadline
---------------------------------------------------
            Total number of simulations
```

The criticality frequency of an activity represents the percentage of simulations in which that activity belongs to a critical path.

---

## Output files

The Monte Carlo results are exported to:

```text
Resultados_PERT_MonteCarlo.xlsx
```

The output workbook contains:

- `PERT_Clasico`: deterministic PERT planning.
- `MonteCarlo`: total durations obtained in the simulations.
- `Criticidad`: criticality frequency of the activities.

The program also generates:

- A graphical representation of the simulated duration distribution.
- An Activity-on-Node diagram of the deterministic reference network.

---

## Interpretation of the results

The deterministic PERT analysis provides a reference planning based on expected activity durations.

However, when activity durations are uncertain:

- The mean simulated project duration may differ from the deterministic duration.
- The critical path may change between scenarios.
- Activities that are not critical in the deterministic analysis may become critical in some simulations.
- The classical deadline probability may differ from the empirical Monte Carlo probability.

Therefore, the Monte Carlo simulation does not replace PERT. It extends the deterministic analysis by quantifying:

- Duration uncertainty.
- Deadline-compliance risk.
- Dispersion of possible results.
- Variability of the critical path.
- Criticality frequency of individual activities.

---

## Recommended workflow

1. Download or clone the repository.
2. Install the required Python libraries.
3. Install Graphviz.
4. Complete the `Caso_Estudio.xlsx` input file.
5. Check that activity identifiers and predecessors are correct.
6. Set the target deadline in the scripts.
7. Set the number of Monte Carlo simulations.
8. Run the deterministic PERT analysis.
9. Run the Monte Carlo simulation.
10. Review the numerical, graphical and Excel results.

Commands:

```bash
python PERT.py
python MONTE-CARLO.py
```

---

## Limitations

The results depend on the quality of the optimistic, most likely and pessimistic duration estimates.

The current implementation also assumes that:

- Activity durations are independent.
- The precedence network remains fixed.
- The beta-PERT distribution adequately represents activity durations.
- Resource availability does not restrict the schedule.
- Costs and working calendars are not included.

Possible future improvements include:

- Correlated activity durations.
- Probability distributions fitted to historical data.
- Resource constraints.
- Cost uncertainty.
- Working calendars.
- Automatic convergence and stopping criteria.

---

## Author

**Luis Rodríguez-Caso López**  
Aerospace Engineering student  
University of Seville
