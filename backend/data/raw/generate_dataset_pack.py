#!/usr/bin/env python3
"""
Pharmacy Stock-Out Prediction - synthetic dataset pack generator + validator.
Run:  python generate_dataset_pack.py [output_dir]
Everything transactional is SYNTHETIC. See README.md for limitations.
"""
import os, sys, math
from collections import defaultdict, deque
import numpy as np
import pandas as pd

SEED = 20260101
OUT = sys.argv[1] if len(sys.argv) > 1 else "pharmacy_stockout_dataset_pack"
START, END = pd.Timestamp("2021-01-01"), pd.Timestamp("2025-12-31")
HORIZON = 7
N_DAYS = (END - START).days + 1                     # 1826
T = N_DAYS + HORIZON                                # simulated days incl. 7-day look-ahead
DATES = pd.date_range(START, periods=T, freq="D")
rng = np.random.default_rng(SEED)

# ---------------------------------------------------------------- categories
CATS = [  # id, name, description, seasonal peak month, seasonal amplitude, demand multiplier
 ("CAT01", "Analgesics & Antipyretics", "Pain and fever relief", 1, 0.10, 1.8),
 ("CAT02", "Antibiotics", "Antibacterial agents", 1, 0.15, 1.0),
 ("CAT03", "Cardiovascular", "Antihypertensives, lipid-lowering, antiplatelets, diuretics", 1, 0.03, 1.5),
 ("CAT04", "Antidiabetics", "Glucose-lowering agents and insulin", 1, 0.03, 1.4),
 ("CAT05", "Gastrointestinal", "Acid suppression, antiemetics, rehydration", 7, 0.20, 1.3),
 ("CAT06", "Respiratory & Allergy", "Antihistamines, asthma and cough products", 12, 0.30, 1.0),
 ("CAT07", "Antifungals & Antiparasitics", "Antifungal, anthelmintic and antimalarial agents", 8, 0.25, 0.5),
 ("CAT08", "Neurology & Psychiatry", "Anticonvulsants, antidepressants, anxiolytics", 1, 0.03, 0.8),
 ("CAT09", "Vitamins & Supplements", "Vitamins, minerals and nutritional supplements", 12, 0.08, 1.3),
 ("CAT10", "Dermatology & Topicals", "Topical anti-infectives, steroids, antiseptics", 7, 0.15, 1.0),
 ("CAT11", "Endocrine, Urology & Others", "Thyroid, corticosteroids, urology, gout, contraception", 1, 0.03, 0.7),
]
V, U = "VERIFIED_STANDARD_REFERENCE", "UNVERIFIED_REQUIRES_REVIEW"
FDC = "Fixed-dose combination: strength/ratio varies by market and manufacturer; confirm against product label before use."
# name, active ingredients (salt form), strength, dosage form, category no, status, note
MEDS = [
 # CAT01
 ("Paracetamol","Paracetamol","500 mg","Tablet",1,V,""),
 ("Paracetamol","Paracetamol","120 mg/5 mL","Oral Suspension",1,V,""),
 ("Ibuprofen","Ibuprofen","400 mg","Tablet",1,V,""),
 ("Diclofenac","Diclofenac Sodium","50 mg","Gastro-Resistant Tablet",1,V,""),
 ("Naproxen","Naproxen","250 mg","Tablet",1,V,""),
 ("Aceclofenac","Aceclofenac","100 mg","Tablet",1,V,""),
 ("Tramadol","Tramadol Hydrochloride","50 mg","Capsule",1,V,""),
 ("Paracetamol + Ibuprofen","Paracetamol; Ibuprofen","UNVERIFIED","Tablet",1,U,FDC+" Indicative only: 325 mg + 400 mg."),
 # CAT02
 ("Amoxicillin","Amoxicillin Trihydrate","500 mg","Capsule",2,V,""),
 ("Amoxicillin + Clavulanic Acid","Amoxicillin Trihydrate; Potassium Clavulanate","500 mg + 125 mg","Tablet",2,V,"Strengths expressed as amoxicillin and clavulanic acid."),
 ("Azithromycin","Azithromycin Dihydrate","500 mg","Tablet",2,V,""),
 ("Ciprofloxacin","Ciprofloxacin Hydrochloride","500 mg","Tablet",2,V,""),
 ("Doxycycline","Doxycycline Hyclate","100 mg","Capsule",2,V,""),
 ("Cefixime","Cefixime Trihydrate","200 mg","Tablet",2,V,""),
 ("Metronidazole","Metronidazole","400 mg","Tablet",2,V,""),
 ("Cotrimoxazole","Sulfamethoxazole; Trimethoprim","400 mg + 80 mg","Tablet",2,V,""),
 ("Ofloxacin + Ornidazole","Ofloxacin; Ornidazole","UNVERIFIED","Tablet",2,U,FDC+" Indicative only: 200 mg + 500 mg."),
 # CAT03
 ("Amlodipine","Amlodipine Besilate","5 mg","Tablet",3,V,"Strength expressed as amlodipine."),
 ("Atenolol","Atenolol","50 mg","Tablet",3,V,""),
 ("Losartan","Losartan Potassium","50 mg","Tablet",3,V,""),
 ("Telmisartan","Telmisartan","40 mg","Tablet",3,V,""),
 ("Atorvastatin","Atorvastatin Calcium","10 mg","Tablet",3,V,"Strength expressed as atorvastatin."),
 ("Clopidogrel","Clopidogrel Bisulfate","75 mg","Tablet",3,V,"Strength expressed as clopidogrel."),
 ("Aspirin","Aspirin","75 mg","Enteric-Coated Tablet",3,V,""),
 ("Furosemide","Furosemide","40 mg","Tablet",3,V,""),
 ("Telmisartan + Amlodipine","Telmisartan; Amlodipine Besilate","UNVERIFIED","Tablet",3,U,FDC+" Indicative only: 40 mg + 5 mg."),
 # CAT04
 ("Metformin","Metformin Hydrochloride","500 mg","Tablet",4,V,""),
 ("Glimepiride","Glimepiride","2 mg","Tablet",4,V,""),
 ("Gliclazide","Gliclazide","80 mg","Tablet",4,V,""),
 ("Sitagliptin","Sitagliptin Phosphate Monohydrate","100 mg","Tablet",4,V,"Strength expressed as sitagliptin."),
 ("Pioglitazone","Pioglitazone Hydrochloride","15 mg","Tablet",4,V,"Strength expressed as pioglitazone."),
 ("Empagliflozin","Empagliflozin","10 mg","Tablet",4,V,""),
 ("Insulin Human (Regular)","Insulin Human (recombinant, soluble)","100 IU/mL (10 mL vial)","Injection",4,V,"Requires refrigeration."),
 ("Metformin + Glimepiride","Metformin Hydrochloride; Glimepiride","UNVERIFIED","Tablet",4,U,FDC+" Indicative only: 500 mg + 1 mg."),
 # CAT05
 ("Omeprazole","Omeprazole","20 mg","Capsule",5,V,""),
 ("Pantoprazole","Pantoprazole Sodium","40 mg","Gastro-Resistant Tablet",5,V,"Strength expressed as pantoprazole."),
 ("Rabeprazole","Rabeprazole Sodium","20 mg","Gastro-Resistant Tablet",5,V,""),
 ("Famotidine","Famotidine","20 mg","Tablet",5,V,""),
 ("Domperidone","Domperidone","10 mg","Tablet",5,V,""),
 ("Ondansetron","Ondansetron Hydrochloride Dihydrate","4 mg","Tablet",5,V,"Strength expressed as ondansetron."),
 ("Oral Rehydration Salts (WHO low-osmolarity)","Sodium Chloride; Glucose Anhydrous; Potassium Chloride; Trisodium Citrate Dihydrate","2.6 g + 13.5 g + 1.5 g + 2.9 g per litre (20.5 g sachet)","Powder for Oral Solution",5,V,"WHO/UNICEF low-osmolarity formula."),
 ("Pantoprazole + Domperidone","Pantoprazole Sodium; Domperidone","UNVERIFIED","Capsule",5,U,FDC+" Indicative only: 40 mg + 30 mg (SR)."),
 # CAT06
 ("Cetirizine","Cetirizine Dihydrochloride","10 mg","Tablet",6,V,""),
 ("Levocetirizine","Levocetirizine Dihydrochloride","5 mg","Tablet",6,V,""),
 ("Montelukast","Montelukast Sodium","10 mg","Tablet",6,V,"Strength expressed as montelukast."),
 ("Salbutamol","Salbutamol Sulfate","100 mcg/actuation","Metered-Dose Inhaler",6,V,"Strength expressed as salbutamol."),
 ("Budesonide","Budesonide","200 mcg/actuation","Metered-Dose Inhaler",6,V,""),
 ("Fexofenadine","Fexofenadine Hydrochloride","120 mg","Tablet",6,V,""),
 ("Dextromethorphan","Dextromethorphan Hydrobromide","15 mg/5 mL","Syrup",6,V,""),
 ("Levocetirizine + Montelukast","Levocetirizine Dihydrochloride; Montelukast Sodium","UNVERIFIED","Tablet",6,U,FDC+" Indicative only: 5 mg + 10 mg."),
 # CAT07
 ("Fluconazole","Fluconazole","150 mg","Capsule",7,V,""),
 ("Clotrimazole","Clotrimazole","1% w/w","Cream",7,V,""),
 ("Terbinafine","Terbinafine Hydrochloride","250 mg","Tablet",7,V,"Strength expressed as terbinafine."),
 ("Albendazole","Albendazole","400 mg","Chewable Tablet",7,V,""),
 ("Ivermectin","Ivermectin","12 mg","Tablet",7,V,""),
 ("Artemether + Lumefantrine","Artemether; Lumefantrine","20 mg + 120 mg","Tablet",7,V,"WHO-listed antimalarial combination."),
 ("Itraconazole","Itraconazole","100 mg","Capsule",7,V,""),
 # CAT08
 ("Gabapentin","Gabapentin","300 mg","Capsule",8,V,""),
 ("Levetiracetam","Levetiracetam","500 mg","Tablet",8,V,""),
 ("Sertraline","Sertraline Hydrochloride","50 mg","Tablet",8,V,"Strength expressed as sertraline."),
 ("Escitalopram","Escitalopram Oxalate","10 mg","Tablet",8,V,"Strength expressed as escitalopram."),
 ("Alprazolam","Alprazolam","0.25 mg","Tablet",8,V,""),
 ("Amitriptyline","Amitriptyline Hydrochloride","10 mg","Tablet",8,V,""),
 ("Carbamazepine","Carbamazepine","200 mg","Tablet",8,V,""),
 ("Clonazepam","Clonazepam","0.5 mg","Tablet",8,V,""),
 # CAT09
 ("Folic Acid","Folic Acid","5 mg","Tablet",9,V,""),
 ("Cholecalciferol (Vitamin D3)","Cholecalciferol","60,000 IU","Capsule",9,V,""),
 ("Cyanocobalamin (Vitamin B12)","Cyanocobalamin","500 mcg","Tablet",9,V,""),
 ("Ascorbic Acid (Vitamin C)","Ascorbic Acid","500 mg","Chewable Tablet",9,V,""),
 ("Zinc Sulfate","Zinc Sulfate Monohydrate","20 mg (as elemental zinc)","Dispersible Tablet",9,V,"WHO-recommended paediatric diarrhoea zinc dose form."),
 ("Ferrous Sulfate","Ferrous Sulfate (dried)","200 mg (approx. 65 mg elemental iron)","Tablet",9,V,""),
 ("Multivitamin + Multimineral","UNVERIFIED - composition varies by manufacturer","UNVERIFIED","Tablet",9,U,"Composition is product-specific; no standard formulation exists."),
 # CAT10
 ("Betamethasone Valerate","Betamethasone Valerate","0.1% w/w","Cream",10,V,""),
 ("Mupirocin","Mupirocin","2% w/w","Ointment",10,V,""),
 ("Hydrocortisone","Hydrocortisone","1% w/w","Cream",10,V,""),
 ("Povidone-Iodine","Povidone-Iodine","5% w/v","Topical Solution",10,V,""),
 ("Permethrin","Permethrin","5% w/w","Cream",10,V,""),
 ("Clindamycin","Clindamycin Phosphate","1% w/w","Gel",10,V,"Strength expressed as clindamycin."),
 # CAT11
 ("Levothyroxine","Levothyroxine Sodium","50 mcg","Tablet",11,V,""),
 ("Prednisolone","Prednisolone","10 mg","Tablet",11,V,""),
 ("Dexamethasone","Dexamethasone","4 mg","Tablet",11,V,""),
 ("Tamsulosin","Tamsulosin Hydrochloride","0.4 mg","Modified-Release Capsule",11,V,""),
 ("Finasteride","Finasteride","5 mg","Tablet",11,V,""),
 ("Allopurinol","Allopurinol","100 mg","Tablet",11,V,""),
 ("Levonorgestrel","Levonorgestrel","1.5 mg","Tablet",11,V,"Emergency contraceptive."),
]
assert len(MEDS) == 85 and len(CATS) == 11

