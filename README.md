# TravelIntel
TravelIntel provides curated security intelligence, regional threat data, and safety insights tailored to your destination so you can travel smarter and safer.

## Quick start / deployment

The repository includes a helper script that runs the entire project end‑to‑end
(including unit tests) so you can validate a new environment or prepare for
deployment:

```bash
python run_all.py
```

When the script completes you’ll have scraped data in the Postgres database
and all checks passing; the dashboard will launch automatically so you can
inspect the results.  On deployed platforms such as Render you can set the
start command to `python run_all.py` to guarantee the database is populated
before the web service begins handling requests.

For Render's managed Postgres service the platform will inject a
``DATABASE_URL`` environment variable.  Our configuration honors that URL or
falls back to the individual ``DB_*`` variables described in the QUICKSTART.
