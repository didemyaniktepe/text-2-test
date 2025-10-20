import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['figure.figsize'] = (12, 6)

COLORS = {
    'primary': '#2E86AB',
    'secondary': '#A23B72',
    'success': '#06A77D',
    'warning': '#F18F01',
    'danger': '#C73E1D',
    'info': '#6C757D'
}

sns.set_palette("husl")
sns.set_style("whitegrid")

def parse_fraction(value):
    if pd.isna(value) or value == 'NaN':
        return None
    try:
        if isinstance(value, str) and '/' in value:
            parts = value.split('/')
            return float(parts[0]) / float(parts[1])
        return float(value)
    except:
        return None

def load_all_data():
    excel_file = 'Step Decomposition.xlsx'
    data = {}
    
    sheets = ['BLUDIT', 'Checkturio', 'ToDo', 'SauceDemo']
    
    for sheet in sheets:
        df = pd.read_excel(excel_file, sheet_name=sheet)
        data[sheet] = df
        
    return data

def create_output_dir():
    output_dir = Path('thesis_charts')
    output_dir.mkdir(exist_ok=True)
    return output_dir

def calculate_statistics(data):
    stats = []
    
    for app_name, df in data.items():
        if 'Per-Step Exec. Rate (1st try)' in df.columns:
            df['exec_rate'] = df['Per-Step Exec. Rate (1st try)'].apply(parse_fraction)
        
        success_count = df['Scenario Success'].value_counts().get('Yes', 0)
        total_scenarios = len(df[df['Scenario Success'].notna()])
        success_rate = (success_count / total_scenarios * 100) if total_scenarios > 0 else 0
        
        if 'Hallucination Step Rate' in df.columns:
            df['hallucination'] = df['Hallucination Step Rate'].apply(parse_fraction)
            avg_hallucination = df['hallucination'].mean() * 100 if df['hallucination'].notna().any() else 0
        else:
            avg_hallucination = 0
        
        avg_steps = df['#Steps (GT)'].mean() if '#Steps (GT)' in df.columns else 0
        
        avg_exec_rate = df['exec_rate'].mean() * 100 if 'exec_rate' in df.columns and df['exec_rate'].notna().any() else 0
        
        stats.append({
            'Application': app_name,
            'Total Scenarios': len(df),
            'Success Rate (%)': success_rate,
            'Avg Steps per Scenario': avg_steps,
            'Avg Execution Rate (%)': avg_exec_rate,
            'Avg Hallucination Rate (%)': avg_hallucination
        })
    
    return pd.DataFrame(stats)

def plot_success_rates(data, output_dir):
    fig, ax = plt.subplots(figsize=(10, 6))
    
    success_data = []
    for app_name, df in data.items():
        success = df['Scenario Success'].value_counts()
        success_rate = (success.get('Yes', 0) / len(df[df['Scenario Success'].notna()])) * 100
        success_data.append({'Application': app_name, 'Success Rate': success_rate})
    
    success_df = pd.DataFrame(success_data)
    
    bars = ax.bar(success_df['Application'], success_df['Success Rate'], 
                  color=[COLORS['success'], COLORS['primary'], COLORS['secondary'], COLORS['warning']])
    
    ax.set_ylabel('Success Rate (%)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Application', fontsize=12, fontweight='bold')
    ax.set_title('Scenario Success Rates by Application', fontsize=14, fontweight='bold', pad=20)
    ax.set_ylim(0, 100)
    
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_dir / '1_success_rates_by_application.png', bbox_inches='tight')
    print(f"✓ Chart 1 saved: Success Rates by Application")
    plt.close()