# ---------------------------------------------------------------- suppliers (fictional)
SUP_NAMES = [
 ("Aravali Pharma Distributors","Wholesaler","Sonipat","Haryana"),
 ("Yamuna Healthcare Supplies","Wholesaler","Panipat","Haryana"),
 ("Kurukshetra Medico Traders","Regional Distributor","Kurukshetra","Haryana"),
 ("Capital Drug House","Wholesaler","New Delhi","Delhi"),
 ("Northern Lifecare Logistics","Regional Distributor","Gurugram","Haryana"),
 ("Satluj Generics Direct","Manufacturer-Direct","Ludhiana","Punjab"),
 ("Himalaya Valley Pharma Supply","Manufacturer-Direct","Baddi","Himachal Pradesh"),
 ("Doab Medical Agencies","Regional Distributor","Meerut","Uttar Pradesh"),
 ("Ganga Plains Pharma","Wholesaler","Ghaziabad","Uttar Pradesh"),
 ("Rajputana Drug Distributors","Wholesaler","Jaipur","Rajasthan"),
 ("Sapphire Biologicals Supply","Specialist (Cold Chain)","Chandigarh","Chandigarh"),
 ("Metro Rx Wholesale","Wholesaler","Faridabad","Haryana"),
 ("Trident Pharma Logistics","Regional Distributor","Rohtak","Haryana"),
 ("Greenfield Generic Direct","Manufacturer-Direct","Panchkula","Haryana"),
 ("Prime Meds Cooperative","Cooperative","Karnal","Haryana"),
]
sup_rows = []
for i, (nm, ty, city, st) in enumerate(SUP_NAMES, 1):
    sup_rows.append(dict(
        supplier_id=f"SUP{i:02d}", supplier_name=nm, supplier_type=ty, city=city, state=st,
        lead_time_mean_days=round(float(rng.uniform(2, 6)), 1),
        lead_time_sd_days=round(float(rng.uniform(0.5, 1.8)), 1),
        on_time_probability=round(float(rng.uniform(0.80, 0.97)), 2),
        full_fill_probability=round(float(rng.uniform(0.84, 0.97)), 2),
        payment_terms_days=int(rng.choice([15, 30, 45])),
        is_synthetic=1))
