#!/usr/bin/env python3
"""
Performance Benchmark for PTIL Semantic Encoder

This script benchmarks the PTIL system's performance in terms of:
- Processing speed
- Token reduction efficiency
- Memory usage
- Tokenizer compatibility
"""

import sys
import os
import time
import tracemalloc
from typing import List, Dict, Any

# Add the parent directory to the path to import ptil
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ptil import (
    PTILEncoder, EfficiencyAnalyzer, TokenizerCompatibilityValidator,
    TokenizerType, EfficiencyMetrics
)


class PerformanceBenchmark:
    """Comprehensive performance benchmark for PTIL encoder."""
    
    def __init__(self):
        """Initialize benchmark with test data and components."""
        self.encoder = None
        self.efficiency_analyzer = None
        self.tokenizer_validator = None
        
        # Test sentences of varying complexity
        self.test_sentences = [
            # Simple sentences
            "The cat sleeps.",
            "She runs fast.",
            "Birds fly high.",
            
            # Medium complexity
            "The boy will not go to school tomorrow.",
            "She carefully placed the book on the table.",
            "Did you see the movie last night?",
            
            # Complex sentences
            "The experienced teacher who had worked at the school for twenty years decided to retire next summer.",
            "Although it was raining heavily, the determined athletes continued their training session in the park.",
            "The innovative technology that was developed by the research team could potentially revolutionize the entire industry.",
            
            # Various sentence types
            "Please close the door quietly.",  # Command
            "What time does the meeting start?",  # Question
            "I think it might rain today.",  # Uncertain
            "Wow, that's amazing!",  # Emotive
            
            # Different domains
            "The patient underwent surgery yesterday.",  # Medical
            "The stock market crashed dramatically.",  # Financial
            "Scientists discovered a new species.",  # Scientific
            "The chef prepared a delicious meal.",  # Culinary
        ]
        
        # Batch test data
        self.batch_sizes = [1, 10, 50, 100]
        
    def initialize_components(self) -> bool:
        """Initialize all PTIL components for benchmarking."""
        print("Initializing PTIL components...")
        
        try:
            self.encoder = PTILEncoder()
            print("   ✓ PTIL Encoder initialized")
        except Exception as e:
            print(f"   ✗ PTIL Encoder failed: {e}")
            return False
        
        try:
            self.efficiency_analyzer = EfficiencyAnalyzer()
            print("   ✓ Efficiency Analyzer initialized")
        except Exception as e:
            print(f"   ✗ Efficiency Analyzer failed: {e}")
            return False
        
        try:
            self.tokenizer_validator = TokenizerCompatibilityValidator()
            print("   ✓ Tokenizer Validator initialized")
        except Exception as e:
            print(f"   ✗ Tokenizer Validator failed: {e}")
            return False
        
        return True
    
    def benchmark_processing_speed(self) -> Dict[str, Any]:
        """Benchmark processing speed for individual sentences and batches."""
        print("\n" + "=" * 60)
        print("PROCESSING SPEED BENCHMARK")
        print("=" * 60)
        
        results = {
            "individual_sentences": [],
            "batch_processing": [],
            "average_speed": 0.0,
            "total_sentences": 0,
            "total_time": 0.0
        }
        
        # Individual sentence processing
        print("\n1. Individual sentence processing:")
        print("-" * 40)
        
        total_time = 0.0
        successful_processes = 0
        
        for i, sentence in enumerate(self.test_sentences):
            print(f"   Sentence {i+1}: '{sentence[:50]}{'...' if len(sentence) > 50 else ''}'")
            
            try:
                start_time = time.time()
                cscs = self.encoder.encode(sentence)
                end_time = time.time()
                
                processing_time = end_time - start_time
                total_time += processing_time
                successful_processes += 1
                
                result = {
                    "sentence": sentence,
                    "processing_time": processing_time,
                    "cscs_generated": len(cscs),
                    "success": True
                }
                
                print(f"     Time: {processing_time:.4f}s, CSCs: {len(cscs)}")
                
            except Exception as e:
                result = {
                    "sentence": sentence,
                    "processing_time": 0.0,
                    "cscs_generated": 0,
                    "success": False,
                    "error": str(e)
                }
                print(f"     ✗ Error: {e}")
            
            results["individual_sentences"].append(result)
        
        # Batch processing
        print("\n2. Batch processing:")
        print("-" * 40)
        
        for batch_size in self.batch_sizes:
            print(f"   Batch size: {batch_size}")
            
            # Create batch
            batch = (self.test_sentences * ((batch_size // len(self.test_sentences)) + 1))[:batch_size]
            
            try:
                start_time = time.time()
                
                batch_results = []
                for sentence in batch:
                    cscs = self.encoder.encode(sentence)
                    batch_results.append(cscs)
                
                end_time = time.time()
                
                batch_time = end_time - start_time
                sentences_per_second = batch_size / batch_time if batch_time > 0 else 0
                
                batch_result = {
                    "batch_size": batch_size,
                    "processing_time": batch_time,
                    "sentences_per_second": sentences_per_second,
                    "success": True
                }
                
                print(f"     Time: {batch_time:.4f}s, Speed: {sentences_per_second:.2f} sent/s")
                
            except Exception as e:
                batch_result = {
                    "batch_size": batch_size,
                    "processing_time": 0.0,
                    "sentences_per_second": 0.0,
                    "success": False,
                    "error": str(e)
                }
                print(f"     ✗ Error: {e}")
            
            results["batch_processing"].append(batch_result)
        
        # Calculate overall statistics
        if successful_processes > 0:
            results["average_speed"] = successful_processes / total_time if total_time > 0 else 0
            results["total_sentences"] = successful_processes
            results["total_time"] = total_time
            
            print(f"\n   Overall average: {results['average_speed']:.2f} sentences/second")
        
        return results
    
    def benchmark_token_efficiency(self) -> Dict[str, Any]:
        """Benchmark token reduction efficiency."""
        print("\n" + "=" * 60)
        print("TOKEN EFFICIENCY BENCHMARK")
        print("=" * 60)
        
        results = {
            "sentence_results": [],
            "overall_metrics": None,
            "efficiency_summary": {}
        }
        
        print("\n1. Individual sentence efficiency:")
        print("-" * 40)
        
        all_metrics = []
        
        for i, sentence in enumerate(self.test_sentences):
            print(f"   Sentence {i+1}: '{sentence[:50]}{'...' if len(sentence) > 50 else ''}'")
            
            try:
                # Analyze efficiency
                metrics = self.efficiency_analyzer.analyze_efficiency(sentence, self.encoder)
                all_metrics.append(metrics)
                
                result = {
                    "sentence": sentence,
                    "metrics": metrics,
                    "success": True
                }
                
                print(f"     Original tokens: {metrics.original_tokens}")
                print(f"     CSC tokens: {metrics.csc_tokens}")
                print(f"     Reduction: {metrics.reduction_percentage:.1f}%")
                print(f"     Compression ratio: {metrics.compression_ratio:.2f}")
                
            except Exception as e:
                result = {
                    "sentence": sentence,
                    "metrics": None,
                    "success": False,
                    "error": str(e)
                }
                print(f"     ✗ Error: {e}")
            
            results["sentence_results"].append(result)
        
        # Calculate overall metrics
        if all_metrics:
            print("\n2. Overall efficiency metrics:")
            print("-" * 40)
            
            try:
                overall_metrics = self.efficiency_analyzer.calculate_aggregate_metrics(all_metrics)
                results["overall_metrics"] = overall_metrics
                
                print(f"   Average original tokens: {overall_metrics.original_tokens:.1f}")
                print(f"   Average CSC tokens: {overall_metrics.csc_tokens:.1f}")
                print(f"   Average reduction: {overall_metrics.reduction_percentage:.1f}%")
                print(f"   Average compression ratio: {overall_metrics.compression_ratio:.2f}")
                
                # Efficiency categories
                excellent_count = sum(1 for m in all_metrics if m.reduction_percentage >= 70)
                good_count = sum(1 for m in all_metrics if 60 <= m.reduction_percentage < 70)
                fair_count = sum(1 for m in all_metrics if 40 <= m.reduction_percentage < 60)
                poor_count = sum(1 for m in all_metrics if m.reduction_percentage < 40)
                
                results["efficiency_summary"] = {
                    "excellent": excellent_count,
                    "good": good_count,
                    "fair": fair_count,
                    "poor": poor_count,
                    "total": len(all_metrics)
                }
                
                print(f"\n   Efficiency distribution:")
                print(f"     Excellent (≥70%): {excellent_count}")
                print(f"     Good (60-69%): {good_count}")
                print(f"     Fair (40-59%): {fair_count}")
                print(f"     Poor (<40%): {poor_count}")
                
            except Exception as e:
                print(f"   ✗ Overall metrics calculation failed: {e}")
        
        return results
    
    def benchmark_tokenizer_compatibility(self) -> Dict[str, Any]:
        """Benchmark compatibility with different tokenizers."""
        print("\n" + "=" * 60)
        print("TOKENIZER COMPATIBILITY BENCHMARK")
        print("=" * 60)
        
        results = {
            "tokenizer_results": {},
            "compatibility_summary": {}
        }
        
        tokenizer_types = [TokenizerType.BPE, TokenizerType.UNIGRAM, TokenizerType.WORDPIECE]
        
        for tokenizer_type in tokenizer_types:
            print(f"\n1. Testing {tokenizer_type.value} tokenizer:")
            print("-" * 40)
            
            tokenizer_results = []
            successful_tests = 0
            
            for i, sentence in enumerate(self.test_sentences):
                print(f"   Sentence {i+1}: '{sentence[:30]}{'...' if len(sentence) > 30 else ''}'")
                
                try:
                    # Get CSC serialization
                    serialized = self.encoder.encode_and_serialize(sentence)
                    
                    # Test compatibility
                    compatibility_result = self.tokenizer_validator.validate_compatibility(
                        serialized, tokenizer_type
                    )
                    
                    result = {
                        "sentence": sentence,
                        "serialized": serialized,
                        "compatibility_result": compatibility_result,
                        "success": True
                    }
                    
                    if compatibility_result.is_compatible:
                        print(f"     ✓ Compatible, tokens: {compatibility_result.token_count}")
                        successful_tests += 1
                    else:
                        print(f"     ✗ Incompatible: {compatibility_result.error_message}")
                    
                except Exception as e:
                    result = {
                        "sentence": sentence,
                        "serialized": "",
                        "compatibility_result": None,
                        "success": False,
                        "error": str(e)
                    }
                    print(f"     ✗ Error: {e}")
                
                tokenizer_results.append(result)
            
            results["tokenizer_results"][tokenizer_type.value] = tokenizer_results
            
            # Summary for this tokenizer
            total_tests = len(self.test_sentences)
            compatibility_rate = successful_tests / total_tests * 100 if total_tests > 0 else 0
            
            print(f"\n   {tokenizer_type.value} Summary:")
            print(f"     Compatible: {successful_tests}/{total_tests} ({compatibility_rate:.1f}%)")
            
            results["compatibility_summary"][tokenizer_type.value] = {
                "compatible": successful_tests,
                "total": total_tests,
                "rate": compatibility_rate
            }
        
        return results
    
    def benchmark_memory_usage(self) -> Dict[str, Any]:
        """Benchmark memory usage during processing."""
        print("\n" + "=" * 60)
        print("MEMORY USAGE BENCHMARK")
        print("=" * 60)
        
        results = {
            "baseline_memory": 0,
            "peak_memory": 0,
            "memory_per_sentence": [],
            "batch_memory": []
        }
        
        # Start memory tracing
        tracemalloc.start()
        
        # Baseline memory
        baseline_snapshot = tracemalloc.take_snapshot()
        baseline_memory = sum(stat.size for stat in baseline_snapshot.statistics('lineno'))
        results["baseline_memory"] = baseline_memory
        
        print(f"\n1. Baseline memory usage: {baseline_memory / 1024 / 1024:.2f} MB")
        
        # Individual sentence memory usage
        print("\n2. Memory usage per sentence:")
        print("-" * 40)
        
        peak_memory = baseline_memory
        
        for i, sentence in enumerate(self.test_sentences[:10]):  # Test first 10 for memory
            print(f"   Sentence {i+1}: '{sentence[:30]}{'...' if len(sentence) > 30 else ''}'")
            
            try:
                # Take snapshot before processing
                before_snapshot = tracemalloc.take_snapshot()
                before_memory = sum(stat.size for stat in before_snapshot.statistics('lineno'))
                
                # Process sentence
                cscs = self.encoder.encode(sentence)
                serialized = self.encoder.encode_and_serialize(sentence)
                
                # Take snapshot after processing
                after_snapshot = tracemalloc.take_snapshot()
                after_memory = sum(stat.size for stat in after_snapshot.statistics('lineno'))
                
                memory_used = after_memory - before_memory
                peak_memory = max(peak_memory, after_memory)
                
                result = {
                    "sentence": sentence,
                    "memory_before": before_memory,
                    "memory_after": after_memory,
                    "memory_used": memory_used,
                    "success": True
                }
                
                print(f"     Memory used: {memory_used / 1024:.2f} KB")
                
            except Exception as e:
                result = {
                    "sentence": sentence,
                    "memory_before": 0,
                    "memory_after": 0,
                    "memory_used": 0,
                    "success": False,
                    "error": str(e)
                }
                print(f"     ✗ Error: {e}")
            
            results["memory_per_sentence"].append(result)
        
        results["peak_memory"] = peak_memory
        
        print(f"\n3. Peak memory usage: {peak_memory / 1024 / 1024:.2f} MB")
        print(f"   Memory increase: {(peak_memory - baseline_memory) / 1024 / 1024:.2f} MB")
        
        # Stop memory tracing
        tracemalloc.stop()
        
        return results
    
    def run_full_benchmark(self) -> Dict[str, Any]:
        """Run complete performance benchmark suite."""
        print("=== PTIL PERFORMANCE BENCHMARK ===\n")
        
        if not self.initialize_components():
            print("Failed to initialize components. Benchmark aborted.")
            return {}
        
        benchmark_results = {}
        
        try:
            # Speed benchmark
            benchmark_results["speed"] = self.benchmark_processing_speed()
        except Exception as e:
            print(f"Speed benchmark failed: {e}")
            benchmark_results["speed"] = {"error": str(e)}
        
        try:
            # Efficiency benchmark
            benchmark_results["efficiency"] = self.benchmark_token_efficiency()
        except Exception as e:
            print(f"Efficiency benchmark failed: {e}")
            benchmark_results["efficiency"] = {"error": str(e)}
        
        try:
            # Tokenizer compatibility benchmark
            benchmark_results["compatibility"] = self.benchmark_tokenizer_compatibility()
        except Exception as e:
            print(f"Compatibility benchmark failed: {e}")
            benchmark_results["compatibility"] = {"error": str(e)}
        
        try:
            # Memory usage benchmark
            benchmark_results["memory"] = self.benchmark_memory_usage()
        except Exception as e:
            print(f"Memory benchmark failed: {e}")
            benchmark_results["memory"] = {"error": str(e)}
        
        # Print summary
        self.print_benchmark_summary(benchmark_results)
        
        return benchmark_results
    
    def print_benchmark_summary(self, results: Dict[str, Any]):
        """Print a summary of all benchmark results."""
        print("\n" + "=" * 60)
        print("BENCHMARK SUMMARY")
        print("=" * 60)
        
        # Speed summary
        if "speed" in results and "error" not in results["speed"]:
            speed_data = results["speed"]
            if speed_data.get("average_speed", 0) > 0:
                print(f"   Processing Speed: {speed_data['average_speed']:.2f} sentences/second")
            else:
                print("   Processing Speed: Unable to calculate")
        
        # Efficiency summary
        if "efficiency" in results and "error" not in results["efficiency"]:
            efficiency_data = results["efficiency"]
            if efficiency_data.get("overall_metrics"):
                metrics = efficiency_data["overall_metrics"]
                print(f"   Token Reduction: {metrics.reduction_percentage:.1f}% average")
                print(f"   Compression Ratio: {metrics.compression_ratio:.2f}x")
        
        # Compatibility summary
        if "compatibility" in results and "error" not in results["compatibility"]:
            compat_data = results["compatibility"]
            if compat_data.get("compatibility_summary"):
                for tokenizer, summary in compat_data["compatibility_summary"].items():
                    print(f"   {tokenizer} Compatibility: {summary['rate']:.1f}%")
        
        # Memory summary
        if "memory" in results and "error" not in results["memory"]:
            memory_data = results["memory"]
            baseline = memory_data.get("baseline_memory", 0)
            peak = memory_data.get("peak_memory", 0)
            if baseline > 0 and peak > 0:
                print(f"   Memory Usage: {(peak - baseline) / 1024 / 1024:.2f} MB increase")
        
        print("\n=== BENCHMARK COMPLETE ===")


def main():
    """Run the performance benchmark."""
    benchmark = PerformanceBenchmark()
    results = benchmark.run_full_benchmark()
    
    # Optionally save results to file
    try:
        import json
        with open("benchmark_results.json", "w") as f:
            # Convert any non-serializable objects to strings
            serializable_results = json.loads(json.dumps(results, default=str))
            json.dump(serializable_results, f, indent=2)
        print(f"\nBenchmark results saved to benchmark_results.json")
    except Exception as e:
        print(f"Failed to save results: {e}")


if __name__ == "__main__":
    main()