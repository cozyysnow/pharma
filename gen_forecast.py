import csv, random, math
from datetime import datetime, timedelta

random.seed(123)

with open(r'c:\Users\kc\Downloads\pharma\pharmacy_stockout_dataset_pack\demand_sales_daily.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    med_demand = {}
    for row in reader:
        mid = row['medicine_id']
        if row['date'] >= '2025-10-01':
            if mid not in med_demand:
                med_demand[mid] = []
            med_demand[mid].append({'date': row['date'], 'units_sold': int(row['units_sold'])})

def gen_forecast(mid, history):
    if not history:
        return []
    avg = sum(d['units_sold'] for d in history) / len(history)
    points = []
    for d in history[-60:]:
        points.append('    { date: "' + d['date'] + '", predicted_demand: ' + str(d['units_sold']) + ', lower_bound: ' + str(d['units_sold']) + ', upper_bound: ' + str(d['units_sold']) + ', is_forecast: false }')
    base_date = datetime(2026, 1, 1)
    for i in range(30):
        date = (base_date + timedelta(days=i)).strftime('%Y-%m-%d')
        noise = random.gauss(0, avg * 0.15)
        pred = max(0, round(avg + noise))
        lb = max(0, round(pred - avg * 0.25))
        ub = round(pred + avg * 0.25)
        points.append('    { date: "' + date + '", predicted_demand: ' + str(pred) + ', lower_bound: ' + str(lb) + ', upper_bound: ' + str(ub) + ', is_forecast: true }')
    return points

lines = []
fid = 1
for mid in ['MED001', 'MED003', 'MED009', 'MED020', 'MED033', 'MED034', 'MED079', 'MED062']:
    history = med_demand.get(mid, [])
    if not history:
        continue
    pts = gen_forecast(mid, history)
    if not pts:
        continue
    pts_str = '[\n' + ',\n'.join(pts) + '\n  ]'
    lines.append('  { id: "FC' + f'{fid:04d}' + '", medicine_id: "' + mid + '", model: "XGBoost", horizon_days: 30, run_date: "2025-12-31T23:00:00Z", points: ' + pts_str + ', mae: ' + str(round(random.uniform(3, 12), 2)) + ', rmse: ' + str(round(random.uniform(5, 18), 2)) + ', mape: ' + str(round(random.uniform(0.05, 0.18), 3)) + ' }')
    fid += 1

with open(r'c:\Users\kc\Downloads\pharma\forecast_data.txt', 'w', encoding='utf-8') as out:
    out.write(',\n'.join(lines))
print('Done:', fid-1, 'forecasts')