suppliers = pd.DataFrame(sup_rows)
SUP = suppliers.set_index("supplier_id")

# disruption events
dis_rows = []
for sid in suppliers.supplier_id:
    for _ in range(int(rng.integers(2, 5))):
        s = START + pd.Timedelta(days=int(rng.integers(0, N_DAYS - 25)))
        ln = int(rng.integers(7, 22))
        dis_rows.append(dict(supplier_id=sid, start_date=s.date().isoformat(),
                             end_date=(s + pd.Timedelta(days=ln - 1)).date().isoformat(),
                             extra_lead_time_days=int(rng.integers(3, 9)),
                             full_fill_probability_multiplier=round(float(rng.uniform(0.4, 0.7)), 2)))
disr = pd.DataFrame(dis_rows).sort_values(["start_date", "supplier_id"]).reset_index(drop=True)
disr.insert(0, "event_id", [f"DIS{i:03d}" for i in range(1, len(disr) + 1)])
disr_idx = defaultdict(list)       # supplier -> list of (start_idx, end_idx, extra, mult)
for r in disr.itertuples():
    disr_idx[r.supplier_id].append(((pd.Timestamp(r.start_date) - START).days, (pd.Timestamp(r.end_date) - START).days,
                                    r.extra_lead_time_days, r.full_fill_probability_multiplier))

def disruption(sid, t):
    for a, b, e, m in disr_idx[sid]:
        if a <= t <= b:
            return e, m
    return 0, 1.0

# ---------------------------------------------------------------- medicines
order_sup = list(range(85)); rng.shuffle(order_sup)
prim_of = {}
for k, mi in enumerate(order_sup):
    prim_of[mi] = f"SUP{(k % 15) + 1:02d}"
# cold chain preference for insulin
ins = [i for i, m in enumerate(MEDS) if m[0].startswith("Insulin")][0]
prim_of[ins] = "SUP11"

def is_discrete(form): return ("Tablet" in form) or ("Capsule" in form)
def uom(form):
    if "Tablet" in form: return "tablet"
    if "Capsule" in form: return "capsule"
    return {"Cream": "tube", "Ointment": "tube", "Gel": "tube", "Injection": "vial", "Metered-Dose Inhaler": "inhaler",
            "Powder for Oral Solution": "sachet"}.get(form, "bottle")
def route(form):
    if form in ("Cream", "Ointment", "Gel", "Topical Solution"): return "Topical"
    if form == "Injection": return "Parenteral"
    if "Inhaler" in form: return "Inhalation"
    return "Oral"

med_rows = []
for i, (nm, ing, st, form, cn, status, note) in enumerate(MEDS):
    u = uom(form)
    cost = {"tablet": rng.uniform(0.4, 14), "capsule": rng.uniform(0.8, 12), "tube": rng.uniform(25, 90),
            "vial": rng.uniform(120, 220), "inhaler": rng.uniform(110, 260), "sachet": rng.uniform(8, 20),
            "bottle": rng.uniform(25, 85)}[u]
    cost = round(float(cost), 2)
    med_rows.append(dict(
        medicine_id=f"MED{i+1:03d}", generic_name=nm, active_ingredients=ing, strength=st, dosage_form=form,
        route=route(form), category_id=CATS[cn - 1][0], primary_supplier_id=prim_of[i],
        unit_of_measure=u, pack_size=10 if is_discrete(form) else 1,
        storage_condition="Refrigerated (2-8 C)" if nm.startswith("Insulin") else "Room temperature",
        unit_cost_inr_2021=cost, unit_price_inr_2021=round(cost * float(rng.uniform(1.15, 1.4)), 2),
        composition_status=status,
        composition_note=note if note else ("Standard INN/pharmacopoeial composition." if status == V else ""),
        price_is_synthetic=1))
medicines = pd.DataFrame(med_rows)
medicines.insert(2, "display_name", medicines.generic_name + " " + medicines.strength.where(
    medicines.strength != "UNVERIFIED", "[strength unverified]") + " " + medicines.dosage_form)

# secondary suppliers
sec_rows = []
for i, m in medicines.iterrows():
    others = [s for s in suppliers.supplier_id if s != m.primary_supplier_id]
    sec = m.primary_supplier_id if False else str(rng.choice(others))
    sec_rows.append(dict(medicine_id=m.medicine_id, supplier_id=m.primary_supplier_id, supplier_role="Primary", order_share=0.85))
    sec_rows.append(dict(medicine_id=m.medicine_id, supplier_id=sec, supplier_role="Secondary", order_share=0.15))
med_sup = pd.DataFrame(sec_rows)
SEC = med_sup[med_sup.supplier_role == "Secondary"].set_index("medicine_id").supplier_id.to_dict()

categories = pd.DataFrame([dict(category_id=c[0], category_name=c[1], description=c[2]) for c in CATS])

# ---------------------------------------------------------------- simulation
doy = DATES.dayofyear.values
month_f = (doy - 0.5) / 365.25 * 12 + 0.5
dow_f = np.array([1.10, 1.00, 1.00, 1.00, 1.05, 0.95, 0.70])[DATES.dayofweek.values]
years_f = (np.arange(T)) / 365.25
OVR = {"Oral Rehydration Salts (WHO low-osmolarity)": (6, 0.5), "Cholecalciferol (Vitamin D3)": (12, 0.15),
       "Dextromethorphan": (12, 0.40), "Zinc Sulfate": (7, 0.25)}
price_year_f = (1.04 ** (DATES.year.values - 2021))

