// MOCK DATA — categories (real data from dataset)
import type { Category } from '../types/domain';

export const MOCK_CATEGORIES: Category[] = [
  { category_id: 'CAT01', category_name: 'Analgesics & Antipyretics', description: 'Pain and fever relief' },
  { category_id: 'CAT02', category_name: 'Antibiotics', description: 'Antibacterial agents' },
  { category_id: 'CAT03', category_name: 'Cardiovascular', description: 'Antihypertensives, lipid-lowering, antiplatelets, diuretics' },
  { category_id: 'CAT04', category_name: 'Antidiabetics', description: 'Glucose-lowering agents and insulin' },
  { category_id: 'CAT05', category_name: 'Gastrointestinal', description: 'Acid suppression, antiemetics, rehydration' },
  { category_id: 'CAT06', category_name: 'Respiratory & Allergy', description: 'Antihistamines, asthma and cough products' },
  { category_id: 'CAT07', category_name: 'Antifungals & Antiparasitics', description: 'Antifungal, anthelmintic and antimalarial agents' },
  { category_id: 'CAT08', category_name: 'Neurology & Psychiatry', description: 'Anticonvulsants, antidepressants, anxiolytics' },
  { category_id: 'CAT09', category_name: 'Vitamins & Supplements', description: 'Vitamins, minerals and nutritional supplements' },
  { category_id: 'CAT10', category_name: 'Dermatology & Topicals', description: 'Topical anti-infectives, steroids, antiseptics' },
  { category_id: 'CAT11', category_name: 'Endocrine, Urology & Others', description: 'Thyroid, corticosteroids, urology, gout, contraception' },
];

export const categoryMap = Object.fromEntries(MOCK_CATEGORIES.map(c => [c.category_id, c]));
