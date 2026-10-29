# Study A — datasets

The split is fixed in `common/data.py` and was set before any reasoning-mode run. A dataset is DEVELOPMENT or UNSEEN, never both.
Large datasets are row-sampled to 15,000 (seed 20261027) for the ML evidence; the source row count is shown in every evidence
packet. Holdout: 25 % test split that mirrors deployment (time-ordered for temporal data, grouped for repeated entities,
stratified otherwise). The test split is used **only** for regret and never appears in an evidence packet.

| Dataset | Split | Family | Task | Source rows | Used | Notes |
|---|---|---|---|---|---|---|
| telco_churn | DEV | churn | binary | 7,043 | 7,043 | IBM Telco sample; mixed types |
| german_credit | DEV | credit | binary | 1,000 | 1,000 | UCI 144; coded categoricals A11..A202 |
| bank_marketing | DEV | cross-sell | binary | 45,211 | 15,000 | UCI 222; `duration` (post-call) removed from Study A features |
| adult_income | DEV | generic (census) | binary | 32,561 | 15,000 | UCI 2 |
| bike_sharing | DEV | demand | regression | 17,379 | 15,000 | UCI 275 hourly; `casual`/`registered` (target components) removed; time-ordered holdout |
| vehicle_silhouettes | DEV | generic | multiclass (4) | 846 | 846 | UCI 149; anonymous geometry features |
| iranian_churn | UNSEEN | churn | binary | 3,150 | 3,150 | UCI 563; 9-month window, month-12 label |
| taiwan_default | UNSEEN | credit | binary | 30,000 | 15,000 | UCI 350 |
| coil_caravan | UNSEEN | cross-sell | binary (6 % pos.) | 5,822 | 5,822 | UCI 125; 85 features (high-dimensional) |
| diabetes_readmission | UNSEEN | medical | binary (11 % pos.) | 101,766 | 15,000 | UCI 296; patients repeat → grouped holdout |
| card_fraud_synth | UNSEEN | fraud | binary (3.5 % pos.) | 14,000 | 14,000 | **synthetic**, documented generator in `data.py`; time-ordered holdout |
| online_shoppers | UNSEEN | generic (e-commerce) | binary (15 % pos.) | 12,330 | 12,330 | UCI 468 |
| thyroid_sick | UNSEEN | medical | binary (6 % pos.) | 2,800 | 2,800 | UCI 102 |
| image_segment | UNSEEN | generic | multiclass (7) | 2,310 | 2,310 | UCI 50 |
| hillstrom_email | UNSEEN | uplift | binary (1 % conv.) | 64,000 | 64,000 | MineThatData randomized e-mail test; CAUSAL tasks only |

Coverage against the brief: binary (11), multiclass (2), regression (1), high-dimensional (coil 85 features; diabetes 113
encoded), high row count (diabetes 101k, hillstrom 64k, bank 45k), imbalanced (coil, fraud, thyroid, diabetes, bank),
mixed numeric/categorical (telco, german, bank, adult, diabetes, online), semantically rich business data (churn ×2,
credit ×2, cross-sell ×2, medical ×2, fraud, uplift).

Raw sources live outside the repository in `~/.cache/athena-decision-corpus-v2` (archives already used by decision-corpus-v2)
and `~/.cache/athena-research-ablation/raw/<name>/` (downloaded 2026-10-27 from archive.ics.uci.edu, the IBM GitHub
sample and minethatdata.com).