orders, inv_rec = [], []
for i, m in enumerate(MEDS):
    cat = CATS[m[4] - 1]
    peak, amp = OVR.get(m[0], (cat[3], cat[4]))
    disc = is_discrete(m[3])
    base = (40.0 if disc else 6.0) * cat[5] * float(rng.lognormal(0, 0.45))
    growth = float(rng.normal(0.04, 0.03))
    seas = 1 + amp * np.cos(2 * np.pi * (month_f - peak) / 12)
    spike = np.ones(T); t = 0
    while t < T:
        if rng.random() < 0.003:
            L = int(rng.integers(4, 11)); spike[t:t + L] = rng.uniform(1.4, 2.2); t += L
        t += 1
    mean = base * seas * dow_f * (1 + growth * years_f) * spike
    lam = mean * rng.gamma(8.0, 1 / 8.0, size=T)
    demand = rng.poisson(lam).astype(int)

    pack = 10 if disc else 1
    sid_p, sid_s = prim_of[i], SEC[f"MED{i+1:03d}"]
    Lmean = SUP.loc[sid_p, "lead_time_mean_days"]
    ss_days = float(rng.uniform(0.0, 2.5)); cycle = float(rng.uniform(7, 21))
    hist = deque([base] * 28, maxlen=28)
    stock = int(base * (Lmean + ss_days + cycle / 2)); on_order = 0
    pipe = defaultdict(list)
    med_id = f"MED{i+1:03d}"
    for t in range(T):
        opening = stock
        arr = pipe.pop(t, [])
        recv = sum(a[1] for a in arr)
        for a in arr: on_order -= a[0]
        avail = opening + recv
        d = int(demand[t]); sold = min(d, avail); lost = d - sold
        closing = avail - sold; waste = 0
        if closing > 50 and rng.random() < 0.004:
            waste = int(closing * rng.uniform(0.01, 0.05)); closing -= waste
        hist.append(d)
        rate = float(np.mean(hist))
        rop = int(round(rate * (Lmean + ss_days))); S = int(round(rop + rate * cycle))
        pos = closing + on_order; ordered_today = 0
        if pos <= rop:
            qty = int(math.ceil((S - pos) / pack) * pack)
            qty = max(qty, pack)
            sid = sid_p if rng.random() < 0.85 else sid_s
            sp = SUP.loc[sid]
            ex, mult = disruption(sid, t)
            lt = max(1, int(round(rng.normal(sp.lead_time_mean_days, sp.lead_time_sd_days))))
            if rng.random() > sp.on_time_probability: lt += int(rng.integers(2, 7))
            lt += ex
            if rng.random() < sp.full_fill_probability * mult: got = qty
            else: got = int(math.floor(qty * rng.uniform(0.4, 0.95) / pack) * pack)
            got = max(got, pack) if got > 0 else pack
            exp_lt = int(round(sp.lead_time_mean_days))
            pipe[t + lt].append((qty, got)); on_order += qty; ordered_today = qty
            if t < N_DAYS:
                orders.append(dict(med_idx=i, medicine_id=med_id, supplier_id=sid, order_idx=t, exp_idx=t + exp_lt,
                                   act_idx=t + lt, quantity_ordered=qty, got=got))
        stock = closing
        if t < N_DAYS or True:
            inv_rec.append((i, t, opening, recv, sold, waste, closing, on_order, ordered_today, rop, S, d, lost))

cols = ["mi", "t", "opening_stock", "units_received", "units_sold", "wastage_units", "closing_stock", "on_order_units",
        "units_ordered_today", "reorder_point", "order_up_to_level", "units_demanded", "lost_sales_units"]
sim = pd.DataFrame(inv_rec, columns=cols)
sim["stockout_flag"] = (sim.lost_sales_units > 0).astype(int)
sim = sim.sort_values(["mi", "t"]).reset_index(drop=True)

# label: any stock-out on t+1..t+7 (look-ahead rows exist for 2026-01-01..07)
sim["stockout_next_7d"] = 0
for mi, g in sim.groupby("mi"):
    f = g.stockout_flag.values; n = len(f)
    lab = np.zeros(n, dtype=int)
    for k in range(1, HORIZON + 1):
        lab[:n - k] |= f[k:]
    sim.loc[g.index, "stockout_next_7d"] = lab

look = sim[sim.t >= N_DAYS][["mi", "t", "stockout_flag"]].copy()
sim = sim[sim.t < N_DAYS].reset_index(drop=True)
sim["medicine_id"] = sim.mi.map(lambda x: f"MED{x+1:03d}")
sim["date"] = DATES[sim.t.values].strftime("%Y-%m-%d")
sim["record_id"] = [f"REC{k:06d}" for k in range(1, len(sim) + 1)]
look["medicine_id"] = look.mi.map(lambda x: f"MED{x+1:03d}")
look["date"] = DATES[look.t.values].strftime("%Y-%m-%d")
lookahead = look[["medicine_id", "date", "stockout_flag"]].reset_index(drop=True)

# ---------------------------------------------------------------- derived tables
price_idx = lambda t: price_year_f[t]
sim["unit_price_inr"] = (sim.medicine_id.map(medicines.set_index("medicine_id").unit_price_inr_2021) * price_year_f[sim.t.values]).round(2)
sim["sales_revenue_inr"] = (sim.units_sold * sim.unit_price_inr).round(2)

inventory = sim[["record_id", "date", "medicine_id", "opening_stock", "units_received", "units_sold", "wastage_units",
                 "closing_stock", "units_ordered_today", "on_order_units", "reorder_point", "order_up_to_level"]]
demand_sales = sim[["record_id", "date", "medicine_id", "units_demanded", "units_sold", "lost_sales_units",
                    "stockout_flag", "unit_price_inr", "sales_revenue_inr"]]

od = pd.DataFrame(orders).sort_values(["order_idx", "medicine_id"]).reset_index(drop=True)
od["order_id"] = [f"PO{k:07d}" for k in range(1, len(od) + 1)]
od["order_date"] = DATES[od.order_idx.values].strftime("%Y-%m-%d")
od["expected_delivery_date"] = DATES[od.exp_idx.values].strftime("%Y-%m-%d")
done = od.act_idx < N_DAYS
od["actual_delivery_date"] = pd.Series(DATES[np.minimum(od.act_idx.values, T-1)].strftime("%Y-%m-%d"), index=od.index).where(done)
od["quantity_received"] = od.got.where(done).astype("Int64")
od["lead_time_days"] = (od.act_idx - od.order_idx).where(done).astype("Int64")
od["status"] = np.where(~done, "In_Transit_At_Period_End", np.where(od.got < od.quantity_ordered, "Partially_Received", "Received"))
od["unit_cost_inr"] = (od.medicine_id.map(medicines.set_index("medicine_id").unit_cost_inr_2021) *
                       price_year_f[od.order_idx.values]).round(2)
od["order_value_inr"] = (od.quantity_ordered * od.unit_cost_inr).round(2)
replen = od[["order_id", "medicine_id", "supplier_id", "order_date", "expected_delivery_date", "actual_delivery_date",
             "lead_time_days", "quantity_ordered", "quantity_received", "status", "unit_cost_inr", "order_value_inr"]]

