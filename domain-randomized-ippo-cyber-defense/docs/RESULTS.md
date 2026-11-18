# Results

All numbers are the ones reported in the paper (source: `results/paper_table2_single_seed.csv`, `results/paper_multiseed_results.json`). Mean episode reward / containment rate, 20 deterministic episodes per cell.

## Table II — single-run seen/unseen matrix

| Topology | Profile | Baseline reward / contain. | DR reward / contain. |
|---|---|---|---|
| topo_1 | aggressive | -153.0 / 0% | 238.0 / 100% |
| topo_1 | stealthy | -113.0 / 0% | 238.0 / 100% |
| topo_1 | opportunistic | -137.2 / 0% | 238.0 / 100% |
| topo_2 | aggressive | 218.0 / 100% | 259.0 / 100% |
| topo_2 | stealthy | 218.0 / 100% | 259.0 / 100% |
| topo_2 | opportunistic | 218.0 / 100% | 259.0 / 100% |
| topo_3 | aggressive | -139.0 / 0% | 248.0 / 100% |
| topo_3 | stealthy | -119.0 / 0% | 248.0 / 100% |
| topo_3 | opportunistic | -132.2 / 0% | 248.0 / 100% |
| topo_1 | cloud_pivot (unseen) | -107.0 / 0% | -107.0 / 0% |
| topo_2 | cloud_pivot (unseen) | -107.0 / 0% | -107.0 / 0% |
| topo_3 | cloud_pivot (unseen) | -107.0 / 0% | -107.0 / 0% |
| topo_4 (unseen) | aggressive | -149.0 / 0% | 238.0 / 100% |
| topo_4 (unseen) | stealthy | -124.0 / 0% | 238.0 / 100% |
| topo_4 (unseen) | opportunistic | -144.4 / 0% | 238.0 / 100% |
| topo_5 (unseen) | aggressive | -141.0 / 0% | 259.0 / 100% |
| topo_5 (unseen) | stealthy | -126.0 / 0% | 259.0 / 100% |
| topo_5 (unseen) | opportunistic | -140.0 / 0% | 259.0 / 100% |
| topo_4 (unseen) | cloud_pivot (unseen) | -107.0 / 0% | -107.0 / 0% |
| topo_5 (unseen) | cloud_pivot (unseen) | -107.0 / 0% | -107.0 / 0% |

## Table III — multi-seed topology generalization (aggressive profile)

Mean ± std across 3 independent training seeds (0, 1, 2).

| Topology | Baseline | DR | per-seed baseline | per-seed DR |
|---|---|---|---|---|
| topo_1 | -142.7 ± 14.6 | 264.7 ± 9.4 | [-153.0, -122.0, -153.0] | [258.0, 278.0, 258.0] |
| topo_2 | -134.7 ± 9.4 | 259.0 ± 0.0 | [-128.0, -128.0, -148.0] | [259.0, 259.0, 259.0] |
| topo_3 | -27.0 ± 172.7 | 261.3 ± 9.4 | [-139.0, 217.0, -159.0] | [248.0, 268.0, 268.0] |
| topo_4 (unseen) | -152.0 ± 12.8 | 238.0 ± 16.3 | [-149.0, -138.0, -169.0] | [218.0, 238.0, 258.0] |
| topo_5 (unseen) | -39.3 ± 166.2 | 259.0 ± 0.0 | [-141.0, 195.0, -172.0] | [259.0, 259.0, 259.0] |

## Reading the results

* **Structural generalization:** DR reaches 100 % containment with positive reward on all seen-attacker conditions, including topo_4 and topo_5, which were never sampled in training.
* **Baseline instability:** the baseline's std across seeds is 172.7 (topo_3) and 166.2 (topo_5): one seed occasionally succeeds, the others fail. The single positive baseline cell in Table II (topo_2) is seed luck, not a transferable policy.
* **Attack-mechanism limit:** against held-out `cloud_pivot` both defenders score −107.0 with 0 % containment on every topology; topology- and behaviour-level DR does not confer robustness to a new attack mechanism.

Figures: `results/figures/` (regenerate with `python scripts/make_figures.py results`).
