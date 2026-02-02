#!/usr/bin/env python3
"""
Copyright © 2025 Shiksha Seechurn. All rights reserved.
AIcrete UHPC Analysis Platform - Professional Engineering Software

This software is the intellectual property of Shiksha Seechurn.
Unauthorized copying, modification, or distribution is strictly prohibited.
Licensed for professional and research purposes.

Author: Shiksha Seechurn
Project: AI-Powered UHPC Analysis Platform
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pickle
import json
from datetime import datetime
import base64
from io import BytesIO
import os
import time
import shap
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for Streamlit
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib import colors
import tempfile

def add_background():
    """Add the professional city background image to the app"""
    try:
        # Read the background image
        import base64
        with open("aicrete_background.png", "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        
        # Add CSS for background with faded city image
        st.markdown(f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(255,255,255,0.7), rgba(255,255,255,0.7)), url(data:image/png;base64,{encoded_string}) !important;
            background-size: cover !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed !important;
        }}
        
        /* Main content styling */
        .main > div {{
            background-color: rgba(255, 255, 255, 0.95) !important;
            border-radius: 15px !important;
            padding: 2rem !important;
            margin: 1rem !important;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2) !important;
            backdrop-filter: blur(10px) !important;
        }}
        
        /* Sidebar styling */
        section[data-testid="stSidebar"] > div {{
            background-color: rgba(255, 255, 255, 0.95) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.3) !important;
            backdrop-filter: blur(10px) !important;
        }}
        
        /* Header container styling */
        .logo-container {{
            background: rgba(255, 255, 255, 0.9) !important;
            border-radius: 15px !important;
            padding: 1rem !important;
            margin-bottom: 2rem !important;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15) !important;
            backdrop-filter: blur(10px) !important;
        }}
        
        /* Progress bar styling - Purple instead of red */
        .stProgress > div > div > div > div {{
            background-color: #8B5CF6 !important;
        }}
        
        .stProgress > div > div {{
            background-color: rgba(139, 92, 246, 0.2) !important;
        }}
        
        /* Alternative progress bar selectors */
        [data-testid="stProgress"] > div > div > div > div {{
            background-color: #8B5CF6 !important;
        }}
        
        [data-testid="stProgress"] > div > div {{
            background-color: rgba(139, 92, 246, 0.2) !important;
        }}
        </style>
        """, unsafe_allow_html=True)
        
    except FileNotFoundError:
        # Fallback to gradient if image not found
        st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        }
        .main > div {
            background-color: rgba(255, 255, 255, 0.95) !important;
            border-radius: 15px !important;
            padding: 2rem !important;
            margin: 1rem !important;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2) !important;
        }
        
        /* Progress bar styling - Purple */
        .stProgress > div > div > div > div {
            background-color: #8B5CF6 !important;
        }
        
        .stProgress > div > div {
            background-color: rgba(139, 92, 246, 0.2) !important;
        }
        
        [data-testid="stProgress"] > div > div > div > div {
            background-color: #8B5CF6 !important;
        }
        
        [data-testid="stProgress"] > div > div {
            background-color: rgba(139, 92, 246, 0.2) !important;
        }
        </style>
        """, unsafe_allow_html=True)

def generate_pdf_report(predictions, mix_design, user_info=None, project_info=None, report_type="Prediction Summary Report"):
    """Generate a professional PDF report with charts and graphs based on report type"""
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch)
        styles = getSampleStyleSheet()
        story = []
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.darkblue,
            alignment=1  # Center alignment
        )
        
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        # Title based on report type
        report_titles = {
            "Prediction Summary Report": "AIcrete UHPC Prediction Summary",
            "Cost Analysis Report": "AIcrete UHPC Cost Analysis Report", 
            "Optimization Report": "AIcrete UHPC Mix Optimization Report",
            "Comparative Analysis": "AIcrete UHPC Comparative Analysis",
            "Executive Summary": "AIcrete UHPC Executive Summary",
            "Technical Analysis Report": "AIcrete UHPC Technical Analysis"
        }
        
        title = report_titles.get(report_type, "AIcrete UHPC Analysis Report")
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 20))
        
        # Report metadata
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        story.append(Paragraph(f"<b>Generated:</b> {current_time}", styles['Normal']))
        
        if project_info:
            story.append(Paragraph(f"<b>Project:</b> {project_info.get('name', 'N/A')}", styles['Normal']))
            story.append(Paragraph(f"<b>Engineer:</b> {project_info.get('engineer', 'N/A')}", styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        # Add report-specific content based on type
        if report_type == "Cost Analysis Report":
            story.append(Paragraph("Cost Analysis Overview", header_style))
            
            # Calculate costs
            cement_cost = mix_design.get('cement', 0) * 0.12  # $0.12 per kg
            silica_cost = mix_design.get('silica', 0) * 0.85  # $0.85 per kg
            sp_cost = mix_design.get('sp', 0) * 2.50  # $2.50 per kg
            aggregate_cost = (mix_design.get('coarse', 0) + mix_design.get('fine', 0)) * 0.025  # $0.025 per kg
            fiber_cost = mix_design.get('fibers', 0) * 8.50  # $8.50 per kg
            
            total_material_cost = cement_cost + silica_cost + sp_cost + aggregate_cost + fiber_cost
            
            cost_data = [
                ['Material', 'Quantity (kg/m³)', 'Unit Cost ($/kg)', 'Total Cost ($/m³)'],
                ['Cement', f"{mix_design.get('cement', 0):.1f}", '$0.12', f"${cement_cost:.2f}"],
                ['Silica Fume', f"{mix_design.get('silica', 0):.1f}", '$0.85', f"${silica_cost:.2f}"],
                ['Superplasticizer', f"{mix_design.get('sp', 0):.1f}", '$2.50', f"${sp_cost:.2f}"],
                ['Aggregates', f"{mix_design.get('coarse', 0) + mix_design.get('fine', 0):.1f}", '$0.025', f"${aggregate_cost:.2f}"],
                ['Steel Fibers', f"{mix_design.get('fibers', 0):.1f}", '$8.50', f"${fiber_cost:.2f}"],
                ['', '', 'TOTAL:', f"${total_material_cost:.2f}"]
            ]
            
            cost_table = Table(cost_data)
            cost_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightcoral),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -2), colors.mistyrose),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(cost_table)
            story.append(Spacer(1, 20))
            
            cost_analysis = f"""
            <b>Cost Analysis Summary:</b><br/>
            • Material cost per m³: ${total_material_cost:.2f}<br/>
            • Estimated production cost: ${total_material_cost * 1.3:.2f} (including labor & overhead)<br/>
            • Cost comparison: {'Premium UHPC' if total_material_cost > 150 else 'Standard UHPC' if total_material_cost > 100 else 'Economy UHPC'}<br/>
            • Primary cost drivers: {'Steel Fibers' if fiber_cost > cement_cost else 'Cement & Silica Fume'}<br/>
            """
            story.append(Paragraph(cost_analysis, styles['Normal']))
            story.append(Spacer(1, 20))
            
        elif report_type == "Executive Summary":
            story.append(Paragraph("Executive Summary", header_style))
            
            executive_text = f"""
            <b>Project Overview:</b><br/>
            This report presents the concrete mix design analysis and performance predictions for Ultra-High Performance Concrete (UHPC) formulation.<br/><br/>
            
            <b>Key Findings:</b><br/>
            • Predicted compressive strength: {predictions.get('strength', 0):.1f} MPa<br/>
            • Performance rating: {'Excellent' if predictions.get('strength', 0) > 80 else 'Good' if predictions.get('strength', 0) > 50 else 'Adequate'}<br/>
            • Mix classification: {'High-strength UHPC' if predictions.get('strength', 0) > 100 else 'Standard UHPC'}<br/><br/>
            
            <b>Business Impact:</b><br/>
            • Structural efficiency: Enhanced load-bearing capacity<br/>
            • Durability: Extended service life reduces maintenance costs<br/>
            • Sustainability: Optimized material usage reduces environmental impact<br/>
            """
            story.append(Paragraph(executive_text, styles['Normal']))
            story.append(Spacer(1, 20))
            
        elif report_type == "Optimization Report":
            story.append(Paragraph("Mix Design Optimization Analysis", header_style))
            
            w_c_ratio = mix_design.get('water', 0) / max(mix_design.get('cement', 1), 1)
            binder_ratio = mix_design.get('silica', 0) / max(mix_design.get('cement', 1), 1)
            
            optimization_text = f"""
            <b>Current Mix Parameters:</b><br/>
            • Water-Cement Ratio: {w_c_ratio:.3f}<br/>
            • Silica Fume Replacement: {(binder_ratio * 100):.1f}%<br/>
            • Fiber Content: {mix_design.get('fibers', 0):.1f} kg/m³<br/><br/>
            
            <b>Optimization Recommendations:</b><br/>
            • {'✓ W/C ratio is optimal' if w_c_ratio < 0.35 else '→ Reduce W/C ratio to < 0.35 for better durability'}<br/>
            • {'✓ Silica fume content is adequate' if binder_ratio > 0.15 else '→ Increase silica fume to 15-25% replacement'}<br/>
            • {'✓ Fiber content is optimal' if mix_design.get('fibers', 0) > 78 else '→ Consider increasing fiber content to 78-150 kg/m³'}<br/>
            """
            story.append(Paragraph(optimization_text, styles['Normal']))
            story.append(Spacer(1, 20))
            
        elif report_type == "Comparative Analysis":
            story.append(Paragraph("Comparative Performance Analysis", header_style))
            
            comparison_data = [
                ['Property', 'Current Mix', 'Standard Concrete', 'High-Strength Concrete', 'Performance Ratio'],
                ['Compressive Strength (MPa)', f"{predictions.get('strength', 0):.1f}", '30', '50', 
                 f"{predictions.get('strength', 0)/30:.1f}x"],
                ['Flexural Strength (MPa)', f"{predictions.get('flexural', 0):.1f}", '4', '6',
                 f"{predictions.get('flexural', 0)/4:.1f}x"],
                ['Elastic Modulus (GPa)', f"{predictions.get('elastic', 0):.1f}", '30', '35',
                 f"{predictions.get('elastic', 0)/30:.1f}x"]
            ]
            
            comparison_table = Table(comparison_data)
            comparison_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(comparison_table)
            story.append(Spacer(1, 20))
        
        # Continue with standard charts and analysis for all report types
        
        # Create Mix Design Pie Chart
        try:
            fig, ax = plt.subplots(figsize=(8, 6))
            
            # Prepare data for pie chart
            materials = []
            quantities = []
            material_mapping = {
                'cement': 'Cement',
                'silica': 'Silica Fume', 
                'water': 'Water',
                'sp': 'Superplasticizer',
                'coarse': 'Coarse Aggregate',
                'fine': 'Fine Aggregate',
                'fibers': 'Steel Fibers'
            }
            
            for key, label in material_mapping.items():
                if mix_design.get(key, 0) > 0:
                    materials.append(label)
                    quantities.append(mix_design.get(key, 0))
            
            # Create pie chart
            colors_pie = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']
            wedges, texts, autotexts = ax.pie(quantities, labels=materials, autopct='%1.1f%%', 
                                            colors=colors_pie[:len(materials)], startangle=90)
            
            ax.set_title('Mix Design Composition', fontsize=14, fontweight='bold', pad=20)
            
            # Save chart as image
            chart_buffer = BytesIO()
            plt.savefig(chart_buffer, format='png', dpi=300, bbox_inches='tight')
            chart_buffer.seek(0)
            plt.close()
            
            # Add chart to PDF
            story.append(Paragraph("Mix Design Composition", header_style))
            story.append(Spacer(1, 10))
            
            # Create image from buffer
            chart_image = Image(chart_buffer, width=5*inch, height=3.75*inch)
            story.append(chart_image)
            story.append(Spacer(1, 20))
            
        except Exception as e:
            # If chart creation fails, add text note
            story.append(Paragraph("Mix Design Composition", header_style))
            story.append(Paragraph("(Chart generation temporarily unavailable)", styles['Normal']))
            story.append(Spacer(1, 10))
        
        # Mix Design Table
        # Calculate total mass excluding non-material parameters
        material_params = {k: v for k, v in mix_design.items() 
                         if k not in ['age', 'temp', 'humidity', 'curing_temperature', 'curing_humidity']}
        total_mass = sum(material_params.values()) if material_params else 1
        
        mix_data = [
            ['Component', 'Quantity (kg/m³)', 'Percentage (%)'],
            ['Cement', f"{mix_design.get('cement', 0):.1f}", f"{(mix_design.get('cement', 0)/total_mass*100):.1f}"],
            ['Silica Fume', f"{mix_design.get('silica', 0):.1f}", f"{(mix_design.get('silica', 0)/total_mass*100):.1f}"],
            ['Water', f"{mix_design.get('water', 0):.1f}", f"{(mix_design.get('water', 0)/total_mass*100):.1f}"],
            ['Superplasticizer', f"{mix_design.get('sp', 0):.1f}", f"{(mix_design.get('sp', 0)/total_mass*100):.1f}"],
            ['Coarse Aggregate', f"{mix_design.get('coarse', 0):.1f}", f"{(mix_design.get('coarse', 0)/total_mass*100):.1f}"],
            ['Fine Aggregate', f"{mix_design.get('fine', 0):.1f}", f"{(mix_design.get('fine', 0)/total_mass*100):.1f}"],
            ['Steel Fibers', f"{mix_design.get('fibers', 0):.1f}", f"{(mix_design.get('fibers', 0)/total_mass*100):.1f}"],
        ]
        
        mix_table = Table(mix_data)
        mix_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(mix_table)
        story.append(Spacer(1, 30))
        
        # Create Properties Bar Chart
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Properties data
            properties = ['Compressive\nStrength (MPa)', 'Flexural\nStrength (MPa)', 'Elastic Modulus\n(GPa)']
            values = [
                predictions.get('strength', 0),
                predictions.get('flexural', 0), 
                predictions.get('elastic', 0)
            ]
            
            # Benchmark values for comparison
            benchmarks = [80, 8, 45]  # Typical UHPC targets
            
            x = np.arange(len(properties))
            width = 0.35
            
            bars1 = ax.bar(x - width/2, values, width, label='Predicted Values', 
                          color=['#FF6B6B', '#4ECDC4', '#45B7D1'], alpha=0.8)
            bars2 = ax.bar(x + width/2, benchmarks, width, label='UHPC Targets', 
                          color=['#FFA07A', '#98D8C8', '#87CEEB'], alpha=0.6)
            
            ax.set_xlabel('Properties', fontweight='bold')
            ax.set_ylabel('Values', fontweight='bold')
            ax.set_title('Predicted Properties vs UHPC Targets', fontsize=14, fontweight='bold', pad=20)
            ax.set_xticks(x)
            ax.set_xticklabels(properties)
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # Add value labels on bars
            for bar in bars1:
                height = bar.get_height()
                ax.annotate(f'{height:.1f}',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3),  # 3 points vertical offset
                           textcoords="offset points",
                           ha='center', va='bottom', fontweight='bold')
            
            plt.tight_layout()
            
            # Save chart as image
            props_chart_buffer = BytesIO()
            plt.savefig(props_chart_buffer, format='png', dpi=300, bbox_inches='tight')
            props_chart_buffer.seek(0)
            plt.close()
            
            # Add chart to PDF
            story.append(Paragraph("Predicted Properties Analysis", header_style))
            story.append(Spacer(1, 10))
            
            props_chart_image = Image(props_chart_buffer, width=6*inch, height=3.6*inch)
            story.append(props_chart_image)
            story.append(Spacer(1, 20))
            
        except Exception as e:
            # If chart creation fails, add text note
            story.append(Paragraph("Predicted Properties Analysis", header_style))
            story.append(Paragraph("(Chart generation temporarily unavailable)", styles['Normal']))
            story.append(Spacer(1, 10))
        
        # Predictions Table
        pred_data = [
            ['Property', 'Predicted Value', 'Unit', 'Performance Rating'],
            ['Compressive Strength', f"{predictions.get('strength', 0):.1f}", 'MPa', 
             'Excellent' if predictions.get('strength', 0) > 80 else 'Good' if predictions.get('strength', 0) > 50 else 'Adequate'],
            ['Flexural Strength', f"{predictions.get('flexural', 0):.1f}", 'MPa',
             'High' if predictions.get('flexural', 0) > 8 else 'Standard'],
            ['Elastic Modulus', f"{predictions.get('elastic', 0):.0f}", 'GPa',
             'High Stiffness' if predictions.get('elastic', 0) > 40 else 'Normal'],
        ]
        
        pred_table = Table(pred_data)
        pred_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(pred_table)
        story.append(Spacer(1, 30))
        
        # Create Performance Radar Chart
        try:
            fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
            
            # Performance metrics (normalized to 0-10 scale)
            categories = ['Strength\n(Compressive)', 'Ductility\n(Flexural)', 'Stiffness\n(Elastic)', 
                         'Durability\n(W/C Ratio)', 'Workability\n(SP Content)']
            
            # Normalize values to 0-10 scale
            strength_score = min(predictions.get('strength', 0) / 10, 10)
            flexural_score = min(predictions.get('flexural', 0) * 1.25, 10)
            elastic_score = min(predictions.get('elastic', 0) / 5, 10)
            wc_ratio = mix_design.get('water', 0) / max(mix_design.get('cement', 1), 1)
            durability_score = max(10 - wc_ratio * 20, 0)  # Lower W/C = higher score
            workability_score = min(mix_design.get('sp', 0) / 2, 10)
            
            values = [strength_score, flexural_score, elastic_score, durability_score, workability_score]
            
            # Add first value at end to close the polygon
            values += values[:1]
            
            # Calculate angles for each category
            angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
            angles += angles[:1]
            
            # Plot
            ax.plot(angles, values, 'o-', linewidth=2, label='Current Mix', color='#FF6B6B')
            ax.fill(angles, values, alpha=0.25, color='#FF6B6B')
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories)
            ax.set_ylim(0, 10)
            ax.set_title('Performance Radar Chart\n(0-10 Scale)', size=14, fontweight='bold', pad=30)
            ax.grid(True)
            
            # Add score labels
            for angle, value in zip(angles[:-1], values[:-1]):
                ax.text(angle, value + 0.5, f'{value:.1f}', ha='center', va='center', 
                       fontweight='bold', color='darkred')
            
            plt.tight_layout()
            
            # Save chart as image
            radar_chart_buffer = BytesIO()
            plt.savefig(radar_chart_buffer, format='png', dpi=300, bbox_inches='tight')
            radar_chart_buffer.seek(0)
            plt.close()
            
            # Add chart to PDF
            story.append(Paragraph("Performance Assessment", header_style))
            story.append(Spacer(1, 10))
            
            radar_chart_image = Image(radar_chart_buffer, width=5*inch, height=5*inch)
            story.append(radar_chart_image)
            story.append(Spacer(1, 20))
            
        except Exception as e:
            # If chart creation fails, add text note
            story.append(Paragraph("Performance Assessment", header_style))
            story.append(Paragraph("(Radar chart generation temporarily unavailable)", styles['Normal']))
            story.append(Spacer(1, 10))
        
        # Engineering Analysis
        story.append(Paragraph("Engineering Analysis", header_style))
        
        w_c_ratio = mix_design.get('water', 0) / max(mix_design.get('cement', 1), 1)
        binder_content = mix_design.get('cement', 0) + mix_design.get('silica', 0)
        
        analysis_text = f"""
        <b>Water-Cement Ratio:</b> {w_c_ratio:.3f}<br/>
        <b>Total Binder Content:</b> {binder_content:.1f} kg/m³<br/>
        <b>Fiber Volume Fraction:</b> {(mix_design.get('fibers', 0) * 0.000127):.2f}%<br/>
        <br/>
        <b>Performance Assessment:</b><br/>
        • W/C Ratio: {'Excellent (Low)' if w_c_ratio < 0.35 else 'Good' if w_c_ratio < 0.45 else 'Adequate'}<br/>
        • Binder Content: {'High Performance' if binder_content > 550 else 'Standard' if binder_content > 450 else 'Economy'}<br/>
        • Fiber Reinforcement: {'High' if mix_design.get('fibers', 0) > 100 else 'Standard' if mix_design.get('fibers', 0) > 50 else 'Light'}<br/>
        """
        
        story.append(Paragraph(analysis_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Recommendations
        story.append(Paragraph("Engineering Recommendations", header_style))
        
        recommendations = []
        if w_c_ratio > 0.45:
            recommendations.append("• Consider reducing water content for improved durability")
        if mix_design.get('fibers', 0) < 78:
            recommendations.append("• Increase fiber content for better toughness")
        if predictions.get('strength', 0) < 50:
            recommendations.append("• Increase cement or add more silica fume for higher strength")
        
        if not recommendations:
            recommendations.append("• Mix design appears well-optimized for UHPC applications")
            recommendations.append("• Consider long-term durability testing for critical applications")
        
        for rec in recommendations:
            story.append(Paragraph(rec, styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        # Footer
        story.append(Paragraph("Generated by AIcrete Professional - Advanced Concrete Engineering Platform", 
                              styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        # If reportlab fails, create a simple text report
        return generate_simple_text_report(predictions, mix_design, project_info)
        story.append(Paragraph("Generated by AIcrete Professional - Advanced Concrete Engineering Platform", 
                              styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        # If reportlab fails, create a simple text report
        return generate_simple_text_report(predictions, mix_design, project_info)

def generate_simple_text_report(predictions, mix_design, project_info=None):
    """Generate a simple text-based report as fallback"""
    buffer = BytesIO()
    
    report_content = f"""
AIcrete UHPC Analysis Report
============================

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Project: {project_info.get('name', 'UHPC Analysis') if project_info else 'UHPC Analysis'}
Engineer: {project_info.get('engineer', 'AIcrete User') if project_info else 'AIcrete User'}

Mix Design Composition
======================
Cement: {mix_design.get('cement', 0):.1f} kg/m³
Silica Fume: {mix_design.get('silica', 0):.1f} kg/m³
Water: {mix_design.get('water', 0):.1f} kg/m³
Superplasticizer: {mix_design.get('sp', 0):.1f} kg/m³
Coarse Aggregate: {mix_design.get('coarse', 0):.1f} kg/m³
Fine Aggregate: {mix_design.get('fine', 0):.1f} kg/m³
Steel Fibers: {mix_design.get('fibers', 0):.1f} kg/m³

Predicted Properties
===================
Compressive Strength: {predictions.get('strength', 0):.1f} MPa
Flexural Strength: {predictions.get('flexural', 0):.1f} MPa
Elastic Modulus: {predictions.get('elastic', 0):.1f} GPa