def plot_steps_distribution(data, output_dir):
    fig, ax = plt.subplots(figsize=(12, 6))
    
    positions = []
    labels = []
    all_steps = []
    
    for i, (app_name, df) in enumerate(data.items()):
        if '#Steps (GT)' in df.columns:
            steps = df['#Steps (GT)'].dropna()
            positions.extend([i] * len(steps))
            labels.append(app_name)
            all_steps.extend(steps)
    
    apps_data = [data[app]['#Steps (GT)'].dropna() for app in data.keys() if '#Steps (GT)' in data[app].columns]
    bp = ax.boxplot(apps_data, labels=list(data.keys()), patch_artist=True,
                    showmeans=True, meanline=True)
    
    colors = [COLORS['success'], COLORS['primary'], COLORS['secondary'], COLORS['warning']]
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax.set_ylabel('Number of Steps', fontsize=12, fontweight='bold')
    ax.set_xlabel('Application', fontsize=12, fontweight='bold')
    ax.set_title('Distribution of Steps per Scenario Across Applications', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / '2_steps_distribution.png', bbox_inches='tight')
    print(f"✓ Chart 2 saved: Steps Distribution")
    plt.close()

def plot_execution_rates(data, output_dir):
    fig, ax = plt.subplots(figsize=(12, 7))
    
    exec_data = []
    for app_name, df in data.items():
        if 'Per-Step Exec. Rate (1st try)' in df.columns:
            df['exec_rate'] = df['Per-Step Exec. Rate (1st try)'].apply(parse_fraction)
            for idx, row in df.iterrows():
                if pd.notna(row['exec_rate']):
                    exec_data.append({
                        'Application': app_name,
                        'Scenario': row['Scenario'],
                        'Execution Rate': row['exec_rate'] * 100
                    })
    
    exec_df = pd.DataFrame(exec_data)
    
    sns.violinplot(data=exec_df, x='Application', y='Execution Rate', ax=ax,
                   palette=[COLORS['success'], COLORS['primary'], COLORS['secondary'], COLORS['warning']])
    
    ax.set_ylabel('Execution Rate (%)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Application', fontsize=12, fontweight='bold')
    ax.set_title('Per-Step Execution Rate Distribution (First Try)', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_ylim(0, 105)
    
    plt.tight_layout()
    plt.savefig(output_dir / '3_execution_rates.png', bbox_inches='tight')
    print(f"✓ Chart 3 saved: Execution Rate Distribution")
    plt.close()

def plot_hallucination_rates(data, output_dir):
    fig, ax = plt.subplots(figsize=(10, 6))
    
    hall_data = []
    for app_name, df in data.items():
        if 'Hallucination Step Rate' in df.columns:
            df['hallucination'] = df['Hallucination Step Rate'].apply(parse_fraction)
            avg_hall = df['hallucination'].mean() * 100 if df['hallucination'].notna().any() else 0
            hall_data.append({'Application': app_name, 'Hallucination Rate': avg_hall})
    
    hall_df = pd.DataFrame(hall_data)
    
    bars = ax.bar(hall_df['Application'], hall_df['Hallucination Rate'],
                  color=[COLORS['danger'], COLORS['warning'], COLORS['info'], COLORS['secondary']])
    
    ax.set_ylabel('Hallucination Rate (%)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Application', fontsize=12, fontweight='bold')
    ax.set_title('Average Hallucination Rate by Application', 
                 fontsize=14, fontweight='bold', pad=20)
    
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}%',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_dir / '4_hallucination_rates.png', bbox_inches='tight')
    print(f"✓ Chart 4 saved: Hallucination Rates")
    plt.close()

def plot_scenario_complexity(data, output_dir):
    fig, ax = plt.subplots(figsize=(12, 7))
    
    complexity_data = []
    for app_name, df in data.items():
        if '#Steps (GT)' in df.columns and 'Per-Step Exec. Rate (1st try)' in df.columns:
            df['exec_rate'] = df['Per-Step Exec. Rate (1st try)'].apply(parse_fraction)
            for idx, row in df.iterrows():
                if pd.notna(row['exec_rate']) and pd.notna(row['#Steps (GT)']):
                    complexity_data.append({
                        'Application': app_name,
                        'Steps': row['#Steps (GT)'],
                        'Execution Rate': row['exec_rate'] * 100,
                        'Success': 1 if row['Scenario Success'] == 'Yes' else 0
                    })
    
    comp_df = pd.DataFrame(complexity_data)
    
    for app_name in comp_df['Application'].unique():
        app_data = comp_df[comp_df['Application'] == app_name]
        
        success_data = app_data[app_data['Success'] == 1]
        fail_data = app_data[app_data['Success'] == 0]
        
        ax.scatter(success_data['Steps'], success_data['Execution Rate'], 
                  label=f'{app_name} (Success)', s=100, alpha=0.7, marker='o')
        ax.scatter(fail_data['Steps'], fail_data['Execution Rate'], 
                  label=f'{app_name} (Failure)', s=100, alpha=0.7, marker='x')
    
    ax.set_xlabel('Number of Steps (Complexity)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Execution Rate (%)', fontsize=12, fontweight='bold')
    ax.set_title('Scenario Complexity vs Execution Rate', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / '5_complexity_vs_success.png', bbox_inches='tight')
    print(f"✓ Chart 5 saved: Complexity vs Success")
    plt.close()

