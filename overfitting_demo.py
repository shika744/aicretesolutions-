"""
Overfitting Analysis Demo for AIcrete UHPC Project
Copyright 2025 Shiksha Seechurn / AIcrete

This script demonstrates how to perform overfitting analysis on your UHPC models
to address supervisor feedback about missing overfitting considerations.
"""

import sys
import os
from Training import UHPCPredictor

def run_overfitting_analysis():
    """
    Run comprehensive overfitting analysis on UHPC models
    """
    
    print("🎯 AIcrete UHPC Overfitting Analysis Demo")
    print("=" * 50)
    print("Addressing supervisor feedback: 'Missing overfitting analysis'")
    print()
    
    # Initialize the UHPC predictor
    try:
        # Use your dataset file - adjust path as needed
        data_file = "AI Model Datasets Final with units.xlsx"
        
        if not os.path.exists(data_file):
            print(f"❌ Dataset file not found: {data_file}")
            print("Please ensure the dataset file is in the current directory")
            return
        
        print(f"📊 Loading dataset: {data_file}")
        predictor = UHPCPredictor(data_file)
        
        # Load and prepare data
        print("🔄 Preparing data...")
        predictor.load_and_prepare_data()
        
        # Train basic models first
        print("🤖 Training models...")
        predictor.train_models()
        
        # Now perform overfitting analysis
        print("\n🔍 Starting comprehensive overfitting analysis...")
        predictor.analyze_overfitting()
        
        print("\n✅ Overfitting analysis completed successfully!")
        print("\n📋 What this analysis provides:")
        print("   ✓ Training vs Test performance comparison")
        print("   ✓ Learning curves to visualize overfitting")
        print("   ✓ Cross-validation for robust evaluation")
        print("   ✓ Overfitting risk assessment")
        print("   ✓ Model-specific recommendations")
        
        print("\n📝 Generated files:")
        print("   • overfitting_analysis_*.png - Comparison plots")
        print("   • learning_curves_*.png - Learning curve plots")
        print("   • cv_analysis_*.png - Cross-validation plots")
        
        print("\n🎓 For your research/dissertation:")
        print("   • Include these plots in your methodology section")
        print("   • Discuss overfitting risks and mitigation strategies")
        print("   • Compare model generalization across different properties")
        print("   • Reference cross-validation results for model reliability")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        print("Please check your dataset and try again")


def explain_overfitting():
    """
    Explain what overfitting means and why it's important
    """
    
    print("\n📚 OVERFITTING EXPLAINED - What Your Supervisor Wants")
    print("=" * 60)
    
    print("""
🎯 What is Overfitting?
   Overfitting occurs when a model learns the training data too well,
   memorizing noise and specific patterns rather than general relationships.
   
🚨 Signs of Overfitting:
   • High training accuracy but poor test accuracy
   • Large gap between training and validation performance
   • Model performs well on your dataset but fails on new data
   
🔍 Why It Matters for UHPC Research:
   • Your model must work on NEW concrete mixes, not just your dataset
   • Real-world applicability depends on generalization
   • Industry adoption requires reliable predictions on unseen data
   
✅ How This Analysis Helps:
   • Compares training vs test performance (gap analysis)
   • Shows learning curves to visualize overfitting behavior
   • Provides cross-validation for robust evaluation
   • Gives specific recommendations for each model
   
📊 What to Include in Your Research:
   • Learning curves showing model behavior as data increases
   • Cross-validation scores demonstrating model reliability
   • Discussion of overfitting risks for each property prediction
   • Comparison of model generalization across different UHPC properties
   • Mitigation strategies (regularization, feature selection, etc.)
   
🎓 Academic Impact:
   • Demonstrates understanding of ML best practices
   • Shows critical evaluation of model performance
   • Addresses generalization concerns proactively
   • Provides evidence of rigorous model validation
""")


if __name__ == "__main__":
    # Explain overfitting concept
    explain_overfitting()
    
    # Ask user if they want to run the analysis
    print("\n" + "="*60)
    response = input("Would you like to run the overfitting analysis now? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        run_overfitting_analysis()
    else:
        print("\n📝 To run the analysis later, execute:")
        print("   python overfitting_demo.py")
        print("\n📚 Or integrate into your main training script by calling:")
        print("   predictor.analyze_overfitting()")
