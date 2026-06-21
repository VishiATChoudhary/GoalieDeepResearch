# Analysis Results — World Cup Goalkeeper Showcase Effect

Dataset: 40 goalkeeper-tournament rows across 5 World Cups (2006–2022).

## 1. Showcase success by nation tier

| nation_tier   |   n |   success_rate |   mean_mv_growth |
|:--------------|----:|---------------:|-----------------:|
| elite         |  11 |          0.364 |           20.595 |
| mid           |  20 |          0.35  |           39.25  |
| smaller       |   9 |          0.333 |           30.556 |

*Mann–Whitney U test (smaller/mid MV growth > elite):* U=110, p=0.873, n_small=29, n_elite=10

## 2. Driving factors

### Cross-validated performance (honest, small-sample)

```
logit    acc=0.57  roc_auc=0.58  base_rate=0.35  n=40
forest   acc=0.53  roc_auc=0.60  base_rate=0.35  n=40
```

### Logistic-regression coefficients (standardized; sign = direction)

| feature            |   coef |
|:-------------------|-------:|
| team_stage_rank    | -0.837 |
| age_at_wc          | -0.731 |
| club_pre_tier_rank | -0.61  |
| fifa_rank_pre      | -0.416 |
| save_pct           |  0.338 |
| clean_sheets       |  0.3   |
| ga_per90           | -0.216 |
| goals_conceded     |  0.199 |
| pen_saves          | -0.187 |
| mv_pre_eur_m       |  0.179 |
| matches            |  0.166 |
| minutes            | -0.101 |
| saves_per90        | -0.058 |
| saves              | -0.055 |

### Random-forest permutation importance (ROC-AUC drop)

| feature            |   perm_importance |   perm_std |
|:-------------------|------------------:|-----------:|
| age_at_wc          |            0.0747 |     0.0305 |
| saves_per90        |            0.0138 |     0.0066 |
| save_pct           |            0.0112 |     0.0062 |
| saves              |            0.0081 |     0.003  |
| fifa_rank_pre      |            0.0042 |     0.0037 |
| mv_pre_eur_m       |            0.0034 |     0.004  |
| minutes            |            0.0019 |     0.0018 |
| club_pre_tier_rank |            0.0016 |     0.0021 |
| ga_per90           |            0.0015 |     0.0036 |
| matches            |            0.001  |     0.0013 |
| pen_saves          |            0.0009 |     0.0029 |
| goals_conceded     |            0.0005 |     0.0026 |
| team_stage_rank    |            0      |     0.002  |
| clean_sheets       |           -0.0014 |     0.0017 |

## 3. Sensitivity analysis

### (a) Success definition — vary the market-value growth threshold

|   threshold_% |   overall |   smaller |   mid |   elite |
|--------------:|----------:|----------:|------:|--------:|
|            25 |     0.375 |     0.333 |  0.35 |   0.455 |
|            50 |     0.35  |     0.333 |  0.35 |   0.364 |
|            75 |     0.325 |     0.222 |  0.35 |   0.364 |
|           100 |     0.325 |     0.222 |  0.35 |   0.364 |
|           150 |     0.325 |     0.222 |  0.35 |   0.364 |

### (b) Tier cutoff — vary the FIFA-rank boundary defining 'smaller'

|   smaller_if_rank> |   n_smaller |   success_smaller |   success_rest |    gap |
|-------------------:|------------:|------------------:|---------------:|-------:|
|                 20 |          17 |             0.353 |          0.348 |  0.005 |
|                 25 |          12 |             0.333 |          0.357 | -0.024 |
|                 30 |           9 |             0.333 |          0.355 | -0.022 |
|                 35 |           8 |             0.375 |          0.344 |  0.031 |
|                 40 |           6 |             0.333 |          0.353 | -0.02  |

### (c) Leave-one-tournament-out — stability of the top driver

|   held_out_year | top_feature   |   importance |
|----------------:|:--------------|-------------:|
|            2006 | age_at_wc     |       0.0458 |
|            2010 | age_at_wc     |       0.0301 |
|            2014 | age_at_wc     |       0.0352 |
|            2018 | age_at_wc     |       0.0142 |
|            2022 | age_at_wc     |       0.1255 |
