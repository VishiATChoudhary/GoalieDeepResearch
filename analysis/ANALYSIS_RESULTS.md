# Analysis Results — World Cup Goalkeeper Showcase Effect

Dataset: 45 goalkeeper-tournament rows across 5 World Cups (2006–2022).

## 1. Showcase success by nation tier

| nation_tier   |   n |   success_rate |   mean_mv_growth |
|:--------------|----:|---------------:|-----------------:|
| elite         |  12 |          0.333 |           15.693 |
| mid           |  22 |          0.364 |           39.091 |
| smaller       |  11 |          0.273 |           25.758 |

*Mann–Whitney U test (smaller/mid MV growth > elite):* U=160, p=0.722, n_small=33, n_elite=11

## 2. Driving factors

### Cross-validated performance (honest, small-sample)

```
logit    acc=0.64  roc_auc=0.59  base_rate=0.33  n=45
forest   acc=0.62  roc_auc=0.52  base_rate=0.33  n=45
```

### Logistic-regression coefficients (standardized; sign = direction)

| feature            |   coef |
|:-------------------|-------:|
| team_stage_rank    | -1.094 |
| age_at_wc          | -0.623 |
| club_pre_tier_rank | -0.548 |
| ga_per90           | -0.501 |
| clean_sheets       |  0.444 |
| save_pct           | -0.434 |
| saves_per90        | -0.388 |
| pen_saves          | -0.356 |
| fifa_rank_pre      | -0.339 |
| saves              |  0.232 |
| matches            |  0.215 |
| goals_conceded     |  0.16  |
| mv_pre_eur_m       |  0.144 |
| minutes            | -0.013 |

### Random-forest permutation importance (ROC-AUC drop)

| feature            |   perm_importance |   perm_std |
|:-------------------|------------------:|-----------:|
| age_at_wc          |            0.0508 |     0.0207 |
| fifa_rank_pre      |            0.011  |     0.0073 |
| saves              |            0.0086 |     0.0047 |
| save_pct           |            0.008  |     0.0057 |
| saves_per90        |            0.0077 |     0.0048 |
| mv_pre_eur_m       |            0.0065 |     0.0053 |
| ga_per90           |            0.0056 |     0.0042 |
| club_pre_tier_rank |            0.0049 |     0.0029 |
| minutes            |            0.0034 |     0.0023 |
| pen_saves          |            0.0023 |     0.0025 |
| goals_conceded     |            0.002  |     0.0012 |
| team_stage_rank    |            0.0011 |     0.0014 |
| matches            |            0      |     0      |
| clean_sheets       |            0      |     0      |

## 4. What drives the *size* of the post-WC value bump

Ridge regression on market-value growth % (standardized features), n=44, cross-validated R²=-1.66 (small sample — interpret signs/ranking, not fit).

| feature            |   ridge_coef_per_sd |
|:-------------------|--------------------:|
| age_at_wc          |               -6.46 |
| goals_conceded     |               -3.66 |
| pen_saves          |               -3.46 |
| club_pre_tier_rank |               -3.4  |
| save_pct           |                2.84 |
| ga_per90           |               -2.77 |
| mv_pre_eur_m       |               -2.6  |
| team_stage_rank    |               -1.98 |
| non_elite_nation   |                1.73 |
| saves_per90        |                1.53 |
| fifa_rank_pre      |                1.23 |
| clean_sheets       |                1.16 |
| minutes            |               -0.77 |
| saves              |                0.59 |
| matches            |               -0.55 |

*The `non_elite_nation` coefficient (`+1.7` pp of value growth per SD, after controlling for age/club/performance) is the smaller-nation 'showcase premium'. It is small relative to the shot-stopping and age effects — i.e. once you account for how well a keeper actually played and how old they are, nationality adds little to the value bump.*

### Gradient-boosted permutation importance for value growth

| feature            |   perm_importance_r2 |
|:-------------------|---------------------:|
| save_pct           |               0.5146 |
| age_at_wc          |               0.439  |
| mv_pre_eur_m       |               0.3068 |
| saves_per90        |               0.1812 |
| saves              |               0.0633 |
| club_pre_tier_rank |               0.049  |
| minutes            |               0.0364 |
| fifa_rank_pre      |               0.0351 |
| ga_per90           |               0.0249 |
| goals_conceded     |               0.019  |
| clean_sheets       |               0.0145 |
| team_stage_rank    |               0.0128 |
| pen_saves          |               0.0065 |
| matches            |               0.0031 |
| non_elite_nation   |               0      |

## 3. Sensitivity analysis

### (a) Success definition — vary the market-value growth threshold

|   threshold_% |   overall |   smaller |   mid |   elite |
|--------------:|----------:|----------:|------:|--------:|
|            25 |     0.356 |     0.273 | 0.364 |   0.417 |
|            50 |     0.333 |     0.273 | 0.364 |   0.333 |
|            75 |     0.311 |     0.182 | 0.364 |   0.333 |
|           100 |     0.311 |     0.182 | 0.364 |   0.333 |
|           150 |     0.311 |     0.182 | 0.364 |   0.333 |

### (b) Tier cutoff — vary the FIFA-rank boundary defining 'smaller'

|   smaller_if_rank> |   n_smaller |   success_smaller |   success_rest |    gap |
|-------------------:|------------:|------------------:|---------------:|-------:|
|                 20 |          20 |             0.3   |          0.36  | -0.06  |
|                 25 |          14 |             0.286 |          0.355 | -0.069 |
|                 30 |          11 |             0.273 |          0.353 | -0.08  |
|                 35 |          10 |             0.3   |          0.343 | -0.043 |
|                 40 |           8 |             0.25  |          0.351 | -0.101 |

### (c) Leave-one-tournament-out — stability of the top driver

|   held_out_year | top_feature   |   importance |
|----------------:|:--------------|-------------:|
|            2006 | age_at_wc     |       0.0318 |
|            2010 | age_at_wc     |       0.0251 |
|            2014 | age_at_wc     |       0.0338 |
|            2018 | fifa_rank_pre |       0.0119 |
|            2022 | age_at_wc     |       0.0736 |
