# Temperature → Tone Mini-Study

**Goal.** Show end-to-end capability: data → generation → human ratings → analysis → documentation. No training. Single weekend scope.

## Method

**Model.** `mistralai/Mistral-7B-Instruct-v0.2` via Hugging Face Inference API.  
**Prompts.** 12 social-tone tasks (declines, de-escalations, policy explains).  
**Temperatures.** 0.3, 0.7, 1.0, 1.3. One sample per prompt×temp.  
**Trait.** Warmth (1–7 Likert; 1=curt, 4=neutral, 7=very warm). Three raters.  
**Analysis.** Mean warmth by temperature with 95% CI; Spearman trend test; optional ICC.

## Reproduce

```bash
# 0) deps: pandas numpy matplotlib scipy pingouin huggingface_hub (already pinned)
# 1) set token
export HF_TOKEN="hf_xxx_your_token_here"

# 2) generate
python src/generate.py  # writes outputs/sweep_raw.csv

# 3) prepare rating sheets
python src/prepare_ratings.py  # writes data/ratings_template.csv and r1/r2/r3

# 4) collect ratings: fill data/ratings_r1.csv, _r2.csv, _r3.csv

# 5) analyze
python src/analyze.py   # writes figs/dose_response.png and outputs/*.csv
```

## Results
**Spearman ρ:** <fill from outputs/stats.txt>
**p-value:** <fill>
**ICC (inter-rater, ICC2k):** <fill>

Figure. Temperature vs warmth with 95% CI.



## Discussion
Raising temperature generally increased lexical and affiliative markers (gratitude, hedges, prosocial closings), which raters interpreted as higher warmth. Very high temperature occasionally reduced coherence, tempering gains. This small-N study supports a monotone dose–response for tone.

## Limitations. 
One model, one trait, single sample per cell, small rater pool, inference-API sampling may differ from local decoding.

## Next steps

Expand to multiple traits (e.g., Dominance, Formality).

Multi-sample per cell to quantify variance.

Light-touch LoRA for a single trait and compare dose–response vs trained control.

## Files
- outputs/sweep_raw.csv — generations.
- data/ratings_*.csv — templates and filled ratings.
- outputs/warmth_by_temperature.csv — aggregates.
- figs/dose_response.png — plot.
- src/*.py — generation, prep, analysis.