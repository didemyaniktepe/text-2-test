import json
import pandas as pd

def load_and_analyze_evaluation_data():
    
    with open('bluedt_evaluation_results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    deepseek_deepseek_scores = {
        'scenario_code_alignment': [],
        'code_structure': [],
        'selector_quality': [],
        'best_practices': []
    }
    
    deepseek_openai_scores = {
        'scenario_code_alignment': [],
        'code_structure': [],
        'selector_quality': [],
        'best_practices': []
    }
    
    openai_deepseek_scores = {
        'scenario_code_alignment': [],
        'code_structure': [],
        'selector_quality': [],
        'best_practices': []
    }
    
    openai_openai_scores = {
        'scenario_code_alignment': [],
        'code_structure': [],
        'selector_quality': [],
        'best_practices': []
    }
    
    for test_eval in data['test_evaluations']:
        test_model = test_eval['test_info']['model']
        
        if 'deepseek' in test_eval['evaluations']:
            deepseek_eval = test_eval['evaluations']['deepseek']
            if 'criteria_scores' in deepseek_eval:
                for criteria, score in deepseek_eval['criteria_scores'].items():
                    if test_model == 'deepseek':
                        deepseek_deepseek_scores[criteria].append(score)
                    elif test_model == 'openai':
                        openai_deepseek_scores[criteria].append(score)
        
        if 'openai' in test_eval['evaluations']:
            openai_eval = test_eval['evaluations']['openai']
            if 'criteria_scores' in openai_eval:
                for criteria, score in openai_eval['criteria_scores'].items():
                    if test_model == 'deepseek':
                        deepseek_openai_scores[criteria].append(score)
                    elif test_model == 'openai':
                        openai_openai_scores[criteria].append(score)
    
    def calculate_averages(scores_dict):
        averages = {}
        for criteria, scores in scores_dict.items():
            if scores:
                averages[criteria] = sum(scores) / len(scores)
            else:
                averages[criteria] = 0.0
        return averages
    
    deepseek_deepseek_avg = calculate_averages(deepseek_deepseek_scores)
    deepseek_openai_avg = calculate_averages(deepseek_openai_scores)
    openai_deepseek_avg = calculate_averages(openai_deepseek_scores)
    openai_openai_avg = calculate_averages(openai_openai_scores)
    
    def calc_percentage(avg_dict):
        total = sum(avg_dict.values()) / len(avg_dict)
        return (total / 5.0) * 100
    
    deepseek_deepseek_pct = calc_percentage(deepseek_deepseek_avg)
    deepseek_openai_pct = calc_percentage(deepseek_openai_avg)
    openai_deepseek_pct = calc_percentage(openai_deepseek_avg)
    openai_openai_pct = calc_percentage(openai_openai_avg)
    
    return {
        'deepseek_deepseek': deepseek_deepseek_avg,
        'deepseek_openai': deepseek_openai_avg,
        'openai_deepseek': openai_deepseek_avg,
        'openai_openai': openai_openai_avg,
        'percentages': {
            'deepseek_deepseek': deepseek_deepseek_pct,
            'deepseek_openai': deepseek_openai_pct,
            'openai_deepseek': openai_deepseek_pct,
            'openai_openai': openai_openai_pct
        }
    }

def generate_csv_data():
    
    with open('bluedt_evaluation_results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    csv_rows = []
    
    for test_eval in data['test_evaluations']:
        test_info = test_eval['test_info']
        test_model = test_info['model']
        test_name = test_info['test_name']
        
        if 'deepseek' in test_eval['evaluations']:
            deepseek_eval = test_eval['evaluations']['deepseek']
            if deepseek_eval['success']:
                criteria_scores = deepseek_eval['criteria_scores']
                alignment_summary = deepseek_eval['alignment_summary']
                
                csv_rows.append({
                    'Test_Name': test_name,
                    'Test_Model': test_model,
                    'Evaluator_Model': 'DeepSeek',
                    'Overall_Score': deepseek_eval['overall_score'],
                    'Scenario_Code_Alignment': criteria_scores['scenario_code_alignment'],
                    'Code_Structure': criteria_scores['code_structure'],
                    'Selector_Quality': criteria_scores['selector_quality'],
                    'Best_Practices': criteria_scores['best_practices'],
                    'Alignment_Percentage': alignment_summary.get('alignment_percentage', 0),
                    'Is_Well_Aligned': alignment_summary.get('is_well_aligned', False)
                })
        
        if 'openai' in test_eval['evaluations']:
            openai_eval = test_eval['evaluations']['openai']
            if openai_eval['success']:
                criteria_scores = openai_eval['criteria_scores']
                alignment_summary = openai_eval['alignment_summary']
                
                csv_rows.append({
                    'Test_Name': test_name,
                    'Test_Model': test_model,
                    'Evaluator_Model': 'OpenAI',
                    'Overall_Score': openai_eval['overall_score'],
                    'Scenario_Code_Alignment': criteria_scores['scenario_code_alignment'],
                    'Code_Structure': criteria_scores['code_structure'],
                    'Selector_Quality': criteria_scores['selector_quality'],
                    'Best_Practices': criteria_scores['best_practices'],
                    'Alignment_Percentage': alignment_summary.get('alignment_percentage', 0),
                    'Is_Well_Aligned': alignment_summary.get('is_well_aligned', False)
                })
    
    return pd.DataFrame(csv_rows)

     
if __name__ == "__main__":

    csv_df = generate_csv_data()
    csv_df.to_csv('bluedt_evaluation_results.csv', index=False, encoding='utf-8')
    print("CSV data saved to 'bluedt_evaluation_results.csv'")
    
    results = load_and_analyze_evaluation_data()
    print(f"\nTotal {len(csv_df)} rows of data in CSV")
