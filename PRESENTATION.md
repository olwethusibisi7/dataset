ISAZI Recruitment Dashboard — Presentation Notes

Goal
- Demo the interactive recruitment dashboard and key analytics for stakeholders.
- Show data flow, sample metrics, and quick ROI insights.

Timing and checklist (4-hour delivery)
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

Commands to run locally

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

Colab quick steps
- Open `colab_run_dashboard_lightweight.ipynb` in Colab
- Click "Copy to Drive"
- Run cells top-to-bottom
- When the ngrok public URL appears, open it in a browser to demo

Presentation assets
- `recruitment_dashboard.ipynb` — analysis notebooks
- `demo_execution.ipynb` — a short demo flow that clones, runs tests, creates sample data, and starts Streamlit
- `colab_run_dashboard_lightweight.ipynb` — quick Colab run

Troubleshooting
- If imports fail, run `pip install -r requirements.cleaned.txt`
- If the DB is empty, run `from recruitment_functions import create_sample_data; create_sample_data(force=True)`
- If Streamlit won't start, check `streamlit.log` for errors

Speaker notes (short)
- Lead with the business problem: reduce time-to-hire and improve source ROI
- Show the funnel and highlight drop-off stages (use filter to narrow time range)
- Call out top-sources and a recommended experiment (reallocate spend, track A/B)
- Mention that the analytics module can produce candidate-fit scores and shortlists

Deliverables
- Live dashboard at presentation time (URL or local)
- Short README with run instructions (already included)
- Follow-up: embed dashboards into internal BI portal or export periodic reports
