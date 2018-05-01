import json
from db.data.manager import load_json_file

if __name__ == '__main__':
    report = load_json_file('report_closest_search')
    values = [report[thr] for thr in report]
    mean_scores = [x['mean_score'] for x in values]
    max_mean = max(mean_scores)
    print(max_mean)
    print([report[x] for x in report if report[x]['mean_score'] == max_mean])
    print([report[x] for x in report if x == '0.55'])