# modelling table
ds = sim.copy()
g = ds.groupby("medicine_id")
ds["sales_7d_avg"] = g.units_sold.transform(lambda s: s.rolling(7, min_periods=1).mean()).round(3)
ds["sales_30d_avg"] = g.units_sold.transform(lambda s: s.rolling(30, min_periods=1).mean()).round(3)
ds["stockout_days_last_30d"] = g.stockout_flag.transform(lambda s: s.rolling(30, min_periods=1).sum()).astype(int)
ds["days_of_cover"] = (ds.closing_stock / ds.sales_30d_avg.clip(lower=0.1)).clip(upper=365).round(2)
ds["stock_position_cover_days"] = ((ds.closing_stock + ds.on_order_units) / ds.sales_30d_avg.clip(lower=0.1)).clip(upper=365).round(2)
lastr = np.where(ds.units_received > 0, ds.t, np.nan)
ds["_lr"] = lastr
ds["_lr"] = ds.groupby("medicine_id")._lr.ffill()
ds["days_since_last_receipt"] = (ds.t - ds._lr).fillna(ds.t + 1).clip(upper=365).astype(int)
med_i = medicines.set_index("medicine_id")
ds["category_id"] = ds.medicine_id.map(med_i.category_id)
ds["supplier_id"] = ds.medicine_id.map(med_i.primary_supplier_id)
ds["supplier_lead_time_mean_days"] = ds.supplier_id.map(SUP.lead_time_mean_days)
ds["supplier_full_fill_probability"] = ds.supplier_id.map(SUP.full_fill_probability)
ds["supplier_disruption_active"] = [int(disruption(s, t)[0] > 0) for s, t in zip(ds.supplier_id, ds.t)]
dts = pd.to_datetime(ds.date)
ds["year"] = dts.dt.year; ds["month"] = dts.dt.month; ds["day_of_week"] = dts.dt.dayofweek
ds["is_weekend"] = (ds.day_of_week >= 5).astype(int)
ds["season"] = ds.month.map(lambda m: "winter" if m in (12, 1, 2) else "summer" if m <= 6 else "monsoon" if m <= 9 else "post_monsoon")
model = ds[["record_id", "date", "medicine_id", "category_id", "supplier_id", "year", "month", "day_of_week", "is_weekend", "season",
            "closing_stock", "on_order_units", "reorder_point", "units_demanded", "units_sold", "sales_7d_avg", "sales_30d_avg",
            "days_of_cover", "stock_position_cover_days", "days_since_last_receipt", "stockout_days_last_30d",
            "supplier_lead_time_mean_days", "supplier_full_fill_probability", "supplier_disruption_active",
            "unit_price_inr", "stockout_flag", "stockout_next_7d"]].rename(columns={"stockout_flag": "stockout_today"})

calendar = pd.DataFrame({"date": DATES[:N_DAYS].strftime("%Y-%m-%d")})
cd = DATES[:N_DAYS]
calendar["year"] = cd.year; calendar["month"] = cd.month; calendar["day_of_week"] = cd.dayofweek
calendar["is_weekend"] = (cd.dayofweek >= 5).astype(int)
calendar["season"] = [("winter" if m in (12, 1, 2) else "summer" if m <= 6 else "monsoon" if m <= 9 else "post_monsoon") for m in cd.month]

# ---------------------------------------------------------------- write
os.makedirs(OUT, exist_ok=True)
files = {
 "categories.csv": categories, "suppliers.csv": suppliers, "supplier_disruption_events.csv": disr,
 "medicines.csv": medicines, "medicine_suppliers.csv": med_sup, "calendar.csv": calendar,
 "inventory_daily.csv": inventory, "demand_sales_daily.csv": demand_sales,
 "replenishment_orders.csv": replen, "stockout_label_lookahead_2026.csv": lookahead,
 "stockout_prediction_dataset.csv": model,
}
for fn, df in files.items():
    df.to_csv(os.path.join(OUT, fn), index=False)

DD = {
 "categories.csv": {"category_id": "PK, CATnn", "category_name": "Therapeutic category", "description": "Category description"},
 "suppliers.csv": {"supplier_id": "PK, SUPnn", "supplier_name": "FICTIONAL supplier name", "supplier_type": "Supplier channel type",
   "city": "Synthetic location", "state": "Synthetic location", "lead_time_mean_days": "Mean order lead time (days)",
   "lead_time_sd_days": "Std dev of lead time", "on_time_probability": "P(no extra delay)", "full_fill_probability": "P(order delivered in full)",
   "payment_terms_days": "Payment terms", "is_synthetic": "1 = synthetic entity"},
 "supplier_disruption_events.csv": {"event_id": "PK", "supplier_id": "FK suppliers", "start_date": "Start", "end_date": "End",
   "extra_lead_time_days": "Added lead time for orders placed in window", "full_fill_probability_multiplier": "Multiplier on full-fill probability"},
 "medicines.csv": {"medicine_id": "PK, MEDnnn", "generic_name": "Generic (INN-style) name", "display_name": "Name + strength + form",
   "active_ingredients": "Active substance(s) in salt form; ';' separated", "strength": "Strength ('UNVERIFIED' when not confirmed)",
   "dosage_form": "Dosage form", "route": "Route of administration", "category_id": "FK categories", "primary_supplier_id": "FK suppliers",
   "unit_of_measure": "Smallest stock-keeping unit", "pack_size": "Units per order pack (orders are multiples)",
   "storage_condition": "Storage", "unit_cost_inr_2021": "SYNTHETIC unit cost (INR)", "unit_price_inr_2021": "SYNTHETIC unit price (INR)",
   "composition_status": "VERIFIED_STANDARD_REFERENCE or UNVERIFIED_REQUIRES_REVIEW", "composition_note": "Verification note / indicative info",
   "price_is_synthetic": "1 = synthetic price"},
 "medicine_suppliers.csv": {"medicine_id": "FK medicines", "supplier_id": "FK suppliers", "supplier_role": "Primary/Secondary", "order_share": "Approx. share of orders"},
 "calendar.csv": {"date": "Date", "year": "Year", "month": "Month", "day_of_week": "0=Mon", "is_weekend": "Sat/Sun", "season": "Synthetic seasons (north-India style)"},
 "inventory_daily.csv": {"record_id": "PK, RECnnnnnn (shared across daily files)", "date": "Date", "medicine_id": "FK medicines",
   "opening_stock": "Units at start of day", "units_received": "Units delivered (start of day)", "units_sold": "Units dispensed",
   "wastage_units": "Damaged/expired write-off", "closing_stock": "opening+received-sold-wastage",
   "units_ordered_today": "Order qty placed at end of day (0 if none)", "on_order_units": "Ordered, undelivered units at end of day",
   "reorder_point": "Policy reorder point", "order_up_to_level": "Policy order-up-to level"},
 "demand_sales_daily.csv": {"record_id": "PK/FK", "date": "Date", "medicine_id": "FK", "units_demanded": "Underlying customer demand",
   "units_sold": "min(demand, available)", "lost_sales_units": "demand - sold", "stockout_flag": "1 if lost_sales_units>0",
   "unit_price_inr": "Price incl. 4%/yr synthetic inflation", "sales_revenue_inr": "units_sold*unit_price"},
 "replenishment_orders.csv": {"order_id": "PK, POnnnnnnn", "medicine_id": "FK", "supplier_id": "FK", "order_date": "Placed date",
   "expected_delivery_date": "Order date + supplier mean lead time", "actual_delivery_date": "Null if in transit at 2025-12-31",
   "lead_time_days": "Actual lead time", "quantity_ordered": "Ordered units", "quantity_received": "Delivered units (may be partial)",
   "status": "Received / Partially_Received / In_Transit_At_Period_End", "unit_cost_inr": "Synthetic cost", "order_value_inr": "Ordered qty * cost"},
 "stockout_label_lookahead_2026.csv": {"medicine_id": "FK", "date": "2026-01-01..07", "stockout_flag": "Simulated stock-out flag used only to label last 7 days of 2025"},
 "stockout_prediction_dataset.csv": {"record_id": "PK/FK", "date": "Date", "medicine_id": "FK", "category_id": "FK", "supplier_id": "Primary supplier",
   "year": "", "month": "", "day_of_week": "0=Mon", "is_weekend": "", "season": "", "closing_stock": "End-of-day stock",
   "on_order_units": "Outstanding orders", "reorder_point": "", "units_demanded": "Day-t demand", "units_sold": "Day-t sales",
   "sales_7d_avg": "Trailing mean sales incl. day t", "sales_30d_avg": "Trailing 30d mean sales", "days_of_cover": "closing/sales_30d_avg (cap 365)",
   "stock_position_cover_days": "(closing+on_order)/sales_30d_avg (cap 365)", "days_since_last_receipt": "Capped at 365; window start counted as day 0 baseline",
   "stockout_days_last_30d": "Stock-out days in trailing 30d", "supplier_lead_time_mean_days": "", "supplier_full_fill_probability": "",
   "supplier_disruption_active": "Primary supplier disruption in effect", "unit_price_inr": "", "stockout_today": "Day-t stock-out",
   "stockout_next_7d": "TARGET: 1 if any stock-out (lost sales) on days t+1..t+7"},
}
rows = [dict(file=f, column=c, description=d) for f, cd_ in DD.items() for c, d in cd_.items()]
pd.DataFrame(rows).to_csv(os.path.join(OUT, "data_dictionary.csv"), index=False)

