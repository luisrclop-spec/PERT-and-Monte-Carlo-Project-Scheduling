<div align="center">

# PERT and Monte Carlo Project Scheduling

### Project scheduling, critical-path analysis and temporal-risk assessment with Python

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Project](https://img.shields.io/badge/Project-Bachelor's%20Thesis-6f42c1)
![Degree](https://img.shields.io/badge/Degree-Aerospace%20Engineering-0A66C2)
![University](https://img.shields.io/badge/University-University%20of%20Seville-d71920)
![Methods](https://img.shields.io/badge/Methods-PERT%20%7C%20Monte%20Carlo-2E8B57)

</div>

---

## About the project

This repository contains the source code developed as part of a **Bachelor's Thesis in Aerospace Engineering** at the **University of Seville**.

The project develops a computational procedure for the temporal analysis of project networks by combining two complementary approaches:

1. A deterministic implementation of the **PERT method**.
2. A **Monte Carlo simulation** that incorporates uncertainty into activity durations.

The deterministic PERT analysis provides the reference project schedule, including:

- Expected activity durations.
- Early and late start and finish times.
- Activity margins.
- Expected project duration.
- Critical activities and critical paths.
- Approximate deadline-compliance probability.

The Monte Carlo simulation extends this analysis by repeatedly generating possible activity durations and solving the complete project network for each scenario.

This makes it possible to analyse:

- The distribution of the total project duration.
- The probability of meeting a target deadline.
- Duration percentiles.
- The variability of the critical path.
- The criticality frequency of each activity.

> **The deterministic PERT analysis provides the temporal structure of the project, while Monte Carlo simulation quantifies uncertainty and temporal risk.**

---

## Main contributions

The developed implementation allows the user to:

- Import project data from an Excel file.
- Validate activity identifiers and precedence relationships.
- Detect duplicated activities and invalid predecessors.
- Verify the consistency of temporal estimates.
- Construct an Activity-on-Node network.
- Obtain a valid topological ordering.
- Perform the forward and backward passes.
- Calculate activity margins.
- Identify critical activities.
- Estimate the classical PERT deadline probability.
- Generate beta-PERT activity durations.
- Solve the complete network in each Monte Carlo simulation.
- Calculate duration statistics and percentiles.
- Estimate the empirical probability of meeting a deadline.
- Calculate activity and path criticality frequencies.
- Export the results to Excel.
- Generate graphical representations of the project network and simulated duration distribution.

---

## Repository structure

```text
PERT-and-Monte-Carlo-Project-Scheduling/
│
├── PERT.py
├── MONTE-CARLO.py
├── Caso_Estudio.xlsx
└── README.md
```

### Files

| File | Description |
|---|---|
| `PERT.py` | Deterministic implementation of the PERT method |
| `MONTE-CARLO.py` | Monte Carlo simulation applied to the PERT network |
| `Caso_Estudio.xlsx` | Input file containing activities, predecessors and time estimates |
| `README.md` | Installation, input and execution instructions |

---

## Requirements

The programs require **Python 3** and the following Python libraries:

```bash
pip install pandas numpy matplotlib scipy tqdm openpyxl graphviz
```

The Graphviz application must also be installed on the computer because the Python `graphviz` package requires the Graphviz executable to generate the Activity-on-Node diagrams.

### Graphviz verification

After installing Graphviz, verify that it is available by running:

```bash
dot -V
```

If the command is not recognised, the Graphviz installation directory may need to be added to the system `PATH`.

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

### Example

| ID | Predecesoras | To | Tmp | Tp |
|---|---|---:|---:|---:|
| A | - | 1 | 2 | 3 |
| B | A | 3 | 4 | 5 |
| C | B | 3 | 5 | 7 |
| G | D,F | 2 | 3 | 4 |

### Input requirements

- Every activity must have a unique identifier.
- Activities without predecessors must contain an empty cell or a hyphen (`-`).
- Multiple predecessors must be separated by commas.
- Every predecessor must correspond to an activity included in the input table.
- Temporal estimates must satisfy:

```math
T_o(a_i)\leq T_{mp}(a_i)\leq T_p(a_i)
```

---

## Methodological overview

### Deterministic PERT analysis

For each activity $a_i$, the expected duration is calculated as:

```math
t_e(a_i)=
\frac{
T_o(a_i)+4T_{mp}(a_i)+T_p(a_i)
}{6}
```

The variance of each activity is:

```math
\mathrm{Var}(a_i)=
\left(
\frac{T_p(a_i)-T_o(a_i)}{6}
\right)^2
```

The project is represented as a directed acyclic graph, and the program obtains a valid topological ordering of its activities.

---

### Forward pass

The early start of activity $a_i$ is:

```math
ES(a_i)=
\begin{cases}
0,
& \mathrm{Pred}(a_i)=\varnothing,\\
\displaystyle
\max_{a_j\in\mathrm{Pred}(a_i)}
EF(a_j),
& \mathrm{Pred}(a_i)\neq\varnothing.
\end{cases}
```

The early finish is:

```math
EF(a_i)=ES(a_i)+t_e(a_i)
```

The expected project duration is:

```math
T_{\mathrm{PERT}}
=
\max_{a_i\in A}EF(a_i)
```

---

### Backward pass

The late finish of activity $a_i$ is:

```math
LF(a_i)=
\begin{cases}
T_{\mathrm{PERT}},
& \mathrm{Succ}(a_i)=\varnothing,\\
\displaystyle
\min_{a_j\in\mathrm{Succ}(a_i)}
LS(a_j),
& \mathrm{Succ}(a_i)\neq\varnothing.
\end{cases}
```

The late start is:

```math
LS(a_i)=LF(a_i)-t_e(a_i)
```

The total margin is:

```math
M(a_i)=LS(a_i)-ES(a_i)
```

An activity is considered critical when:

```math
M(a_i)\approx 0
```

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

### Target deadline

The target project deadline is defined inside the script:

```python
plazo_objetivo = 64
```

Modify this value before running the program when a different deadline must be analysed.

### Deterministic outputs

The deterministic program provides:

- Expected duration of every activity.
- Activity variance.
- Predecessor and successor lists.
- Early start and early finish times.
- Late start and late finish times.
- Total activity margins.
- Expected project duration.
- Critical activities.
- Approximate project variance.
- Approximate project standard deviation.
- Approximate probability of meeting the target deadline.
- Activity-on-Node network diagram.

---

## Monte Carlo simulation

The Monte Carlo simulation considers activity durations as random variables.

In simulation $k$, the duration of activity $a_i$ is generated according to a beta-PERT distribution:

```math
D_i^{(k)}
\sim
\mathrm{BetaPERT}
\left(
T_{o,i},
T_{mp,i},
T_{p,i};
\lambda=4
\right)
```

where:

- $T_{o,i}$ is the optimistic duration of activity $a_i$.
- $T_{mp,i}$ is its most likely duration.
- $T_{p,i}$ is its pessimistic duration.
- $\lambda=4$ is the shape parameter used in the implementation.

The generated duration always satisfies:

```math
T_{o,i}
\leq
D_i^{(k)}
\leq
T_{p,i}
```

Values close to the most likely estimate $T_{mp,i}$ have a greater probability of being generated.

When the three estimates are equal:

```math
T_{o,i}=T_{mp,i}=T_{p,i}
```

the activity duration is deterministic and remains constant in every simulation.

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

where:

- `plazo_objetivo` is the project deadline to be analysed.
- `N` is the total number of Monte Carlo simulations.

A larger value of $N$ generally produces more stable statistical estimates, although it also increases the execution time.

---

## Monte Carlo procedure

The simulation is repeated for:

```math
k=1,2,\ldots,N
```

In every iteration, the program performs the following operations:

```text
Generate one beta-PERT duration for every activity
                         ↓
Solve the complete PERT network
                         ↓
Calculate the total project duration
                         ↓
Identify the critical activities and paths
                         ↓
Store the simulation results
```

The precedence structure of the project remains fixed throughout the analysis. Only the activity durations change between simulated scenarios.

For simulation $k$, the generated duration vector can be represented as:

```math
\mathbf{D}^{(k)}
=
\left(
D_1^{(k)},
D_2^{(k)},
\ldots,
D_n^{(k)}
\right)
```

Using this set of durations, the program solves the PERT network and obtains:

- The total project duration $T^{(k)}$.
- The early and late activity times.
- The activity margins.
- The critical activities.
- The critical path or paths associated with the scenario.

The process is repeated $N$ times to obtain a sample of possible project outcomes.

---
## Statistical estimators

### Simulated mean duration

Let $T^{(k)}$ be the total project duration obtained in simulation $k$.

The mean simulated project duration is:

```math
\overline{T}_N=\frac{1}{N}\sum_{k=1}^{N}T^{(k)}
```

According to the law of large numbers:

```math
\overline{T}_N\longrightarrow\mathrm{E}[T]\qquad(N\longrightarrow\infty)
```

This means that the simulated mean approaches the expected project duration as the number of simulations increases.

---

### Deadline-compliance probability

For each simulation $k$, define the indicator variable:

```math
I_k=
\begin{cases}
1, & T^{(k)}\leq T_{\mathrm{obj}},\\
0, & T^{(k)}>T_{\mathrm{obj}}.
\end{cases}
```

The empirical probability of meeting the target deadline is:

```math
\widehat{P}\left(T\leq T_{\mathrm{obj}}\right)
=
\frac{1}{N}\sum_{k=1}^{N}I_k
```

Therefore, the estimated probability is the proportion of simulated scenarios in which the total project duration does not exceed the target deadline.

---

### Activity criticality frequency

Let $\mathcal{C}^{(k)}$ be the set of critical activities obtained in simulation $k$.

For activity $a_i$, define:

```math
C_i^{(k)}=
\begin{cases}
1, & a_i\in\mathcal{C}^{(k)},\\
0, & a_i\notin\mathcal{C}^{(k)}.
\end{cases}
```

The criticality frequency of activity $a_i$ is:

```math
FC_i=
\frac{1}{N}\sum_{k=1}^{N}C_i^{(k)}
```

Expressed as a percentage:

```math
FC_i(\%)=
100\frac{\displaystyle\sum_{k=1}^{N}C_i^{(k)}}{N}
```

This indicator represents the percentage of simulations in which activity $a_i$ belongs to a critical path.

---

### Critical-path frequency

Let $\mathcal{R}_j$ denote a possible critical path of the project.

For each simulation, define:

```math
R_j^{(k)}=
\begin{cases}
1, & \mathcal{R}_j\text{ is critical in simulation }k,\\
0, & \text{otherwise}.
\end{cases}
```

The frequency of occurrence of path $\mathcal{R}_j$ is:

```math
FR_j=
\frac{1}{N}\sum_{k=1}^{N}R_j^{(k)}
```

Expressed as a percentage:

```math
FR_j(\%)=
100\frac{\displaystyle\sum_{k=1}^{N}R_j^{(k)}}{N}
```

This makes it possible to determine how often each possible project path becomes critical.

---

## Convergence and statistical error

The statistical error of a Monte Carlo estimator decreases approximately according to:

```math
\mathrm{Error}\propto\frac{1}{\sqrt{N}}
```

Therefore, multiplying the number of simulations by four approximately divides the statistical error by two:

```math
N\longrightarrow4N
\qquad\Rightarrow\qquad
\mathrm{Error}\longrightarrow\frac{\mathrm{Error}}{2}
```

The number of simulations is considered sufficient when the main statistical indicators remain stable as $N$ increases.

The convergence analysis considers the stability of:

- Mean project duration.
- Standard deviation.
- Duration percentiles.
- Deadline-compliance probability.
- Activity criticality frequencies.
- Critical-path frequencies.

The final number of simulations should therefore be selected according to the stability of the results, rather than solely because it is numerically large.

## Monte Carlo results

After completing all simulations, the program calculates:

- Mean simulated project duration.
- Standard deviation.
- Minimum and maximum duration.
- Percentiles $P_5$, $P_{50}$, $P_{80}$, $P_{90}$ and $P_{95}$.
- Empirical probability of meeting the target deadline.
- Number and percentage of simulations in which each activity is critical.
- Number and percentage of appearances of each critical path.
- Simulated distribution of the total project duration.

---

## Output files

The Monte Carlo results are exported to:

```text
Resultados_PERT_MonteCarlo.xlsx
```

The output workbook contains the following sheets:

| Sheet | Description |
|---|---|
| `PERT_Clasico` | Deterministic PERT planning |
| `MonteCarlo` | Total durations obtained in the simulations |
| `Criticidad` | Activity criticality frequencies |

The program also generates:

- A graphical representation of the simulated project-duration distribution.
- An Activity-on-Node diagram of the deterministic reference network.

---

## Interpretation of the results

The deterministic PERT analysis provides a reference schedule based on expected activity durations.

However, when activity durations are uncertain:

- The mean simulated duration may differ from the deterministic project duration.
- The critical path may change between scenarios.
- Activities that are not critical in the deterministic analysis may become critical in some simulations.
- The classical PERT deadline probability may differ from the empirical Monte Carlo probability.
- Several alternative paths may accumulate significant criticality frequencies.

Therefore, Monte Carlo simulation does not replace PERT. It extends the deterministic analysis by quantifying:

- Duration uncertainty.
- Deadline-compliance risk.
- Dispersion of possible results.
- Critical-path variability.
- Activity criticality frequency.

---

## Recommended workflow

1. Download or clone the repository.
2. Install the required Python libraries.
3. Install Graphviz.
4. Complete the `Caso_Estudio.xlsx` input file.
5. Verify the activity identifiers and predecessors.
6. Set the target deadline.
7. Set the number of Monte Carlo simulations.
8. Run the deterministic PERT analysis.
9. Run the Monte Carlo simulation.
10. Review the numerical, graphical and Excel outputs.

### Execution commands

```bash
python PERT.py
python MONTE-CARLO.py
```

---

## Academic context

This repository complements the theoretical and methodological development presented in the Bachelor's Thesis.

The complete academic work includes:

- Mathematical formulation of the PERT method.
- Representation of projects through directed acyclic graphs.
- Topological ordering of project activities.
- Forward and backward passes.
- Activity margins and critical paths.
- Probabilistic foundations of Monte Carlo simulation.
- Beta-PERT probability distributions.
- Convergence and statistical-error analysis.
- Comparison between deterministic PERT and Monte Carlo results.
- Analysis of activity and path criticality frequencies.

This repository focuses primarily on the source code, input data and instructions required to reproduce the computational analysis.

---

## Limitations

The results depend on the quality of the optimistic, most likely and pessimistic duration estimates.

The current implementation assumes that:

- Activity durations are independent.
- The precedence network remains fixed.
- The beta-PERT distribution adequately represents activity durations.
- Resource availability does not restrict the schedule.
- Costs are not included.
- Working calendars are not included.
- Equipment availability is not modelled.
- The number of simulations is defined before execution.

Possible future improvements include:

- Correlated activity durations.
- Probability distributions fitted to historical data.
- Resource constraints.
- Cost uncertainty.
- Working calendars.
- Equipment-availability constraints.
- Automatic convergence and stopping criteria.

---

## Author

**Luis Rodríguez-Caso López**  
Bachelor's Degree in Aerospace Engineering  
University of Seville

---

<div align="center">

Developed as part of a Bachelor's Thesis in Aerospace Engineering.

</div>
