from pprint import pprint

from app.pipeline.diagnosis_pipeline import DiagnosisPipeline

pipeline = DiagnosisPipeline()

result = pipeline.run(1)

print()

print("="*80)

print("QUERY")

print("="*80)

print(result["query"])

print()

print("="*80)

print("DIAGNOSIS")

print("="*80)

print(result["diagnosis"])

print()

print("="*80)

print("PAPERS")

print("="*80)

for paper in result["evidence"]:

    print()

    print(paper["paper_title"])

    print(paper["paper_id"])