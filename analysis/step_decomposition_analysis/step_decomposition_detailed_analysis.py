import openpyxl
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

excel_path = Path('/Users/didem/Desktop/scenarios/Step Decomposition (3).xlsx')
wb = openpyxl.load_workbook(excel_path)

all_data = []
sheets = ['BLUDIT', 'Checkturio', 'ToDo', 'SauceDemo']

for sheet_name in sheets:
    ws = wb[sheet_name]
    
    for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        if row[0] is None: 
            continue
            
        model = row[0]
        scenario = row[1]
        
        if model in ['OpenAi', 'OpenAI']:
            model = 'OpenAi'
        
        steps_gt = row[2] if row[2] else 0
        steps_llm = row[3] if row[3] else 0
        missing_steps = row[4] if row[4] else 0
        hallucination = row[5] if row[5] else 0
        
        def parse_rate(rate_str):
            if rate_str is None:
                return 0
            
            if isinstance(rate_str, (int, float)):
                return float(rate_str)
            
            if isinstance(rate_str, str):
                rate_str = rate_str.strip()
                if '/' in rate_str:
                    parts = rate_str.split('/')
                    try:
                        numerator = float(parts[0])
                        denominator = float(parts[1])
                        return numerator / denominator if denominator > 0 else 0
                    except (ValueError, IndexError):
                        return 0
                else:
                    try:
                        return float(rate_str)
                    except ValueError:
                        return 0
            
            return 0
        
        step_match_rate = parse_rate(row[6])
        missing_rate = parse_rate(row[7])
        hallucination_rate = parse_rate(row[8])
        exec_rate = parse_rate(row[9])
        
        success = row[10] if row[10] else 'No'
        
        all_data.append({
            'Application': sheet_name,
            'Model': model,
            'Scenario': scenario,
            'Steps_GT': int(steps_gt) if steps_gt else 0,
            'Steps_LLM': int(steps_llm) if steps_llm else 0,
            'Missing_Steps': int(missing_steps) if missing_steps else 0,
            'Hallucination': int(hallucination) if hallucination else 0,
            'Step_Match_Rate': step_match_rate,
            'Missing_Rate': missing_rate,
            'Hallucination_Rate': hallucination_rate,
            'Exec_Rate': exec_rate,
            'Success': 1 if success == 'Yes' else 0
        })

df = pd.DataFrame(all_data)

print("=" * 80)
print("DATA VALIDATION")
print("=" * 80)

print("\nData types before conversion:")
print(df.dtypes)

numeric_columns = ['Steps_GT', 'Steps_LLM', 'Missing_Steps', 'Hallucination', 
                  'Step_Match_Rate', 'Missing_Rate', 'Hallucination_Rate', 'Exec_Rate', 'Success']

for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

print("\nData types after conversion:")
print(df.dtypes)

print("\nSample data:")
print(df.head())

print(f"\nTotal rows: {len(df)}")
print(f"Missing values per column:")
print(df.isnull().sum())

output_dir = Path('/Users/didem/Desktop/scenarios/step_decomposition_analysis')
output_dir.mkdir(exist_ok=True)

print("=" * 80)
print("STEP DECOMPOSITION ANALYSIS")
print("=" * 80)
print(f"\nTotal Data Points: {len(df)}")
print(f"Applications: {df['Application'].unique()}")
print(f"Models: {df['Model'].unique()}")


print("\n" + "=" * 80)
print("TABLE 1: MODEL COMPARISON")
print("=" * 80)

model_comparison = df.groupby('Model').agg({
    'Scenario': 'count',
    'Success': 'sum',
    'Steps_GT': 'sum',
    'Steps_LLM': 'sum',
    'Missing_Steps': 'sum',
    'Hallucination': 'sum',
    'Step_Match_Rate': 'mean',
    'Missing_Rate': 'mean',
    'Hallucination_Rate': 'mean',
    'Exec_Rate': 'mean'
}).round(4)

model_comparison.columns = [
    'Total Scenarios',
    'Successful Scenarios',
    'Total GT Steps',
    'Total LLM Steps',
    'Total Missing Steps',
    'Total Hallucinations',
    'Avg Step Match',
    'Avg Missing Rate',
    'Avg Hallucination Rate',
    'Avg Execution Rate'
]