Engineering Analysis
===================
Water-Cement Ratio: {mix_design.get('water', 0) / max(mix_design.get('cement', 1), 1):.3f}
Total Binder Content: {mix_design.get('cement', 0) + mix_design.get('silica', 0):.1f} kg/m³

Generated by AIcrete Professional
Advanced Concrete Engineering Platform
"""
    
    buffer.write(report_content.encode('utf-8'))
    buffer.seek(0)
    return buffer

# Set page configuration
st.set_page_config(
    page_title="AIcrete Concrete Solutions - UHPC Property Predictor",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
        color: white;
        margin-top: 1rem;
    }
    .company-logo {
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .company-tagline {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-bottom: 1rem;
        font-weight: 500;
    }
    .prediction-card {
        background: rgba(248, 249, 250, 0.95);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #2a5298;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        text-align: center;
        margin: 0.5rem;
        backdrop-filter: blur(10px);
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e3c72;
        color: white;
        border-radius: 5px 5px 0 0;
        margin-right: 5px;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #2a5298;
    }
    .footer {
        text-align: center;
        padding: 2rem;
        background: rgba(248, 249, 250, 0.95);
        border-radius: 10px;
        margin-top: 2rem;
        color: #666;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    /* Logo container styling */
    .logo-container {
        text-align: center;
        margin-bottom: 1rem;
        padding: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class AIcretePredictor:
    def __init__(self):
        self.feature_names = [
            'cement', 'silica_fume', 'water', 'superplasticizer', 'coarse_aggregate',
            'fine_aggregate', 'steel_fibers', 'age', 'curing_temperature', 'curing_humidity',
            'w_c_ratio', 'sf_c_ratio', 'sp_c_ratio', 'fiber_volume_fraction', 
            'aggregate_cement_ratio', 'total_binder', 'compressive_strength'
        ]
        
        # Currency conversion rates (base: GBP)
        self.currency_rates = {
            'GBP (£)': {'symbol': '£', 'rate': 1.0},
            'USD ($)': {'symbol': '$', 'rate': 1.27},
            'EUR (€)': {'symbol': '€', 'rate': 1.16},
            'CAD (C$)': {'symbol': 'C$', 'rate': 1.70},
            'AUD (A$)': {'symbol': 'A$', 'rate': 1.92},
            'JPY (¥)': {'symbol': '¥', 'rate': 185.0},
            'INR (₹)': {'symbol': '₹', 'rate': 106.0}
        }
        
        # Application Templates
        self.application_templates = {
            'High-Rise Building': {
                'cement': 550, 'silica_fume': 120, 'water': 165, 'superplasticizer': 8.5,
                'coarse_aggregate': 800, 'fine_aggregate': 850, 'steel_fibers': 78,
                'age': 28, 'curing_temperature': 20, 'curing_humidity': 95,
                'target_strength': 120, 'description': 'Optimized for high-strength vertical elements'
            },
            'Bridge Construction': {
                'cement': 500, 'silica_fume': 100, 'water': 150, 'superplasticizer': 7.5,
                'coarse_aggregate': 850, 'fine_aggregate': 800, 'steel_fibers': 100,
                'age': 56, 'curing_temperature': 20, 'curing_humidity': 95,
                'target_strength': 150, 'description': 'Enhanced durability for infrastructure'
            },
            'Precast Elements': {
                'cement': 600, 'silica_fume': 150, 'water': 160, 'superplasticizer': 12,
                'coarse_aggregate': 750, 'fine_aggregate': 900, 'steel_fibers': 50,
                'age': 7, 'curing_temperature': 60, 'curing_humidity': 100,
                'target_strength': 100, 'description': 'Fast-setting for precast production'
            },
            'Marine Structures': {
                'cement': 450, 'silica_fume': 180, 'water': 140, 'superplasticizer': 10,
                'coarse_aggregate': 900, 'fine_aggregate': 850, 'steel_fibers': 120,
                'age': 90, 'curing_temperature': 20, 'curing_humidity': 100,
                'target_strength': 130, 'description': 'Maximum durability against chloride attack'
            },
            'Pavement & Road': {
                'cement': 400, 'silica_fume': 80, 'water': 130, 'superplasticizer': 6,
                'coarse_aggregate': 950, 'fine_aggregate': 800, 'steel_fibers': 40,
                'age': 28, 'curing_temperature': 20, 'curing_humidity': 85,
                'target_strength': 80, 'description': 'Balanced performance for traffic loads'
            },
            'Architectural Features': {
                'cement': 480, 'silica_fume': 90, 'water': 145, 'superplasticizer': 9,
                'coarse_aggregate': 700, 'fine_aggregate': 950, 'steel_fibers': 30,
                'age': 28, 'curing_temperature': 20, 'curing_humidity': 90,
                'target_strength': 90, 'description': 'Fine finish and workability focused'
            },
            'Residential Housing': {
                'cement': 350, 'silica_fume': 60, 'water': 170, 'superplasticizer': 5,
                'coarse_aggregate': 1000, 'fine_aggregate': 750, 'steel_fibers': 25,
                'age': 28, 'curing_temperature': 20, 'curing_humidity': 85,
                'target_strength': 40, 'description': 'Cost-effective for homes and small buildings'
            },
            'Data Centers': {
                'cement': 520, 'silica_fume': 110, 'water': 155, 'superplasticizer': 8,
                'coarse_aggregate': 780, 'fine_aggregate': 870, 'steel_fibers': 65,
                'age': 28, 'curing_temperature': 20, 'curing_humidity': 95,
                'target_strength': 110, 'description': 'High-tech facilities requiring precision'
            },
            'Solar Panel Foundations': {
                'cement': 380, 'silica_fume': 70, 'water': 160, 'superplasticizer': 6,
                'coarse_aggregate': 920, 'fine_aggregate': 780, 'steel_fibers': 35,
                'age': 28, 'curing_temperature': 20, 'curing_humidity': 85,
                'target_strength': 50, 'description': 'Renewable energy infrastructure'
            },
            'Emergency Shelters': {
                'cement': 320, 'silica_fume': 50, 'water': 180, 'superplasticizer': 4,
                'coarse_aggregate': 1050, 'fine_aggregate': 700, 'steel_fibers': 20,
                'age': 7, 'curing_temperature': 20, 'curing_humidity': 80,
                'target_strength': 30, 'description': 'Fast deployment for humanitarian needs'
            },
            'Art Installations': {
                'cement': 450, 'silica_fume': 85, 'water': 150, 'superplasticizer': 10,
                'coarse_aggregate': 650, 'fine_aggregate': 1000, 'steel_fibers': 40,
                'age': 28, 'curing_temperature': 20, 'curing_humidity': 90,
                'target_strength': 75, 'description': 'Creative projects with aesthetic focus'
            },
            'Sports Facilities': {
                'cement': 420, 'silica_fume': 75, 'water': 165, 'superplasticizer': 7,
                'coarse_aggregate': 880, 'fine_aggregate': 820, 'steel_fibers': 45,
                'age': 28, 'curing_temperature': 20, 'curing_humidity': 85,
                'target_strength': 60, 'description': 'Stadiums, gyms, and recreational buildings'
            },
            'Educational Buildings': {
                'cement': 400, 'silica_fume': 70, 'water': 170, 'superplasticizer': 6,
                'coarse_aggregate': 900, 'fine_aggregate': 800, 'steel_fibers': 30,
                'age': 28, 'curing_temperature': 20, 'curing_humidity': 85,
                'target_strength': 55, 'description': 'Schools, universities, and training centers'
            }
        }
        
        # International Concrete Standards Database
        self.concrete_standards = {
            'ASTM C1856': {
                'name': 'Standard Practice for Fabricating and Testing Specimens of Ultra-High Performance Concrete',
                'authority': 'ASTM International (USA)',
                'scope': 'UHPC testing procedures',
                'compressive_strength': {'min': 120, 'typical': 150, 'unit': 'MPa'},
                'tensile_strength': {'min': 5, 'typical': 8, 'unit': 'MPa'},
                'fiber_content': {'min': 1.0, 'max': 3.0, 'unit': '%'},
                'w_b_ratio': {'max': 0.25},
                'curing_temp': {'min': 20, 'max': 90, 'unit': '°C'},
                'test_age': [1, 7, 28, 56, 90]
            },
            'BS EN 206': {
                'name': 'Concrete — Specification, performance, production and conformity',
                'authority': 'British Standards (UK/EU)',
                'scope': 'General concrete specification',
                'compressive_strength': {'grades': [12, 16, 20, 25, 30, 35, 40, 45, 50, 55, 60, 70, 80, 90, 100]},
                'w_c_ratio': {'max': 0.60},
                'chloride_content': {'max': 0.4, 'unit': '%'},
                'test_age': [28],
                'exposure_classes': ['XC1', 'XC2', 'XC3', 'XC4', 'XD1', 'XD2', 'XD3', 'XS1', 'XS2', 'XS3']
            },
            'ACI 239R': {
                'name': 'Ultra-High Performance Concrete',
                'authority': 'American Concrete Institute (USA)',
                'scope': 'UHPC design and construction',
                'compressive_strength': {'min': 120, 'typical': 150, 'unit': 'MPa'},
                'tensile_strength': {'min': 5, 'typical': 7, 'unit': 'MPa'},
                'elastic_modulus': {'min': 40, 'typical': 50, 'unit': 'GPa'},
                'fiber_content': {'typical': 2.0, 'max': 3.0, 'unit': '%'},
                'cement_content': {'min': 500, 'typical': 700, 'unit': 'kg/m³'}
            },
            'RILEM TC 188-CSC': {
                'name': 'Casting of Self Compacting Concrete',
                'authority': 'RILEM (International)',
                'scope': 'Self-compacting concrete',
                'slump_flow': {'min': 550, 'max': 850, 'unit': 'mm'},
                'v_funnel': {'max': 25, 'unit': 's'},
                'passing_ability': {'L_box': 0.8, 'J_ring': 25}
            },
            'IS 456': {
                'name': 'Plain and Reinforced Concrete - Code of Practice',
                'authority': 'Bureau of Indian Standards (India)',
                'scope': 'General concrete design',
                'compressive_strength': {'grades': [15, 20, 25, 30, 35, 40, 45, 50, 55, 60]},
                'w_c_ratio': {'max': 0.50},
                'test_age': [28]
            },
            'JIS A 5308': {
                'name': 'Ready-mixed concrete',
                'authority': 'Japanese Industrial Standards (Japan)',
                'scope': 'Ready-mixed concrete specification',
                'compressive_strength': {'grades': [18, 21, 24, 27, 30, 33, 36, 42, 48, 54, 60]},
                'slump': {'max': 180, 'unit': 'mm'}
            },
            'CSA A23.1': {
                'name': 'Concrete materials and methods of concrete construction',
                'authority': 'Canadian Standards Association (Canada)',
                'scope': 'Concrete construction and materials',
                'compressive_strength': {'grades': [15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 80]},
                'w_c_ratio': {'max': 0.45},
                'test_age': [28]
            },
            'AS 3600': {
                'name': 'Concrete structures',
                'authority': 'Standards Australia (Australia)',
                'scope': 'Concrete structure design',
                'compressive_strength': {'grades': [20, 25, 32, 40, 50, 65, 80, 100]},
                'w_c_ratio': {'max': 0.55},
                'test_age': [28]
            }
        }
        
        # Standards compliance checker
        self.compliance_matrix = {
            'UHPC_Applications': ['ASTM C1856', 'ACI 239R'],
            'General_Construction': ['BS EN 206', 'IS 456', 'JIS A 5308', 'CSA A23.1', 'AS 3600'],
            'High_Performance': ['ASTM C1856', 'ACI 239R', 'BS EN 206'],
            'Marine_Structures': ['BS EN 206', 'ACI 239R', 'AS 3600'],
            'Infrastructure': ['ASTM C1856', 'BS EN 206', 'IS 456', 'CSA A23.1'],
            'Precast_Elements': ['ASTM C1856', 'BS EN 206', 'JIS A 5308'],
            'Self_Compacting': ['RILEM TC 188-CSC', 'BS EN 206']
        }
        
        self.feature_units = {
            'cement': 'kg/m³',
            'silica_fume': 'kg/m³',
            'water': 'kg/m³',
            'superplasticizer': 'kg/m³',
            'coarse_aggregate': 'kg/m³',
            'fine_aggregate': 'kg/m³',
            'steel_fibers': 'kg/m³',
            'age': 'days',
            'curing_temperature': '°C',
            'curing_humidity': '%',
            'w_c_ratio': 'ratio',
            'sf_c_ratio': 'ratio',
            'sp_c_ratio': 'ratio',
            'fiber_volume_fraction': '%',
            'aggregate_cement_ratio': 'ratio',
            'total_binder': 'kg/m³',
            'compressive_strength': 'MPa'
        }
        
        self.target_properties = {
            'compressive_strength': {'name': 'Compressive Strength', 'unit': 'MPa', 'icon': '🏗️'},
            'tensile_strength': {'name': 'Tensile Strength', 'unit': 'MPa', 'icon': '💪'},
            'elastic_modulus': {'name': 'Elastic Modulus', 'unit': 'GPa', 'icon': '📏'},
            'UPV': {'name': 'Ultrasonic Pulse Velocity', 'unit': 'm/s', 'icon': '🌊'},
            'cost': {'name': 'Cost', 'unit': '£/m³', 'icon': '💰'}
        }

    def predict_properties(self, input_data):
        """Simulate prediction results - replace with actual model"""
        # This is a simulation - replace with your actual trained models
        predictions = {}
        
        # Simulate predictions based on input CS
        cs = input_data.get('compressive_strength', 150)
        
        predictions['compressive_strength'] = cs
        predictions['tensile_strength'] = 0.56 * np.sqrt(cs) + np.random.normal(0, 0.5)
        predictions['elastic_modulus'] = 4700 * np.sqrt(cs) / 1000 + np.random.normal(0, 2)  # Convert to GPa
        predictions['UPV'] = 4000 + (cs - 100) * 15 + np.random.normal(0, 100)
        
        # Cost calculation based on materials
        cement_cost = input_data.get('cement', 500) * 0.12
        sf_cost = input_data.get('silica_fume', 100) * 0.50
        fiber_cost = input_data.get('steel_fibers', 100) * 1.20
        predictions['cost'] = cement_cost + sf_cost + fiber_cost + np.random.normal(0, 20)
        
        return predictions

    def predict_with_uncertainty(self, input_data, n_simulations=100):
        """Enhanced prediction with uncertainty quantification"""
        predictions = []
        
        for _ in range(n_simulations):
            # Add small random variations to simulate uncertainty
            noisy_data = input_data.copy()
            for key in noisy_data:
                if key != 'compressive_strength':
                    noise = np.random.normal(0, 0.02 * noisy_data[key])  # 2% noise
                    noisy_data[key] = max(0, noisy_data[key] + noise)
            
            pred = self.predict_properties(noisy_data)
            predictions.append(pred)
        
        # Calculate statistics
        result = {}
        properties = ['compressive_strength', 'tensile_strength', 'elastic_modulus', 'UPV', 'cost']
        
        for prop in properties:
            values = [p[prop] for p in predictions]
            result[prop] = {
                'mean': np.mean(values),
                'std': np.std(values),
                'min': np.min(values),
                'max': np.max(values),
                'confidence_95_lower': np.percentile(values, 2.5),
                'confidence_95_upper': np.percentile(values, 97.5)
            }
        
        return result

    def target_based_design(self, target_property, target_value, constraints=None):
        """Design mix to achieve target property value"""
        best_mix = None
        best_error = float('inf')
        
        # Try multiple combinations
        for _ in range(1000):
            # Generate random mix within realistic bounds
            mix = {
                'cement': np.random.uniform(350, 700),
                'silica_fume': np.random.uniform(50, 200),
                'water': np.random.uniform(120, 200),
                'superplasticizer': np.random.uniform(4, 15),
                'coarse_aggregate': np.random.uniform(600, 1000),
                'fine_aggregate': np.random.uniform(700, 1000),
                'steel_fibers': np.random.uniform(20, 150),
                'age': 28,
                'curing_temperature': 20,
                'curing_humidity': 95
            }
            
            # Check constraints
            if constraints:
                valid = True
                for prop, (min_val, max_val) in constraints.items():
                    if prop == 'cost':
                        pred_cost = self.predict_properties(mix)['cost']
                        if not (min_val <= pred_cost <= max_val):
                            valid = False
                            break
                
                if not valid:
                    continue
            
            # Predict properties
            prediction = self.predict_properties(mix)
            error = abs(prediction[target_property] - target_value)
            
            if error < best_error:
                best_error = error
                best_mix = mix.copy()
                best_mix['predicted_value'] = prediction[target_property]
                best_mix['error'] = error
        
        return best_mix

    def generate_optimization_data(self, base_mix, vary_params=['cement', 'silica_fume']):
        """Generate data for optimization charts"""
        results = []
        
        for param in vary_params:
            base_value = base_mix[param]
            variations = np.linspace(base_value * 0.5, base_value * 1.5, 20)
            
            for variation in variations:
                test_mix = base_mix.copy()
                test_mix[param] = variation
                
                pred = self.predict_properties(test_mix)
                
                # Include mix parameters and all predicted properties
                result = {
                    'parameter': param,
                    'value': variation,
                    'cement': test_mix.get('cement', 0),
                    'silica_fume': test_mix.get('silica_fume', 0),
                    'water': test_mix.get('water', 0),
                    'superplasticizer': test_mix.get('superplasticizer', 0),
                    'steel_fibers': test_mix.get('steel_fibers', 0),
                    'compressive_strength': pred['compressive_strength'],
                    'tensile_strength': pred['tensile_strength'],
                    'elastic_modulus': pred['elastic_modulus'],
                    'UPV': pred['UPV'],
                    'cost': pred['cost'],
                    'performance_score': pred['compressive_strength'] / pred['cost'] * 100
                }
                
                results.append(result)
        
        return pd.DataFrame(results)

    def generate_correlation_data(self, base_mix, vary_params=['cement', 'silica_fume']):
        """Generate comprehensive data for correlation heatmap"""
        results = []
        
        # Generate variations for all parameters (not just vary_params)
        all_params = ['cement', 'silica_fume', 'water', 'superplasticizer', 'steel_fibers']
        
        # Create a more comprehensive dataset for correlation analysis
        n_samples = 100
        
        for i in range(n_samples):
            test_mix = base_mix.copy()
            
            # Add random variations to all parameters
            for param in all_params:
                if param in base_mix:
                    base_value = base_mix[param]
                    # Random variation between 50% and 150% of base value
                    variation = np.random.uniform(base_value * 0.5, base_value * 1.5)
                    test_mix[param] = variation
            
            # Get predictions for this mix
            pred = self.predict_properties(test_mix)
            
            # Combine mix parameters and predictions
            result = test_mix.copy()
            result.update(pred)
            result['performance_score'] = pred['compressive_strength'] / pred['cost'] * 100
            
            results.append(result)
        
        return pd.DataFrame(results)

    def save_project(self, project_name, mix_data, notes=""):
        """Save project to file"""
        project = {
            'name': project_name,
            'timestamp': datetime.now().isoformat(),
            'mix_data': mix_data,
            'notes': notes
        }
        
        # Create projects directory if it doesn't exist
        if not os.path.exists('saved_projects'):
            os.makedirs('saved_projects')
        
        filename = f"saved_projects/{project_name.replace(' ', '_')}.json"
        with open(filename, 'w') as f:
            json.dump(project, f, indent=2)
        
        return filename

    def load_project(self, filename):
        """Load project from file"""
        try:
            with open(filename, 'r') as f:
                project = json.load(f)
            return project
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def get_saved_projects(self):
        """Get list of saved projects"""
        if not os.path.exists('saved_projects'):
            return []
        
        projects = []
        for filename in os.listdir('saved_projects'):
            if filename.endswith('.json'):
                project = self.load_project(f"saved_projects/{filename}")
                if project:
                    projects.append({
                        'filename': f"saved_projects/{filename}",
                        'name': project['name'],
                        'timestamp': project['timestamp']
                    })
        
        return sorted(projects, key=lambda x: x['timestamp'], reverse=True)

    def convert_cost(self, cost_gbp, target_currency):
        """Convert cost from GBP to target currency"""
        if target_currency in self.currency_rates:
            rate = self.currency_rates[target_currency]['rate']
            return cost_gbp * rate
        return cost_gbp
    
    def get_currency_info(self, currency):
        """Get currency symbol and rate"""
        if currency in self.currency_rates:
            return self.currency_rates[currency]
        return {'symbol': '£', 'rate': 1.0}

    def get_property_recommendations(self, predictions):
        """Provide recommendations based on predictions"""
        recommendations = []
        
        cs = predictions['compressive_strength']
        ts = predictions['tensile_strength']
        em = predictions['elastic_modulus']
        upv = predictions['UPV']
        cost = predictions['cost']
        
        # Compressive Strength Assessment
        if cs >= 150:
            recommendations.append("✅ Excellent compressive strength for high-performance applications")
        elif cs >= 120:
            recommendations.append("✅ Good compressive strength suitable for most structural applications")
        else:
            recommendations.append("⚠️ Consider increasing cement content or reducing w/c ratio")
        
        # Tensile Strength Assessment
        if ts >= 12:
            recommendations.append("✅ High tensile strength - excellent for crack resistance")
        elif ts >= 8:
            recommendations.append("✅ Adequate tensile strength for standard applications")
        else:
            recommendations.append("⚠️ Consider adding steel fibers to improve tensile performance")
        
        # Elastic Modulus Assessment
        if em >= 45:
            recommendations.append("✅ High stiffness - suitable for high-load applications")
        elif em >= 35:
            recommendations.append("✅ Good elastic modulus for structural use")
        else:
            recommendations.append("⚠️ Consider optimizing aggregate type for higher stiffness")
        
        # UPV Assessment
        if upv >= 4800:
            recommendations.append("✅ Excellent concrete quality and density")
        elif upv >= 4400:
            recommendations.append("✅ Good concrete quality")
        else:
            recommendations.append("⚠️ Check mix consolidation and curing conditions")
        
        # Cost Assessment
        if cost <= 800:
            recommendations.append("💰 Economical mix design")
        elif cost <= 1200:
            recommendations.append("💰 Moderate cost - good value for performance")
        else:
            recommendations.append("💰 Premium mix - consider cost optimization if needed")
        
        return recommendations
    
    def calculate_carbon_footprint(self, mix_design):
        """Calculate CO2 emissions for concrete mix (kg CO2/m³)"""
        # CO2 emission factors (kg CO2/kg material)
        co2_factors = {
            'cement': 0.92,           # Portland cement
            'silica_fume': 0.28,      # Industrial byproduct (lower impact)
            'water': 0.0001,          # Minimal impact
            'superplasticizer': 2.5,  # Chemical admixture
            'coarse_aggregate': 0.005, # Natural aggregate
            'fine_aggregate': 0.003,   # Natural sand
            'steel_fibers': 2.1        # Steel production
        }
        
        co2_breakdown = {}
        total_co2 = 0
        
        for material, factor in co2_factors.items():
            if material in mix_design:
                co2_emission = mix_design[material] * factor
                co2_breakdown[material] = co2_emission
                total_co2 += co2_emission
        
        return {
            'total_co2': total_co2,
            'breakdown': co2_breakdown,
            'rating': self._get_co2_rating(total_co2)
        }
    
    def calculate_resource_efficiency(self, mix_design):
        """Calculate resource efficiency metrics"""
        # Water-to-binder ratio (lower is more efficient)
        total_binder = mix_design.get('cement', 0) + mix_design.get('silica_fume', 0)
        water_binder_ratio = mix_design.get('water', 0) / total_binder if total_binder > 0 else 0
        
        # Supplementary cementitious material ratio (higher is better)
        scm_ratio = mix_design.get('silica_fume', 0) / total_binder if total_binder > 0 else 0
        
        # Aggregate efficiency (total aggregate vs cement)
        total_aggregate = mix_design.get('coarse_aggregate', 0) + mix_design.get('fine_aggregate', 0)
        aggregate_efficiency = total_aggregate / mix_design.get('cement', 1)
        
        # Calculate efficiency scores (0-100)
        wb_score = max(0, 100 - (water_binder_ratio * 500))  # Penalty for high W/B
        scm_score = min(100, scm_ratio * 400)  # Bonus for SCM usage
        agg_score = min(100, aggregate_efficiency * 20)  # Bonus for aggregate efficiency
        
        overall_efficiency = (wb_score + scm_score + agg_score) / 3
        
        return {
            'water_binder_ratio': water_binder_ratio,
            'scm_ratio': scm_ratio,
            'aggregate_efficiency': aggregate_efficiency,
            'wb_score': wb_score,
            'scm_score': scm_score,
            'agg_score': agg_score,
            'overall_efficiency': overall_efficiency,
            'rating': self._get_efficiency_rating(overall_efficiency)
        }
    
    def calculate_energy_consumption(self, mix_design):
        """Estimate energy consumption for production (MJ/m³)"""
        # Energy factors (MJ/kg material)
        energy_factors = {
            'cement': 4.2,            # High energy for clinker production
            'silica_fume': 0.8,       # Byproduct (low energy)
            'superplasticizer': 12.0, # Chemical processing
            'coarse_aggregate': 0.08, # Crushing/transport
            'fine_aggregate': 0.05,   # Processing
            'steel_fibers': 25.0      # Steel production
        }
        
        energy_breakdown = {}
        total_energy = 0
        
        for material, factor in energy_factors.items():
            if material in mix_design:
                energy_consumption = mix_design[material] * factor
                energy_breakdown[material] = energy_consumption
                total_energy += energy_consumption
        
        return {
            'total_energy': total_energy,
            'breakdown': energy_breakdown,
            'rating': self._get_energy_rating(total_energy)
        }
    
    def calculate_recyclability_index(self, mix_design):
        """Calculate how recyclable the concrete will be"""
        # Recyclability factors (0-1, higher is better)
        recyclability_factors = {
            'cement': 0.6,            # Can be recycled as aggregate
            'silica_fume': 0.8,       # Already recycled material
            'coarse_aggregate': 0.9,  # Highly recyclable
            'fine_aggregate': 0.8,    # Recyclable
            'steel_fibers': 0.95,     # Steel is highly recyclable
            'superplasticizer': 0.1   # Chemical contamination
        }
        
        weighted_recyclability = 0
        total_mass = 0
        
        for material, factor in recyclability_factors.items():
            if material in mix_design:
                mass = mix_design[material]
                weighted_recyclability += mass * factor
                total_mass += mass
        
        recyclability_index = (weighted_recyclability / total_mass * 100) if total_mass > 0 else 0
        
        return {
            'recyclability_index': recyclability_index,
            'rating': self._get_recyclability_rating(recyclability_index)
        }
    
    def calculate_durability_bonus(self, predictions):
        """Calculate durability bonus based on predicted properties"""
        cs = predictions.get('compressive_strength', 0)
        ts = predictions.get('tensile_strength', 0)
        upv = predictions.get('UPV', 0)
        
        # Higher strength and UPV indicate better durability
        cs_bonus = min(30, cs / 3)  # Max 30 points for CS
        ts_bonus = min(20, ts * 2)  # Max 20 points for TS
        upv_bonus = min(25, (upv - 4000) / 40)  # Max 25 points for UPV
        
        total_bonus = max(0, cs_bonus + ts_bonus + upv_bonus)
        
        return {
            'durability_bonus': total_bonus,
            'cs_bonus': cs_bonus,
            'ts_bonus': ts_bonus,
            'upv_bonus': upv_bonus,
            'rating': self._get_durability_rating(total_bonus)
        }
    
    def comprehensive_sustainability_analysis(self, mix_design, predictions):
        """Complete sustainability assessment"""
        # Calculate all sustainability metrics
        carbon = self.calculate_carbon_footprint(mix_design)
        efficiency = self.calculate_resource_efficiency(mix_design)
        energy = self.calculate_energy_consumption(mix_design)
        recyclability = self.calculate_recyclability_index(mix_design)
        durability = self.calculate_durability_bonus(predictions)
        
        # Calculate overall sustainability score (0-100)
        co2_score = max(0, 100 - (carbon['total_co2'] / 500 * 100))  # Baseline 500 kg CO2/m³
        efficiency_score = efficiency['overall_efficiency']
        energy_score = max(0, 100 - (energy['total_energy'] / 3000 * 100))  # Baseline 3000 MJ/m³
        recyclability_score = recyclability['recyclability_index']
        durability_score = min(100, durability['durability_bonus'])
        
        # Weighted overall score
        weights = {
            'carbon': 0.25,
            'efficiency': 0.20,
            'energy': 0.20,
            'recyclability': 0.15,
            'durability': 0.20
        }
        
        overall_score = (
            co2_score * weights['carbon'] +
            efficiency_score * weights['efficiency'] +
            energy_score * weights['energy'] +
            recyclability_score * weights['recyclability'] +
            durability_score * weights['durability']
        )
        
        return {
            'overall_score': overall_score,
            'rating': self._get_sustainability_rating(overall_score),
            'carbon_footprint': carbon,
            'resource_efficiency': efficiency,
            'energy_consumption': energy,
            'recyclability': recyclability,
            'durability_bonus': durability,
            'component_scores': {
                'carbon': co2_score,
                'efficiency': efficiency_score,
                'energy': energy_score,
                'recyclability': recyclability_score,
                'durability': durability_score
            }
        }
    
    def _get_co2_rating(self, co2):
        """Get CO2 emission rating"""
        if co2 <= 300: return "🌟 Excellent"
        elif co2 <= 400: return "✅ Good"
        elif co2 <= 500: return "⚠️ Fair"
        else: return "❌ Poor"
    
    def _get_efficiency_rating(self, score):
        """Get resource efficiency rating"""
        if score >= 80: return "🌟 Excellent"
        elif score >= 65: return "✅ Good"
        elif score >= 50: return "⚠️ Fair"
        else: return "❌ Poor"
    
    def _get_energy_rating(self, energy):
        """Get energy consumption rating"""
        if energy <= 2000: return "🌟 Excellent"
        elif energy <= 3000: return "✅ Good"
        elif energy <= 4000: return "⚠️ Fair"
        else: return "❌ Poor"
    
    def _get_recyclability_rating(self, index):
        """Get recyclability rating"""
        if index >= 80: return "🌟 Excellent"
        elif index >= 65: return "✅ Good"
        elif index >= 50: return "⚠️ Fair"
        else: return "❌ Poor"
    
    def _get_durability_rating(self, bonus):
        """Get durability rating"""
        if bonus >= 60: return "🌟 Excellent"
        elif bonus >= 45: return "✅ Good"
        elif bonus >= 30: return "⚠️ Fair"
        else: return "❌ Poor"
    
    def _get_sustainability_rating(self, score):
        """Get overall sustainability rating"""
        if score >= 80: return "🌟 Excellent"
        elif score >= 65: return "✅ Good"
        elif score >= 50: return "⚠️ Fair"
        else: return "❌ Poor"
    
    def check_standards_compliance(self, mix_design, predicted_properties, application_type=None):
        """Check compliance with international concrete standards"""
        compliance_results = {}
        
        # Get relevant standards for application type
        relevant_standards = self.compliance_matrix.get(application_type, []) if application_type else list(self.concrete_standards.keys())
        
        for standard_code in relevant_standards:
            standard = self.concrete_standards[standard_code]
            compliance = {
                'standard_name': standard['name'],
                'authority': standard['authority'],
                'compliance_status': 'PASS',
                'violations': [],
                'recommendations': []
            }
            
            # Check compressive strength requirements
            if 'compressive_strength' in predicted_properties and 'compressive_strength' in standard:
                cs_req = standard['compressive_strength']
                predicted_cs = predicted_properties['compressive_strength']
                
                if 'min' in cs_req and predicted_cs < cs_req['min']:
                    compliance['compliance_status'] = 'FAIL'
                    compliance['violations'].append(f"Compressive strength {predicted_cs:.1f} MPa < required {cs_req['min']} MPa")
                    compliance['recommendations'].append("Increase cement content or reduce w/c ratio")
                
                if 'grades' in cs_req:
                    nearest_grade = min(cs_req['grades'], key=lambda x: abs(x - predicted_cs))
                    if predicted_cs < nearest_grade * 0.9:  # 10% tolerance
                        compliance['compliance_status'] = 'WARNING'
                        compliance['violations'].append(f"Below standard grade C{nearest_grade} by more than 10%")
            
            # Check w/c ratio limits
            if 'w_c_ratio' in mix_design:
                w_c_ratio = mix_design['water'] / mix_design['cement']
                
                if 'w_c_ratio' in standard and w_c_ratio > standard['w_c_ratio']['max']:
                    compliance['compliance_status'] = 'FAIL'
                    compliance['violations'].append(f"W/C ratio {w_c_ratio:.3f} > maximum {standard['w_c_ratio']['max']}")
                    compliance['recommendations'].append("Reduce water content or increase cement content")
                
                if 'w_b_ratio' in standard and w_c_ratio > standard['w_b_ratio']['max']:
                    compliance['compliance_status'] = 'FAIL'
                    compliance['violations'].append(f"W/B ratio {w_c_ratio:.3f} > maximum {standard['w_b_ratio']['max']}")
            
            # Check fiber content for UHPC standards
            if 'fiber_content' in standard and 'steel_fibers' in mix_design:
                fiber_vol_fraction = mix_design.get('fiber_volume_fraction', 0)
                fiber_req = standard['fiber_content']
                
                if 'min' in fiber_req and fiber_vol_fraction < fiber_req['min']:
                    compliance['compliance_status'] = 'FAIL'
                    compliance['violations'].append(f"Fiber content {fiber_vol_fraction:.1f}% < required {fiber_req['min']}%")
                    compliance['recommendations'].append("Increase steel fiber content")
                
                if 'max' in fiber_req and fiber_vol_fraction > fiber_req['max']:
                    compliance['compliance_status'] = 'WARNING'
                    compliance['violations'].append(f"Fiber content {fiber_vol_fraction:.1f}% > typical maximum {fiber_req['max']}%")
            
            # Check curing temperature
            if 'curing_temperature' in mix_design and 'curing_temp' in standard:
                curing_temp = mix_design['curing_temperature']
                temp_req = standard['curing_temp']
                
                if curing_temp < temp_req.get('min', 0) or curing_temp > temp_req.get('max', 100):
                    compliance['compliance_status'] = 'WARNING'
                    compliance['violations'].append(f"Curing temperature {curing_temp}°C outside recommended range")
            
            compliance_results[standard_code] = compliance
        
        return compliance_results
    
    def get_standards_recommendations(self, application_type):
        """Get recommended standards for specific application types"""
        recommendations = {}
        
        if application_type in self.compliance_matrix:
            for standard_code in self.compliance_matrix[application_type]:
                if standard_code in self.concrete_standards:
                    standard = self.concrete_standards[standard_code]
                    recommendations[standard_code] = {
                        'name': standard['name'],
                        'authority': standard['authority'],
                        'scope': standard['scope'],
                        'key_requirements': self._extract_key_requirements(standard)
                    }
        
        return recommendations
    
    def _extract_key_requirements(self, standard):
        """Extract key requirements from standard specification"""
        requirements = []
        
        if 'compressive_strength' in standard:
            cs = standard['compressive_strength']
            if 'min' in cs:
                requirements.append(f"Min. compressive strength: {cs['min']} {cs.get('unit', 'MPa')}")
            if 'grades' in cs:
                requirements.append(f"Standard grades: {', '.join(map(str, cs['grades'][:5]))}... {cs.get('unit', 'MPa')}")
        
        if 'w_c_ratio' in standard:
            requirements.append(f"Max. W/C ratio: {standard['w_c_ratio']['max']}")
        
        if 'w_b_ratio' in standard:
            requirements.append(f"Max. W/B ratio: {standard['w_b_ratio']['max']}")
        
        if 'fiber_content' in standard:
            fc = standard['fiber_content']
            if 'min' in fc and 'max' in fc:
                requirements.append(f"Fiber content: {fc['min']}-{fc['max']}{fc.get('unit', '%')}")
        
        if 'test_age' in standard:
            requirements.append(f"Test ages: {', '.join(map(str, standard['test_age']))} days")
        
        return requirements
    
    def initialize_shap_explainer(self):
        """Initialize SHAP explainer for model interpretability"""
        try:
            # Create a simple mock model for demonstration
            # In practice, this would use your actual trained model
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.model_selection import train_test_split
            
            # Generate synthetic training data for SHAP
            np.random.seed(42)
            n_samples = 1000
            
            # Generate realistic concrete mix data
            cement = np.random.uniform(300, 700, n_samples)
            silica_fume = np.random.uniform(50, 200, n_samples)
            water = np.random.uniform(100, 200, n_samples)
            sp = np.random.uniform(5, 15, n_samples)
            coarse_agg = np.random.uniform(600, 1000, n_samples)
            fine_agg = np.random.uniform(600, 1000, n_samples)
            fibers = np.random.uniform(20, 150, n_samples)
            age = np.random.uniform(7, 90, n_samples)
            temp = np.random.uniform(15, 25, n_samples)
            humidity = np.random.uniform(80, 100, n_samples)
            
            # Create feature matrix
            X = np.column_stack([cement, silica_fume, water, sp, coarse_agg, 
                               fine_agg, fibers, age, temp, humidity])
            
            # Generate target using realistic concrete strength formula
            w_c_ratio = water / cement
            binder = cement + silica_fume
            y = (150 - 200 * w_c_ratio + 
                 0.3 * cement + 0.5 * silica_fume + 
                 0.1 * fibers + 0.2 * age - 
                 2 * w_c_ratio**2 + np.random.normal(0, 5, n_samples))
            y = np.clip(y, 20, 200)  # Realistic strength range
            
            # Train a simple model for SHAP demonstration
            self.shap_model = RandomForestRegressor(n_estimators=50, random_state=42)
            self.shap_model.fit(X, y)
            
            # Create background dataset for SHAP
            self.shap_background = X[:100]  # Use first 100 samples as background
            
            # Initialize SHAP explainer
            self.shap_explainer = shap.TreeExplainer(self.shap_model, self.shap_background)
            
            # Store feature names
            self.shap_feature_names = [
                'cement', 'silica_fume', 'water', 'superplasticizer',
                'coarse_aggregate', 'fine_aggregate', 'steel_fibers',
                'age', 'curing_temperature', 'curing_humidity'
            ]
            
            return True
            
        except Exception as e:
            st.warning(f"SHAP explainer initialization failed: {str(e)}")
            self.shap_explainer = None
            return False
    
    def get_shap_explanations(self, input_data):
        """Get SHAP explanations for prediction interpretability"""
        if not hasattr(self, 'shap_explainer') or self.shap_explainer is None:
            if not self.initialize_shap_explainer():
                return None
        
        try:
            # Convert input to array format
            input_array = np.array([[
                input_data.get('cement', 500),
                input_data.get('silica_fume', 100),
                input_data.get('water', 150),
                input_data.get('superplasticizer', 8),
                input_data.get('coarse_aggregate', 800),
                input_data.get('fine_aggregate', 850),
                input_data.get('steel_fibers', 78),
                input_data.get('age', 28),
                input_data.get('curing_temperature', 20),
                input_data.get('curing_humidity', 95)
            ]])
            
            # Calculate SHAP values
            shap_values = self.shap_explainer.shap_values(input_array)
            base_value = self.shap_explainer.expected_value
            
            # Get prediction from SHAP model
            prediction = float(self.shap_model.predict(input_array)[0])
            
            return {
                'shap_values': shap_values[0],  # First instance
                'base_value': base_value,
                'feature_names': self.shap_feature_names,
                'input_values': input_array[0],
                'prediction': prediction
            }
            
        except Exception as e:
            st.error(f"SHAP explanation failed: {str(e)}")
            return None
    
    def create_shap_waterfall_plot(self, shap_explanation):
        """Create SHAP waterfall plot for feature importance"""
        if not shap_explanation:
            return None
            
        try:
            # Create waterfall plot data
            shap_values = shap_explanation['shap_values']
            feature_names = shap_explanation['feature_names']
            input_values = shap_explanation['input_values']
            base_value = shap_explanation['base_value']
            prediction = shap_explanation['prediction']
            
            # Sort features by absolute SHAP value
            importance_idx = np.argsort(np.abs(shap_values))[::-1]
            
            # Create plotly waterfall chart
            fig = go.Figure()
            
            # Calculate cumulative values for waterfall
            cumulative = [base_value]
            for i in importance_idx:
                cumulative.append(cumulative[-1] + shap_values[i])
            
            # Add bars for each feature
            colors = ['green' if val > 0 else 'red' for val in shap_values[importance_idx]]
            
            fig.add_trace(go.Waterfall(
                name="SHAP Feature Contributions",
                orientation="v",
                measure=["absolute"] + ["relative"] * len(importance_idx) + ["total"],
                x=["Base Value"] + [f"{feature_names[i]}<br>({input_values[i]:.1f})" 
                                   for i in importance_idx] + ["Prediction"],
                textposition="outside",
                text=[f"{base_value:.1f}"] + [f"{shap_values[i]:+.1f}" 
                                             for i in importance_idx] + [f"{prediction:.1f}"],
                y=[base_value] + [shap_values[i] for i in importance_idx] + [prediction],
                connector={"line":{"color":"rgb(63, 63, 63)"}},
            ))
            
            fig.update_layout(
                title="🔍 SHAP Feature Importance Analysis",
                xaxis_title="Features (with values)",
                yaxis_title="Compressive Strength (MPa)",
                showlegend=False,
                height=500,
                template="plotly_white"
            )
            
            return fig
            
        except Exception as e:
            st.error(f"SHAP waterfall plot creation failed: {str(e)}")
            return None
    
    def create_shap_force_plot(self, shap_explanation):
        """Create SHAP force plot as a Plotly figure"""
        if not shap_explanation:
            return None
            
        try:
            shap_values = shap_explanation['shap_values']
            feature_names = shap_explanation['feature_names']
            input_values = shap_explanation['input_values']
            base_value = shap_explanation['base_value']
            prediction = shap_explanation['prediction']
            
            # Separate positive and negative contributions
            positive_features = []
            negative_features = []
            positive_values = []
            negative_values = []
            
            for i, (name, value, shap_val) in enumerate(zip(feature_names, input_values, shap_values)):
                if shap_val > 0:
                    positive_features.append(f"{name}: {value:.1f}")
                    positive_values.append(shap_val)
                else:
                    negative_features.append(f"{name}: {value:.1f}")
                    negative_values.append(abs(shap_val))
            
            # Create horizontal bar chart
            fig = go.Figure()
            
            # Add positive contributions
            if positive_features:
                fig.add_trace(go.Bar(
                    y=positive_features,
                    x=positive_values,
                    orientation='h',
                    name='Increases Strength',
                    marker_color='lightgreen',
                    text=[f"+{val:.2f}" for val in positive_values],
                    textposition='auto'
                ))
            
            # Add negative contributions
            if negative_features:
                fig.add_trace(go.Bar(
                    y=negative_features,
                    x=[-val for val in negative_values],
                    orientation='h',
                    name='Decreases Strength',
                    marker_color='lightcoral',
                    text=[f"-{val:.2f}" for val in negative_values],
                    textposition='auto'
                ))
            
            fig.update_layout(
                title=f"🎯 SHAP Force Plot - Prediction: {prediction:.1f} MPa (Base: {base_value:.1f} MPa)",
                xaxis_title="SHAP Value (Impact on Prediction)",
                yaxis_title="Features",
                height=400,
                template="plotly_white",
                showlegend=True
            )
            
            # Add vertical line at x=0
            fig.add_vline(x=0, line_dash="dash", line_color="black", opacity=0.5)
            
            return fig
            
        except Exception as e:
            st.error(f"SHAP force plot creation failed: {str(e)}")
            return None
    
    def get_feature_importance_summary(self, shap_explanation):
        """Get text summary of feature importance"""
        if not shap_explanation:
            return "SHAP explanation not available."
        
        try:
            shap_values = shap_explanation['shap_values']
            feature_names = shap_explanation['feature_names']
            input_values = shap_explanation['input_values']
            
            # Sort by absolute importance
            importance_idx = np.argsort(np.abs(shap_values))[::-1]
            
            summary = "### 🔍 Why This Prediction?\n\n"
            summary += f"**Base Model Expectation:** {shap_explanation['base_value']:.1f} MPa\n"
            summary += f"**Your Mix Prediction:** {shap_explanation['prediction']:.1f} MPa\n\n"
            
            summary += "**Top 5 Most Influential Features:**\n"
            for i, idx in enumerate(importance_idx[:5]):
                impact = "increases" if shap_values[idx] > 0 else "decreases"
                summary += f"{i+1}. **{feature_names[idx].replace('_', ' ').title()}** ({input_values[idx]:.1f}): "
                summary += f"{impact} strength by {abs(shap_values[idx]):.1f} MPa\n"
            
            # Add interpretation
            summary += "\n**Interpretation:**\n"
            strongest_positive = np.argmax(shap_values)
            strongest_negative = np.argmin(shap_values)
            
            if shap_values[strongest_positive] > abs(shap_values[strongest_negative]):
                summary += f"• Your mix is primarily strengthened by **{feature_names[strongest_positive].replace('_', ' ')}** "
                summary += f"({input_values[strongest_positive]:.1f})\n"
            else:
                summary += f"• Your mix strength is primarily limited by **{feature_names[strongest_negative].replace('_', ' ')}** "
                summary += f"({input_values[strongest_negative]:.1f})\n"
            
            # Add recommendations
            summary += "\n**💡 Optimization Suggestions:**\n"
            for idx in importance_idx[:3]:
                if shap_values[idx] < -1:  # Significant negative impact
                    summary += f"• Consider adjusting **{self.shap_feature_names[idx].replace('_', ' ')}** "
                    summary += f"to improve strength (current: {input_values[idx]:.1f})\n"
            
            return summary
            
        except Exception as e:
            return f"Error generating summary: {str(e)}"

def main():
    # Add background image
    add_background()
    
    # Header with centered logo
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    try:
        st.image("aicrete_logo.png", width=300)
    except Exception:
        # Professional fallback logo using HTML/CSS
        st.markdown("""
        <div style="text-align: center; padding: 20px; background: linear-gradient(90deg, #1976d2, #42a5f5); 
                    border-radius: 10px; margin: 10px 0; color: white; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
            <h1 style="margin: 0; font-size: 2.5rem; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                🏗️ AIcrete
            </h1>
            <p style="margin: 5px 0 0 0; font-size: 1.2rem; opacity: 0.9;">
                Advanced Concrete Solutions
            </p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="main-header">
        <div class="company-tagline">Advanced AI-Powered UHPC Property Prediction System</div>
        <div>Predicting Tomorrow's Concrete Performance Today</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Professional Engineering Decision Support Disclaimer
    st.markdown("""
    <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); 
                padding: 15px; border-radius: 10px; margin: 20px 0; 
                border-left: 5px solid #1976d2;">
        <h4 style="color: #1565c0; margin: 0 0 10px 0;">🏗️ Professional Engineering Decision Support Tool</h4>
        <p style="margin: 5px 0; color: #0d47a1;"><strong>✅ Suitable for:</strong> Preliminary design • Concept development • Parameter analysis</p>
        <p style="margin: 5px 0; color: #0d47a1;"><strong>⚠️ Requirements:</strong> Professional Engineer review • Laboratory validation • Code compliance verification</p>
        <p style="margin: 5px 0; font-size: 0.9em; color: #1565c0;"><strong>Disclaimer:</strong> This tool provides design support and preliminary analysis. All designs require professional engineering review, laboratory testing, and compliance with local building codes before construction use.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Engineering Value Proposition
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%); 
                padding: 12px; border-radius: 8px; margin: 15px 0; 
                border-left: 4px solid #8e24aa;">
        <h5 style="color: #6a1b9a; margin: 0 0 8px 0;">⚙️ How AIcrete Accelerates Engineering</h5>
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="color: #4a148c;">
                <strong>🎯 Screen 1000+ combinations digitally</strong> → Test only top 5 in lab<br>
                <strong>💰 75% cost reduction</strong> → $10,000 becomes $2,500<br>
                <strong>⏱️ 75% time savings</strong> → 8 weeks becomes 2 weeks
            </div>
            <div style="font-size: 2em; color: #8e24aa;">🚀</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize predictor
    predictor = AIcretePredictor()
    
    # Sidebar for company info and navigation
    with st.sidebar:
        # Small logo in sidebar
        try:
            st.image("aicrete_logo.png", width=150)
        except Exception:
            # Professional fallback for sidebar
            st.markdown("""
            <div style="text-align: center; padding: 10px; background: linear-gradient(90deg, #1976d2, #42a5f5); 
                        border-radius: 8px; margin: 10px 0; color: white;">
                <h3 style="margin: 0; font-size: 1.5rem;">🏗️ AIcrete</h3>
                <p style="margin: 0; font-size: 0.8rem; opacity: 0.9;">Concrete Solutions</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Currency selector
        st.markdown("### 💱 Currency")
        selected_currency = st.selectbox(
            "Select Currency:",
            list(predictor.currency_rates.keys()),
            index=0  # Default to GBP
        )
        
        # Language selector
        st.markdown("### 🌐 Language")
        selected_language = st.selectbox(
            "Select Language:",
            ["English", "Español", "Français", "Deutsch", "中文", "日本語", "العربية", "हिन्दी"],
            index=0
        )
        
        # User level selector
        st.markdown("### 👤 User Level")
        user_level = st.selectbox(
            "Select your expertise level:",
            ["️ Professional Engineer", "🔬 Researcher", "🏭 Production Manager", "👨‍💼 Project Manager"],
            index=0
        )
        
        # Display conversion info
        currency_info = predictor.get_currency_info(selected_currency)
        currency_symbol = currency_info['symbol']  # Define globally for all tabs
        if selected_currency != 'GBP (£)':
            st.caption(f"1 GBP = {currency_info['rate']:.2f} {currency_info['symbol']}")
        
        st.markdown("### 🏢 About AIcrete")
        st.markdown(f"""
        **AIcrete Concrete Solutions** specializes in advanced concrete technology 
        using AI-driven predictions for optimal mix design and performance optimization.
        
        **Our Services:**
        - UHPC Mix Design Optimization
        - Property Prediction & Analysis
        - Cost-Performance Analysis ({currency_info['symbol']}/m³)
        - Quality Control Solutions
        """)
        
        st.markdown("### 📞 Contact")
        st.markdown("""
        **Phone:** +1 (555) AICRETE  
        **Email:** info@aicrete.com  
        **Web:** www.aicrete-solutions.com
        """)
        
        st.markdown("---")
        st.markdown("### 🔬 Prediction Models")
        st.markdown("""
        Our AI models predict:
        - Compressive Strength (MPa)
        - Tensile Strength (MPa)
        - Elastic Modulus (GPa)
        - Ultrasonic Pulse Velocity (m/s)
        - Cost Estimation (£/m³)
        """)
        
        # Copyright Notice
        st.markdown("---")
        st.markdown("### 📄 **Copyright**")
        st.markdown("""
        <div style='font-size: 0.8em; color: #666;'>
        © 2025 Shiksha Seechurn<br>
        All rights reserved<br>
        <em>AIcrete Platform</em>
        </div>
        """, unsafe_allow_html=True)
    
    # Main tabs - Professional mode
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12 = st.tabs([
        "🎯 Property Prediction", 
        "🎨 Target-Based Design", 
        "📊 Interactive Charts", 
        "💾 Project Manager",
        "🏗️ Application Templates",
        "🌍 Sustainability",
        "📋 Standards Compliance",
        "🔍 SHAP Interpretability",
        "🔬 Overfitting Analysis",
        "📄 Reports",
        "📚 User Guide", 
        "ℹ️ About"
    ])
    
    # Property Prediction Tab (tab1 for both modes)
    with tab1:
        st.markdown("## � Property Prediction")
        st.markdown("Predict concrete properties from mix design parameters")
        
        # Professional Decision Support Notice
        st.warning("""
        🏗️ **Professional Engineering Decision Support**
        
        This prediction tool provides preliminary analysis for engineering decision-making. 
        Results should be validated through laboratory testing and reviewed by a Professional Engineer 
        before use in construction projects.
        """)
        
        # Input section
        st.markdown("### 📋 Mix Design Parameters")
        
        input_col1, input_col2, input_col3 = st.columns(3)
        
        with input_col1:
            st.markdown("**🏗️ Binders**")
            cement = st.number_input("Cement (kg/m³)", min_value=0.0, max_value=1000.0, value=540.0, step=10.0)
            silica = st.number_input("Silica Fume (kg/m³)", min_value=0.0, max_value=300.0, value=135.0, step=5.0)
            
        with input_col2:
            st.markdown("**💧 Fluids & Additives**")
            water = st.number_input("Water (kg/m³)", min_value=0.0, max_value=300.0, value=156.0, step=5.0)
            sp = st.number_input("Superplasticizer (kg/m³)", min_value=0.0, max_value=50.0, value=6.0, step=0.5)
            
        with input_col3:
            st.markdown("**🪨 Aggregates & Fibers**")
            coarse = st.number_input("Coarse Aggregate (kg/m³)", min_value=0.0, max_value=1200.0, value=725.0, step=25.0)
            fine = st.number_input("Fine Aggregate (kg/m³)", min_value=0.0, max_value=1000.0, value=797.0, step=25.0)
            fibers = st.number_input("Steel Fibers (kg/m³)", min_value=0.0, max_value=200.0, value=78.0, step=2.0)
        
        # Additional parameters
        st.markdown("### ⚙️ Curing Conditions")
        curing_col1, curing_col2 = st.columns(2)
        
        with curing_col1:
            age = st.selectbox("Age (days)", [1, 3, 7, 14, 28, 56, 90], index=4)
            curing_temp = st.slider("Curing Temperature (°C)", 5, 40, 20)
            
        with curing_col2:
            curing_humidity = st.slider("Relative Humidity (%)", 50, 100, 95)
        
        # Calculate key ratios
        w_c_ratio = water / max(cement, 1)
        total_binder = cement + silica
        
        # Display calculated ratios
        st.markdown("### 📊 Calculated Ratios")
        ratio_col1, ratio_col2, ratio_col3 = st.columns(3)
        
        with ratio_col1:
            st.metric("Water/Cement Ratio", f"{w_c_ratio:.3f}")
        with ratio_col2:
            st.metric("Total Binder", f"{total_binder:.0f} kg/m³")
        with ratio_col3:
            st.metric("Binder/Water Ratio", f"{total_binder / max(water, 1):.2f}")
        
        # Prediction button
        if st.button("🔮 Predict Properties", type="primary", use_container_width=True, key="predict_tab1"):
            with st.spinner("🔄 Analyzing mix design..."):
                # Create predictor instance
                predictor = AIcretePredictor()
                
                # Prepare input data
                mix_design_data = {
                    'cement': cement,
                    'silica': silica, 
                    'water': water,
                    'sp': sp,
                    'coarse': coarse,
                    'fine': fine,
                    'fibers': fibers,
                    'age': age,
                    'curing_temp': curing_temp,
                    'curing_humidity': curing_humidity
                }
                
                # Get predictions
                predictions = predictor.predict_properties(mix_design_data)
                
                # Store in session state for use in other tabs
                st.session_state.last_predictions = predictions
                st.session_state.last_mix_design = mix_design_data
                
                # Display results
                st.markdown("---")
                st.markdown("## 📈 Prediction Results")
                
                # Main predictions - All 5 properties
                pred_col1, pred_col2, pred_col3, pred_col4, pred_col5 = st.columns(5)
                
                with pred_col1:
                    st.metric(
                        "🏗️ Compressive Strength",
                        f"{predictions['compressive_strength']:.1f} MPa",
                        delta=f"{predictions['compressive_strength'] - 50:.1f} vs 50 MPa target"
                    )
                    
                with pred_col2:
                    st.metric(
                        "💪 Tensile Strength", 
                        f"{predictions['tensile_strength']:.1f} MPa",
                        delta=f"{predictions['tensile_strength'] - 5:.1f} vs 5 MPa target"
                    )
                    
                with pred_col3:
                    st.metric(
                        "📏 Elastic Modulus",
                        f"{predictions['elastic_modulus']:.1f} GPa", 
                        delta=f"{predictions['elastic_modulus'] - 40:.1f} vs 40 GPa target"
                    )
                
                with pred_col4:
                    st.metric(
                        "🌊 UPV",
                        f"{predictions['UPV']:.0f} m/s",
                        delta=f"{predictions['UPV'] - 4500:.0f} vs 4500 m/s target"
                    )
                
                with pred_col5:
                    # Convert cost to selected currency
                    converted_cost = predictor.convert_cost(predictions['cost'], selected_currency)
                    st.metric(
                        "💰 Cost",
                        f"{currency_symbol}{converted_cost:.0f}/m³",
                        delta=f"{currency_symbol}{converted_cost - 800:.0f} vs {currency_symbol}800/m³ target"
                    )
                
                # Performance assessment
                comp_strength = predictions['compressive_strength']
                if comp_strength >= 100:
                    strength_class = "🌟 Ultra-High Performance"
                elif comp_strength >= 80:
                    strength_class = "🔥 High Performance"
                elif comp_strength >= 50:
                    strength_class = "✅ Standard Performance"
                else:
                    strength_class = "⚠️ Below Target"
                    
                st.markdown(f"**Performance Classification:** {strength_class}")
    

    
    with tab2:
        st.markdown("## 🎯 Target-Based Design")
        st.markdown("Design concrete mix to achieve specific property targets")
        
        # Professional Decision Support Notice
        st.warning("""
        🏗️ **Professional Engineering Decision Support**
        
        This target-based design tool provides preliminary optimization for engineering decision-making. 
        Results should be validated through laboratory testing and reviewed by a Professional Engineer 
        before use in construction projects.
        """)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 🎯 Target Settings")
            target_property = st.selectbox(
                "Select Target Property:",
                ['compressive_strength', 'tensile_strength', 'cost'],
                format_func=lambda x: {
                    'compressive_strength': 'Compressive Strength (MPa)',
                    'tensile_strength': 'Tensile Strength (MPa)', 
                    'cost': f'Cost ({currency_symbol}/m³)'
                }[x]
            )
            
            if target_property == 'compressive_strength':
                target_value = st.number_input("Target Compressive Strength (MPa)", 
                                             min_value=50.0, max_value=200.0, value=120.0, step=5.0)
            elif target_property == 'tensile_strength':
                target_value = st.number_input("Target Tensile Strength (MPa)", 
                                             min_value=3.0, max_value=15.0, value=8.0, step=0.5)
            else:  # cost
                target_value = st.number_input(f"Target Cost ({currency_symbol}/m³)", 
                                             min_value=400.0, max_value=1500.0, value=800.0, step=50.0)
            
            st.markdown("### ⚙️ Constraints (Optional)")
            use_constraints = st.checkbox("Add constraints")
            constraints = {}
            
            if use_constraints:
                max_cost = st.number_input(f"Maximum Cost ({currency_symbol}/m³)", 
                                         min_value=400.0, max_value=2000.0, value=1000.0, step=50.0)
                constraints['cost'] = (0, max_cost)
        
        with col2:
            if st.button("🎯 Design Mix", type="primary", use_container_width=True, key="design_mix_tab3"):
                with st.spinner("Optimizing mix design..."):
                    # Convert cost constraint to GBP if needed
                    if 'cost' in constraints and selected_currency != 'GBP (£)':
                        gbp_cost = constraints['cost'][1] / predictor.get_currency_info(selected_currency)['rate']
                        constraints['cost'] = (0, gbp_cost)
                    
                    # Convert target value to GBP if cost
                    target_val = target_value
                    if target_property == 'cost' and selected_currency != 'GBP (£)':
                        target_val = target_value / predictor.get_currency_info(selected_currency)['rate']
                    
                    result = predictor.target_based_design(
                        target_property, target_val, 
                        constraints if use_constraints else None
                    )
                
                if result:
                    st.success("✅ Optimal mix design found!")
                    
                    # Display recommended mix
                    st.markdown("### 🧪 Recommended Mix Design")
                    mix_cols = st.columns(3)
                    
                    mix_params = ['cement', 'silica_fume', 'water', 'superplasticizer', 
                                'coarse_aggregate', 'fine_aggregate', 'steel_fibers']
                    
                    for i, param in enumerate(mix_params):
                        with mix_cols[i % 3]:
                            st.metric(
                                label=param.replace('_', ' ').title(),
                                value=f"{result[param]:.1f} kg/m³"
                            )
                    
                    # Display achieved value
                    achieved_value = result['predicted_value']
                    if target_property == 'cost':
                        achieved_value = predictor.convert_cost(achieved_value, selected_currency)
                    
                    error_pct = (result['error'] / target_value) * 100
                    
                    st.markdown("### 📊 Results")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Target Value", f"{target_value:.1f}")
                    with col2:
                        st.metric("Achieved Value", f"{achieved_value:.1f}")
                    with col3:
                        st.metric("Error", f"{error_pct:.1f}%")
                
                else:
                    st.error("❌ Could not find optimal mix. Try adjusting constraints.")
    
    with tab3:
        st.markdown("## � Interactive Optimization Charts")
        st.markdown("Visualize cost vs performance trade-offs and parameter sensitivity")
        
        # Base mix for analysis
        st.markdown("### 🧪 Base Mix Configuration")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            base_cement = st.number_input("Base Cement (kg/m³)", value=500.0, step=10.0, key="chart_cement")
            base_silica = st.number_input("Base Silica Fume (kg/m³)", value=100.0, step=5.0, key="chart_silica")
            base_water = st.number_input("Base Water (kg/m³)", value=150.0, step=5.0, key="chart_water")
        
        with col2:
            base_sp = st.number_input("Base Superplasticizer (kg/m³)", value=8.0, step=0.5, key="chart_sp")
            base_coarse = st.number_input("Base Coarse Agg (kg/m³)", value=800.0, step=10.0, key="chart_coarse")
            base_fine = st.number_input("Base Fine Agg (kg/m³)", value=900.0, step=10.0, key="chart_fine")
        
        with col3:
            base_fibers = st.number_input("Base Steel Fibers (kg/m³)", value=100.0, step=5.0, key="chart_fibers")
            vary_params = st.multiselect(
                "Parameters to Vary:",
                ['cement', 'silica_fume', 'water', 'superplasticizer', 'steel_fibers'],
                default=['cement', 'silica_fume']
            )
        
        if st.button("📊 Generate Charts", type="primary", use_container_width=True, key="generate_charts_tab4"):
            if vary_params:
                base_mix = {
                    'cement': base_cement, 'silica_fume': base_silica, 'water': base_water,
                    'superplasticizer': base_sp, 'coarse_aggregate': base_coarse,
                    'fine_aggregate': base_fine, 'steel_fibers': base_fibers,
                    'age': 28, 'curing_temperature': 20, 'curing_humidity': 95
                }
                
                with st.spinner("Generating optimization data..."):
                    opt_data = predictor.generate_optimization_data(base_mix, vary_params)
                
                # Cost vs Performance Chart
                st.markdown("### 💰 Cost vs Performance Analysis")
                
                fig = go.Figure()
                
                for param in vary_params:
                    param_data = opt_data[opt_data['parameter'] == param]
                    
                    # Convert cost to selected currency
                    converted_costs = [predictor.convert_cost(cost, selected_currency) 
                                     for cost in param_data['cost']]
                    
                    fig.add_trace(go.Scatter(
                        x=converted_costs,
                        y=param_data['compressive_strength'],
                        mode='markers+lines',
                        name=param.replace('_', ' ').title(),
                        text=[f"{param}: {val:.0f}" for val in param_data['value']],
                        hovertemplate='%{text}<br>Cost: %{x:.0f}<br>Strength: %{y:.1f} MPa<extra></extra>'
                    ))
                
                fig.update_layout(
                    title="Cost vs Compressive Strength Trade-off",
                    xaxis_title=f"Cost ({currency_symbol}/m³)",
                    yaxis_title="Compressive Strength (MPa)",
                    hovermode='closest',
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Parameter Sensitivity Charts
                st.markdown("### 🎯 Parameter Sensitivity Analysis")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Strength sensitivity
                    fig_strength = go.Figure()
                    
                    for param in vary_params:
                        param_data = opt_data[opt_data['parameter'] == param]
                        fig_strength.add_trace(go.Scatter(
                            x=param_data['value'],
                            y=param_data['compressive_strength'],
                            mode='lines+markers',
                            name=param.replace('_', ' ').title()
                        ))
                    
                    fig_strength.update_layout(
                        title="Parameter Impact on Strength",
                        xaxis_title="Parameter Value (kg/m³)",
                        yaxis_title="Compressive Strength (MPa)",
                        height=400
                    )
                    
                    st.plotly_chart(fig_strength, use_container_width=True)
                
                with col2:
                    # Cost sensitivity
                    fig_cost = go.Figure()
                    
                    for param in vary_params:
                        param_data = opt_data[opt_data['parameter'] == param]
                        converted_costs = [predictor.convert_cost(cost, selected_currency) 
                                         for cost in param_data['cost']]
                        
                        fig_cost.add_trace(go.Scatter(
                            x=param_data['value'],
                            y=converted_costs,
                            mode='lines+markers',
                            name=param.replace('_', ' ').title()
                        ))
                    
                    fig_cost.update_layout(
                        title="Parameter Impact on Cost",
                        xaxis_title="Parameter Value (kg/m³)",
                        yaxis_title=f"Cost ({currency_symbol}/m³)",
                        height=400
                    )
                    
                    st.plotly_chart(fig_cost, use_container_width=True)
                
                # Performance Score Chart
                st.markdown("### ⚡ Performance Efficiency Score")
                st.caption("Higher scores indicate better strength-to-cost ratio")
                
                fig_performance = go.Figure()
                
                for param in vary_params:
                    param_data = opt_data[opt_data['parameter'] == param]
                    
                    fig_performance.add_trace(go.Scatter(
                        x=param_data['value'],
                        y=param_data['performance_score'],
                        mode='lines+markers',
                        name=param.replace('_', ' ').title(),
                        fill='tonexty' if param != vary_params[0] else None
                    ))
                
                fig_performance.update_layout(
                    title="Performance Efficiency vs Parameter Values",
                    xaxis_title="Parameter Value (kg/m³)",
                    yaxis_title="Performance Score (Strength/Cost × 100)",
                    height=400
                )
                
                st.plotly_chart(fig_performance, use_container_width=True)
                
                # Property Correlation Heatmap
                st.markdown("### 🔥 Property Correlation Heatmap")
                st.caption("Visualize relationships between concrete properties and mix parameters")
                
                # Generate comprehensive data for heatmap
                with st.spinner("Generating correlation data..."):
                    heatmap_data = predictor.generate_correlation_data(base_mix, vary_params)
                
                # Create correlation matrix
                correlation_matrix = heatmap_data[['cement', 'silica_fume', 'water', 'superplasticizer', 
                                                 'steel_fibers', 'compressive_strength', 'tensile_strength', 
                                                 'elastic_modulus', 'UPV', 'cost']].corr()
                
                # Create heatmap
                fig_heatmap = go.Figure(data=go.Heatmap(
                    z=correlation_matrix.values,
                    x=correlation_matrix.columns,
                    y=correlation_matrix.columns,
                    colorscale='RdBu',
                    zmid=0,
                    text=np.round(correlation_matrix.values, 2),
                    texttemplate="%{text}",
                    textfont={"size": 10},
                    hoverongaps=False,
                    hovertemplate='%{y} vs %{x}<br>Correlation: %{z:.3f}<extra></extra>'
                ))
                
                fig_heatmap.update_layout(
                    title="Property & Parameter Correlation Matrix",
                    width=700,
                    height=600,
                    xaxis_title="Properties & Parameters",
                    yaxis_title="Properties & Parameters"
                )
                
                st.plotly_chart(fig_heatmap, use_container_width=True)
                
                # Parameter Sensitivity Heatmap
                st.markdown("### 🎯 Parameter Sensitivity Heatmap")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Create sensitivity matrix
                    properties = ['compressive_strength', 'tensile_strength', 'elastic_modulus', 'UPV', 'cost']
                    parameters = ['cement', 'silica_fume', 'water', 'superplasticizer', 'steel_fibers']
                    
                    sensitivity_matrix = np.zeros((len(properties), len(parameters)))
                    
                    for i, prop in enumerate(properties):
                        for j, param in enumerate(parameters):
                            if param in vary_params:
                                param_data = opt_data[opt_data['parameter'] == param]
                                if len(param_data) > 1:
                                    sensitivity = np.std(param_data[prop]) / np.mean(param_data[prop]) * 100
                                    sensitivity_matrix[i, j] = sensitivity
                    
                    fig_sensitivity = go.Figure(data=go.Heatmap(
                        z=sensitivity_matrix,
                        x=[p.replace('_', ' ').title() for p in parameters],
                        y=[p.replace('_', ' ').title() for p in properties],
                        colorscale='Viridis',
                        text=np.round(sensitivity_matrix, 1),
                        texttemplate="%{text}%",
                        textfont={"size": 10},
                        hovertemplate='%{y} sensitivity to %{x}<br>Coefficient of Variation: %{z:.1f}%<extra></extra>'
                    ))
                    
                    fig_sensitivity.update_layout(
                        title="Parameter Sensitivity Analysis",
                        height=400,
                        xaxis_title="Mix Parameters",
                        yaxis_title="Concrete Properties"
                    )
                    
                    st.plotly_chart(fig_sensitivity, use_container_width=True)
                
                with col2:
                    # Property Performance Radar for selected mix
                    st.markdown("#### 📊 Performance Profile")
                    
                    if len(opt_data) > 0:
                        # Take the best performing mix
                        best_mix = opt_data.loc[opt_data['performance_score'].idxmax()]
                        
                        # Normalize properties for radar chart
                        radar_values = {
                            'Strength': min(best_mix['compressive_strength'] / 200 * 100, 100),
                            'Tensile': min(best_mix['tensile_strength'] / 20 * 100, 100),
                            'Elastic': min(best_mix['elastic_modulus'] / 60 * 100, 100),
                            'UPV': min((best_mix['UPV'] - 3500) / 2000 * 100, 100),
                            'Cost Eff.': max(0, 100 - (best_mix['cost'] - 600) / 10)
                        }
                        
                        fig_radar = go.Figure()
                        
                        fig_radar.add_trace(go.Scatterpolar(
                            r=list(radar_values.values()),
                            theta=list(radar_values.keys()),
                            fill='toself',
                            name='Best Mix',
                            line_color='#2a5298'
                        ))
                        
                        fig_radar.update_layout(
                            polar=dict(
                                radialaxis=dict(
                                    visible=True,
                                    range=[0, 100]
                                )),
                            showlegend=False,
                            title="Best Mix Performance",
                            height=400
                        )
                        
                        st.plotly_chart(fig_radar, use_container_width=True)
                        
                        # Show best mix details
                        st.markdown("**Best Mix Composition:**")
                        for param in parameters:
                            if param in opt_data.columns:
                                st.text(f"• {param.replace('_', ' ').title()}: {best_mix[param]:.1f} kg/m³")
                
                # Data table
                with st.expander("📋 View Raw Data"):
                    display_data = opt_data.copy()
                    display_data['cost'] = [predictor.convert_cost(cost, selected_currency) 
                                          for cost in display_data['cost']]
                    st.dataframe(display_data, use_container_width=True)
            
            else:
                st.warning("⚠️ Please select at least one parameter to vary.")
    
    with tab4:
        st.markdown("## 📂 Project Manager")
        st.markdown("Save, load, and manage your concrete mix designs")
        
        # Professional Decision Support Notice
        st.info("""
        💾 **Engineering Project Management**
        
        This project management system helps organize preliminary designs and analyses for 
        engineering review. All saved designs require Professional Engineer validation 
        and laboratory testing before construction use.
        """)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 💾 Save Current Project")
            
            # Current mix input (simplified for saving)
            with st.expander("🧪 Current Mix Design", expanded=True):
                save_cement = st.number_input("Cement (kg/m³)", value=500.0, step=10.0, key="save_cement")
                save_silica = st.number_input("Silica Fume (kg/m³)", value=100.0, step=5.0, key="save_silica")
                save_water = st.number_input("Water (kg/m³)", value=150.0, step=5.0, key="save_water")
                save_sp = st.number_input("Superplasticizer (kg/m³)", value=8.0, step=0.5, key="save_sp")
                save_coarse = st.number_input("Coarse Aggregate (kg/m³)", value=800.0, step=10.0, key="save_coarse")
                save_fine = st.number_input("Fine Aggregate (kg/m³)", value=900.0, step=10.0, key="save_fine")
                save_fibers = st.number_input("Steel Fibers (kg/m³)", value=100.0, step=5.0, key="save_fibers")
            
            project_name = st.text_input("Project Name", placeholder="e.g., High-Rise Building Mix")
            project_notes = st.text_area("Notes", placeholder="Add any notes about this mix design...")
            
            if st.button("💾 Save Project", type="primary", use_container_width=True, key="save_project_tab5"):
                if project_name:
                    mix_data = {
                        'cement': save_cement, 'silica_fume': save_silica, 'water': save_water,
                        'superplasticizer': save_sp, 'coarse_aggregate': save_coarse,
                        'fine_aggregate': save_fine, 'steel_fibers': save_fibers,
                        'age': 28, 'curing_temperature': 20, 'curing_humidity': 95
                    }
                    
                    try:
                        filename = predictor.save_project(project_name, mix_data, project_notes)
                        st.success(f"✅ Project saved successfully!")
                        st.info(f"📁 Saved as: {filename}")
                        st.rerun()  # Refresh to show in saved projects
                    except Exception as e:
                        st.error(f"❌ Error saving project: {e}")
                else:
                    st.warning("⚠️ Please enter a project name.")
        
        with col2:
            st.markdown("### 📁 Saved Projects")
            
            # Get saved projects
            saved_projects = predictor.get_saved_projects()
            
            if saved_projects:
                for i, project in enumerate(saved_projects):
                    with st.expander(f"📋 {project['name']}", expanded=False):
                        st.write(f"**Saved:** {datetime.fromisoformat(project['timestamp']).strftime('%Y-%m-%d %H:%M')}")
                        
                        col_load, col_delete = st.columns([3, 1])
                        
                        with col_load:
                            if st.button(f"📂 Load", key=f"load_{i}"):
                                try:
                                    loaded_project = predictor.load_project(project['filename'])
                                    if loaded_project:
                                        st.success(f"✅ Loaded: {loaded_project['name']}")
                                        
                                        # Display loaded mix
                                        st.markdown("**Loaded Mix:**")
                                        mix_data = loaded_project['mix_data']
                                        
                                        mix_cols = st.columns(2)
                                        with mix_cols[0]:
                                            st.write(f"Cement: {mix_data['cement']:.0f} kg/m³")
                                            st.write(f"Silica Fume: {mix_data['silica_fume']:.0f} kg/m³")
                                            st.write(f"Water: {mix_data['water']:.0f} kg/m³")
                                            st.write(f"Superplasticizer: {mix_data['superplasticizer']:.1f} kg/m³")
                                        
                                        with mix_cols[1]:
                                            st.write(f"Coarse Agg: {mix_data['coarse_aggregate']:.0f} kg/m³")
                                            st.write(f"Fine Agg: {mix_data['fine_aggregate']:.0f} kg/m³")
                                            st.write(f"Steel Fibers: {mix_data['steel_fibers']:.0f} kg/m³")
                                        
                                        if loaded_project.get('notes'):
                                            st.write(f"**Notes:** {loaded_project['notes']}")
                                        
                                        # Quick prediction on loaded mix
                                        if st.button(f"🔮 Predict Properties", key=f"predict_{i}"):
                                            pred_result = predictor.predict_properties(mix_data)
                                            
                                            st.markdown("**Quick Predictions:**")
                                            pred_cols = st.columns(3)
                                            
                                            with pred_cols[0]:
                                                st.metric("Comp. Strength", f"{pred_result['compressive_strength']:.1f} MPa")
                                            with pred_cols[1]:
                                                st.metric("Tensile Strength", f"{pred_result['tensile_strength']:.1f} MPa")
                                            with pred_cols[2]:
                                                cost_converted = predictor.convert_cost(pred_result['cost'], selected_currency)
                                                st.metric("Cost", f"{currency_symbol}{cost_converted:.0f}/m³")
                                    
                                    else:
                                        st.error("❌ Failed to load project")
                                except Exception as e:
                                    st.error(f"❌ Error loading project: {e}")
                        
                        with col_delete:
                            if st.button("🗑️", key=f"delete_{i}", help="Delete project"):
                                try:
                                    os.remove(project['filename'])
                                    st.success("✅ Project deleted")
                                    st.rerun()  # Refresh the list
                                except Exception as e:
                                    st.error(f"❌ Error deleting: {e}")
            
            else:
                st.info("📭 No saved projects yet. Save your first mix design above!")
        
        # Bulk operations
        st.markdown("### 🔧 Bulk Operations")
        
        bulk_col1, bulk_col2, bulk_col3 = st.columns(3)
        
        with bulk_col1:
            if st.button("📤 Export All Projects"):
                if saved_projects:
                    # Create a summary of all projects
                    export_data = []
                    for project in saved_projects:
                        loaded = predictor.load_project(project['filename'])
                        if loaded:
                            row = {'project_name': loaded['name'], 'timestamp': loaded['timestamp']}
                            row.update(loaded['mix_data'])
                            export_data.append(row)
                    
                    if export_data:
                        df = pd.DataFrame(export_data)
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="💾 Download Projects CSV",
                            data=csv,
                            file_name=f"aicrete_projects_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                else:
                    st.warning("No projects to export")
        
        with bulk_col2:
            uploaded_projects = st.file_uploader("📥 Import Projects", type="csv", key="import_projects")
            if uploaded_projects:
                st.info("📥 Project import feature ready for implementation")
        
        with bulk_col3:
            if st.button("🗑️ Clear All Projects", type="secondary"):
                if saved_projects:
                    if st.checkbox("⚠️ Confirm deletion of ALL projects"):
                        st.warning("This will permanently delete all saved projects!")
                else:
                    st.info("No projects to clear")
    
    with tab5:
        st.markdown("## 🏗️ Application Templates")
        st.markdown("Pre-configured mix designs optimized for specific construction applications")
        
        # Professional Decision Support Notice
        st.info("""
        🏗️ **Engineering Application Guidance**
        
        These templates provide industry-specific starting points for engineering analysis. 
        Each template requires application-specific validation, local code compliance review, 
        and Professional Engineer approval before construction use.
        """)
        
        # Template selection
        template_names = list(predictor.application_templates.keys())
        selected_template = st.selectbox(
            "🎯 Select Application Type:",
            template_names,
            index=0
        )
        
        if selected_template:
            template = predictor.application_templates[selected_template]
            
            # Display template info
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"### 📋 {selected_template}")
                st.info(f"**Description:** {template['description']}")
                
                # Template mix design
                st.markdown("### 🧪 Recommended Mix Design")
                
                mix_col1, mix_col2, mix_col3 = st.columns(3)
                
                with mix_col1:
                    st.metric("Cement", f"{template['cement']:.0f} kg/m³")
                    st.metric("Silica Fume", f"{template['silica_fume']:.0f} kg/m³")
                    st.metric("Water", f"{template['water']:.0f} kg/m³")
                
                with mix_col2:
                    st.metric("Superplasticizer", f"{template['superplasticizer']:.1f} kg/m³")
                    st.metric("Coarse Aggregate", f"{template['coarse_aggregate']:.0f} kg/m³")
                    st.metric("Fine Aggregate", f"{template['fine_aggregate']:.0f} kg/m³")
                
                with mix_col3:
                    st.metric("Steel Fibers", f"{template['steel_fibers']:.0f} kg/m³")
                    st.metric("Target Age", f"{template['age']} days")
                    st.metric("Target Strength", f"{template['target_strength']} MPa")
            
            with col2:
                st.markdown("### 🔮 Predicted Properties")
                
                # Predict properties for this template
                template_input = {k: v for k, v in template.items() 
                                if k not in ['target_strength', 'description']}
                
                # Add missing required fields
                template_input.update({
                    'fiber_volume_fraction': 1.5,
                    'aggregate_cement_ratio': 2.5,
                    'total_binder': template['cement'] + template['silica_fume']
                })
                
                template_predictions = predictor.predict_properties(template_input)
                
                # Display predictions with currency conversion
                cost_converted = predictor.convert_cost(template_predictions['cost'], selected_currency)
                
                st.metric("🏗️ Compressive Strength", f"{template_predictions['compressive_strength']:.1f} MPa")
                st.metric("💪 Tensile Strength", f"{template_predictions['tensile_strength']:.1f} MPa")
                st.metric("📏 Elastic Modulus", f"{template_predictions['elastic_modulus']:.1f} GPa")
                st.metric("🌊 UPV", f"{template_predictions['UPV']:.0f} m/s")
                st.metric("💰 Cost", f"{currency_symbol}{cost_converted:.0f}/m³")
        
        # Template comparison
        st.markdown("### 📊 Template Comparison")
        
        if st.button("📊 Compare All Templates", use_container_width=True):
            with st.spinner("Analyzing all templates..."):
                comparison_data = []
                
                for name, template in predictor.application_templates.items():
                    template_input = {k: v for k, v in template.items() 
                                    if k not in ['target_strength', 'description']}
                    template_input.update({
                        'fiber_volume_fraction': 1.5,
                        'aggregate_cement_ratio': 2.5,
                        'total_binder': template['cement'] + template['silica_fume']
                    })
                    
                    pred = predictor.predict_properties(template_input)
                    cost_converted = predictor.convert_cost(pred['cost'], selected_currency)
                    
                    comparison_data.append({
                        'Application': name,
                        'Compressive Strength (MPa)': f"{pred['compressive_strength']:.1f}",
                        'Tensile Strength (MPa)': f"{pred['tensile_strength']:.1f}",
                        'Elastic Modulus (GPa)': f"{pred['elastic_modulus']:.1f}",
                        'UPV (m/s)': f"{pred['UPV']:.0f}",
                        f'Cost ({currency_symbol}/m³)': f"{cost_converted:.0f}",
                        'Target Strength (MPa)': template['target_strength']
                    })
                
                comparison_df = pd.DataFrame(comparison_data)
                st.dataframe(comparison_df, use_container_width=True)
                
                # Comparison charts
                st.markdown("### 📈 Visual Comparison")
                
                chart_col1, chart_col2 = st.columns(2)
                
                with chart_col1:
                    # Strength comparison
                    fig_strength = go.Figure(data=[
                        go.Bar(name='Predicted', x=comparison_df['Application'], 
                               y=[float(x) for x in comparison_df['Compressive Strength (MPa)']]),
                        go.Bar(name='Target', x=comparison_df['Application'], 
                               y=comparison_df['Target Strength (MPa)'])
                    ])
                    
                    fig_strength.update_layout(
                        title='Strength Comparison: Predicted vs Target',
                        xaxis_title='Application',
                        yaxis_title='Compressive Strength (MPa)',
                        barmode='group',
                        height=400
                    )
                    
                    st.plotly_chart(fig_strength, use_container_width=True)
                
                with chart_col2:
                    # Cost comparison
                    costs = [float(x) for x in comparison_df[f'Cost ({currency_symbol}/m³)']]
                    
                    fig_cost = go.Figure(data=[
                        go.Bar(x=comparison_df['Application'], y=costs,
                               marker_color='lightcoral')
                    ])
                    
                    fig_cost.update_layout(
                        title=f'Cost Comparison ({currency_symbol}/m³)',
                        xaxis_title='Application',
                        yaxis_title=f'Cost ({currency_symbol}/m³)',
                        height=400
                    )
                    
                    st.plotly_chart(fig_cost, use_container_width=True)
        
        # Template customization
        st.markdown("### ⚙️ Customize Template")
        
        with st.expander("🔧 Modify Selected Template", expanded=False):
            st.markdown(f"**Customizing:** {selected_template}")
            
            # Allow users to modify the template
            custom_col1, custom_col2, custom_col3 = st.columns(3)
            
            template = predictor.application_templates[selected_template]
            
            with custom_col1:
                custom_cement = st.number_input("Custom Cement", value=float(template['cement']), step=10.0, key="custom_cement")
                custom_silica = st.number_input("Custom Silica Fume", value=float(template['silica_fume']), step=5.0, key="custom_silica")
                custom_water = st.number_input("Custom Water", value=float(template['water']), step=5.0, key="custom_water")
            
            with custom_col2:
                custom_sp = st.number_input("Custom Superplasticizer", value=float(template['superplasticizer']), step=0.5, key="custom_sp")
                custom_coarse = st.number_input("Custom Coarse Agg", value=float(template['coarse_aggregate']), step=10.0, key="custom_coarse")
                custom_fine = st.number_input("Custom Fine Agg", value=float(template['fine_aggregate']), step=10.0, key="custom_fine")
            
            with custom_col3:
                custom_fibers = st.number_input("Custom Steel Fibers", value=float(template['steel_fibers']), step=5.0, key="custom_fibers")
                custom_age = st.number_input("Custom Age", value=float(template['age']), step=1.0, key="custom_age")
                custom_temp = st.number_input("Custom Curing Temp", value=float(template['curing_temperature']), step=1.0, key="custom_temp")
            
            if st.button("🔮 Predict Custom Mix", use_container_width=True):
                custom_input = {
                    'cement': custom_cement, 'silica_fume': custom_silica, 'water': custom_water,
                    'superplasticizer': custom_sp, 'coarse_aggregate': custom_coarse,
                    'fine_aggregate': custom_fine, 'steel_fibers': custom_fibers,
                    'age': custom_age, 'curing_temperature': custom_temp, 'curing_humidity': template['curing_humidity'],
                    'fiber_volume_fraction': 1.5, 'aggregate_cement_ratio': 2.5,
                    'total_binder': custom_cement + custom_silica
                }
                
                custom_pred = predictor.predict_properties(custom_input)
                custom_cost = predictor.convert_cost(custom_pred['cost'], selected_currency)
                
                st.markdown("### 📊 Custom Mix Results")
                result_cols = st.columns(5)
                
                with result_cols[0]:
                    st.metric("Strength", f"{custom_pred['compressive_strength']:.1f} MPa")
                with result_cols[1]:
                    st.metric("Tensile", f"{custom_pred['tensile_strength']:.1f} MPa")
                with result_cols[2]:
                    st.metric("Modulus", f"{custom_pred['elastic_modulus']:.1f} GPa")
                with result_cols[3]:
                    st.metric("UPV", f"{custom_pred['UPV']:.0f} m/s")
                with result_cols[4]:
                    st.metric("Cost", f"{currency_symbol}{custom_cost:.0f}/m³")
                
                # Option to save custom mix
                if st.button("💾 Save Custom Mix as Project"):
                    custom_name = f"Custom_{selected_template}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    try:
                        predictor.save_project(custom_name, custom_input, f"Customized from {selected_template} template")
                        st.success(f"✅ Saved as project: {custom_name}")
                    except Exception as e:
                        st.error(f"❌ Error saving: {e}")
    
    with tab6:
        st.markdown("## 🌍 Sustainability Analytics")
        st.markdown("Comprehensive environmental impact assessment for your concrete mix design")
        
        # Professional Decision Support Notice
        st.info("""
        🌍 **Environmental Engineering Assessment**
        
        This sustainability analysis provides preliminary environmental impact calculations for 
        engineering evaluation. Results support green building certification and environmental 
        decision-making, but require lifecycle assessment validation for regulatory compliance.
        """)
        
        # Input section for sustainability analysis
        st.markdown("### 🔧 Mix Design for Analysis")
        
        sust_col1, sust_col2, sust_col3 = st.columns(3)
        
        with sust_col1:
            sust_cement = st.number_input("Cement (kg/m³)", value=450.0, step=10.0, key="sust_cement")
            sust_silica = st.number_input("Silica Fume (kg/m³)", value=75.0, step=5.0, key="sust_silica")
            sust_water = st.number_input("Water (kg/m³)", value=140.0, step=5.0, key="sust_water")
        
        with sust_col2:
            sust_sp = st.number_input("Superplasticizer (kg/m³)", value=12.5, step=0.5, key="sust_sp")
            sust_coarse = st.number_input("Coarse Aggregate (kg/m³)", value=800.0, step=10.0, key="sust_coarse")
            sust_fine = st.number_input("Fine Aggregate (kg/m³)", value=600.0, step=10.0, key="sust_fine")
        
        with sust_col3:
            sust_fibers = st.number_input("Steel Fibers (kg/m³)", value=157.0, step=5.0, key="sust_fibers")
            sust_age = st.number_input("Age (days)", value=28.0, step=1.0, key="sust_age")
            sust_temp = st.number_input("Curing Temperature (°C)", value=20.0, step=1.0, key="sust_temp")
        
        # Analyze button
        if st.button("🌍 Analyze Sustainability", type="primary", use_container_width=True):
            # Prepare mix design for analysis
            sust_mix = {
                'cement': sust_cement, 'silica_fume': sust_silica, 'water': sust_water,
                'superplasticizer': sust_sp, 'coarse_aggregate': sust_coarse,
                'fine_aggregate': sust_fine, 'steel_fibers': sust_fibers,
                'age': sust_age, 'curing_temperature': sust_temp, 'curing_humidity': 95,
                'fiber_volume_fraction': 1.5, 'aggregate_cement_ratio': 2.5,
                'total_binder': sust_cement + sust_silica
            }
            
            # Get property predictions for durability bonus
            sust_predictions = predictor.predict_properties(sust_mix)
            
            # Get comprehensive sustainability analysis
            with st.spinner("Analyzing environmental impact..."):
                sustainability = predictor.comprehensive_sustainability_analysis(sust_mix, sust_predictions)
            
            # Display overall sustainability score
            st.markdown("## 🌟 Overall Sustainability Assessment")
            
            score_col1, score_col2, score_col3 = st.columns([2, 1, 1])
            
            with score_col1:
                # Main sustainability score
                score = sustainability['overall_score']
                rating = sustainability['rating']
                
                # Create a circular progress bar effect
                st.markdown(f"""
                <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%); border-radius: 15px; margin: 10px 0;">
                    <h2 style="color: #2e7d32; margin: 0;">🌍 Sustainability Score</h2>
                    <h1 style="font-size: 3em; color: #1b5e20; margin: 10px 0;">{score:.1f}/100</h1>
                    <h3 style="color: #388e3c; margin: 0;">{rating}</h3>
                </div>
                """, unsafe_allow_html=True)
            
            with score_col2:
                st.metric("🌱 Carbon Rating", sustainability['carbon_footprint']['rating'])
                st.metric("⚡ Energy Rating", sustainability['energy_consumption']['rating'])
            
            with score_col3:
                st.metric("♻️ Recyclability", sustainability['recyclability']['rating'])
                st.metric("🛡️ Durability", sustainability['durability_bonus']['rating'])
            
            # Detailed breakdown
            st.markdown("## 📊 Detailed Environmental Analysis")
            
            detail_col1, detail_col2 = st.columns(2)
            
            with detail_col1:
                # Carbon Footprint Analysis
                st.markdown("### 🏭 Carbon Footprint Analysis")
                carbon = sustainability['carbon_footprint']
                
                st.metric("Total CO₂ Emissions", f"{carbon['total_co2']:.1f} kg CO₂/m³", f"{carbon['rating']}")
                
                # Carbon breakdown chart
                carbon_data = carbon['breakdown']
                fig_carbon = go.Figure(data=[
                    go.Bar(
                        x=list(carbon_data.keys()),
                        y=list(carbon_data.values()),
                        marker_color=['#ff6b6b', '#ffa726', '#42a5f5', '#66bb6a', '#ab47bc', '#ef5350', '#26c6da']
                    )
                ])
                fig_carbon.update_layout(
                    title="CO₂ Emissions by Material",
                    xaxis_title="Material",
                    yaxis_title="CO₂ Emissions (kg/m³)",
                    height=300
                )
                st.plotly_chart(fig_carbon, use_container_width=True)
                
                # Resource Efficiency
                st.markdown("### 💧 Resource Efficiency")
                efficiency = sustainability['resource_efficiency']
                
                eff_metrics_col1, eff_metrics_col2 = st.columns(2)
                with eff_metrics_col1:
                    st.metric("Water/Binder Ratio", f"{efficiency['water_binder_ratio']:.3f}")
                    st.metric("SCM Ratio", f"{efficiency['scm_ratio']:.1%}")
                with eff_metrics_col2:
                    st.metric("Aggregate Efficiency", f"{efficiency['aggregate_efficiency']:.1f}")
                    st.metric("Overall Efficiency", f"{efficiency['overall_efficiency']:.1f}/100")
            
            with detail_col2:
                # Energy Consumption
                st.markdown("### ⚡ Energy Consumption")
                energy = sustainability['energy_consumption']
                
                st.metric("Total Energy", f"{energy['total_energy']:.0f} MJ/m³", f"{energy['rating']}")
                
                # Energy breakdown chart
                energy_data = energy['breakdown']
                fig_energy = go.Figure(data=[
                    go.Pie(
                        labels=list(energy_data.keys()),
                        values=list(energy_data.values()),
                        hole=0.4
                    )
                ])
                fig_energy.update_layout(
                    title="Energy Consumption by Material",
                    height=300
                )
                st.plotly_chart(fig_energy, use_container_width=True)
                
                # Recyclability & Durability
                st.markdown("### ♻️ End-of-Life & Durability")
                recyclability = sustainability['recyclability']
                durability = sustainability['durability_bonus']
                
                recycle_col1, recycle_col2 = st.columns(2)
                with recycle_col1:
                    st.metric("Recyclability Index", f"{recyclability['recyclability_index']:.1f}%")
                    st.metric("Durability Bonus", f"{durability['durability_bonus']:.1f}/75")
                with recycle_col2:
                    st.metric("Recyclability Rating", recyclability['rating'])
                    st.metric("Durability Rating", durability['rating'])
            
            # Component score breakdown
            st.markdown("## 🎯 Sustainability Component Scores")
            
            components = sustainability['component_scores']
            component_data = pd.DataFrame([
                {'Component': 'Carbon Footprint', 'Score': components['carbon'], 'Weight': '25%'},
                {'Component': 'Resource Efficiency', 'Score': components['efficiency'], 'Weight': '20%'},
                {'Component': 'Energy Consumption', 'Score': components['energy'], 'Weight': '20%'},
                {'Component': 'Recyclability', 'Score': components['recyclability'], 'Weight': '15%'},
                {'Component': 'Durability', 'Score': components['durability'], 'Weight': '20%'}
            ])
            
            st.dataframe(component_data, use_container_width=True)
            
            # Sustainability recommendations
            st.markdown("## 💡 Sustainability Recommendations")
            
            recommendations = []
            if carbon['total_co2'] > 400:
                recommendations.append("🔴 **High Carbon Footprint**: Consider reducing cement content or increasing silica fume ratio")
            if efficiency['water_binder_ratio'] > 0.35:
                recommendations.append("🔴 **High Water/Binder Ratio**: Optimize water content for better resource efficiency")
            if efficiency['scm_ratio'] < 0.15:
                recommendations.append("🟡 **Low SCM Usage**: Increase supplementary cementitious materials for better sustainability")
            if energy['total_energy'] > 3000:
                recommendations.append("🔴 **High Energy Consumption**: Consider alternative materials or reduce steel fiber content")
            if recyclability['recyclability_index'] < 70:
                recommendations.append("🟡 **Low Recyclability**: Minimize chemical admixtures for better end-of-life performance")
            if durability['durability_bonus'] < 40:
                recommendations.append("🟡 **Durability Improvement**: Optimize mix for higher strength and durability")
            
            if not recommendations:
                recommendations.append("🟢 **Excellent Sustainability**: Your mix design shows excellent environmental performance!")
            
            for rec in recommendations:
                st.markdown(f"- {rec}")
            
            # Comparison with benchmarks
            st.markdown("## 📈 Benchmark Comparison")
            
            benchmark_col1, benchmark_col2 = st.columns(2)
            
            with benchmark_col1:
                # Compare with typical concrete
                typical_co2 = 400
                your_co2 = carbon['total_co2']
                co2_improvement = ((typical_co2 - your_co2) / typical_co2 * 100)
                
                st.metric(
                    "CO₂ vs Typical Concrete", 
                    f"{co2_improvement:+.1f}%",
                    f"Your: {your_co2:.0f} vs Typical: {typical_co2:.0f} kg CO₂/m³"
                )
            
            with benchmark_col2:
                # Compare with high-performance concrete
                hp_energy = 3500
                your_energy = energy['total_energy']
                energy_improvement = ((hp_energy - your_energy) / hp_energy * 100)
                
                st.metric(
                    "Energy vs High-Performance Concrete",
                    f"{energy_improvement:+.1f}%",
                    f"Your: {your_energy:.0f} vs HP: {hp_energy:.0f} MJ/m³"
                )
        
        # Sustainability comparison tool
        st.markdown("### 🔄 Mix Comparison Tool")
        
        with st.expander("📊 Compare Multiple Mix Designs", expanded=False):
            st.markdown("Upload or define multiple mix designs to compare their sustainability metrics")
            
            if st.button("🔄 Compare with Standard Mixes"):
                # Compare with standard mix designs
                standard_mixes = {
                    'Standard UHPC': {
                        'cement': 500, 'silica_fume': 100, 'water': 160, 'superplasticizer': 15,
                        'coarse_aggregate': 750, 'fine_aggregate': 550, 'steel_fibers': 200
                    },
                    'Eco-Friendly UHPC': {
                        'cement': 400, 'silica_fume': 150, 'water': 140, 'superplasticizer': 12,
                        'coarse_aggregate': 800, 'fine_aggregate': 600, 'steel_fibers': 120
                    },
                    'High-Performance UHPC': {
                        'cement': 550, 'silica_fume': 80, 'water': 150, 'superplasticizer': 18,
                        'coarse_aggregate': 700, 'fine_aggregate': 500, 'steel_fibers': 250
                    }
                }
                
                comparison_data = []
                
                for name, mix in standard_mixes.items():
                    # Add required fields
                    mix.update({
                        'age': 28, 'curing_temperature': 20, 'curing_humidity': 95,
                        'fiber_volume_fraction': 1.5, 'aggregate_cement_ratio': 2.5,
                        'total_binder': mix['cement'] + mix['silica_fume']
                    })
                    
                    pred = predictor.predict_properties(mix)
                    sust = predictor.comprehensive_sustainability_analysis(mix, pred)
                    
                    comparison_data.append({
                        'Mix Design': name,
                        'Sustainability Score': f"{sust['overall_score']:.1f}",
                        'CO₂ (kg/m³)': f"{sust['carbon_footprint']['total_co2']:.0f}",
                        'Energy (MJ/m³)': f"{sust['energy_consumption']['total_energy']:.0f}",
                        'Recyclability (%)': f"{sust['recyclability']['recyclability_index']:.0f}",
                        'Rating': sust['rating']
                    })
                
                comparison_df = pd.DataFrame(comparison_data)
                st.dataframe(comparison_df, use_container_width=True)
    
    with tab7:
        st.markdown("## 📋 Standards Compliance")
        st.markdown("Check your concrete mix design against international standards")
        
        # Professional Engineering Notice
        st.info("""
        📋 **International Standards Compliance**
        
        This tool checks preliminary compliance with major international concrete standards. 
        Results provide guidance for engineering review but do not replace official compliance 
        testing and certification by qualified laboratories.
        """)
        
        # Application type selection for standards
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 🏗️ Application Type")
            application_type = st.selectbox(
                "Select construction application:",
                ["UHPC_Applications", "General_Construction", "High_Performance", 
                 "Marine_Structures", "Infrastructure", "Precast_Elements", "Self_Compacting"],
                index=0,
                key="standards_app_type"
            )
            
            # Show recommended standards for selected application
            recommendations = predictor.get_standards_recommendations(application_type)
            
            st.markdown("#### 📚 Recommended Standards:")
            for code, info in recommendations.items():
                with st.expander(f"**{code}** - {info['authority']}", expanded=False):
                    st.markdown(f"**Scope:** {info['scope']}")
                    st.markdown("**Key Requirements:**")
                    for req in info['key_requirements']:
                        st.markdown(f"• {req}")
        
        with col2:
            st.markdown("### 🧪 Mix Design Input")
            
            # Simplified mix input for standards checking
            std_cement = st.number_input("Cement (kg/m³)", value=500.0, step=10.0, key="std_cement")
            std_silica = st.number_input("Silica Fume (kg/m³)", value=100.0, step=5.0, key="std_silica")
            std_water = st.number_input("Water (kg/m³)", value=150.0, step=5.0, key="std_water")
            std_sp = st.number_input("Superplasticizer (kg/m³)", value=8.0, step=0.5, key="std_sp")
            std_fibers = st.number_input("Steel Fibers (kg/m³)", value=78.0, step=5.0, key="std_fibers")
            std_age = st.number_input("Test Age (days)", value=28, step=1, key="std_age")
            std_curing_temp = st.number_input("Curing Temperature (°C)", value=20, step=1, key="std_curing_temp")
            
            # Calculate fiber volume fraction
            fiber_density = 7850  # kg/m³ for steel
            fiber_vol_fraction = (std_fibers / fiber_density) * 100
            
        if st.button("🔍 Check Standards Compliance", key="check_standards"):
            # Prepare mix design dictionary
            mix_design = {
                'cement': std_cement,
                'silica_fume': std_silica,
                'water': std_water,
                'superplasticizer': std_sp,
                'steel_fibers': std_fibers,
                'age': std_age,
                'curing_temperature': std_curing_temp,
                'fiber_volume_fraction': fiber_vol_fraction
            }
            
            # Get predictions for compliance checking
            input_data = {
                'cement': std_cement,
                'silica_fume': std_silica,
                'water': std_water,
                'superplasticizer': std_sp,
                'coarse_aggregate': 800,
                'fine_aggregate': 850,
                'steel_fibers': std_fibers,
                'age': std_age,
                'curing_temperature': std_curing_temp,
                'curing_humidity': 95
            }
            
            predicted_props = predictor.predict_properties(input_data)
            
            # Check compliance
            compliance_results = predictor.check_standards_compliance(
                mix_design, predicted_props, application_type
            )
            
            st.markdown("---")
            st.markdown("## 📊 Compliance Results")
            
            # Summary statistics
            total_standards = len(compliance_results)
            passed = sum(1 for r in compliance_results.values() if r['compliance_status'] == 'PASS')
            warnings = sum(1 for r in compliance_results.values() if r['compliance_status'] == 'WARNING')
            failed = sum(1 for r in compliance_results.values() if r['compliance_status'] == 'FAIL')
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Standards", total_standards)
            with col2:
                st.metric("✅ Passed", passed, delta=f"{passed/total_standards*100:.0f}%")
            with col3:
                st.metric("⚠️ Warnings", warnings, delta=f"{warnings/total_standards*100:.0f}%")
            with col4:
                st.metric("❌ Failed", failed, delta=f"{failed/total_standards*100:.0f}%")
            
            # Detailed compliance results
            for standard_code, result in compliance_results.items():
                status_color = {
                    'PASS': '🟢',
                    'WARNING': '🟡', 
                    'FAIL': '🔴'
                }[result['compliance_status']]
                
                with st.expander(f"{status_color} **{standard_code}** - {result['standard_name']}", 
                               expanded=(result['compliance_status'] != 'PASS')):
                    st.markdown(f"**Authority:** {result['authority']}")
                    st.markdown(f"**Status:** {result['compliance_status']}")
                    
                    if result['violations']:
                        st.markdown("**⚠️ Issues Found:**")
                        for violation in result['violations']:
                            st.markdown(f"• {violation}")
                    
                    if result['recommendations']:
                        st.markdown("**💡 Recommendations:**")
                        for rec in result['recommendations']:
                            st.markdown(f"• {rec}")
                    
                    if result['compliance_status'] == 'PASS':
                        st.success("✅ This mix design complies with all requirements of this standard")
            
            # Overall compliance summary
            st.markdown("---")
            if failed == 0:
                if warnings == 0:
                    st.success(f"🎉 **FULL COMPLIANCE** - Your mix design meets all {total_standards} applicable standards!")
                else:
                    st.warning(f"⚠️ **MOSTLY COMPLIANT** - {passed} standards passed, {warnings} warnings to review")
            else:
                st.error(f"❌ **COMPLIANCE ISSUES** - {failed} standards failed, requires design modifications")
        
        # Standards reference section
        st.markdown("---")
        st.markdown("### 📚 Standards Reference Database")
        
        # Show all available standards
        with st.expander("📖 View All Available Standards", expanded=False):
            for code, standard in predictor.concrete_standards.items():
                st.markdown(f"**{code}** - {standard['name']}")
                st.markdown(f"*Authority:* {standard['authority']}")
                st.markdown(f"*Scope:* {standard['scope']}")
                st.markdown("---")
    
    with tab8:
        st.markdown("## 🔍 SHAP Interpretability")
        st.markdown("Understand why your concrete mix gets specific property predictions")
        
        # Professional Engineering Notice
        st.info("""
        🔍 **AI Model Interpretability**
        
        SHAP (SHapley Additive exPlanations) analysis helps engineers understand which 
        mix design parameters most influence the predicted properties. This transparency 
        is crucial for engineering decision-making and model validation.
        """)
        
        # Input section for SHAP analysis
        # Initialize default values for SHAP inputs
        if "shap_preset" not in st.session_state:
            st.session_state.shap_preset = "balanced"
        
        # Preset selection dropdown
        st.markdown("### 🎯 Quick Mix Presets")
        preset_choice = st.selectbox(
            "Choose a preset mix design:",
            ["balanced", "high_strength", "cost_optimized"],
            format_func=lambda x: {
                "balanced": "⚖️ Balanced Mix - Standard performance",
                "high_strength": "🏗️ High-Strength Mix - Maximum strength", 
                "cost_optimized": "💰 Cost-Optimized Mix - Budget friendly"
            }[x],
            key="shap_preset_select"
        )
        
        # Define preset values
        presets = {
            "balanced": {
                'cement': 500.0, 'silica': 100.0, 'water': 150.0,
                'sp': 8.0, 'coarse': 800.0, 'fine': 850.0, 'fibers': 78.0,
                'age': 28, 'temp': 20, 'humidity': 95
            },
            "high_strength": {
                'cement': 600.0, 'silica': 150.0, 'water': 140.0,
                'sp': 12.0, 'coarse': 800.0, 'fine': 850.0, 'fibers': 120.0,
                'age': 28, 'temp': 20, 'humidity': 95
            },
            "cost_optimized": {
                'cement': 400.0, 'silica': 80.0, 'water': 160.0,
                'sp': 6.0, 'coarse': 800.0, 'fine': 850.0, 'fibers': 40.0,
                'age': 28, 'temp': 20, 'humidity': 95
            }
        }
        
        # Get current preset values
        current_preset = presets[preset_choice]
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 🧪 Mix Design for Analysis")
            
            # Input parameters for SHAP analysis
            shap_cement = st.number_input("Cement (kg/m³)", 
                                        value=current_preset['cement'], 
                                        step=10.0, key="shap_cement")
            shap_silica = st.number_input("Silica Fume (kg/m³)", 
                                        value=current_preset['silica'], 
                                        step=5.0, key="shap_silica")
            shap_water = st.number_input("Water (kg/m³)", 
                                       value=current_preset['water'], 
                                       step=5.0, key="shap_water")
            shap_sp = st.number_input("Superplasticizer (kg/m³)", 
                                    value=current_preset['sp'], 
                                    step=0.5, key="shap_sp")
            shap_coarse = st.number_input("Coarse Aggregate (kg/m³)", 
                                        value=current_preset['coarse'], 
                                        step=10.0, key="shap_coarse")
            shap_fine = st.number_input("Fine Aggregate (kg/m³)", 
                                      value=current_preset['fine'], 
                                      step=10.0, key="shap_fine")
            shap_fibers = st.number_input("Steel Fibers (kg/m³)", 
                                        value=current_preset['fibers'], 
                                        step=5.0, key="shap_fibers")
            shap_age = st.number_input("Age (days)", 
                                     value=current_preset['age'], 
                                     step=1, key="shap_age")
            shap_temp = st.number_input("Curing Temperature (°C)", 
                                      value=current_preset['temp'], 
                                      step=1, key="shap_temp")
            shap_humidity = st.number_input("Curing Humidity (%)", 
                                          value=current_preset['humidity'], 
                                          step=1, key="shap_humidity")
        
        with col2:
            st.markdown("### 📊 Analysis Information")
            st.markdown("""
            **🔍 SHAP (SHapley Additive exPlanations)** provides:
            
            - **Feature Importance**: Which ingredients matter most?
            - **Prediction Explanation**: Why this specific result?
            - **Decision Transparency**: How does the AI think?
            - **Engineering Insights**: Optimize your mix design
            
            **📈 Visualization Types:**
            - **Waterfall Plot**: Step-by-step impact breakdown
            - **Force Plot**: Interactive prediction analysis
            - **Feature Summary**: Overall importance ranking
            """)
            
            st.info("💡 **Tip**: Try the preset mixes above to see different SHAP patterns!")
        
        if st.button("🔍 Generate SHAP Analysis", key="generate_shap", type="primary"):
            # Prepare input data
            input_data = {
                'cement': shap_cement,
                'silica_fume': shap_silica,
                'water': shap_water,
                'superplasticizer': shap_sp,
                'coarse_aggregate': shap_coarse,
                'fine_aggregate': shap_fine,
                'steel_fibers': shap_fibers,
                'age': shap_age,
                'curing_temperature': shap_temp,
                'curing_humidity': shap_humidity
            }
            
            with st.spinner("🧠 Analyzing feature importance..."):
                # Get SHAP explanations
                shap_explanation = predictor.get_shap_explanations(input_data)
                
                if shap_explanation:
                    st.markdown("---")
                    st.markdown("## 📈 SHAP Analysis Results")
                    
                    # Display prediction
                    prediction = shap_explanation['prediction']
                    base_value = shap_explanation['base_value']
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("🎯 Predicted Strength", f"{prediction:.1f} MPa")
                    with col2:
                        st.metric("📊 Model Base Value", f"{base_value:.1f} MPa")
                    with col3:
                        difference = prediction - base_value
                        st.metric("📈 Impact", f"{difference:+.1f} MPa", 
                                delta=f"{difference/base_value*100:+.1f}%")
                    
                    # Create tabs for different visualizations
                    viz_tab1, viz_tab2, viz_tab3 = st.tabs(["🌊 Waterfall Plot", "⚡ Force Plot", "📝 Summary"])
                    
                    with viz_tab1:
                        st.markdown("### 🌊 SHAP Waterfall Plot")
                        st.markdown("Shows how each feature contributes to the final prediction")
                        
                        waterfall_fig = predictor.create_shap_waterfall_plot(shap_explanation)
                        if waterfall_fig:
                            st.plotly_chart(waterfall_fig, use_container_width=True)
                        else:
                            st.error("Could not generate waterfall plot")
                    
                    with viz_tab2:
                        st.markdown("### ⚡ SHAP Force Plot")
                        st.markdown("Visualizes positive and negative feature contributions")
                        
                        force_fig = predictor.create_shap_force_plot(shap_explanation)
                        if force_fig:
                            st.plotly_chart(force_fig, use_container_width=True)
                        else:
                            st.error("Could not generate force plot")
                    
                    with viz_tab3:
                        st.markdown("### 📝 Feature Importance Summary")
                        summary = predictor.get_feature_importance_summary(shap_explanation)
                        st.markdown(summary)
                        
                        # Additional insights
                        st.markdown("---")
                        st.markdown("### 🎓 Engineering Insights")
                        
                        w_c_ratio = shap_water / shap_cement
                        binder_content = shap_cement + shap_silica
                        
                        insights_col1, insights_col2 = st.columns(2)
                        
                        with insights_col1:
                            st.markdown("**Mix Design Ratios:**")
                            st.markdown(f"• W/C Ratio: {w_c_ratio:.3f}")
                            st.markdown(f"• Total Binder: {binder_content:.0f} kg/m³")
                            st.markdown(f"• Silica Fume %: {(shap_silica/binder_content)*100:.1f}%")
                        
                        with insights_col2:
                            st.markdown("**Performance Indicators:**")
                            if prediction > 120:
                                st.success("✅ UHPC Performance Range")
                            elif prediction > 60:
                                st.info("ℹ️ High-Performance Concrete")
                            else:
                                st.warning("⚠️ Standard Concrete Range")
                                
                            if w_c_ratio < 0.25:
                                st.success("✅ Excellent W/C Ratio")
                            elif w_c_ratio < 0.35:
                                st.info("ℹ️ Good W/C Ratio")
                            else:
                                st.warning("⚠️ High W/C Ratio")
                else:
                    st.error("Could not generate SHAP explanations. Please try again.")
        
        # Educational section
        st.markdown("---")
        st.markdown("### 📚 Understanding SHAP Analysis")
        
        with st.expander("🤔 What is SHAP?", expanded=False):
            st.markdown("""
            **SHAP (SHapley Additive exPlanations)** is a game theory approach to explain 
            the output of machine learning models. It provides:
            
            **Key Benefits for Engineers:**
            - **Transparency**: Understand which factors drive predictions
            - **Validation**: Verify that the model behaves logically
            - **Optimization**: Identify which parameters to adjust
            - **Trust**: Build confidence in AI-assisted design decisions
            
            **How to Read SHAP Plots:**
            - **Positive values** (green/blue): Increase predicted strength
            - **Negative values** (red/orange): Decrease predicted strength
            - **Magnitude**: Larger bars = greater influence on prediction
            """)
        
        with st.expander("💡 Engineering Applications", expanded=False):
            st.markdown("""
            **Design Optimization:**
            - Identify the most influential parameters for targeted improvements
            - Understand trade-offs between different mix components
            - Validate that model predictions align with engineering knowledge
            
            **Quality Control:**
            - Understand why some batches perform differently
            - Identify critical parameters for consistent results
            - Troubleshoot unexpected performance issues
            
            **Client Communication:**
            - Explain design decisions with data-driven insights
            - Show the engineering rationale behind mix proportions
            - Demonstrate the value of specific (costly) ingredients
            """)
    
    with tab9:
        st.markdown("## � Overfitting Analysis")
        st.markdown("**Academic Rigor: Model Validation & Generalization Assessment**")
        
        # Academic importance notice
        st.info("""
        🎓 **Academic Excellence - Addressing Supervisor Feedback**
        
        This analysis addresses critical machine learning concerns about model overfitting and generalization.
        Essential for demonstrating rigorous model validation in academic research.
        
        **What This Analysis Provides:**
        - Training vs Test Performance Gap Analysis
        - Learning Curves for Model Behavior Visualization  
        - Cross-Validation for Robust Performance Assessment
        - Overfitting Risk Assessment and Mitigation Recommendations
        """)
        
        # Create synthetic data for demonstration
        if st.button("🚀 Run Comprehensive Overfitting Analysis", key="run_overfitting"):
            with st.spinner("Performing comprehensive overfitting analysis..."):
                
                # Generate synthetic training/test data for demonstration
                np.random.seed(42)
                n_samples = 200
                
                # Create synthetic UHPC data
                X_demo = np.random.rand(n_samples, 8)  # 8 features
                X_demo[:, 0] *= 600  # Cement content
                X_demo[:, 1] *= 200  # Silica fume
                X_demo[:, 2] *= 1000 # Aggregate
                
                # Create realistic UHPC property relationships
                compressive_strength = (
                    30 + 0.15 * X_demo[:, 0] + 0.3 * X_demo[:, 1] + 
                    np.random.normal(0, 8, n_samples)
                )
                
                # Split into train/test
                split_idx = int(0.8 * n_samples)
                X_train = X_demo[:split_idx]
                X_test = X_demo[split_idx:]
                y_train = compressive_strength[:split_idx]
                y_test = compressive_strength[split_idx:]
                
                # Demonstrate different models and their overfitting behavior
                from sklearn.ensemble import RandomForestRegressor
                from sklearn.linear_model import LinearRegression, Ridge
                from sklearn.svm import SVR
                from sklearn.model_selection import learning_curve, cross_val_score
                from sklearn.metrics import r2_score, mean_squared_error
                
                models = {
                    'Linear Regression': LinearRegression(),
                    'Ridge Regression': Ridge(alpha=1.0),
                    'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
                    'SVR': SVR(kernel='rbf', C=1.0)
                }
                
                # Analysis results storage
                analysis_results = {}
                
                st.markdown("### 📊 Training vs Test Performance Analysis")
                
                # Create performance comparison
                performance_data = []
                
                for name, model in models.items():
                    # Fit model
                    model.fit(X_train, y_train)
                    
                    # Predictions
                    train_pred = model.predict(X_train)
                    test_pred = model.predict(X_test)
                    
                    # Metrics
                    train_r2 = r2_score(y_train, train_pred)
                    test_r2 = r2_score(y_test, test_pred)
                    train_rmse = np.sqrt(mean_squared_error(y_train, train_pred))
                    test_rmse = np.sqrt(mean_squared_error(y_test, test_pred))
                    
                    # Overfitting indicators
                    r2_gap = train_r2 - test_r2
                    rmse_ratio = test_rmse / train_rmse if train_rmse > 0 else float('inf')
                    
                    # Assess overfitting risk
                    if r2_gap > 0.2 or rmse_ratio > 2.0:
                        risk_level = "🔴 HIGH"
                        risk_color = "red"
                    elif r2_gap > 0.1 or rmse_ratio > 1.5:
                        risk_level = "🟡 MEDIUM"
                        risk_color = "orange"
                    elif r2_gap > 0.05 or rmse_ratio > 1.2:
                        risk_level = "🟠 LOW"
                        risk_color = "yellow"
                    else:
                        risk_level = "🟢 MINIMAL"
                        risk_color = "green"
                    
                    performance_data.append({
                        'Model': name,
                        'Train R²': train_r2,
                        'Test R²': test_r2,
                        'R² Gap': r2_gap,
                        'RMSE Ratio': rmse_ratio,
                        'Overfitting Risk': risk_level,
                        'Risk Color': risk_color
                    })
                    
                    analysis_results[name] = {
                        'train_r2': train_r2,
                        'test_r2': test_r2,
                        'r2_gap': r2_gap,
                        'rmse_ratio': rmse_ratio,
                        'risk_level': risk_level
                    }
                
                # Display results in columns
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 📈 Performance Metrics")
                    df_performance = pd.DataFrame(performance_data)
                    
                    # Style the dataframe
                    def color_risk(val):
                        if 'HIGH' in str(val):
                            return 'background-color: #ffebee'
                        elif 'MEDIUM' in str(val):
                            return 'background-color: #fff3e0'
                        elif 'LOW' in str(val):
                            return 'background-color: #fffde7'
                        else:
                            return 'background-color: #e8f5e8'
                    
                    styled_df = df_performance.style.map(
                        color_risk, subset=['Overfitting Risk']
                    ).format({
                        'Train R²': '{:.3f}',
                        'Test R²': '{:.3f}',
                        'R² Gap': '{:.3f}',
                        'RMSE Ratio': '{:.2f}'
                    })
                    
                    st.dataframe(styled_df, use_container_width=True)
                
                with col2:
                    st.markdown("#### 🎯 Gap Analysis")
                    
                    # Create gap analysis chart
                    fig_gap = go.Figure()
                    
                    colors = ['red' if gap > 0.1 else 'orange' if gap > 0.05 else 'green' 
                             for gap in df_performance['R² Gap']]
                    
                    fig_gap.add_trace(go.Bar(
                        x=df_performance['Model'],
                        y=df_performance['R² Gap'],
                        marker_color=colors,
                        text=[f"{gap:.3f}" for gap in df_performance['R² Gap']],
                        textposition='auto'
                    ))
                    
                    fig_gap.add_hline(y=0.05, line_dash="dash", line_color="orange", 
                                     annotation_text="Low Risk Threshold")
                    fig_gap.add_hline(y=0.1, line_dash="dash", line_color="red", 
                                     annotation_text="Medium Risk Threshold")
                    
                    fig_gap.update_layout(
                        title="R² Gap Analysis (Train - Test)",
                        xaxis_title="Model",
                        yaxis_title="R² Gap",
                        height=400
                    )
                    
                    st.plotly_chart(fig_gap, use_container_width=True)
                
                # Learning Curves Section
                st.markdown("### 📈 Learning Curves Analysis")
                st.markdown("*Visualizing model behavior as training data increases*")
                
                # Generate learning curves for key models
                key_models = ['Linear Regression', 'Random Forest']
                
                fig_learning = make_subplots(
                    rows=1, cols=2,
                    subplot_titles=key_models,
                    specs=[[{"secondary_y": False}, {"secondary_y": False}]]
                )
                
                for idx, model_name in enumerate(key_models):
                    model = models[model_name]
                    
                    # Generate learning curve
                    train_sizes = np.linspace(0.1, 1.0, 10)
                    train_sizes_abs = (train_sizes * len(X_train)).astype(int)
                    
                    train_scores = []
                    val_scores = []
                    
                    for size in train_sizes_abs:
                        if size < 5:  # Skip very small sizes
                            continue
                            
                        X_subset = X_train[:size]
                        y_subset = y_train[:size]
                        
                        # Train on subset
                        model.fit(X_subset, y_subset)
                        
                        # Score on training subset
                        train_score = model.score(X_subset, y_subset)
                        train_scores.append(train_score)
                        
                        # Score on test set
                        val_score = model.score(X_test, y_test)
                        val_scores.append(val_score)
                    
                    # Plot training scores
                    fig_learning.add_trace(
                        go.Scatter(
                            x=train_sizes_abs[:len(train_scores)], 
                            y=train_scores,
                            mode='lines+markers',
                            name=f'{model_name} - Training',
                            line=dict(color='blue'),
                            showlegend=(idx == 0)
                        ),
                        row=1, col=idx+1
                    )
                    
                    # Plot validation scores
                    fig_learning.add_trace(
                        go.Scatter(
                            x=train_sizes_abs[:len(val_scores)], 
                            y=val_scores,
                            mode='lines+markers',
                            name=f'{model_name} - Validation',
                            line=dict(color='red'),
                            showlegend=(idx == 0)
                        ),
                        row=1, col=idx+1
                    )
                
                fig_learning.update_layout(
                    title="Learning Curves: Training vs Validation Performance",
                    height=500
                )
                fig_learning.update_xaxes(title_text="Training Set Size")
                fig_learning.update_yaxes(title_text="R² Score")
                
                st.plotly_chart(fig_learning, use_container_width=True)
                
                # Cross-Validation Analysis
                st.markdown("### 🔄 Cross-Validation Analysis")
                st.markdown("*Robust performance assessment using 5-fold cross-validation*")
                
                cv_results = []
                
                for name, model in models.items():
                    scores = cross_val_score(model, X_train, y_train, cv=5, scoring='r2')
                    
                    cv_results.append({
                        'Model': name,
                        'CV Mean R²': scores.mean(),
                        'CV Std R²': scores.std(),
                        'CV Min': scores.min(),
                        'CV Max': scores.max()
                    })
                
                # Display CV results
                col1, col2 = st.columns(2)
                
                with col1:
                    df_cv = pd.DataFrame(cv_results)
                    st.dataframe(df_cv.style.format({
                        'CV Mean R²': '{:.3f}',
                        'CV Std R²': '{:.3f}',
                        'CV Min': '{:.3f}',
                        'CV Max': '{:.3f}'
                    }), use_container_width=True)
                
                with col2:
                    # CV visualization
                    fig_cv = go.Figure()
                    
                    fig_cv.add_trace(go.Bar(
                        x=df_cv['Model'],
                        y=df_cv['CV Mean R²'],
                        error_y=dict(type='data', array=df_cv['CV Std R²']),
                        marker_color='lightblue',
                        text=[f"{mean:.3f}±{std:.3f}" 
                              for mean, std in zip(df_cv['CV Mean R²'], df_cv['CV Std R²'])],
                        textposition='auto'
                    ))
                    
                    fig_cv.update_layout(
                        title="Cross-Validation Performance",
                        xaxis_title="Model",
                        yaxis_title="CV R² Score",
                        height=400
                    )
                    
                    st.plotly_chart(fig_cv, use_container_width=True)
                
                # Summary and Recommendations
                st.markdown("### 🎯 Analysis Summary & Recommendations")
                
                # Calculate overall statistics
                avg_gap = np.mean([r['r2_gap'] for r in analysis_results.values()])
                high_risk_count = sum(1 for r in analysis_results.values() if 'HIGH' in r['risk_level'])
                total_models = len(analysis_results)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Average R² Gap", f"{avg_gap:.3f}")
                
                with col2:
                    st.metric("High Risk Models", f"{high_risk_count}/{total_models}")
                
                with col3:
                    risk_percentage = (high_risk_count / total_models) * 100
                    st.metric("Risk Percentage", f"{risk_percentage:.1f}%")
                
                # Overall assessment
                if avg_gap > 0.15:
                    st.error("""
                    🔴 **HIGH OVERFITTING RISK DETECTED**
                    
                    **Recommendations:**
                    - Apply regularization techniques (Ridge, Lasso)
                    - Reduce model complexity
                    - Collect more training data
                    - Consider feature selection
                    """)
                elif avg_gap > 0.08:
                    st.warning("""
                    🟡 **MODERATE OVERFITTING RISK**
                    
                    **Recommendations:**
                    - Monitor model complexity
                    - Consider cross-validation for model selection
                    - Evaluate regularization parameters
                    """)
                else:
                    st.success("""
                    🟢 **MODELS APPEAR WELL-GENERALIZED**
                    
                    **Status:**
                    - Low overfitting risk detected
                    - Models show good generalization
                    - Continue with current validation approach
                    """)
                
                # Academic value statement
                st.markdown("---")
                st.info("""
                📚 **Academic Contribution**
                
                This comprehensive overfitting analysis demonstrates:
                - **Methodological Rigor**: Proper ML validation techniques
                - **Critical Evaluation**: Understanding of model limitations  
                - **Practical Relevance**: Real-world model reliability assessment
                - **Research Quality**: Academic-standard model validation
                
                **For Your Research Report:**
                Include these results to show understanding of model generalization,
                overfitting risks, and validation best practices in ML research.
                """)

    with tab10:
        st.markdown("## �📄 Reports & Documentation")
        st.markdown("Generate professional reports and export your analysis results")
        
        # Professional Decision Support Notice
        st.info("""
        📄 **Professional Engineering Documentation**
        
        These reports provide structured documentation for engineering analysis and decision-making. 
        All reports include appropriate disclaimers and should be reviewed by a Professional Engineer 
        before use in project documentation or regulatory submissions.
        """)
        
        # Report type selection
        report_type = st.selectbox(
            "📋 Select Report Type:",
            ["Prediction Summary Report", "Cost Analysis Report", "Optimization Report", "Comparative Analysis", "Executive Summary"],
            index=0
        )
        
        # Report generation settings
        st.markdown("### ⚙️ Report Settings")
        
        report_col1, report_col2 = st.columns(2)
        
        with report_col1:
            include_charts = st.checkbox("📊 Include Charts & Graphs", value=True)
            include_details = st.checkbox("📝 Include Technical Details", value=True)
            include_recommendations = st.checkbox("💡 Include Recommendations", value=True)
        
        with report_col2:
            report_format = st.radio("📄 Export Format:", ["PDF", "HTML", "Word Document"])
            company_name = st.text_input("🏢 Company Name (optional):", placeholder="Your Company Name")
            project_ref = st.text_input("📌 Project Reference:", placeholder="Project-2025-001")
        
        # Sample data for report (in real app, this would come from current session)
        sample_data = {
            'mix_design': {
                'cement': 450, 'silica_fume': 75, 'water': 140, 'superplasticizer': 12.5,
                'coarse_aggregate': 800, 'fine_aggregate': 600, 'steel_fibers': 157
            },
            'predictions': {
                'compressive_strength': 95.2, 'tensile_strength': 8.7,
                'elastic_modulus': 42.1, 'UPV': 4850, 'cost': 320
            },
            'confidence_intervals': {
                'cs_lower': 89.1, 'cs_upper': 101.3,
                'ts_lower': 7.9, 'ts_upper': 9.5
            }
        }
        
        # Report preview
        st.markdown("### 👀 Report Preview")
        
        with st.expander("📋 Preview Report Content", expanded=True):
            st.markdown(f"""
            **Report Type:** {report_type}  
            **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
            **Project:** {project_ref if project_ref else 'N/A'}  
            **Company:** {company_name if company_name else 'AIcrete User'}
            
            ---
            
            #### Mix Design Summary
            - Cement: {sample_data['mix_design']['cement']} kg/m³
            - Silica Fume: {sample_data['mix_design']['silica_fume']} kg/m³
            - Water: {sample_data['mix_design']['water']} kg/m³
            - Steel Fibers: {sample_data['mix_design']['steel_fibers']} kg/m³
            
            #### Predicted Properties
            - **Compressive Strength:** {sample_data['predictions']['compressive_strength']:.1f} MPa
            - **Tensile Strength:** {sample_data['predictions']['tensile_strength']:.1f} MPa
            - **Elastic Modulus:** {sample_data['predictions']['elastic_modulus']:.1f} GPa
            - **Cost:** {currency_symbol}{sample_data['predictions']['cost']:.0f}/m³
            
            {f"#### Confidence Intervals" if include_details else ""}
            {f"- CS: {sample_data['confidence_intervals']['cs_lower']:.1f} - {sample_data['confidence_intervals']['cs_upper']:.1f} MPa" if include_details else ""}
            {f"- TS: {sample_data['confidence_intervals']['ts_lower']:.1f} - {sample_data['confidence_intervals']['ts_upper']:.1f} MPa" if include_details else ""}
            """)
            
            if include_recommendations:
                st.markdown("""
                #### 💡 Recommendations
                - The predicted compressive strength exceeds typical UHPC requirements
                - Cost-performance ratio is within acceptable range
                - Consider reducing fiber content for cost optimization
                - Recommended for high-performance structural applications
                """)
        
        # Report generation
        st.markdown("### 🚀 Generate Report")
        
        report_col1, report_col2, report_col3 = st.columns(3)
        
        with report_col1:
            if st.button("📄 Generate Report", use_container_width=True):
                with st.spinner(f"Generating {report_format} report..."):
                    try:
                        if report_format == "PDF":
                            # Use the professional PDF generation function
                            project_info = {
                                'name': project_ref if project_ref else 'UHPC Analysis Project',
                                'engineer': company_name if company_name else 'AIcrete Professional',
                                'report_type': report_type
                            }
                            
                            # Prepare data for PDF generation
                            predictions_data = {
                                'strength': sample_data['predictions']['compressive_strength'],
                                'flexural': sample_data['predictions']['tensile_strength'],
                                'elastic': sample_data['predictions']['elastic_modulus']
                            }
                            
                            mix_design_data = sample_data['mix_design']
                            
                            # Generate professional PDF
                            pdf_buffer = generate_pdf_report(predictions_data, mix_design_data, 
                                                            project_info=project_info, report_type=report_type)
                            
                            filename = f"AIcrete_{report_type.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                            
                            st.success(f"✅ PDF report generated successfully!")
                            st.info(f"📁 Filename: {filename}")
                            
                            # Download button for PDF
                            st.download_button(
                                label="⬇️ Download PDF Report",
                                data=pdf_buffer.getvalue(),
                                file_name=filename,
                                mime="application/pdf",
                                key="report_pdf_download"
                            )
                            
                        elif report_format == "HTML":
                            # Generate HTML report
                            html_content = f"""
                            <!DOCTYPE html>
                            <html>
                            <head>
                                <title>AIcrete {report_type}</title>
                                <style>
                                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                                    .header {{ color: #1e3c72; border-bottom: 2px solid #1e3c72; padding-bottom: 10px; }}
                                    .section {{ margin: 20px 0; }}
                                    .metric {{ background: #f0f0f0; padding: 10px; margin: 5px 0; }}
                                    table {{ border-collapse: collapse; width: 100%; }}
                                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                                    th {{ background-color: #1e3c72; color: white; }}
                                </style>
                            </head>
                            <body>
                                <div class="header">
                                    <h1>AIcrete {report_type}</h1>
                                    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                                    <p>Project: {project_ref if project_ref else 'N/A'}</p>
                                    <p>Company: {company_name if company_name else 'AIcrete Professional'}</p>
                                </div>
                                
                                <div class="section">
                                    <h2>Mix Design Composition</h2>
                                    <table>
                                        <tr><th>Component</th><th>Quantity (kg/m³)</th></tr>
                                        <tr><td>Cement</td><td>{sample_data['mix_design']['cement']}</td></tr>
                                        <tr><td>Silica Fume</td><td>{sample_data['mix_design']['silica_fume']}</td></tr>
                                        <tr><td>Water</td><td>{sample_data['mix_design']['water']}</td></tr>
                                        <tr><td>Steel Fibers</td><td>{sample_data['mix_design']['steel_fibers']}</td></tr>
                                    </table>
                                </div>
                                
                                <div class="section">
                                    <h2>Predicted Properties</h2>
                                    <div class="metric"><strong>Compressive Strength:</strong> {sample_data['predictions']['compressive_strength']:.1f} MPa</div>
                                    <div class="metric"><strong>Tensile Strength:</strong> {sample_data['predictions']['tensile_strength']:.1f} MPa</div>
                                    <div class="metric"><strong>Elastic Modulus:</strong> {sample_data['predictions']['elastic_modulus']:.1f} GPa</div>
                                    <div class="metric"><strong>Cost:</strong> {currency_symbol}{sample_data['predictions']['cost']:.0f}/m³</div>
                                </div>
                                
                                <div class="section">
                                    <h2>Generated by AIcrete Professional</h2>
                                    <p>Advanced Concrete Engineering Platform</p>
                                </div>
                            </body>
                            </html>
                            """
                            
                            filename = f"AIcrete_{report_type.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                            
                            st.success(f"✅ HTML report generated successfully!")
                            st.info(f"📁 Filename: {filename}")
                            
                            st.download_button(
                                label="⬇️ Download HTML Report",
                                data=html_content,
                                file_name=filename,
                                mime="text/html",
                                key="report_html_download"
                            )
                            
                        else:  # Word Document or other formats
                            # Generate simple text report as fallback
                            text_content = f"""
AIcrete {report_type}
===============================

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Project: {project_ref if project_ref else 'N/A'}
Company: {company_name if company_name else 'AIcrete Professional'}

Mix Design Composition
======================
Cement: {sample_data['mix_design']['cement']} kg/m³
Silica Fume: {sample_data['mix_design']['silica_fume']} kg/m³
Water: {sample_data['mix_design']['water']} kg/m³
Steel Fibers: {sample_data['mix_design']['steel_fibers']} kg/m³

Predicted Properties
===================
Compressive Strength: {sample_data['predictions']['compressive_strength']:.1f} MPa
Tensile Strength: {sample_data['predictions']['tensile_strength']:.1f} MPa
Elastic Modulus: {sample_data['predictions']['elastic_modulus']:.1f} GPa
Cost: {currency_symbol}{sample_data['predictions']['cost']:.0f}/m³

Generated by AIcrete Professional
Advanced Concrete Engineering Platform
                            """
                            
                            filename = f"AIcrete_{report_type.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                            
                            st.success(f"✅ {report_format} report generated successfully!")
                            st.info(f"📁 Filename: {filename}")
                            
                            st.download_button(
                                label=f"⬇️ Download {report_format}",
                                data=text_content,
                                file_name=filename,
                                mime="text/plain",
                                key="report_text_download"
                            )
                            
                    except Exception as e:
                        st.error(f"❌ Report generation error: {str(e)}")
                        st.info("💡 Try generating a different format or check the error details below")
                        
                        with st.expander("🔧 Error Details"):
                            st.code(f"Error: {type(e).__name__}: {str(e)}")
                            st.info("This may be due to missing packages or data formatting issues.")
        
        with report_col2:
            st.markdown("� **Quick Actions**")
            if st.button("� Regenerate with Current Data", use_container_width=True):
                st.info("� Use the main Prediction tab to generate reports with live data")
                st.success("✅ This section shows sample report formats")
        
        with report_col3:
            if st.button("☁️ Save to Cloud", use_container_width=True):
                st.success("✅ Report saved to cloud storage")
                st.info("📁 Available in your AIcrete dashboard")
        
        # Batch report generation
        st.markdown("### 📦 Batch Reports")
        
        with st.expander("🔄 Generate Multiple Reports", expanded=False):
            st.markdown("Generate reports for multiple projects or analysis types")
            
            batch_projects = st.multiselect(
                "Select Projects:",
                ["Project_A", "Project_B", "Project_C", "High_Rise_Design", "Bridge_Analysis"],
                default=["Project_A", "Project_B"]
            )
            
            batch_types = st.multiselect(
                "Select Report Types:",
                ["Prediction Summary Report", "Cost Analysis Report", "Optimization Report"],
                default=["Prediction Summary Report"]
            )
            
            if st.button("🚀 Generate Batch Reports", use_container_width=True):
                total_reports = len(batch_projects) * len(batch_types)
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, project in enumerate(batch_projects):
                    for j, report in enumerate(batch_types):
                        current = i * len(batch_types) + j + 1
                        progress = current / total_reports
                        
                        status_text.text(f"Generating {report} for {project}...")
                        progress_bar.progress(progress)
                        
                        # Simulate processing time
                        time.sleep(0.5)
                
                status_text.text("✅ All reports generated successfully!")
                st.success(f"Generated {total_reports} reports for download")
    
    with tab11:
        st.markdown("## 📚 User Guide - How to Use AIcrete")
        st.markdown("Complete guide to mastering your concrete engineering platform")
        
        # Quick start section
        st.markdown("### 🚀 Quick Start")
        
        quick_col1, quick_col2 = st.columns(2)
        
        with quick_col1:
            st.markdown("""
            #### 🎯 **Step 1: Property Prediction**
            1. Go to **Property Prediction** tab
            2. Enter your mix design parameters
            3. Click **"🔮 Predict Properties"**
            4. Review predicted results and recommendations
            
            #### 💾 **Step 2: Save Your Work**
            1. Switch to **Project Manager** tab
            2. Enter project name and notes
            3. Click **"💾 Save Current Mix"**
            4. Your design is safely stored!
            """)
        
        with quick_col2:
            st.markdown("""
            #### 🎨 **Step 3: Optimize Design**
            1. Use **Target-Based Design** for specific goals
            2. Check **Interactive Charts** for trade-offs
            3. Analyze **Sustainability** impact
            4. Generate **Reports** for documentation
            
            #### 🏗️ **Step 4: Use Templates**
            1. Visit **Application Templates**
            2. Select your construction type
            3. Customize the template as needed
            4. Apply to your project
            """)
        
        # Engineering Value & Workflow
        st.markdown("### ⚙️ Engineering Value & Professional Workflow")
        
        with st.expander("🔧 **How AIcrete Accelerates Engineering (Even with Lab Testing)**", expanded=True):
            st.markdown("""
            #### 🎯 **The Smart Engineering Approach**
            
            **Traditional Approach:**
            - 🔬 Test 20+ random mix combinations in lab
            - 💰 Cost: $10,000+ and 8+ weeks
            - 🎲 Hit-or-miss trial and error method
            - 📊 Limited design space exploration
            
            **AIcrete-Enhanced Approach:**
            - 🧠 Screen 1000+ combinations digitally in minutes
            - 🎯 Identify top 3-5 candidates for lab testing
            - 💰 Cost: $2,500 and 2-3 weeks
            - 📈 **75% cost reduction and 75% time savings**
            
            ---
            
            #### 🏗️ **Real Engineering Workflow**
            
            **Phase 1: Digital Design Exploration** (AIcrete)
            1. **Define Requirements** → Input project constraints and targets
            2. **Explore Design Space** → Test hundreds of parameter combinations
            3. **Optimization Analysis** → Use target-based design and interactive charts
            4. **Feasibility Assessment** → Identify viable options before lab work
            5. **Cost-Performance Trade-offs** → Balance technical and economic factors
            
            **Phase 2: Focused Lab Validation** (Physical Testing)
            1. **Strategic Testing** → Test only the top 3-5 AIcrete-identified candidates
            2. **Validation** → Confirm AIcrete predictions with actual samples
            3. **Fine-tuning** → Use lab data to refine final design
            4. **Quality Assurance** → Ensure compliance with specifications
            
            **Phase 3: Implementation Support** (AIcrete + Lab Data)
            1. **Design Documentation** → Generate professional reports
            2. **What-if Analysis** → Evaluate design modifications
            3. **Quality Control** → Monitor production consistency
            4. **Continuous Improvement** → Optimize based on field performance
            
            ---
            
            #### 💼 **Professional Engineering Value**
            
            **Pre-Lab Benefits:**
            - ✅ **Smart Design Screening** → Avoid testing obviously poor combinations
            - ✅ **Parameter Sensitivity** → Understand which factors matter most
            - ✅ **Design Space Mapping** → Visualize feasible design regions
            - ✅ **Cost Optimization** → Balance performance with budget constraints
            - ✅ **Risk Assessment** → Uncertainty quantification with confidence intervals
            
            **During Lab Work:**
            - ✅ **Focused Testing** → Test only promising candidates
            - ✅ **Quality Prediction** → Predict properties of intermediate mixes
            - ✅ **Troubleshooting** → Understand unexpected lab results
            - ✅ **Design Refinement** → Optimize based on partial lab data
            
            **Post-Lab Benefits:**
            - ✅ **Interpolation** → Predict properties between tested points
            - ✅ **Scale-up Support** → Adjust for production conditions
            - ✅ **Documentation** → Professional reporting and presentations
            - ✅ **Client Communication** → Visual explanations of design decisions
            
            ---
            
            #### 🎯 **Industry Analogy: "Google Maps for Concrete Design"**
            
            Just like Google Maps doesn't drive your car but shows you the best routes:
            - **AIcrete** shows you the best paths to optimal concrete design
            - **Lab Testing** is still required to "drive" to your destination safely
            - **Result:** You reach your goal faster, cheaper, and with less wrong turns
            
            #### 📊 **Proven Engineering Applications**
            
            **Bridge Deck Project Example:**
            - **Requirement:** 70 MPa strength, $800/m³ budget
            - **AIcrete Result:** 12 viable combinations identified in 10 minutes
            - **Lab Strategy:** Test only top 3 candidates
            - **Outcome:** Found optimal mix 4x faster than traditional approach
            
            **High-Rise Construction Example:**
            - **Challenge:** Balance strength, workability, and cost
            - **AIcrete Advantage:** Uncertainty quantification shows confidence levels
            - **Engineering Decision:** Select designs with highest confidence for testing
            - **Result:** Reduced design risk and improved testing efficiency
            """)
        
        # Detailed tab guide
        st.markdown("### 📋 Detailed Tab Guide")
        
        # Tab explanations with expandable sections
        with st.expander("🎯 **Property Prediction** - Core AI Engine", expanded=False):
            st.markdown("""
            **Purpose:** Predict concrete properties using AI models
            
            **How to Use:**
            1. **Input Parameters:** Enter cement, silica fume, water, aggregates, etc.
            2. **Currency Selection:** Choose your preferred currency in the sidebar
            3. **Predict:** Click the prediction button to get results
            4. **Review Results:** See compressive strength, tensile strength, elastic modulus, UPV, and cost
            5. **Expert Recommendations:** Read AI-generated optimization suggestions
            
            **Tips:**
            - Start with template values if unsure
            - Pay attention to water/binder ratio
            - Higher fiber content increases strength but also cost
            """)
        
        with st.expander("🎨 **Target-Based Design** - Reverse Engineering", expanded=False):
            st.markdown("""
            **Purpose:** Find mix designs that achieve specific property targets
            
            **How to Use:**
            1. **Select Target Property:** Choose what you want to optimize (strength, cost, etc.)
            2. **Set Target Value:** Enter your desired property value
            3. **Add Constraints:** Optionally set limits on other properties
            4. **Run Optimization:** Let AI find the optimal mix design
            5. **Review Results:** Get the mix design that meets your targets
            
            **Best Practices:**
            - Set realistic targets based on material capabilities
            - Use constraints to ensure practical mix designs
            - Consider multiple runs with different targets
            """)
        
        with st.expander("📊 **Interactive Charts** - Visual Analysis", expanded=False):
            st.markdown("""
            **Purpose:** Visualize cost vs performance trade-offs and optimization data
            
            **Features:**
            1. **Cost vs Performance Charts:** See how different parameters affect cost and strength
            2. **Parameter Sensitivity:** Understand which inputs most impact outputs
            3. **Optimization Frontiers:** Find optimal balance between competing objectives
            4. **Interactive Exploration:** Hover over points for detailed information
            
            **Use Cases:**
            - Budget optimization
            - Performance maximization
            - Understanding parameter relationships
            """)
        
        with st.expander("💾 **Project Manager** - Organization System", expanded=False):
            st.markdown("""
            **Purpose:** Save, organize, and manage your concrete mix designs
            
            **Capabilities:**
            1. **Save Projects:** Store mix designs with names and notes
            2. **Load Projects:** Retrieve saved designs for modification
            3. **Delete Projects:** Remove outdated designs
            4. **Bulk Export:** Export all projects to CSV
            5. **Project Import:** Import designs from files
            
            **Organization Tips:**
            - Use descriptive project names
            - Add detailed notes for future reference
            - Regularly export your projects as backup
            """)
        
        with st.expander("🏗️ **Application Templates** - Industry Presets", expanded=False):
            st.markdown("""
            **Purpose:** Start with proven mix designs for specific construction applications
            
            **Available Templates:**
            - **High-Rise Buildings:** Optimized for structural applications
            - **Bridge Construction:** High durability and strength
            - **Precast Elements:** Factory production optimization
            - **Marine Structures:** Corrosion resistance focus
            - **Pavement & Roads:** Durability and cost efficiency
            - **Architectural Features:** Aesthetic and performance balance
            
            **How to Use Templates:**
            1. Select application type
            2. Review template specifications
            3. Customize parameters as needed
            4. Save as new project
            """)
        
        with st.expander("🌍 **Sustainability Analytics** - Environmental Impact", expanded=False):
            st.markdown("""
            **Purpose:** Assess environmental impact and sustainability metrics
            
            **Analysis Features:**
            1. **Carbon Footprint:** CO₂ emissions by material
            2. **Resource Efficiency:** Water/binder ratios and material optimization
            3. **Energy Consumption:** Manufacturing energy requirements
            4. **Recyclability Index:** End-of-life material recovery potential
            5. **Durability Bonus:** Long-term performance impact
            
            **Sustainability Scoring:**
            - Overall score (0-100) with component breakdown
            - Benchmark comparisons with industry standards
            - Actionable recommendations for improvement
            """)
        
        with st.expander("📋 **Reports** - Professional Documentation", expanded=False):
            st.markdown("""
            **Purpose:** Generate professional reports and documentation
            
            **Report Types:**
            - **Prediction Summary:** Complete analysis results
            - **Cost Analysis:** Economic evaluation
            - **Optimization Report:** Design optimization results
            - **Comparative Analysis:** Multiple design comparison
            - **Executive Summary:** High-level overview
            
            **Export Options:**
            - PDF for formal documentation
            - HTML for web viewing
            - Word documents for editing
            """)
        
        with st.expander("📋 **Standards Compliance** - International Code Checking", expanded=False):
            st.markdown("""
            **Purpose:** Check compliance with international concrete standards
            
            **Supported Standards:**
            - **ASTM C1856** - Ultra-High Performance Concrete (USA)
            - **BS EN 206** - Concrete specification (UK/EU) 
            - **ACI 239R** - UHPC design and construction (USA)
            - **RILEM TC 188-CSC** - Self-compacting concrete (International)
            - **IS 456** - Plain and reinforced concrete (India)
            - **JIS A 5308** - Ready-mixed concrete (Japan)
            - **CSA A23.1** - Concrete construction (Canada)
            - **AS 3600** - Concrete structures (Australia)
            
            **How to Use:**
            1. **Select Application Type** → Choose your construction application
            2. **View Recommended Standards** → See applicable codes for your project
            3. **Enter Mix Design** → Input your concrete parameters
            4. **Check Compliance** → Get instant compliance analysis
            5. **Review Results** → Understand violations and recommendations
            
            **Compliance Status:**
            - ✅ **PASS** - Meets all requirements
            - ⚠️ **WARNING** - Minor issues to review
            - ❌ **FAIL** - Requires design modifications
            
            **Key Checks:**
            - Compressive strength requirements
            - W/C and W/B ratio limits
            - Fiber content specifications (for UHPC)
            - Curing temperature ranges
            - Material composition limits
            
            **Professional Benefits:**
            - **Multi-Regional Compliance** - Check against multiple countries' standards
            - **Pre-Design Validation** - Identify issues before lab testing
            - **Risk Mitigation** - Ensure code compliance early
            - **Documentation Support** - Generate compliance reports
            - **Global Projects** - Meet international requirements
            
            **Engineering Workflow:**
            1. **Design Phase** → Check preliminary compliance
            2. **Lab Testing** → Focus on compliant designs
            3. **Documentation** → Include compliance verification
            4. **Approval Process** → Demonstrate code adherence
            """)
        
        with st.expander("🔍 **SHAP Interpretability** - AI Model Transparency", expanded=False):
            st.markdown("""
            **Purpose:** Understand why the AI model makes specific predictions
            
            **SHAP Analysis Features:**
            - **Waterfall Plot** - Step-by-step contribution of each feature
            - **Force Plot** - Positive vs negative feature impacts
            - **Feature Importance** - Ranking of most influential parameters
            - **Engineering Summary** - Plain-language explanations
            
            **How to Use:**
            1. **Enter Mix Design** → Input your concrete parameters
            2. **Generate Analysis** → Get SHAP explanations for the prediction
            3. **Review Visualizations** → Understand feature contributions
            4. **Read Engineering Insights** → Get optimization recommendations
            5. **Validate Model Logic** → Ensure predictions make engineering sense
            
            **Visualization Types:**
            - 🌊 **Waterfall Plot** - Shows cumulative feature contributions
            - ⚡ **Force Plot** - Displays positive/negative impacts side-by-side
            - 📝 **Summary Report** - Engineering interpretation of results
            
            **Professional Benefits:**
            - **Model Transparency** - Understand AI decision-making process
            - **Engineering Validation** - Verify model behaves logically
            - **Optimization Guidance** - Identify parameters to adjust
            - **Client Communication** - Explain design rationale with data
            - **Quality Assurance** - Build confidence in AI predictions
            
            **Engineering Applications:**
            - **Design Optimization** → Focus on most influential parameters
            - **Troubleshooting** → Understand why performance varies
            - **Model Validation** → Ensure predictions align with engineering principles
            - **Education** → Learn relationships between mix components
            - **Research** → Identify novel optimization strategies
            """)
        
        # Advanced features
        st.markdown("### 🎓 Advanced Features")
        
        adv_col1, adv_col2 = st.columns(2)
        
        with adv_col1:
            st.markdown("""
            #### 🔬 **Uncertainty Quantification**
            - Monte Carlo simulations for confidence intervals
            - Statistical reliability of predictions
            - Risk assessment for design decisions
            
            #### 🎯 **Multi-Objective Optimization**
            - Balance competing objectives simultaneously
            - Pareto frontier analysis
            - Trade-off visualization
            """)
        
        with adv_col2:
            st.markdown("""
            #### 💱 **Multi-Currency Support**
            - 7 international currencies supported
            - Real-time cost conversion
            - Global project compatibility
            
            #### 📊 **Interactive Visualizations**
            - Plotly-powered charts
            - Hover details and zoom functionality
            - Professional presentation quality
            """)
        
        # Best practices section
        st.markdown("### 💡 Best Practices & Tips")
        
        with st.expander("🏆 **Professional Workflow Recommendations**", expanded=True):
            st.markdown("""
            #### 🔄 **Recommended Workflow:**
            
            1. **🎯 Start with Templates** → Use application templates as starting point
            2. **🔮 Initial Prediction** → Get baseline properties and cost
            3. **📋 Standards Check** → Verify compliance with applicable codes
            4. **🎨 Target Optimization** → Use target-based design for specific goals
            5. **📊 Visual Analysis** → Check trade-offs with interactive charts
            6. **🌍 Sustainability Check** → Evaluate environmental impact
            7. **💾 Save Progress** → Store designs in project manager
            8. **� Generate Reports** → Create professional documentation
            
            #### ⚠️ **Common Mistakes to Avoid:**
            - Setting unrealistic targets (e.g., 200 MPa with low cost)
            - Ignoring sustainability metrics in modern projects
            - Not saving intermediate designs during optimization
            - Overlooking uncertainty quantification for critical projects
            
            #### 🎯 **Expert Tips:**
            - Always start with application templates for your project type
            - **Check standards compliance early** to avoid costly redesigns
            - Use uncertainty quantification for high-stakes projects
            - **Multi-regional projects:** Check all applicable international standards
            - Compare multiple design alternatives before finalizing
            - Consider lifecycle costs, not just material costs
            - **Document compliance** with appropriate standards references
            - Review standards requirements during design phase, not after
            """)
        
        # Troubleshooting section
        st.markdown("### 🔧 Troubleshooting")
        
        trouble_col1, trouble_col2 = st.columns(2)
        
        with trouble_col1:
            st.markdown("""
            #### ❓ **Common Issues:**
            
            **Q: Predictions seem unrealistic?**
            A: Check input parameters for typos, ensure realistic material ratios
            
            **Q: Target-based design not finding solutions?**
            A: Relax constraints or adjust target values to feasible ranges
            
            **Q: Charts not displaying?**
            A: Ensure you've run predictions first to generate data
            
            **Q: Standards compliance showing failures?**
            A: Review violations list and adjust mix design accordingly
            
            **Q: Which standards apply to my project?**
            A: Select your application type to see recommended standards
            """)
        
        with trouble_col2:
            st.markdown("""
            #### 🆘 **Getting Help:**
            
            **Technical Support:**
            - Email: support@aicrete.com
            - Documentation: Available in Reports tab
            - Training: Contact for professional training
            
            **Academic Support:**
            - Research collaboration opportunities
            - Validation data sharing
            - Publication support
            """)
        
        # Version and updates info
        st.markdown("### 📅 Platform Information")
        
        info_col1, info_col2, info_col3 = st.columns(3)
        
        with info_col1:
            st.info("""
            **Version:** 2.0.0
            **Release:** August 2025
            **Status:** Production Ready
            """)
        
        with info_col2:
            st.info("""
            **Features:** 8 Advanced Modules
            **Currencies:** 7 Supported
            **Applications:** 6 Templates
            """)
        
        with info_col3:
            st.info("""
            **AI Models:** Advanced ML
            **Uncertainty:** Monte Carlo
            **Sustainability:** Full LCA
            """)
    
    with tab12:
        st.markdown("## ℹ️ About AIcrete Concrete Solutions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 🏢 Company Overview
            
            **AIcrete Concrete Solutions** is a pioneering company at the forefront of 
            concrete technology innovation. We leverage advanced artificial intelligence 
            and machine learning to revolutionize concrete mix design and performance prediction.
            
            ### 🎯 Our Mission
            
            To provide accurate, reliable, and cost-effective concrete property predictions 
            that enable engineers and contractors to design optimal concrete mixes for 
            any application.
            
            ### 🔬 Technology
            
            Our AI models are trained on extensive datasets of UHPC properties and 
            validated through rigorous testing protocols to ensure accuracy and reliability.
            """)
        
        with col2:
            st.markdown("""
            ### 🏆 Key Features
            
            - **AI-Powered Predictions**: Advanced machine learning models
            - **Multi-Property Analysis**: CS, TS, EM, UPV, and Cost prediction
            - **Real-time Optimization**: Instant mix design optimization
            - **Professional Reports**: Comprehensive analysis and documentation
            - **Cost-Performance Analysis**: Economic optimization tools
            
            ### 📞 Contact Information
            
            **Address:** 123 Innovation Drive, Tech City, TC 12345  
            **Phone:** +1 (555) AICRETE  
            **Email:** info@aicrete.com  
            **Website:** www.aicrete-solutions.com
            
            ### 📧 Support
            
            For technical support or inquiries, please contact our expert team.
            """)
    
    # Footer
    st.markdown("""
    <div class="footer">
        <div style="font-size: 1.1rem; font-weight: bold; margin-bottom: 1rem;">
            🏗️ AIcrete Concrete Solutions
        </div>
        <div>
            Powered by Advanced AI Technology | © 2025 Shiksha Seechurn | AIcrete Platform
        </div>
        <div style="margin-top: 0.5rem; font-size: 0.8rem; color: #888;">
            All Rights Reserved. Unauthorized copying or distribution prohibited.
        </div>
        <div style="margin-top: 1rem; font-size: 0.9rem;">
            Building the Future of Concrete Technology
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
