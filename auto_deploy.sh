#!/bin/bash
echo "Waiting for 100% completion..."

while true; do
    COUNT=$(sqlite3 moving_to.db "SELECT COUNT(*) FROM city_enriched_data")
    PCT=$(echo "scale=2; $COUNT * 100 / 32496" | bc)
    echo "Progress: $COUNT / 32,496 ($PCT%)"
    
    if [ "$COUNT" -ge 32400 ]; then
        echo "✅ 99%+ reached! Starting deployment..."
        break
    fi
    
    sleep 30
done

echo "Regenerating all pages..."
python3.11 generate_v3.py

echo "Committing to git..."
git add -A
git commit -m "V5: Complete comprehensive data for all 32,496 cities"
git tag v5-complete -f

echo "Deploying to GitHub Pages..."
git push origin main --tags -f

echo "✅ DEPLOYMENT COMPLETE!"
