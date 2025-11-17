# ISAZI Presentation Slides (Notes)

This file contains the speaker notes and checklist for the 4-hour demo.

## Timing and checklist (4-hour delivery)

- 00:00 — Setup & verification (10 min)
  - Ensure environment is active (conda or Colab)
  - Run `./run_dashboard.sh` locally or run the lightweight Colab notebook
- 00:10 — Dashboard walkthrough (15 min)
  - Application funnel visualization
  - Source effectiveness and top sources
  - Qualification analysis and pivot
  - Live filtering and date-range selection
- 00:25 — Analytics quick demo (10 min)
  - Show `RecruitmentAnalytics` predictions (if available)
  - Explain metrics and next steps
- 00:35 — Q&A and next steps (10-15 min)

## Quick run commands

1) Create environment (recommended):

```bash
conda create -n isazi-recruitment python=3.9 -y
conda activate isazi-recruitment
```

2) Install requirements (lightweight):

```bash
pip install -r requirements.cleaned.txt
```

3) Create sample data & start dashboard (local):

```bash
chmod +x run_dashboard.sh
./run_dashboard.sh
# or
streamlit run dashboard.py
```

4) (Optional) Expose with ngrok:

```bash
python - <<'PY'
from pyngrok import ngrok
print(ngrok.connect(8501))
PY
```

## Colab quick steps

- Open `colab_run_dashboard_lightweight.ipynb` in Colab
- Click "Copy to Drive"
- Run cells top-to-bottom
- When the ngrok public URL appears, open it in a browser to demo

## Troubleshooting

- If imports fail, run `pip install -r requirements.cleaned.txt`
- If the DB is empty, run `from recruitment_functions import create_sample_data; create_sample_data(force=True)`
- If Streamlit won't start, check `streamlit.log` for errors

---

Deliverables:

- `slides.md` — this file (talking points and run checklist)
- `demo_execution.ipynb` — short demo flow (already in repo)
- `colab_run_dashboard_lightweight.ipynb` — Colab runner
