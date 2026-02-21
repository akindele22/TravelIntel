# Quick Start Guide

## Prerequisites

1. **Python 3.8+** installed
2. **PostgreSQL** installed and running
3. **Residential Proxies** (optional but recommended)

## Step-by-Step Setup

### 0. Create and Activate Virtual Environment (Recommended)

**In Git Bash (MINGW64):**
```bash
# Create virtual environment (if it doesn't exist)
python -m venv osint

# Activate virtual environment
source osint/Scripts/activate
```

**In PowerShell:**
```powershell
# Create virtual environment (if it doesn't exist)
python -m venv osint

# Activate virtual environment
.\osint\Scripts\Activate.ps1
```

**In Command Prompt (CMD):**
```cmd
# Create virtual environment (if it doesn't exist)
python -m venv osint

# Activate virtual environment
osint\Scripts\activate.bat
```

**Note:** After activation, you should see `(osint)` at the start of your prompt.

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**If you get build errors on Windows (numpy/pandas "compiler not found"):**

Install using pre-built wheels only (no compilation):
```bash
pip install --upgrade pip
pip install numpy pandas --only-binary :all:
pip install -r requirements.txt
```

**If you get an error with `psycopg2-binary` on Windows:**

Try installing it separately first:
```bash
pip install psycopg2-binary --upgrade
pip install -r requirements.txt
```

**Alternative:** If `psycopg2-binary` still fails, use the modern `psycopg` package instead:
```bash
pip install psycopg[binary] sqlalchemy
pip install -r requirements.txt --ignore-installed psycopg2-binary
```

Then update `database.py` to use `psycopg` instead of `psycopg2` (import changes needed).

### 2. Install Playwright Browsers

```bash
playwright install chromium
```

### 3. Set Up Database

Create a PostgreSQL database:

```sql
CREATE DATABASE travel_advisories;
```

Or use the setup script:

```bash
python setup_database.py
```

### 4. Configure Environment

Copy the example environment file:

```bash
copy .env.example .env
```

Edit `.env` and add your database credentials:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=travel_advisories
DB_USER=postgres
DB_PASSWORD=your_password
```

### 5. Configure Proxies (Optional)

Edit `config.py` and add your proxy credentials:

```python
PROXY_CONFIG = {
    'proxies': [
        'http://username:password@proxy1.example.com:8080',
        'http://username:password@proxy2.example.com:8080',
    ],
    ...
}
```

**Note**: If you don't have proxies, the scraper will still work but may be rate-limited or blocked by some sites.

### 6. Test the Scrapers

Test individual scrapers to ensure they work:

```bash
python test_scrapers.py
```

This will test each scraper and show you what data it can extract.

### 7. Run the Full Pipeline

Run the complete scraping pipeline:

```bash
python main.py
```

This will:
1. Scrape all configured sources
2. Clean and normalize the data
3. Store in PostgreSQL

### 8. Run the Dashboard UI

Once you have some data in the database, start the dashboard:

```bash
streamlit run dashboard.py
```

This provides an interactive view of advisories and location-level insights
for security, safety, and serenity (no ML prediction involved).

### 9. Query the Database

View scraped data:

```bash
# View all advisories
python query_database.py

# Filter by country
python query_database.py --country "France"

# Filter by source
python query_database.py --source "US State Department"

# Limit results
python query_database.py --limit 50
```

## Running on a Schedule

Run the scraper every 6 hours:

```bash
python main.py --schedule 6
```

## Troubleshooting

### "No module named 'playwright'"
```bash
pip install playwright
playwright install chromium
```

### "Database connection failed"
- Check PostgreSQL is running: `pg_isready`
- Verify credentials in `.env`
- Ensure database exists: `python setup_database.py`

### "No advisories found"
- Website structure may have changed
- Check `test_scrapers.py` output
- Update selectors in `scrapers.py` if needed
- Some sites may require JavaScript (use Playwright)

### "Proxy connection failed"
- Verify proxy format: `http://user:pass@host:port`
- Test proxies manually
- Check proxy credentials
- Some proxies may require authentication

## Next Steps

1. **Customize Scrapers**: Update selectors in `scrapers.py` based on actual website structure
2. **Add More Sources**: Create new scraper classes for additional sources
3. **Improve AI Model**: Train on more data or use more sophisticated models
4. **Add Monitoring**: Set up logging and alerting for scraping failures
5. **Create API**: Build a REST API to query the database

## Example Proxy Providers

Popular residential proxy providers:
- Bright Data (formerly Luminati)
- Smartproxy
- Oxylabs
- Proxy-Cheap
- Soax

**Important**: Always comply with website terms of service and use proxies responsibly.
