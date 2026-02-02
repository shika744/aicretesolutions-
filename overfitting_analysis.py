"""
Overfitting Analysis Module for AIcrete UHPC Project
Copyright 2025 Shiksha Seechurn / AIcrete

This module provides comprehensive overfitting detection and analysis
for machine learning models in UHPC property prediction.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import learning_curve, validation_curve, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge, Lasso
from sklearn.svm import SVR
import warnings
warnings.filterwarnings('ignore')

class OverfittingAnalyzer:
    """
    Comprehensive overfitting analysis for UHPC prediction models
    """
    
    def __init__(self, X_train, X_test, y_train, y_test, target_name="Property"):
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test
        self.target_name = target_name
        self.results = {}
        
    def analyze_overfitting(self, models=None):
        """
        Complete overfitting analysis including:
        1. Training vs Validation performance
        2. Learning curves
        3. Validation curves
        4. Cross-validation analysis
        """
        
        if models is None:
            models = {
                'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
                'Ridge Regression': Ridge(alpha=1.0),
                'Support Vector Regression': SVR(kernel='rbf', C=1.0)
            }
        
        print(f"🔍 Overfitting Analysis for {self.target_name}")
        print("=" * 60)
        
        # 1. Training vs Test Performance
        self._training_vs_test_analysis(models)
        
        # 2. Learning Curves
        self._plot_learning_curves(models)
        
        # 3. Cross-Validation Analysis
        self._cross_validation_analysis(models)
        
        # 4. Generate Overfitting Report
        self._generate_overfitting_report()
        
        return self.results
    
    def _training_vs_test_analysis(self, models):
        """Compare training vs test performance to detect overfitting"""
        
        print("\n📊 Training vs Test Performance Analysis")
        print("-" * 50)
        
        performance_data = []
        
        for name, model in models.items():
            # Fit model
            model.fit(self.X_train, self.y_train)
            
            # Predictions
            train_pred = model.predict(self.X_train)
            test_pred = model.predict(self.X_test)
            
            # Metrics
            train_r2 = r2_score(self.y_train, train_pred)
            test_r2 = r2_score(self.y_test, test_pred)
            train_rmse = np.sqrt(mean_squared_error(self.y_train, train_pred))
            test_rmse = np.sqrt(mean_squared_error(self.y_test, test_pred))
            
            # Overfitting indicators
            r2_gap = train_r2 - test_r2
            rmse_ratio = test_rmse / train_rmse if train_rmse > 0 else float('inf')
            
            # Store results
            self.results[name] = {
                'train_r2': train_r2,
                'test_r2': test_r2,
                'train_rmse': train_rmse,
                'test_rmse': test_rmse,
                'r2_gap': r2_gap,
                'rmse_ratio': rmse_ratio,
                'overfitting_risk': self._assess_overfitting_risk(r2_gap, rmse_ratio)
            }
            
            performance_data.append({
                'Model': name,
                'Train R²': train_r2,
                'Test R²': test_r2,
                'R² Gap': r2_gap,
                'RMSE Ratio': rmse_ratio,
                'Overfitting Risk': self._assess_overfitting_risk(r2_gap, rmse_ratio)
            })
            
            print(f"{name}:")
            print(f"  Train R²: {train_r2:.4f} | Test R²: {test_r2:.4f} | Gap: {r2_gap:.4f}")
            print(f"  Train RMSE: {train_rmse:.4f} | Test RMSE: {test_rmse:.4f} | Ratio: {rmse_ratio:.2f}")
            print(f"  Overfitting Risk: {self._assess_overfitting_risk(r2_gap, rmse_ratio)}")
            print()
        
        # Create comparison plot
        self._plot_training_vs_test_comparison(performance_data)
        
    def _assess_overfitting_risk(self, r2_gap, rmse_ratio):
        """Assess overfitting risk based on performance gaps"""
        
        if r2_gap > 0.2 or rmse_ratio > 2.0:
            return "🔴 HIGH"
        elif r2_gap > 0.1 or rmse_ratio > 1.5:
            return "🟡 MEDIUM"
        elif r2_gap > 0.05 or rmse_ratio > 1.2:
            return "🟠 LOW"
        else:
            return "🟢 MINIMAL"
    
    def _plot_training_vs_test_comparison(self, performance_data):
        """Plot training vs test performance comparison"""
        
        df = pd.DataFrame(performance_data)
        
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        
        # R² Comparison
        x = np.arange(len(df))
        width = 0.35
        
        axes[0].bar(x - width/2, df['Train R²'], width, label='Training R²', alpha=0.8, color='skyblue')
        axes[0].bar(x + width/2, df['Test R²'], width, label='Test R²', alpha=0.8, color='lightcoral')
        axes[0].set_xlabel('Models')
        axes[0].set_ylabel('R² Score')
        axes[0].set_title(f'Training vs Test R² - {self.target_name}')
        axes[0].set_xticks(x)
        axes[0].set_xticklabels(df['Model'], rotation=45)
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # R² Gap Analysis
        colors = ['red' if gap > 0.1 else 'orange' if gap > 0.05 else 'green' for gap in df['R² Gap']]
        axes[1].bar(x, df['R² Gap'], color=colors, alpha=0.7)
        axes[1].set_xlabel('Models')
        axes[1].set_ylabel('R² Gap (Train - Test)')
        axes[1].set_title('Overfitting Risk Assessment')
        axes[1].set_xticks(x)
        axes[1].set_xticklabels(df['Model'], rotation=45)
        axes[1].axhline(y=0.1, color='orange', linestyle='--', alpha=0.7, label='Medium Risk')
        axes[1].axhline(y=0.2, color='red', linestyle='--', alpha=0.7, label='High Risk')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'overfitting_analysis_{self.target_name.lower().replace(" ", "_")}.png', 
                   dpi=300, bbox_inches='tight')
        plt.show()
    
    def _plot_learning_curves(self, models):
        """Plot learning curves to visualize overfitting"""
        
        print("\n📈 Learning Curves Analysis")
        print("-" * 50)
        
        fig, axes = plt.subplots(1, len(models), figsize=(5*len(models), 5))
        if len(models) == 1:
            axes = [axes]
        
        for idx, (name, model) in enumerate(models.items()):
            train_sizes, train_scores, val_scores = learning_curve(
                model, self.X_train, self.y_train, 
                cv=5, n_jobs=-1, 
                train_sizes=np.linspace(0.1, 1.0, 10),
                scoring='r2'
            )
            
            train_mean = np.mean(train_scores, axis=1)
            train_std = np.std(train_scores, axis=1)
            val_mean = np.mean(val_scores, axis=1)
            val_std = np.std(val_scores, axis=1)
            
            axes[idx].plot(train_sizes, train_mean, 'o-', color='blue', label='Training R²')
            axes[idx].fill_between(train_sizes, train_mean - train_std, train_mean + train_std, 
                                 alpha=0.1, color='blue')
            
            axes[idx].plot(train_sizes, val_mean, 'o-', color='red', label='Validation R²')
            axes[idx].fill_between(train_sizes, val_mean - val_std, val_mean + val_std, 
                                 alpha=0.1, color='red')
            
            axes[idx].set_xlabel('Training Set Size')
            axes[idx].set_ylabel('R² Score')
            axes[idx].set_title(f'Learning Curve - {name}')
            axes[idx].legend()
            axes[idx].grid(True, alpha=0.3)
            
            # Store learning curve data
            self.results[name]['learning_curve'] = {
                'train_sizes': train_sizes,
                'train_scores_mean': train_mean,
                'val_scores_mean': val_mean,
                'final_gap': train_mean[-1] - val_mean[-1]
            }
        
        plt.tight_layout()
        plt.savefig(f'learning_curves_{self.target_name.lower().replace(" ", "_")}.png', 
                   dpi=300, bbox_inches='tight')
        plt.show()
    
    def _cross_validation_analysis(self, models):
        """Perform cross-validation analysis"""
        
        print("\n🔄 Cross-Validation Analysis")
        print("-" * 50)
        
        cv_results = []
        
        for name, model in models.items():
            scores = cross_val_score(model, self.X_train, self.y_train, cv=5, scoring='r2')
            
            cv_results.append({
                'Model': name,
                'CV Mean R²': scores.mean(),
                'CV Std R²': scores.std(),
                'CV Range': f"{scores.min():.3f} - {scores.max():.3f}"
            })
            
            self.results[name]['cv_scores'] = scores
            self.results[name]['cv_mean'] = scores.mean()
            self.results[name]['cv_std'] = scores.std()
            
            print(f"{name}:")
            print(f"  CV R² Mean: {scores.mean():.4f} ± {scores.std():.4f}")
            print(f"  CV Range: {scores.min():.3f} to {scores.max():.3f}")
            print()
        
        # Plot CV results
        self._plot_cv_results(cv_results)
    
    def _plot_cv_results(self, cv_results):
        """Plot cross-validation results"""
        
        df = pd.DataFrame(cv_results)
        
        plt.figure(figsize=(10, 6))
        plt.errorbar(range(len(df)), df['CV Mean R²'], yerr=df['CV Std R²'], 
                    fmt='o', capsize=5, capthick=2, markersize=8)
        
        plt.xlabel('Models')
        plt.ylabel('Cross-Validation R² Score')
        plt.title(f'Cross-Validation Performance - {self.target_name}')
        plt.xticks(range(len(df)), df['Model'], rotation=45)
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'cv_analysis_{self.target_name.lower().replace(" ", "_")}.png', 
                   dpi=300, bbox_inches='tight')
        plt.show()
    
    def _generate_overfitting_report(self):
        """Generate comprehensive overfitting report"""
        
        print("\n📝 Overfitting Analysis Summary")
        print("=" * 60)
        
        for name, results in self.results.items():
            print(f"\n🔍 {name}:")
            print(f"   Training R²: {results['train_r2']:.4f}")
            print(f"   Test R²: {results['test_r2']:.4f}")
            print(f"   R² Gap: {results['r2_gap']:.4f}")
            print(f"   CV Mean R²: {results['cv_mean']:.4f} ± {results['cv_std']:.4f}")
            print(f"   Overfitting Risk: {results['overfitting_risk']}")
            
            # Recommendations
            if results['r2_gap'] > 0.1:
                print(f"   🚨 Recommendation: Consider regularization or feature selection")
            elif results['r2_gap'] > 0.05:
                print(f"   ⚠️  Recommendation: Monitor model complexity")
            else:
                print(f"   ✅ Recommendation: Model appears well-generalized")
        
        # Overall assessment
        avg_gap = np.mean([r['r2_gap'] for r in self.results.values()])
        print(f"\n📊 Overall Analysis:")
        print(f"   Average R² Gap: {avg_gap:.4f}")
        
        if avg_gap > 0.15:
            print(f"   🔴 Overall Assessment: HIGH overfitting risk across models")
        elif avg_gap > 0.08:
            print(f"   🟡 Overall Assessment: MODERATE overfitting risk")
        else:
            print(f"   🟢 Overall Assessment: Models appear well-generalized")


def analyze_all_properties_overfitting(uhpc_trainer):
    """
    Analyze overfitting for all UHPC properties
    """
    
    print("🎯 COMPREHENSIVE OVERFITTING ANALYSIS - ALL UHPC PROPERTIES")
    print("=" * 80)
    
    properties = ['Compressive_Strength', 'Flexural_Strength', 'Tensile_Strength', 'UPV', 'Cost']
    
    for prop in properties:
        if prop in uhpc_trainer.y_train:
            print(f"\n{'='*20} {prop.replace('_', ' ').title()} {'='*20}")
            
            analyzer = OverfittingAnalyzer(
                uhpc_trainer.X_train_scaled,
                uhpc_trainer.X_test_scaled,
                uhpc_trainer.y_train[prop],
                uhpc_trainer.y_test[prop],
                target_name=prop.replace('_', ' ').title()
            )
            
            analyzer.analyze_overfitting()
            
            print(f"\n✅ Overfitting analysis complete for {prop}")
            print("-" * 60)


if __name__ == "__main__":
    print("🔍 Overfitting Analysis Module for AIcrete UHPC Project")
    print("This module helps detect and analyze overfitting in ML models")
    print("Import this module in your main training script to use.")
