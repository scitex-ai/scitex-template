# MNIST showcase scripts

One script per step, run from the project root in order (`make all` does
this). Every script is a `@scitex_session.session` function; parameters
come from `config/*.yaml` and paths from `config/PATH.yaml`.

| Script | Reads | Writes |
|---|---|---|
| `00_resolve_references.py` (online, `make refs`) | `config/references_seed.bib` | `data/literature/references.bib`, `references_record.json` |
| `01_fetch_mnist.py` | MNIST via scitex-dataset -> `data/raw/mnist/mnist.npz` | `data/mnist/{X,y}_{train,test}.npy`, `dataset_record.json` |
| `02_train_classifiers.py` | `data/mnist/*.npy` | `data/results/{pred_logreg,pred_svc}.npy`, `metrics.json`, `conf_mat_svc.csv`, `per_class_recall.csv` |
| `03_compare_classifiers.py` | `y_test.npy`, both predictions | `data/results/mcnemar.json` |
| `04_plot_figure.py` | test images, confusion matrix, per-class recall | `data/figures/panel_{a,b,c}_*.png` (+ recipes), `fig1_mnist.png` |
| `05_register_claims.py` | the files named in `config/CLAIMS.yaml` | claims in the clew store, `\vclaim` values for the paper |

Each output is written under `<script>_out/` and linked at the path above
(`symlink_from_cwd=True`), so `data/` is a flat view of the latest results
and clew knows which run wrote each file.
