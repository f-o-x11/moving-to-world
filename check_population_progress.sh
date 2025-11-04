#!/bin/bash
# Check population progress

echo "=============================================="
echo "COMPREHENSIVE DATA POPULATION - PROGRESS"
echo "=============================================="
echo ""

# Check if process is running
if ps aux | grep -v grep | grep "populate_all_cities.py" > /dev/null; then
    echo "✅ Process Status: RUNNING"
    PID=$(ps aux | grep -v grep | grep "populate_all_cities.py" | awk '{print $2}')
    echo "   PID: $PID"
else
    echo "⚠️  Process Status: NOT RUNNING"
fi

echo ""

# Check database progress
cd /home/ubuntu/moving_to_world
TOTAL=$(sqlite3 moving_to.db "SELECT COUNT(*) FROM city_enriched_data")
PERCENTAGE=$(echo "scale=2; ($TOTAL / 32496) * 100" | bc)

echo "📊 Database Progress:"
echo "   Cities with enriched data: $TOTAL / 32,496"
echo "   Coverage: $PERCENTAGE%"

echo ""

# Check recent additions
echo "🆕 Recent Additions (last 10):"
sqlite3 moving_to.db "
SELECT '   ' || c.name || ', ' || c.country || ' (' || substr(e.updated_at, 12, 8) || ')'
FROM cities c
JOIN city_enriched_data e ON c.id = e.city_id
ORDER BY e.updated_at DESC
LIMIT 10
"

echo ""

# Estimate completion
if [ -f population_progress.json ]; then
    echo "📈 Progress File:"
    cat population_progress.json | python3 -m json.tool 2>/dev/null || cat population_progress.json
    echo ""
fi

# Calculate ETA
REMAINING=$((32496 - TOTAL))
if [ $REMAINING -gt 0 ]; then
    # Assume 3 seconds per city
    SECONDS_LEFT=$((REMAINING * 3))
    HOURS_LEFT=$(echo "scale=1; $SECONDS_LEFT / 3600" | bc)
    echo "⏱️  Estimated Time Remaining: $HOURS_LEFT hours"
    echo "   ($REMAINING cities remaining)"
fi

echo ""
echo "=============================================="

# Show last few log lines
if [ -f population.log ]; then
    echo ""
    echo "📝 Recent Log Output (last 20 lines):"
    tail -20 population.log
fi