# ================================================================ VALIDATION (re-reads files from disk)
def validate(out):
    R = lambda f: pd.read_csv(os.path.join(out, f), keep_default_na=False, na_values=[""])
    cat, sup, med, ms, dis_, cal = (R(x) for x in ["categories.csv", "suppliers.csv", "medicines.csv",
                                                    "medicine_suppliers.csv", "supplier_disruption_events.csv", "calendar.csv"])
    inv, dsd, rep, la, mod = (R(x) for x in ["inventory_daily.csv", "demand_sales_daily.csv", "replenishment_orders.csv",
                                             "stockout_label_lookahead_2026.csv", "stockout_prediction_dataset.csv"])
    checks = []
    def chk(group, name, ok, detail=""):
        checks.append(dict(group=group, check=name, result="PASS" if ok else "FAIL", detail=str(detail)))
    # structure
    chk("Structure", "Total daily records == 155,210", len(inv) == len(dsd) == len(mod) == 155210, f"{len(inv)}/{len(dsd)}/{len(mod)}")
    chk("Structure", "85 medicines", med.medicine_id.nunique() == 85)
    chk("Structure", "15 suppliers", sup.supplier_id.nunique() == 15)
    chk("Structure", "11 categories", cat.category_id.nunique() == 11)
    chk("Structure", "Date range 2021-01-01..2025-12-31, 1,826 days", inv.date.min() == "2021-01-01" and inv.date.max() == "2025-12-31" and inv.date.nunique() == 1826)
    chk("Structure", "Every medicine has all 1,826 days (no gaps/duplicates)", (inv.groupby("medicine_id").date.nunique() == 1826).all() and not inv.duplicated(["medicine_id", "date"]).any())
    chk("Structure", "record_id unique and identical across 3 daily files", inv.record_id.is_unique and (inv.record_id.values == dsd.record_id.values).all() and (inv.record_id.values == mod.record_id.values).all())
    chk("Structure", "Calendar has 1,826 unique dates", cal.date.nunique() == 1826)
    # IDs / keys
    chk("Keys", "PK uniqueness (medicine, supplier, category, order, event)", med.medicine_id.is_unique and sup.supplier_id.is_unique and cat.category_id.is_unique and rep.order_id.is_unique and dis_.event_id.is_unique)
    chk("Keys", "ID formats consistent (MEDnnn/SUPnn/CATnn/POnnnnnnn/RECnnnnnn)",
        med.medicine_id.str.match(r"^MED\d{3}$").all() and sup.supplier_id.str.match(r"^SUP\d{2}$").all() and cat.category_id.str.match(r"^CAT\d{2}$").all()
        and rep.order_id.str.match(r"^PO\d{7}$").all() and inv.record_id.str.match(r"^REC\d{6}$").all())
    chk("Keys", "FK medicines.category_id -> categories", med.category_id.isin(cat.category_id).all())
    chk("Keys", "FK medicines.primary_supplier_id -> suppliers", med.primary_supplier_id.isin(sup.supplier_id).all())
    chk("Keys", "FK daily/orders medicine_id -> medicines", all(d.medicine_id.isin(med.medicine_id).all() for d in (inv, dsd, rep, mod, ms, la)))
    chk("Keys", "FK orders/bridge/events supplier_id -> suppliers", all(d.supplier_id.isin(sup.supplier_id).all() for d in (rep, ms, dis_)))
    chk("Keys", "Every category has >=1 medicine; every supplier is primary for >=1 medicine", med.category_id.nunique() == 11 and med.primary_supplier_id.nunique() == 15,
        f"min meds/category={med.category_id.value_counts().min()}, min meds/supplier={med.primary_supplier_id.value_counts().min()}")
    chk("Keys", "Order suppliers belong to the medicine's supplier bridge", len(rep.merge(ms, on=["medicine_id", "supplier_id"])) == len(rep))
    chk("Keys", "Modelling table category/supplier match medicines master",
        (mod.category_id.values == mod.medicine_id.map(med.set_index("medicine_id").category_id).values).all() and
        (mod.supplier_id.values == mod.medicine_id.map(med.set_index("medicine_id").primary_supplier_id).values).all())
    # medicine master quality
    chk("Medicine master", "No duplicate (generic, strength, dosage form)", not med.duplicated(["generic_name", "strength", "dosage_form"]).any())
    chk("Medicine master", "No missing generic name/ingredients/strength/form/status", med[["generic_name", "active_ingredients", "strength", "dosage_form", "composition_status"]].notna().all().all())
    nunv = (med.composition_status == "UNVERIFIED_REQUIRES_REVIEW").sum()
    chk("Medicine master", "Unverified compositions are flagged (not guessed): strength='UNVERIFIED' iff flagged",
        ((med.composition_status == "UNVERIFIED_REQUIRES_REVIEW") == (med.strength == "UNVERIFIED")).all(), f"{nunv} flagged, {85 - nunv} standard-reference")
    chk("Medicine master", "Statuses limited to the two allowed values", med.composition_status.isin(["VERIFIED_STANDARD_REFERENCE", "UNVERIFIED_REQUIRES_REVIEW"]).all())
    chk("Medicine master", "Verified rows have no 'UNVERIFIED' text in ingredients/strength",
        not med[med.composition_status.str.startswith("VERIFIED")][["active_ingredients", "strength"]].apply(lambda c: c.str.contains("UNVERIFIED")).any().any())
    chk("Medicine master", "Pack size positive; units per pack in {1,10}", med.pack_size.isin([1, 10]).all())
    # nulls / ranges
    chk("Quality", "No nulls in daily tables", not inv.isna().any().any() and not dsd.isna().any().any() and not mod.isna().any().any())
    num = ["opening_stock", "units_received", "units_sold", "wastage_units", "closing_stock", "units_ordered_today", "on_order_units", "reorder_point"]
    chk("Quality", "No negative inventory values", (inv[num] >= 0).all().all())
    chk("Quality", "No negative demand/sales/lost-sales/revenue", (dsd[["units_demanded", "units_sold", "lost_sales_units", "sales_revenue_inr"]] >= 0).all().all())
    # inventory logic
    chk("Inventory logic", "closing = opening + received - sold - wastage", (inv.closing_stock == inv.opening_stock + inv.units_received - inv.units_sold - inv.wastage_units).all())
    s = inv.sort_values(["medicine_id", "date"]); nxt = s.groupby("medicine_id").opening_stock.shift(-1); prev = s.groupby("medicine_id").closing_stock
    chk("Inventory logic", "opening(t+1) = closing(t)", (nxt.dropna() == s.closing_stock[nxt.notna()]).all())
    chk("Inventory logic", "units_sold <= opening + received", (inv.units_sold <= inv.opening_stock + inv.units_received).all())
    chk("Inventory logic", "Sales identical across inventory/demand/model tables", (inv.units_sold.values == dsd.units_sold.values).all() and (inv.units_sold.values == mod.units_sold.values).all())
    chk("Inventory logic", "sold = min(demand, available); lost = demand - sold",
        ((dsd.units_sold + dsd.lost_sales_units) == dsd.units_demanded).all() and (dsd.units_sold == np.minimum(dsd.units_demanded, inv.opening_stock + inv.units_received)).all())
    chk("Inventory logic", "stockout_flag = (lost_sales_units > 0)", (dsd.stockout_flag == (dsd.lost_sales_units > 0).astype(int)).all())
    chk("Inventory logic", "revenue = units_sold * unit_price (to 0.01)", ((dsd.units_sold * dsd.unit_price_inr - dsd.sales_revenue_inr).abs() <= 0.011).all())
    # replenishment
    chk("Replenishment", "Orders placed within 2021-2025 only", rep.order_date.min() >= "2021-01-01" and rep.order_date.max() <= "2025-12-31")
    rc = rep[rep.actual_delivery_date.notna()]
    chk("Replenishment", "Delivery date > order date; lead_time matches dates",
        ((pd.to_datetime(rc.actual_delivery_date) - pd.to_datetime(rc.order_date)).dt.days == rc.lead_time_days).all() and (rc.lead_time_days >= 1).all())
    chk("Replenishment", "Received qty <= ordered; status consistent",
        (rc.quantity_received <= rc.quantity_ordered).all() and ((rc.status == "Partially_Received") == (rc.quantity_received < rc.quantity_ordered)).all())
    chk("Replenishment", "In-transit orders have null delivery fields and delivery would be after 2025-12-31",
        rep[rep.status == "In_Transit_At_Period_End"][["actual_delivery_date", "quantity_received", "lead_time_days"]].isna().all().all())
    pk = med.set_index("medicine_id").pack_size
    chk("Replenishment", "Ordered/received quantities are multiples of pack size", (rep.quantity_ordered % rep.medicine_id.map(pk) == 0).all() and (rc.quantity_received % rc.medicine_id.map(pk) == 0).all())
    chk("Replenishment", "Expected delivery after order date", (pd.to_datetime(rep.expected_delivery_date) > pd.to_datetime(rep.order_date)).all())
    rsum = rc.groupby(["medicine_id", "actual_delivery_date"]).quantity_received.sum()
    isum = inv[inv.units_received > 0].set_index(["medicine_id", "date"]).units_received
    chk("Replenishment", "Daily units_received == sum of orders delivered that day (per medicine/date)",
        len(rsum) == len(isum) and (rsum.sort_index().values == isum.sort_index().values).all(), f"{len(isum)} receipt days")
    osum = rep.groupby(["medicine_id", "order_date"]).quantity_ordered.sum()
    osum2 = inv[inv.units_ordered_today > 0].set_index(["medicine_id", "date"]).units_ordered_today
    chk("Replenishment", "Daily units_ordered_today == orders placed that day", len(osum) == len(osum2) and (osum.sort_index().values == osum2.sort_index().values).all())
    # recompute on_order
    ev = pd.concat([rep.assign(d=rep.order_date, q=rep.quantity_ordered)[["medicine_id", "d", "q"]],
                    rep.assign(d=rep.expected_delivery_date)[[]].iloc[0:0]])
    # label
    full = pd.concat([dsd[["medicine_id", "date", "stockout_flag"]], la]).sort_values(["medicine_id", "date"]).reset_index(drop=True)
    lab = np.zeros(len(full), dtype=int)
    for k in range(1, 8):
        lab |= (full.groupby("medicine_id").stockout_flag.shift(-k).fillna(0).astype(int).values)
    full["lab"] = lab
    mm = mod.merge(full[["medicine_id", "date", "lab"]], on=["medicine_id", "date"])
    chk("Labels", "Independent recomputation of stockout_next_7d matches for all 155,210 rows", len(mm) == 155210 and (mm.lab == mm.stockout_next_7d).all())
    chk("Labels", "Label is binary, no nulls", mod.stockout_next_7d.isin([0, 1]).all())
    chk("Labels", "Look-ahead file has 85 x 7 rows covering 2026-01-01..07", len(la) == 595 and la.date.min() == "2026-01-01" and la.date.max() == "2026-01-07")
    chk("Labels", "If a stock-out occurs tomorrow, label is 1 (consistency)",
        (mod.sort_values(["medicine_id", "date"]).groupby("medicine_id").stockout_today.shift(-1).fillna(0).values <= mod.sort_values(["medicine_id", "date"]).stockout_next_7d.values).all())
    prev_ = mod.stockout_next_7d.mean()
    chk("Labels", "Positive-class prevalence in 5%-40% (usable class balance)", 0.05 <= prev_ <= 0.40, f"{prev_:.3%}")
    # features
    mm2 = mod.sort_values(["medicine_id", "date"])
    r7 = mm2.groupby("medicine_id").units_sold.transform(lambda x: x.rolling(7, min_periods=1).mean()).round(3)
    chk("Features", "sales_7d_avg recomputes from raw sales (no look-ahead)", ((r7 - mm2.sales_7d_avg).abs() < 1e-6).all())
    so30 = mm2.groupby("medicine_id").stockout_today.transform(lambda x: x.rolling(30, min_periods=1).sum())
    chk("Features", "stockout_days_last_30d recomputes (trailing only)", (so30 == mm2.stockout_days_last_30d).all())
    chk("Features", "Model-table stock/on-order/reorder fields equal inventory table", (mod.closing_stock.values == inv.closing_stock.values).all() and (mod.on_order_units.values == inv.on_order_units.values).all() and (mod.reorder_point.values == inv.reorder_point.values).all())
    # plausibility
    d2 = dsd.merge(med[["medicine_id", "generic_name", "category_id"]], on="medicine_id")
    d2["month"] = pd.to_datetime(d2.date).dt.month
    ors = d2[d2.generic_name.str.startswith("Oral Rehydration")].groupby("month").units_demanded.mean()
    chk("Plausibility", "ORS demand peaks in summer/monsoon months (May-Jul)", ors.idxmax() in (5, 6, 7), f"peak month={ors.idxmax()}")
    dm = d2[d2.generic_name == "Dextromethorphan"].groupby("month").units_demanded.mean()
    chk("Plausibility", "Cough syrup demand peaks in Nov-Feb", dm.idxmax() in (11, 12, 1, 2), f"peak month={dm.idxmax()}")
    wk = d2.assign(dow=pd.to_datetime(d2.date).dt.dayofweek).groupby("dow").units_demanded.mean()
    chk("Plausibility", "Sunday demand lowest weekday", wk.idxmin() == 6)
    chk("Plausibility", "Lead times within 1-30 days", rc.lead_time_days.between(1, 30).all(), f"max={rc.lead_time_days.max()}")
    so_med = dsd.groupby("medicine_id").stockout_flag.mean()
    chk("Plausibility", "Stock-out rate per medicine between 0% and 50% (heterogeneous, none degenerate)", so_med.max() < 0.5, f"min={so_med.min():.2%}, max={so_med.max():.2%}")
    chk("Plausibility", "Both label classes present for most medicines (>=90%)", (mod.groupby("medicine_id").stockout_next_7d.nunique() == 2).mean() >= 0.9,
        f"{(mod.groupby('medicine_id').stockout_next_7d.nunique() == 2).sum()}/85")
    chk("Plausibility", "Medicines with zero stock-outs", True, f"{(so_med == 0).sum()} medicines")
    res = pd.DataFrame(checks)
    res.to_csv(os.path.join(out, "validation_checks.csv"), index=False)

    # report
    def tbl(df):
        h = "| " + " | ".join(df.columns) + " |\n|" + "|".join(["---"] * len(df.columns)) + "|\n"
        return h + "\n".join("| " + " | ".join(str(v) for v in r) + " |" for r in df.itertuples(index=False)) + "\n"
    npass = (res.result == "PASS").sum()
    by_year = mod.groupby("year").agg(rows=("record_id", "count"), stockout_today_rate=("stockout_today", "mean"), label_rate=("stockout_next_7d", "mean")).round(4).reset_index()
    cn = cat.set_index("category_id").category_name
    by_cat = mod.groupby("category_id").agg(medicines=("medicine_id", "nunique"), label_rate=("stockout_next_7d", "mean")).round(4).reset_index()
    by_cat.insert(1, "category", by_cat.category_id.map(cn))
    ordst = rep.status.value_counts().rename_axis("status").reset_index(name="orders")
    lines = [
        "# Validation Report - Pharmacy Stock-Out Prediction Dataset Pack\n",
        f"**Result: {npass}/{len(res)} checks passed.** All checks re-read the CSV files from disk (independent of the generator's in-memory state).\n",
        "## Dataset summary\n",
        f"- Daily records: {len(mod):,} ({med.medicine_id.nunique()} medicines x 1,826 days, 2021-01-01 to 2025-12-31)",
        f"- Suppliers: {len(sup)} | Categories: {len(cat)} | Replenishment orders: {len(rep):,} | Disruption events: {len(dis_)}",
        f"- Target `stockout_next_7d` prevalence: {prev_:.2%}",
        f"- Medicines with verified-standard composition: {85 - nunv}; flagged UNVERIFIED_REQUIRES_REVIEW: {nunv}\n",
        "## Check results\n", tbl(res),
        "## Target and stock-out rate by year\n", tbl(by_year),
        "## Target rate by category\n", tbl(by_cat),
        "## Order status\n", tbl(ordst),
        "## Flagged (unverified) medicines\n",
        tbl(med[med.composition_status != "VERIFIED_STANDARD_REFERENCE"][["medicine_id", "generic_name", "strength", "composition_note"]]),
        "## Label definition\n",
        "`stockout_next_7d` = 1 if `lost_sales_units > 0` (demand exceeded available stock) on any of days t+1 ... t+7 for the same medicine. "
        "Rows in the final 7 days of 2025 are labelled using a simulated look-ahead (`stockout_label_lookahead_2026.csv`); "
        "no row has a missing label. Features use data up to and including day t only.\n",
        "## Limitations\n",
        "- All inventory, demand, sales, orders, prices, suppliers and disruptions are **synthetic**; suppliers are fictional. Do not use for real procurement or clinical decisions.",
        "- Composition 'verification' means agreement with standard INN / WHO Model List / pharmacopoeial reference knowledge; **no live regulatory database (CDSCO, DrugBank, RxNorm) lookup was possible** in the offline build environment. A pharmacist should review before production use.",
        "- Fixed-dose combinations and multivitamins are flagged UNVERIFIED_REQUIRES_REVIEW; strengths were deliberately not asserted.",
        "- Demand follows a seasonal x weekday x trend x spike x gamma-Poisson generator; real demand has promotions, prescribing shifts, regional outbreaks and substitution not modelled.",
        "- Replenishment uses a single (s,S)-type rule with daily review; real pharmacies use mixed manual/automatic ordering. Lost sales are not back-ordered and there is no substitution between medicines.",
        "- Stock-out frequency is tuned to give a usable class balance and may differ from real pharmacies. Models trained here will not transfer without re-training on real data.",
        "- `unit_price_inr`/cost are illustrative and not market prices. Expiry is simplified to random wastage; no batch/lot tracking.",
        "- Look-ahead 2026 simulation is not part of the daily tables; orders placed in 2026 are not exported.",
        "- Seasons follow a generic north-India pattern; no public holiday calendar is included.",
    ]
    with open(os.path.join(out, "validation_report.md"), "w") as f:
        f.write("\n".join(lines))
    return res

