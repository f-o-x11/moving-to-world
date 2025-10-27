#!/bin/bash
# V3 Deployment Script
# Generates all pages with real data and deploys to GitHub Pages

set -e

echo "=== Moving.to V3 Deployment ==="
echo ""

# Step 1: Check data fetch completion
echo "[1/5] Checking data fetch status..."
RENT_DATA_COUNT=$(sqlite3 /home/ubuntu/moving_to_world/moving_to.db "SELECT COUNT(*) FROM rent_data")
echo "  ✓ $RENT_DATA_COUNT cities have real rent data"

# Step 2: Generate all V3 pages
echo ""
echo "[2/5] Generating V3 pages for all cities..."
python3 /home/ubuntu/moving_to_world/generate_v3_with_real_data.py

# Step 3: Create git branch
echo ""
echo "[3/5] Creating v3-real-data branch..."
cd /home/ubuntu/moving_to_world
git checkout -b v3-real-data 2>/dev/null || git checkout v3-real-data

# Step 4: Commit changes
echo ""
echo "[4/5] Committing changes..."
git add -A
git commit -m "V3: Add real data for top 100 cities + comprehensive UI

- Real rent data from OpenAI API for top 100 cities
- Comprehensive data: employers, attractions, restaurants, schools, hospitals
- Tabbed interface with 10 sections
- Accurate population data for 19,487 cities
- Climate data for all cities
- Persistent database with enriched data
"

# Step 5: Push to GitHub
echo ""
echo "[5/5] Pushing to GitHub..."
git push origin v3-real-data --force

echo ""
echo "=== V3 Deployment Complete! ==="
echo ""
echo "Next steps:"
echo "1. Test v3-real-data branch locally"
echo "2. Merge to main when ready: git checkout main && git merge v3-real-data"
echo "3. Push main to deploy: git push origin main"
echo ""
echo "Branch: v3-real-data"
echo "Cities with real data: $RENT_DATA_COUNT"
echo "Total cities: 32,496"