def plot_comparative_metrics(stats_df, output_dir):
    fig, ax = plt.subplots(figsize=(10, 6))
    
    numeric_cols = ['Success Rate (%)', 'Avg Steps per Scenario', 
                    'Avg Execution Rate (%)', 'Avg Hallucination Rate (%)']
    
    heatmap_data = stats_df[['Application'] + numeric_cols].set_index('Application')
    
    heatmap_normalized = (heatmap_data - heatmap_data.min()) / (heatmap_data.max() - heatmap_data.min())
    
    sns.heatmap(heatmap_normalized.T, annot=heatmap_data.T, fmt='.2f', 
                cmap='RdYlGn', center=0.5, ax=ax, cbar_kws={'label': 'Normalized Value'})
    
    ax.set_title('Comparative Metrics Heatmap Across Applications', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Application', fontsize=12, fontweight='bold')
    ax.set_ylabel('Metrics', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_dir / '6_comparative_metrics_heatmap.png', bbox_inches='tight')
    print(f"✓ Chart 6 saved: Comparative Metrics Heatmap")
    plt.close()

def plot_success_failure_breakdown(data, output_dir):
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()
    
    for idx, (app_name, df) in enumerate(data.items()):
        success_counts = df['Scenario Success'].value_counts()
        
        colors_pie = [COLORS['success'] if label == 'Yes' else COLORS['danger'] 
                      for label in success_counts.index]
        
        wedges, texts, autotexts = axes[idx].pie(success_counts, 
                                                   labels=['Success' if x == 'Yes' else 'Failure' 
                                                          for x in success_counts.index],
                                                   autopct='%1.1f%%', startangle=90,
                                                   colors=colors_pie)
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(11)
        
        axes[idx].set_title(f'{app_name}\n({len(df)} scenarios)', 
                           fontsize=12, fontweight='bold')
    
    plt.suptitle('Success/Failure Distribution by Application', 
                 fontsize=14, fontweight='bold', y=1.00)
    plt.tight_layout()
    plt.savefig(output_dir / '7_success_failure_breakdown.png', bbox_inches='tight')
    print(f"✓ Chart 7 saved: Success/Failure Breakdown")
    plt.close()

def plot_model_comparison(data, output_dir):
    all_data = []
    for app_name, df in data.items():
        if 'Model' in df.columns:
            df_copy = df.copy()
            df_copy['Application'] = app_name
            all_data.append(df_copy)
    
    if not all_data:
        print("⚠ Chart 8 skipped: No Model column found")
        return
    
    combined_df = pd.concat(all_data, ignore_index=True)
    
    model_stats = []
    for model in combined_df['Model'].unique():
        model_data = combined_df[combined_df['Model'] == model]
        success_rate = (model_data['Scenario Success'] == 'Yes').sum() / len(model_data) * 100
        model_stats.append({'Model': model, 'Success Rate': success_rate, 'Total Scenarios': len(model_data)})
    
    model_df = pd.DataFrame(model_stats)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(range(len(model_df)), model_df['Success Rate'], color=COLORS['primary'])
    ax.set_xticks(range(len(model_df)))
    ax.set_xticklabels(model_df['Model'])
    
    ax.set_ylabel('Success Rate (%)', fontsize=12, fontweight='bold')
    ax.set_xlabel('AI Model', fontsize=12, fontweight='bold')
    ax.set_title('AI Model Performance Comparison', fontsize=14, fontweight='bold', pad=20)
    ax.set_ylim(0, 100)
    
    for bar, total in zip(bars, model_df['Total Scenarios']):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%\n(n={total})',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_dir / '8_model_comparison.png', bbox_inches='tight')
    print(f"✓ Chart 8 saved: Model Performance Comparison")
    plt.close()

def generate_statistics_table(stats_df, output_dir):
    latex_table = stats_df.to_latex(index=False, float_format="%.2f", 
                                     caption="Comparative Statistics Across Applications",
                                     label="tab:step_decomposition_stats")
    
    with open(output_dir / 'statistics_table.tex', 'w') as f:
        f.write(latex_table)
    
    stats_df.to_csv(output_dir / 'statistics_table.csv', index=False)
    
    print(f"✓ Statistics table saved (CSV and LaTeX)")

def generate_summary_report(data, stats_df, output_dir):
    report = []
    report.append("# Step Decomposition Analysis Report")
    report.append("\n## Executive Summary\n")
    
    total_scenarios = sum(len(df) for df in data.values())
    total_success = sum((df['Scenario Success'] == 'Yes').sum() for df in data.values())
    overall_success_rate = (total_success / total_scenarios) * 100
    
    report.append(f"- **Total Scenarios Analyzed**: {total_scenarios}")
    report.append(f"- **Overall Success Rate**: {overall_success_rate:.2f}%")
    report.append(f"- **Applications Tested**: {len(data)}")
    report.append(f"\n## Application-wise Summary\n")
    
    for _, row in stats_df.iterrows():
        report.append(f"\n### {row['Application']}")
        report.append(f"- Total Scenarios: {row['Total Scenarios']}")
        report.append(f"- Success Rate: {row['Success Rate (%)']:.2f}%")
        report.append(f"- Average Steps: {row['Avg Steps per Scenario']:.2f}")
        report.append(f"- Average Execution Rate: {row['Avg Execution Rate (%)']:.2f}%")
        report.append(f"- Average Hallucination Rate: {row['Avg Hallucination Rate (%)']:.2f}%")
    
    report.append("\n## Charts Generated\n")
    report.append("1. Success Rates by Application")
    report.append("2. Steps Distribution Comparison")
    report.append("3. Execution Rate Distribution")
    report.append("4. Hallucination Rate Analysis")
    report.append("5. Complexity vs Success Scatter Plot")
    report.append("6. Comparative Metrics Heatmap")
    report.append("7. Success/Failure Breakdown")
    report.append("8. Model Performance Comparison")
    
    report_text = '\n'.join(report)
    
    with open(output_dir / 'ANALYSIS_REPORT.md', 'w') as f:
        f.write(report_text)
    
    print(f"✓ Summary report saved")
    return report_text

def main():
    print("="*60)
    print("Step Decomposition Analysis for Thesis")
    print("="*60)
    print()
    
    print("Loading data from Excel...")
    data = load_all_data()
    print(f"✓ Loaded {len(data)} applications")
    print()
    
    output_dir = create_output_dir()
    print(f"✓ Output directory: {output_dir}")
    print()
    
    print("Calculating statistics...")
    stats_df = calculate_statistics(data)
    print(stats_df.to_string())
    print()
    
    print("\nGenerating charts...")
    print("-" * 60)
    
    plot_success_rates(data, output_dir)
    plot_steps_distribution(data, output_dir)
    plot_execution_rates(data, output_dir)
    plot_hallucination_rates(data, output_dir)
    plot_scenario_complexity(data, output_dir)
    plot_comparative_metrics(stats_df, output_dir)
    plot_success_failure_breakdown(data, output_dir)
    plot_model_comparison(data, output_dir)
    
    print("-" * 60)
    print()
    
    print("Generating statistics tables...")
    generate_statistics_table(stats_df, output_dir)
    print()

    print("Generating summary report...")
    report = generate_summary_report(data, stats_df, output_dir)
    print()
    
    print(f"Analysis complete! All files saved in: {output_dir}/")


if __name__ == '__main__':
    main()