res = validate(OUT)

README = f"""# Pharmacy Stock-Out Prediction - Synthetic Dataset Pack

155,210 daily records = 85 medicines x 1,826 days (2021-01-01..2025-12-31), 15 suppliers, 11 categories.
**All transactional data is synthetic** (seed {SEED}); see `validation_report.md` for checks and limitations.

| File | Purpose |
|---|---|
| medicines.csv | Master: generic name, salt form, strength, dosage form, composition_status |
| categories.csv / suppliers.csv / medicine_suppliers.csv / supplier_disruption_events.csv / calendar.csv | Dimensions |
| inventory_daily.csv | Stock movements and reorder policy per medicine-day |
| demand_sales_daily.csv | Demand, sales, lost sales, price, revenue |
| replenishment_orders.csv | Purchase orders with lead time and fill |
| stockout_prediction_dataset.csv | Modelling table: features + target `stockout_next_7d` |
| stockout_label_lookahead_2026.csv | Simulated 2026-01-01..07 flags used to label the last 7 days of 2025 |
| data_dictionary.csv | Column descriptions |
| validation_checks.csv / validation_report.md | Validation outcomes |
| generate_dataset_pack.py | Regenerates and validates everything |

Join key: `record_id` (daily files), `medicine_id`, `supplier_id`, `category_id`.
Suggested split: time-based (train 2021-2023, validation 2024, test 2025); avoid random splits.
Medicines flagged `UNVERIFIED_REQUIRES_REVIEW` have strength intentionally withheld.
"""
open(os.path.join(OUT, "README.md"), "w").write(README)
print("DONE", (res.result == "PASS").sum(), "/", len(res), "checks passed")
