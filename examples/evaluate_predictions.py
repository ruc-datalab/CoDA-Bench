"""Example: Evaluate predictions on CoDA-Bench.

Usage:
    python examples/evaluate_predictions.py
"""
from pathlib import Path

from coda_bench import evaluate, load_predictions, load_tasks


def main():
    # Paths
    data_dir = Path("data")
    gold_file = data_dir / "coda_bench.json"
    pred_file = Path("examples/sample_submission.jsonl")

    if not gold_file.exists():
        print(f"❌ Error: Dataset file not found: {gold_file}")
        print("   Please download the dataset first.")
        return

    if not pred_file.exists():
        print(f"❌ Error: Prediction file not found: {pred_file}")
        print("   Please create a sample submission first.")
        return

    # Load data
    print(f"Loading tasks from {gold_file}...")
    tasks = load_tasks(gold_file)

    print(f"Loading predictions from {pred_file}...")
    predictions = load_predictions(pred_file)

    # Evaluate
    print(f"\nEvaluating {len(predictions)} predictions...")
    result = evaluate(tasks, predictions)

    # Print results
    print("\n" + "="*80)
    print("📊 Evaluation Results")
    print("="*80)
    print(f"Total gold tasks: {result.n_gold}")
    print(f"Total predictions: {result.n_pred}")
    print(f"Scored instances: {result.n_scored}")
    print(f"\n✅ Exact Match Accuracy: {result.exact_accuracy:.2%}")
    print(f"   ({result.exact_correct}/{result.n_gold} correct)")
    print(f"\n🔢 Numeric Match Accuracy: {result.numeric_accuracy:.2%}")
    print(f"   ({result.numeric_correct}/{result.n_gold} correct)")

    if result.missing_ids:
        print(f"\n⚠️  Missing predictions: {len(result.missing_ids)}")
        print(f"   Instance IDs: {result.missing_ids[:10]}{'...' if len(result.missing_ids) > 10 else ''}")

    if result.extra_ids:
        print(f"\n⚠️  Extra predictions (not in gold): {len(result.extra_ids)}")
        print(f"   Instance IDs: {result.extra_ids[:10]}{'...' if len(result.extra_ids) > 10 else ''}")

    print("\n" + "="*80)

    # Show some examples
    print("\n📝 Sample Results (first 5):")
    for i, instance in enumerate(result.per_instance[:5], 1):
        status = "✅" if instance["exact_match"] else ("🔢" if instance["numeric_match"] else "❌")
        print(f"\n{status} Instance {instance['instance_id']}:")
        print(f"   Prediction: {instance['prediction']}")
        print(f"   Gold: {instance['gold']}")
        print(f"   Community: {instance['release_community']}")


if __name__ == "__main__":
    main()
