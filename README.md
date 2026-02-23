# TravelIntel
TravelIntel provides curated security intelligence, regional threat data, and safety insights tailored to your destination so you can travel smarter and safer.

## Quick start / deployment

The repository includes a helper script that runs the entire project end‑to‑end
(including unit tests) so you can validate a new environment or prepare for
deployment:

```bash
python run_all.py
```

When the script completes you’ll have scraped data in the database and all
checks passing; start the dashboard with `streamlit run dashboard.py` to
view the results.
