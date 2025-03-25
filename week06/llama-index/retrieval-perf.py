#!/usr/bin/env python3
"""
Retrieval Performance Evaluation Tool

This script evaluates retrieval performance by running multiple test prompts against a codebase
and calculating average recall, precision, and F1 scores.

Usage:
    python retrieval-perf.py <codebase> [-k <top-K>]
"""

import json
import sys
import os
import glob
import argparse
from pathlib import Path

# Import retrieve_chunks from code-rag.py
try:
    from code_rag import retrieve_chunks
except ImportError:
    import importlib.util
    script_dir = os.path.dirname(os.path.abspath(__file__))
    code_rag_path = os.path.join(script_dir, "code-rag.py")
    
    spec = importlib.util.spec_from_file_location("code_rag", code_rag_path)
    code_rag = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(code_rag)
    retrieve_chunks = code_rag.retrieve_chunks

def load_chunks(filename):
    """Load chunks from a JSON file."""
    with open(filename, 'r') as f:
        return json.load(f)

def get_file_line_mapping(chunks):
    """
    Create a mapping from relpath to a set of line numbers contained in the chunks.
    This allows us to track which lines from which files are included in each JSON.
    """
    file_lines = {}
    for chunk in chunks:
        filepath = chunk["relpath"]
        if filepath not in file_lines:
            file_lines[filepath] = set()
        
        # Add all lines in this chunk to the set
        for line_num in range(chunk["start_line"], chunk["end_line"]):
            file_lines[filepath].add(line_num)
    
    return file_lines

def analyze_overlap(file_lines1, file_lines2):
    """
    Analyze the overlap between two sets of files with their line numbers.
    Handles cases where a chunk in file1 may span multiple chunks in file2.
    """
    overlap_count = 0
    only_in_file1_count = 0
    only_in_file2_count = 0
    
    # Get all unique filepaths from both files
    all_filepaths = set(file_lines1.keys()).union(set(file_lines2.keys()))
    
    # Process each filepath
    for filepath in all_filepaths:
        lines1 = file_lines1.get(filepath, set())
        lines2 = file_lines2.get(filepath, set())
        
        # Calculate overlap and exclusive lines for this file
        file_overlap = lines1.intersection(lines2)
        file_only_in_1 = lines1 - lines2
        file_only_in_2 = lines2 - lines1
        
        overlap_count += len(file_overlap)
        only_in_file1_count += len(file_only_in_1)
        only_in_file2_count += len(file_only_in_2)
    
    d = {
        "overlap_count": overlap_count,
        "only_in_file1_count": only_in_file1_count,
        "only_in_file2_count": only_in_file2_count,
        "lines_in_file1": overlap_count + only_in_file1_count,
        "lines_in_file2": overlap_count + only_in_file2_count
    }

    return d

def print_summary(chunks):
    """Print a summary of a chunk set."""
    # Count unique files
    filepaths = set()
    total_lines = 0
    
    for chunk in chunks:
        filepaths.add(chunk["filepath"])
        # Use length field for total lines count
        total_lines += chunk["end_line"] - chunk["start_line"]
    
    print(f"Total number of files: {len(filepaths)}")
    print(f"Total number of chunks: {len(chunks)}")
    print(f"Total number of lines: {total_lines}")

def calculate_metrics(ground_truth_chunks, test_set_chunks):
    """Calculate recall, precision, and F1 score for a pair of chunk sets."""
    # Create mappings of which files and lines are in each set
    ground_truth_file_lines = get_file_line_mapping(ground_truth_chunks)
    test_set_file_lines = get_file_line_mapping(test_set_chunks)
    
    # Analyze the overlap between the two sets
    results = analyze_overlap(ground_truth_file_lines, test_set_file_lines)
    
    # Calculate metrics
    relevant_retrieved = results["overlap_count"]
    ground_truth_lines = results["lines_in_file1"]
    retrieved_lines = results["lines_in_file2"]
    
    # Calculate recall: (relevant lines retrieved) / (ground truth lines)
    if ground_truth_lines == 0:
        recall = 0.0
    else:
        recall = relevant_retrieved / ground_truth_lines
    
    # Calculate precision: (relevant lines retrieved) / (total lines retrieved)
    if retrieved_lines == 0:
        precision = 0.0
    else:
        precision = relevant_retrieved / retrieved_lines
    
    # Calculate F1 score: harmonic mean of precision and recall
    if precision == 0.0 and recall == 0.0:
        f1_score = 0.0
    else:
        f1_score = 2 * ((precision * recall) / (precision + recall))
    
    return {
        "recall": recall,
        "precision": precision,
        "f1": f1_score
    }

