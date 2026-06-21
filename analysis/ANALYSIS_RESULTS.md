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
logit    acc=0.62  roc_auc=0.66  base_rate=0.35  n=40
forest   acc=0.70  roc_auc=0.65  base_rate=0.35  n=40
```

### Logistic-regression coefficients (standardized; sign = direction)

| feature            |   coef |
|:-------------------|-------:|
| age_at_wc          | -0.963 |
| team_stage_rank    | -0.898 |
| clean_sheets       |  0.583 |
| club_pre_tier_rank | -0.542 |
| save_pct           | -0.484 |
| saves_per90        | -0.44  |
| pen_saves          | -0.32  |
| ga_per90           | -0.285 |
| minutes            | -0.223 |
| saves              |  0.216 |
| fifa_rank_pre      | -0.212 |
| goals_conceded     |  0.192 |
| mv_pre_eur_m       |  0.157 |
| matches            | -0.025 |

### Random-forest permutation importance (ROC-AUC drop)

| feature            |   perm_importance |   perm_std |
|:-------------------|------------------:|-----------:|
| age_at_wc          |            0.127  |     0.0484 |
| save_pct           |            0.0262 |     0.0058 |
| saves              |            0.0166 |     0.0058 |
| mv_pre_eur_m       |            0.0159 |     0.0045 |
| ga_per90           |            0.0155 |     0.0075 |
| saves_per90        |            0.0137 |     0.0053 |
| fifa_rank_pre      |            0.0125 |     0.005  |
| minutes            |            0.0102 |     0.0041 |
| goals_conceded     |            0.0093 |     0.0044 |
| club_pre_tier_rank |            0.0082 |     0.0048 |
| matches            |            0.0061 |     0.0034 |
| team_stage_rank    |            0.0054 |     0.004  |
| pen_saves          |            0.0045 |     0.0045 |
| clean_sheets       |            0.0025 |     0.0035 |

## 4. What drives the *size* of the post-WC value bump

Ridge regression on market-value growth % (standardized features), n=39, cross-validated R²=-0.49 (small sample — interpret signs/ranking, not fit).

| feature            |   ridge_coef_per_sd |
|:-------------------|--------------------:|
| age_at_wc          |               -9.16 |
| goals_conceded     |               -5.78 |
| pen_saves          |               -4.42 |
| ga_per90           |               -3.63 |
| team_stage_rank    |               -3.08 |
| mv_pre_eur_m       |               -3.07 |
| save_pct           |                2.77 |
| club_pre_tier_rank |               -2.72 |
| minutes            |               -2.19 |
| matches            |               -1.98 |
| fifa_rank_pre      |                1.58 |
| saves_per90        |                1.11 |
| non_elite_nation   |                0.85 |
| saves              |               -0.68 |
| clean_sheets       |                0.57 |

*The `non_elite_nation` coefficient (`+0.9` pp of value growth per SD, after controlling for age/club/performance) is the smaller-nation 'showcase premium'. It is small relative to the shot-stopping and age effects — i.e. once you account for how well a keeper actually played and how old they are, nationality adds little to the value bump.*

### Gradient-boosted permutation importance for value growth

| feature            |   perm_importance_r2 |
|:-------------------|---------------------:|
| save_pct           |               0.6146 |
| age_at_wc          |               0.3939 |
| mv_pre_eur_m       |               0.1313 |
| fifa_rank_pre      |               0.1225 |
| saves_per90        |               0.0811 |
| ga_per90           |               0.0743 |
| club_pre_tier_rank |               0.0245 |
| clean_sheets       |               0.0113 |
| pen_saves          |               0.0079 |
| saves              |               0.0065 |
| minutes            |               0.0059 |
| team_stage_rank    |               0.0031 |
| non_elite_nation   |               0.0005 |
| matches            |               0.0005 |
| goals_conceded     |               0.0003 |

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
|            2006 | age_at_wc     |       0.0755 |
|            2010 | age_at_wc     |       0.0496 |
|            2014 | age_at_wc     |       0.0465 |
|            2018 | age_at_wc     |       0.0212 |
|            2022 | age_at_wc     |       0.1333 |
