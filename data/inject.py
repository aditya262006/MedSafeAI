import re

path = 'c:/MIHiimt/data/fetch_data.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

new_drugs = [
    "omeprazole", "lansoprazole", "amoxicillin", "cephalexin", "ciprofloxacin", 
    "levofloxacin", "azithromycin", "doxycycline", "clindamycin", "metronidazole", 
    "fluconazole", "acyclovir", "valacyclovir", "oseltamivir", "tramadol", 
    "alprazolam", "clonazepam", "diazepam", "lorazepam", "zolpidem", "sertraline", 
    "fluoxetine", "citalopram", "escitalopram", "paroxetine", "duloxetine", 
    "venlafaxine", "mirtazapine", "bupropion", "trazodone", "amitriptyline", 
    "nortriptyline", "lithium", "valproic acid", "carbamazepine", "lamotrigine", 
    "gabapentin", "pregabalin", "levetiracetam", "phenytoin", "propofol", 
    "haloperidol", "risperidone", "olanzapine", "quetiapine", "aripiprazole", 
    "clozapine", "donepezil", "memantine", "levodopa", "propranolol", "metoprolol", 
    "atenolol", "bisoprolol", "carvedilol", "amlodipine", "nifedipine", "diltiazem", 
    "verapamil", "lisinopril", "enalapril", "ramipril", "losartan", "valsartan", 
    "spironolactone", "furosemide", "hydrochlorothiazide", "clonidine", "digoxin", 
    "amiodarone", "warfarin", "dabigatran", "rivaroxaban", "apixaban", "clopidogrel", 
    "insulin", "metformin", "glipizide", "pioglitazone", "sitagliptin", "levothyroxine", 
    "hydrocortisone", "prednisone", "dexamethasone", "testosterone", "estradiol", 
    "finasteride", "tamsulosin", "sildenafil", "tadalafil", "oxybutynin"
]
new_drugs_str = '", "'.join(new_drugs)
new_drugs_str = '"' + new_drugs_str + '"'

content = re.sub(r'(TOP_DRUGS\s*=\s*\[)', r'\1\n    ' + new_drugs_str + ',', content)

# Inject more interactions
extra_interactions = '''
    {"drug_a": "sildenafil", "drug_b": "amlodipine", "severity": "Medium", "description": "Additive blood pressure lowering effect."},
    {"drug_a": "amoxicillin", "drug_b": "methotrexate", "severity": "Medium", "description": "Penicillins can decrease methotrexate clearance, increasing toxicity risk."},
    {"drug_a": "citalopram", "drug_b": "omeprazole", "severity": "High", "description": "Omeprazole significantly increases citalopram levels via CYP2C19 inhibition; QT prolongation risk."},
    {"drug_a": "clopidogrel", "drug_b": "fluoxetine", "severity": "Medium", "description": "Fluoxetine inhibits CYP2C19, reducing clopidogrel efficacy."},
    {"drug_a": "warfarin", "drug_b": "levofloxacin", "severity": "High", "description": "Fluoroquinolones can severely enhance the anticoagulant effect of warfarin."},
    {"drug_a": "diltiazem", "drug_b": "atorvastatin", "severity": "High", "description": "Diltiazem inhibits CYP3A4, significantly increasing atorvastatin levels and myopathy risk."},
    {"drug_a": "metronidazole", "drug_b": "warfarin", "severity": "High", "description": "Metronidazole strongly inhibits warfarin metabolism, causing severe bleeding risk."},
    {"drug_a": "spironolactone", "drug_b": "losartan", "severity": "High", "description": "Concurrent use causes significant hyperkalemia risk, especially in renal impairment."},
'''
content = re.sub(r'(DRUG_INTERACTIONS\s*=\s*\[)', r'\1\n' + extra_interactions, content)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Data expansion injected successfully!")