model_comparison['Success Rate (%)'] = (model_comparison['Successful Scenarios'] / model_comparison['Total Scenarios'] * 100).round(2)

print(model_comparison)
model_comparison.to_csv(output_dir / '1_model_comparison.csv', encoding='utf-8-sig')


print("\n" + "=" * 80)
print("TABLE 2: APPLICATION-BASED SUCCESS RATES")
print("=" * 80)

app_success = df.groupby(['Application', 'Model']).agg({
    'Scenario': 'count',
    'Success': 'sum',
    'Step_Match_Rate': 'mean',
    'Exec_Rate': 'mean'
}).round(4)

app_success.columns = ['Total Scenarios', 'Successful Scenarios', 'Avg Step Match', 'Avg Execution']
app_success['Success Rate (%)'] = (app_success['Successful Scenarios'] / app_success['Total Scenarios'] * 100).round(2)

print(app_success)
app_success.to_csv(output_dir / '2_application_based_success.csv', encoding='utf-8-sig')


print("\n" + "=" * 80)
print("TABLE 3: MISSING STEPS AND HALLUCINATION ANALYSIS")
print("=" * 80)

error_analysis = df.groupby(['Application', 'Model']).agg({
    'Missing_Steps': 'sum',
    'Hallucination': 'sum',
    'Steps_GT': 'sum',
    'Steps_LLM': 'sum',
    'Missing_Rate': 'mean',
    'Hallucination_Rate': 'mean'
}).round(4)

error_analysis.columns = [
    'Total Missing Steps',
    'Total Hallucinations',
    'Total GT Steps',
    'Total LLM Steps',
    'Avg Missing Rate',
    'Avg Hallucination Rate'
]

error_analysis['Missing Steps %'] = (error_analysis['Total Missing Steps'] / error_analysis['Total GT Steps'] * 100).round(2)
error_analysis['Hallucination %'] = (error_analysis['Total Hallucinations'] / error_analysis['Total LLM Steps'] * 100).round(2)

print(error_analysis)
error_analysis.to_csv(output_dir / '3_missing_steps_hallucination.csv', encoding='utf-8-sig')

print("\n" + "=" * 80)
print("TABLE 4: STEP MATCHING AND EXECUTION DETAILS")
print("=" * 80)

exec_analysis = df.groupby(['Application', 'Model']).agg({
    'Step_Match_Rate': ['mean', 'min', 'max', 'std'],
    'Exec_Rate': ['mean', 'min', 'max', 'std']
}).round(4)

exec_analysis.columns = [
    'Step Match Mean', 'Step Match Min', 'Step Match Max', 'Step Match Std',
    'Execution Mean', 'Execution Min', 'Execution Max', 'Execution Std'
]

print(exec_analysis)
exec_analysis.to_csv(output_dir / '4_step_matching_execution.csv', encoding='utf-8-sig')


plt.figure(figsize=(12, 6))
model_success = df.groupby('Model').agg({
    'Success': lambda x: (x.sum() / len(x) * 100)
}).round(2)

colors = ['#27ae60', '#c0392b']  # Daha koyu tonlar
bars = plt.bar(model_success.index, model_success['Success'], color=colors, alpha=0.9, edgecolor='black', linewidth=1.5)

for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.2f}%',
             ha='center', va='bottom', fontsize=12, fontweight='bold')

plt.title('Scenario Success Rate by Model', fontsize=16, fontweight='bold', pad=20)
plt.ylabel('Success Rate (%)', fontsize=12, fontweight='bold')
plt.xlabel('Model', fontsize=12, fontweight='bold')
plt.ylim(0, 100)
plt.grid(axis='y', alpha=0.3, linestyle='--')
plt.tight_layout()
plt.savefig(output_dir / 'chart_1_model_success.pdf', bbox_inches='tight')
plt.savefig(output_dir / 'chart_1_model_success.png', bbox_inches='tight', dpi=300)
print(f"\n✓ Chart 1 saved: chart_1_model_success.pdf and .png")
plt.close()


fig, ax = plt.subplots(figsize=(14, 8))

app_model_success = df.groupby(['Application', 'Model']).agg({
    'Success': lambda x: (x.sum() / len(x) * 100)
}).unstack()

