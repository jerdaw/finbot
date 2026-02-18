# Scheduled CI Setup Guide

**Created:** 2026-02-17
**Priority:** Priority 7, Item P7.3
**Workflow:** `.github/workflows/scheduled-update.yml`

---

## Overview

The scheduled CI workflow runs daily at 6:00 AM UTC to automatically update financial data and run freshness checks. This ensures data stays current without manual intervention.

---

## What the Workflow Does

1. **Checks out code** at 6:00 AM UTC daily
2. **Installs dependencies** (Python 3.12 + uv)
3. **Runs daily update script** (`scripts/update_daily.py`)
   - Fetches latest price histories (YFinance, Google Finance)
   - Updates FRED economic data
   - Updates Shiller datasets
   - Re-runs simulations (index sims, fund sims)
4. **Checks data freshness** using `finbot status` command
5. **Creates GitHub issue on failure** (automatic alert)

---

## Required Setup (User Action)

### Step 1: Add GitHub Secrets

The workflow requires API keys to fetch data. Add these as **GitHub Secrets**:

1. Go to your repository on GitHub
2. Navigate to **Settings → Secrets and variables → Actions**
3. Click **New repository secret**
4. Add the following secrets:

| Secret Name | Description | Where to Get |
|-------------|-------------|--------------|
| `ALPHA_VANTAGE_API_KEY` | Alpha Vantage API key | https://www.alphavantage.co/support/#api-key |
| `NASDAQ_DATA_LINK_API_KEY` | NASDAQ Data Link (Quandl) API key | https://data.nasdaq.com/sign-up |
| `US_BUREAU_OF_LABOR_STATISTICS_API_KEY` | BLS API key (optional) | https://www.bls.gov/developers/home.htm |
| `GOOGLE_FINANCE_SERVICE_ACCOUNT_CREDENTIALS_PATH` | Google Sheets service account JSON | https://cloud.google.com/iam/docs/service-accounts-create |

**Note:** If you don't have all API keys, the workflow will skip those data sources (graceful degradation).

### Step 2: Enable Workflow

The workflow is created but may need to be enabled:

1. Go to **Actions** tab on GitHub
2. Find "Scheduled Data Update" workflow
3. Click **Enable workflow** if prompted

### Step 3: Test Manual Run

Before waiting for the scheduled run, test manually:

1. Go to **Actions** tab
2. Select "Scheduled Data Update" workflow
3. Click **Run workflow** dropdown
4. Click **Run workflow** button (green)
5. Wait for completion (~5-10 minutes)
6. Check logs for any errors

---

## Schedule Details

**Cron Schedule:** `0 6 * * *` (6:00 AM UTC daily)

**Why 6:00 AM UTC?**
- US markets close at 4:00 PM ET (9:00 PM UTC)
- Allows time for EOD data to propagate (6-8 hours)
- Runs before most US users wake up (1:00 AM ET, 11:00 PM PT)

**Manual Trigger:** Available via **Actions → Scheduled Data Update → Run workflow**

---

## What Happens on Failure?

If the workflow fails (API errors, data issues, etc.):

1. **GitHub Issue Created:** Automatic issue with failure details and logs link
2. **Labels:** Tagged with `automated` and `data-quality`
3. **Notification:** You'll receive GitHub notification (if enabled)

**Triage Steps:**
1. Check the workflow logs (link in issue)
2. Identify failing data source (YFinance, FRED, etc.)
3. Check API key validity and rate limits
4. Re-run manually after fixing issue

---

## Monitoring Data Freshness

The workflow runs `finbot status` command which checks:
- YFinance data staleness (1 day threshold)
- FRED data staleness (7 days threshold)
- Google Finance data staleness (1 day threshold)
- Shiller data staleness (30 days threshold)

**View Status Locally:**
```bash
uv run finbot status
```

**Expected Output:**
```
Data Source Status:
✓ yfinance: Fresh (last updated: 2026-02-17)
✓ fred: Fresh (last updated: 2026-02-15)
✓ google_finance: Fresh (last updated: 2026-02-17)
✓ shiller: Fresh (last updated: 2026-02-01)
```

---

## Disabling Scheduled Runs

If you want to disable automatic daily updates:

1. Go to `.github/workflows/scheduled-update.yml`
2. Comment out the `schedule:` section:
   ```yaml
   # schedule:
   #   - cron: '0 6 * * *'
   ```
3. Commit and push
4. Manual runs still available via `workflow_dispatch`

---

## Cost Considerations

**GitHub Actions Minutes:**
- Free tier: 2,000 minutes/month (500 minutes for private repos)
- Each run: ~5-10 minutes
- Monthly usage: ~150-300 minutes (30 days × 5-10 min)
- **Well within free tier limits**

**API Rate Limits:**
- Alpha Vantage: 25 calls/day (free tier)
- NASDAQ Data Link: 50 calls/day (free tier)
- YFinance: No official limit (use respectfully)
- FRED: No limit with API key

**Cost:** $0 (all free tier)

---

## Troubleshooting

### Issue: Workflow doesn't run
**Solution:** Check that workflow is enabled in Actions tab. Check that secrets are set.

### Issue: API key errors
**Solution:** Verify secrets are named exactly as shown (case-sensitive). Re-generate API keys if expired.

### Issue: Data freshness warnings
**Solution:** Some data sources update weekly/monthly (FRED, Shiller). Adjust thresholds in `data_source_registry.py` if needed.

### Issue: Workflow times out (>30 min)
**Solution:** Increase `timeout-minutes` in workflow file. Check for API issues or infinite loops in update script.

---

## Related Documentation

- **Data Quality Guide:** `docs/guides/data-quality-guide.md`
- **Data Source Registry:** `finbot/services/data_quality/data_source_registry.py`
- **Update Script:** `scripts/update_daily.py`
- **Priority 7 Plan:** `docs/planning/priority-7-implementation-plan.md`

---

## Next Steps

1. ✅ Create workflow file (`.github/workflows/scheduled-update.yml`)
2. ⬜ **Add GitHub Secrets** (user action required)
3. ⬜ **Enable workflow** on GitHub Actions tab
4. ⬜ **Test manual run** to verify setup
5. ⬜ Monitor first scheduled run (next day at 6:00 AM UTC)

---

**Status:** Workflow created, awaiting user setup of GitHub Secrets.