def find_prompt_files(codebase_dir):
    """Find all prompt files in the codebase directory following the pattern codebase-q*.txt."""
    # Get the codebase name
    codebase_name = os.path.basename(codebase_dir)
    
    # Find all files matching the pattern codebase-q*.txt
    pattern = os.path.join(codebase_dir, f"{codebase_name}-q*.txt")
    prompt_files = glob.glob(pattern)
    
    return sorted(prompt_files)

def process_prompt_file(prompt_file, top_k):
    """Process a single prompt file, retrieve chunks, and return metrics."""
    # Extract codebase and question number
    base_name = os.path.basename(prompt_file)
    codebase_dir = os.path.dirname(prompt_file)
    codebase_name = base_name.split('-q')[0]
    
    # Remove file extension to get base filename
    q_file_base = os.path.splitext(base_name)[0]
    
    # Load prompt text
    with open(prompt_file, 'r', encoding='utf-8') as f:
        prompt_text = f.read().strip()
    
    print(f"\nProcessing prompt: {prompt_file}")
    print(f"Query: {prompt_text}")
    
    # Get the corresponding .json ground truth file
    ground_truth_file = os.path.join(codebase_dir, f"{q_file_base}.json")
    
    # Check if ground truth file exists
    if not os.path.exists(ground_truth_file):
        print(f"WARNING: Ground truth file {ground_truth_file} not found.")
        return None
    
    # Generate test file path
    test_file = os.path.join(codebase_dir, f"{q_file_base}-test.json")
    
    # Use retrieve_chunks to get results
    db_path = f"{codebase_name}.db"
    results = retrieve_chunks(prompt_text, top_k, db_path)
    
    # Save results to test file
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"Saved retrieval results to {test_file}")
    
    # Load ground truth chunks
    ground_truth_chunks = load_chunks(ground_truth_file)
    
    # Calculate metrics
    metrics = calculate_metrics(ground_truth_chunks, results)
    
    print(f"Metrics for {q_file_base}:")
    print(f"  Recall: {metrics['recall']:.4f}")
    print(f"  Precision: {metrics['precision']:.4f}")
    print(f"  F1: {metrics['f1']:.4f}")
    
    return metrics

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Evaluate retrieval performance for a codebase.")
    parser.add_argument("codebase", help="Codebase directory to process")
    parser.add_argument("-k", "--top-k", type=int, default=5, help="Number of top results to retrieve")
    
    # Handle the old command line format as well
    if len(sys.argv) == 3 and '.json' in sys.argv[1] and '.json' in sys.argv[2]:
        # Old format: python retrieval-perf.py <ground-truth.json> <test-set.json>
        ground_truth_file = sys.argv[1]
        test_set_file = sys.argv[2]
        
        # Load the chunk data from files
        ground_truth_chunks = load_chunks(ground_truth_file)
        test_set_chunks = load_chunks(test_set_file)
        
        # Print summary for each set
        print(f"Ground Truth Summary:")
        print_summary(ground_truth_chunks)
        print()
        
        print(f"Test Set Summary:")
        print_summary(test_set_chunks)
        print()
        
        # Calculate metrics
        metrics = calculate_metrics(ground_truth_chunks, test_set_chunks)
        
        # Print metrics
        print(f"Retrieval Performance Metrics:")
        print(f"Recall: {metrics['recall']:.4f}")
        print(f"Precision: {metrics['precision']:.4f}")
        print(f"F1: {metrics['f1']:.4f}")
        
        return
    
    # Parse arguments for the new format
    args = parser.parse_args()
    
    # Find all prompt files in the codebase directory
    prompt_files = find_prompt_files(args.codebase)
    
    if not prompt_files:
        print(f"No prompt files found in {args.codebase}")
        return
    
    print(f"Found {len(prompt_files)} prompt files in {args.codebase}:")
    for i, file in enumerate(prompt_files):
        print(f"  {i+1}. {os.path.basename(file)}")
    
    # Process each prompt file and collect metrics
    all_metrics = []
    
    for prompt_file in prompt_files:
        metrics = process_prompt_file(prompt_file, args.top_k)
        if metrics:
            all_metrics.append(metrics)
    
    # Calculate average metrics
    if all_metrics:
        avg_recall = sum(m["recall"] for m in all_metrics) / len(all_metrics)
        avg_precision = sum(m["precision"] for m in all_metrics) / len(all_metrics)
        avg_f1 = sum(m["f1"] for m in all_metrics) / len(all_metrics)
        
        print("\n" + "=" * 50)
        print(f"Overall Average Metrics ({len(all_metrics)} prompts):")
        print(f"  Average Recall: {avg_recall:.4f}")
        print(f"  Average Precision: {avg_precision:.4f}")
        print(f"  Average F1: {avg_f1:.4f}")
        print("=" * 50)
    else:
        print("\nNo metrics were calculated. Check that the ground truth files exist.")

if __name__ == "__main__":
    main()