app_model_success.columns = app_model_success.columns.droplevel(0)

x = np.arange(len(app_model_success.index))
width = 0.35

bars1 = ax.bar(x - width/2, app_model_success['DeepSeek'], width, 
               label='DeepSeek', color='#2980b9', alpha=0.9, edgecolor='black', linewidth=1.5)
bars2 = ax.bar(x + width/2, app_model_success['OpenAi'], width,
               label='OpenAI', color='#27ae60', alpha=0.9, edgecolor='black', linewidth=1.5)

# Add values
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom', fontsize=10, fontweight='bold')

ax.set_xlabel('Application', fontsize=12, fontweight='bold')
ax.set_ylabel('Success Rate (%)', fontsize=12, fontweight='bold')
ax.set_title('Application-Based Model Comparison', fontsize=16, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(app_model_success.index, fontsize=11)
ax.legend(fontsize=11)
ax.set_ylim(0, 100)
ax.grid(axis='y', alpha=0.3, linestyle='--')

plt.tight_layout()
plt.savefig(output_dir / 'chart_2_application_success.pdf', bbox_inches='tight')
plt.savefig(output_dir / 'chart_2_application_success.png', bbox_inches='tight', dpi=300)
print(f"✓ Chart 2 saved: chart_2_application_success.pdf and .png")
plt.close()


fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

missing_data = df.groupby(['Application', 'Model'])['Missing_Steps'].sum().unstack()
x = np.arange(len(missing_data.index))
width = 0.35

bars1 = ax1.bar(x - width/2, missing_data['DeepSeek'], width,
                label='DeepSeek', color='#ffebee', alpha=0.9, edgecolor='black', linewidth=1.5)
bars2 = ax1.bar(x + width/2, missing_data['OpenAi'], width,
                label='OpenAI', color='#b71c1c', alpha=0.9, edgecolor='black', linewidth=1.5)

for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')

ax1.set_xlabel('Application', fontsize=12, fontweight='bold')
ax1.set_ylabel('Total Missing Steps', fontsize=12, fontweight='bold')
ax1.set_title('Missing Steps Analysis', fontsize=14, fontweight='bold', pad=15)
ax1.set_xticks(x)
ax1.set_xticklabels(missing_data.index, fontsize=11)
ax1.legend(fontsize=11)
ax1.grid(axis='y', alpha=0.3, linestyle='--')

halluc_data = df.groupby(['Application', 'Model'])['Hallucination'].sum().unstack()

bars1 = ax2.bar(x - width/2, halluc_data['DeepSeek'], width,
                label='DeepSeek', color='#f3e5f5', alpha=0.9, edgecolor='black', linewidth=1.5)
bars2 = ax2.bar(x + width/2, halluc_data['OpenAi'], width,
                label='OpenAI', color='#4a148c', alpha=0.9, edgecolor='black', linewidth=1.5)

for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')

ax2.set_xlabel('Application', fontsize=12, fontweight='bold')
ax2.set_ylabel('Total Hallucinations', fontsize=12, fontweight='bold')
ax2.set_title('Hallucination Analysis', fontsize=14, fontweight='bold', pad=15)
ax2.set_xticks(x)
ax2.set_xticklabels(halluc_data.index, fontsize=11)
ax2.legend(fontsize=11)
ax2.grid(axis='y', alpha=0.3, linestyle='--')

plt.tight_layout()
plt.savefig(output_dir / 'chart_3_missing_hallucination.pdf', bbox_inches='tight')
plt.savefig(output_dir / 'chart_3_missing_hallucination.png', bbox_inches='tight', dpi=300)
print(f"✓ Chart 3 saved: chart_3_missing_hallucination.pdf and .png")
plt.close()


fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

match_data = df.groupby(['Application', 'Model'])['Step_Match_Rate'].mean().unstack() * 100

x = np.arange(len(match_data.index))
width = 0.35

bars1 = ax1.bar(x - width/2, match_data['DeepSeek'], width,
                label='DeepSeek', color='#138d75', alpha=0.9, edgecolor='black', linewidth=1.5)
bars2 = ax1.bar(x + width/2, match_data['OpenAi'], width,
                label='OpenAI', color='#1e8449', alpha=0.9, edgecolor='black', linewidth=1.5)

for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom', fontsize=10, fontweight='bold')

ax1.set_xlabel('Application', fontsize=12, fontweight='bold')
ax1.set_ylabel('Average Matching Rate (%)', fontsize=12, fontweight='bold')
ax1.set_title('Step Matching Rates', fontsize=14, fontweight='bold', pad=15)
ax1.set_xticks(x)
ax1.set_xticklabels(match_data.index, fontsize=11)
ax1.legend(fontsize=11)
ax1.set_ylim(0, 105)
ax1.grid(axis='y', alpha=0.3, linestyle='--')

exec_data = df.groupby(['Application', 'Model'])['Exec_Rate'].mean().unstack() * 100

bars1 = ax2.bar(x - width/2, exec_data['DeepSeek'], width,
                label='DeepSeek', color='#1f618d', alpha=0.9, edgecolor='black', linewidth=1.5)
bars2 = ax2.bar(x + width/2, exec_data['OpenAi'], width,
                label='OpenAI', color='#2e86c1', alpha=0.9, edgecolor='black', linewidth=1.5)

for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom', fontsize=10, fontweight='bold')

ax2.set_xlabel('Application', fontsize=12, fontweight='bold')
ax2.set_ylabel('Average Execution Rate (%)', fontsize=12, fontweight='bold')
ax2.set_title('Per-Step Execution Rates (1st Try)', fontsize=14, fontweight='bold', pad=15)
ax2.set_xticks(x)
ax2.set_xticklabels(exec_data.index, fontsize=11)
ax2.legend(fontsize=11)
ax2.set_ylim(0, 105)
ax2.grid(axis='y', alpha=0.3, linestyle='--')

plt.tight_layout()
plt.savefig(output_dir / 'chart_4_matching_execution.pdf', bbox_inches='tight')
plt.savefig(output_dir / 'chart_4_matching_execution.png', bbox_inches='tight', dpi=300)
print(f"✓ Chart 4 saved: chart_4_matching_execution.pdf and .png")
plt.close()


fig, ax = plt.subplots(figsize=(12, 8))

heatmap_data = []
for app in sheets:
    for model in ['DeepSeek', 'OpenAi']:
        subset = df[(df['Application'] == app) & (df['Model'] == model)]
        if len(subset) > 0:
            heatmap_data.append({
                'App-Model': f"{app}\n{model}",
                'Success %': (subset['Success'].sum() / len(subset) * 100),
                'Step Match %': (subset['Step_Match_Rate'].mean() * 100),
                'Execution %': (subset['Exec_Rate'].mean() * 100),
                'Missing %': (subset['Missing_Rate'].mean() * 100),  # Normal: düşük missing = düşük değer = kırmızı
                'Hallucination %': (subset['Hallucination_Rate'].mean() * 100)  # Normal: düşük hallucination = düşük değer = kırmızı
            })

heatmap_df = pd.DataFrame(heatmap_data)
heatmap_df = heatmap_df.set_index('App-Model')

sns.heatmap(heatmap_df.T, annot=True, fmt='.1f', cmap='RdYlGn', 
            cbar_kws={'label': 'Percentage (%)'}, linewidths=0.5,
            vmin=0, vmax=100, ax=ax)

ax.set_title('Application-Model Combinations - Detailed Metrics Heatmap\n(For Missing% & Hallucination%: lower values = better performance)', 
             fontsize=14, fontweight='bold', pad=20)
ax.set_xlabel('')
ax.set_ylabel('Metrics', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig(output_dir / 'chart_5_overall_heatmap.pdf', bbox_inches='tight')
plt.savefig(output_dir / 'chart_5_overall_heatmap.png', bbox_inches='tight', dpi=300)
print(f"✓ Chart 5 saved: chart_5_overall_heatmap.pdf and .png")
plt.close()


fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Metrics Distribution by Model and Application', fontsize=18, fontweight='bold', y=1.00)

df_filtered = df[df['Model'].isin(['DeepSeek', 'OpenAi'])].copy()

ax1 = axes[0, 0]
data_to_plot = [df_filtered[df_filtered['Model'] == model]['Step_Match_Rate'].values * 100 
                for model in ['DeepSeek', 'OpenAi']]
bp1 = ax1.boxplot(data_to_plot, labels=['DeepSeek', 'OpenAI'], patch_artist=True,
                   boxprops=dict(facecolor='#2980b9', alpha=0.8, linewidth=0, edgecolor='none'),
                   medianprops=dict(color='#e74c3c', linewidth=2),
                   whiskerprops=dict(linewidth=1.5),
                   capprops=dict(linewidth=1.5))
ax1.set_ylabel('Step Match Rate (%)', fontsize=11, fontweight='bold')
ax1.set_title('Step Match Rate Distribution', fontsize=12, fontweight='bold')
ax1.grid(axis='y', alpha=0.3, linestyle='--')
ax1.set_ylim(0, 105)

ax2 = axes[0, 1]
data_to_plot = [df_filtered[df_filtered['Model'] == model]['Exec_Rate'].values * 100 
                for model in ['DeepSeek', 'OpenAi']]
bp2 = ax2.boxplot(data_to_plot, labels=['DeepSeek', 'OpenAI'], patch_artist=True,
                   boxprops=dict(facecolor='#27ae60', alpha=0.8, linewidth=0, edgecolor='none'),
                   medianprops=dict(color='#e74c3c', linewidth=2),
                   whiskerprops=dict(linewidth=1.5),
                   capprops=dict(linewidth=1.5))
ax2.set_ylabel('Execution Rate (%)', fontsize=11, fontweight='bold')
ax2.set_title('Per-Step Execution Rate Distribution', fontsize=12, fontweight='bold')
ax2.grid(axis='y', alpha=0.3, linestyle='--')
ax2.set_ylim(0, 105)

ax3 = axes[1, 0]
data_to_plot = [df_filtered[df_filtered['Model'] == model]['Missing_Rate'].values * 100 
                for model in ['DeepSeek', 'OpenAi']]
bp3 = ax3.boxplot(data_to_plot, labels=['DeepSeek', 'OpenAI'], patch_artist=True,
                   boxprops=dict(facecolor='#c0392b', alpha=0.8, linewidth=0, edgecolor='none'),
                   medianprops=dict(color='#2c3e50', linewidth=2),
                   whiskerprops=dict(linewidth=1.5),
                   capprops=dict(linewidth=1.5))
ax3.set_ylabel('Missing Steps Rate (%)', fontsize=11, fontweight='bold')
ax3.set_title('Missing Steps Rate Distribution', fontsize=12, fontweight='bold')
ax3.grid(axis='y', alpha=0.3, linestyle='--')
ax3.set_ylim(-5, max(df_filtered['Missing_Rate'].max() * 100 + 10, 25))

ax4 = axes[1, 1]
data_to_plot = [df_filtered[df_filtered['Model'] == model]['Hallucination_Rate'].values * 100 
                for model in ['DeepSeek', 'OpenAi']]
bp4 = ax4.boxplot(data_to_plot, labels=['DeepSeek', 'OpenAI'], patch_artist=True,
                   boxprops=dict(facecolor='#8e44ad', alpha=0.8, linewidth=0, edgecolor='none'),
                   medianprops=dict(color='#2c3e50', linewidth=2),
                   whiskerprops=dict(linewidth=1.5),
                   capprops=dict(linewidth=1.5))
ax4.set_ylabel('Hallucination Rate (%)', fontsize=11, fontweight='bold')
ax4.set_title('Hallucination Rate Distribution', fontsize=12, fontweight='bold')
ax4.grid(axis='y', alpha=0.3, linestyle='--')
ax4.set_ylim(-5, max(df_filtered['Hallucination_Rate'].max() * 100 + 10, 25))

plt.tight_layout()
plt.savefig(output_dir / 'chart_6_boxplot_metrics.pdf', bbox_inches='tight')
plt.savefig(output_dir / 'chart_6_boxplot_metrics.png', bbox_inches='tight', dpi=300)
print(f"✓ Chart 6 saved: chart_6_boxplot_metrics.pdf and .png")
plt.close()


fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Missing Steps Percentage by Application and Model
missing_pct_data = df.groupby(['Application', 'Model']).apply(
    lambda x: (x['Missing_Steps'].sum() / x['Steps_GT'].sum() * 100)
).unstack()

# Hallucination Percentage by Application and Model
halluc_pct_data = df.groupby(['Application', 'Model']).apply(
    lambda x: (x['Hallucination'].sum() / x['Steps_LLM'].sum() * 100)
).unstack()

x = np.arange(len(missing_pct_data.index))
width = 0.35

# LEFT CHART: MISSING STEPS
bars1 = ax1.bar(x - width/2, missing_pct_data['DeepSeek'], width,
                label='DeepSeek', color='#ffcdd2', alpha=0.9, edgecolor='black', linewidth=1.5)
bars2 = ax1.bar(x + width/2, missing_pct_data['OpenAi'], width,
                label='OpenAI', color='#c62828', alpha=0.9, edgecolor='black', linewidth=1.5)

for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')

ax1.set_xlabel('Application', fontsize=12, fontweight='bold')
ax1.set_ylabel('Missing Steps Rate (%)', fontsize=12, fontweight='bold')
ax1.set_title('Missing Steps Rate by Application and Model', fontsize=14, fontweight='bold', pad=15)
ax1.set_xticks(x)
ax1.set_xticklabels(missing_pct_data.index, fontsize=11)
ax1.legend(fontsize=11)
ax1.grid(axis='y', alpha=0.3, linestyle='--')
ax1.set_ylim(0, max(missing_pct_data.max().max(), halluc_pct_data.max().max()) + 5)

# RIGHT CHART: HALLUCINATION
bars3 = ax2.bar(x - width/2, halluc_pct_data['DeepSeek'], width,
                label='DeepSeek', color='#e1bee7', alpha=0.9, edgecolor='black', linewidth=1.5)
bars4 = ax2.bar(x + width/2, halluc_pct_data['OpenAi'], width,
                label='OpenAI', color='#6a1b9a', alpha=0.9, edgecolor='black', linewidth=1.5)

for bars in [bars3, bars4]:
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')

ax2.set_xlabel('Application', fontsize=12, fontweight='bold')
ax2.set_ylabel('Hallucination Rate (%)', fontsize=12, fontweight='bold')
ax2.set_title('Hallucination Rate by Application and Model', fontsize=14, fontweight='bold', pad=15)
ax2.set_xticks(x)
ax2.set_xticklabels(halluc_pct_data.index, fontsize=11)
ax2.legend(fontsize=11)
ax2.grid(axis='y', alpha=0.3, linestyle='--')
ax2.set_ylim(0, max(missing_pct_data.max().max(), halluc_pct_data.max().max()) + 5)

plt.tight_layout()
plt.savefig(output_dir / 'chart_7_missing_hallucination_combined.pdf', bbox_inches='tight')
plt.savefig(output_dir / 'chart_7_missing_hallucination_combined.png', bbox_inches='tight', dpi=300)
print(f"✓ Chart 7 saved: chart_7_missing_hallucination_combined.pdf and .png")
plt.close()


print("\n" + "=" * 80)
print("OVERALL SUMMARY STATISTICS")
print("=" * 80)

print(f"\nTotal Applications: {df['Application'].nunique()}")
print(f"Total Scenarios: {len(df)}")
print(f"Total GT Steps: {df['Steps_GT'].sum()}")
print(f"Total LLM Steps: {df['Steps_LLM'].sum()}")
print(f"Total Missing Steps: {df['Missing_Steps'].sum()}")
print(f"Total Hallucinations: {df['Hallucination'].sum()}")
print(f"\nOverall Success Rate: {(df['Success'].sum() / len(df) * 100):.2f}%")
print(f"Overall Step Match Rate: {(df['Step_Match_Rate'].mean() * 100):.2f}%")
print(f"Overall Execution Rate: {(df['Exec_Rate'].mean() * 100):.2f}%")


print("\n" + "=" * 80)
print("GENERATING LATEX TABLES")
print("=" * 80)

# Table 1: Overall evaluation results across all applications and models
latex_table1 = """
\\begin{table}[htbp]
    \\centering
    \\setlength{\\tabcolsep}{6pt}
    \\renewcommand{\\arraystretch}{1.1}
    \\footnotesize
    \\begin{tabular}{l r r r r r}
        \\toprule
        \\textbf{App} & \\textbf{\\#Steps (GT)} & \\textbf{\\#Steps (LLM)} & \\textbf{Missing} & \\textbf{Hallucination} & \\textbf{Success (\\%)} \\\\
        \\midrule
"""

for app in sheets:
    for model in ['DeepSeek', 'OpenAi']:
        subset = df[(df['Application'] == app) & (df['Model'] == model)]
        if len(subset) > 0:
            total_gt = int(subset['Steps_GT'].sum())
            total_llm = int(subset['Steps_LLM'].sum())
            missing = int(subset['Missing_Steps'].sum())
            hallucination = int(subset['Hallucination'].sum())
            success_rate = (subset['Success'].sum() / len(subset) * 100)
            
            app_name = app.replace('Checkturio', 'Checkturio')
            model_name = 'GPT-4o' if model == 'OpenAi' else 'DeepSeek'
            
            latex_table1 += f"        {app_name} -- {model_name} & {total_gt} & {total_llm} & {missing} & {hallucination} & {success_rate:.1f} \\\\\n"

total_missing = df['Missing_Steps'].sum()
total_hallucination = df['Hallucination'].sum()
overall_success = (df['Success'].sum() / len(df) * 100)

latex_table1 += f"""        \\midrule
        \\textbf{{Total}} & {df['Steps_GT'].sum()} & {df['Steps_LLM'].sum()} & {total_missing} & {total_hallucination} & \\textbf{{{overall_success:.1f}}} \\\\
        \\bottomrule
    \\end{{tabular}}
    \\caption{{Overall evaluation results across all applications and models. Note: Small differences in GT step counts reflect different test scenarios or manual adjustments.}}
    \\label{{tab:evaluation-summary}}
\\end{{table}}"""

latex_table2 = """
\\begin{table}[htbp]
    \\centering
    \\setlength{\\tabcolsep}{9pt}
    \\renewcommand{\\arraystretch}{1.1}
    \\footnotesize
    \\begin{tabular}{lrrrrr}
        \\toprule
        \\textbf{LLM} & \\textbf{Missing} & \\textbf{Halluc.} & \\textbf{Step Match (\\%)} & \\textbf{Exec. Rate (\\%)} & \\textbf{Scenario Success (\\%)} \\\\
        \\midrule
"""

for model in ['DeepSeek', 'OpenAi']:
    subset = df[df['Model'] == model]
    if len(subset) > 0:
        missing = int(subset['Missing_Steps'].sum())
        hallucination = int(subset['Hallucination'].sum())
        step_match = subset['Step_Match_Rate'].mean() * 100
        exec_rate = subset['Exec_Rate'].mean() * 100
        success_rate = (subset['Success'].sum() / len(subset) * 100)
        
        model_name = 'GPT-4o' if model == 'OpenAi' else 'DeepSeek'
        latex_table2 += f"        {model_name} & {missing} & {hallucination} & {step_match:.1f} & {exec_rate:.1f} & {success_rate:.2f} \\\\\n"

latex_table2 += """        \\bottomrule
    \\end{tabular}
    \\caption{LLM-level summary including execution performance}
    \\label{tab:llm-summary}
\\end{table}"""

# LaTeX tablolarını dosyaya kaydet
with open(output_dir / 'latex_tables.tex', 'w', encoding='utf-8') as f:
    f.write(latex_table1 + "\n\n" + latex_table2)

print("✓ LaTeX tables generated and saved to latex_tables.tex")

print("\n" + "=" * 80)
print(f"✓ All tables and charts saved to '{output_dir}' directory!")
print("Charts generated:")
print("- chart_1_model_success.pdf")
print("- chart_2_application_success.pdf") 
print("- chart_3_missing_hallucination.pdf")
print("- chart_4_matching_execution.pdf")
print("- chart_5_overall_heatmap.pdf")
print("- chart_6_boxplot_metrics.pdf")
print("- chart_7_missing_hallucination_combined.pdf")
print("Tables generated:")
print("- 1_model_comparison.csv")
print("- 2_application_based_success.csv")
print("- 3_missing_steps_hallucination.csv")
print("- 4_step_matching_execution.csv")
print("- latex_tables.tex")
print("=" * 80)

