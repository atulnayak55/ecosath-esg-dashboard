"""
Create SQLite databases with pre-generated AI insights for each dashboard
"""
import sqlite3
import json
from datetime import datetime

def create_emissions_insights_db():
    """Create emissions AI insights database"""
    conn = sqlite3.connect('emissions_ai_insights.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_key TEXT NOT NULL,
            insight_type TEXT NOT NULL,
            question TEXT,
            answer TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quick_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_key TEXT NOT NULL,
            stat_name TEXT NOT NULL,
            stat_value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert emissions insights
    emissions_insights = [
        # General insights
        ('general', 'overview', 'What are the emission trends?', 
         'Based on Aurora Renewables\' emissions data, production emissions show a slight increase over the past year at 7,050.7 kg CO2e, with an "Infinity% from previous" indicator suggesting this is new tracking. Travel emissions remain at 0.0 kg CO2e, indicating excellent remote work policies. Energy consumption stands at 41,276.3 kWh. The key opportunity is to increase renewable energy mix from the current 0.0% to reduce the carbon footprint.'),
        
        ('general', 'recommendation', 'How can we reduce CO2?',
         'To reduce CO2 emissions at Aurora Renewables:\n\n1. **Increase Renewable Energy**: Currently at 0%, prioritize solar/wind installations\n2. **Energy Efficiency**: With 41,276 kWh consumption, implement LED lighting and efficient HVAC systems\n3. **Carbon Offsets**: Leverage your tree planting initiatives to offset production emissions\n4. **Supply Chain**: Audit suppliers for low-carbon alternatives\n5. **Monitor Air Quality**: Current AQI of 49.4 is moderate - maintain through emission controls'),
        
        ('production_emissions', 'analysis', 'Analyze production emissions',
         'Production emissions at 7,050.7 kg CO2e represent your primary carbon source. This translates to approximately 7 tons of CO2 annually. Key insights:\n\n• **Intensity**: ~0.17 kg CO2e per kWh of energy consumed\n• **Trend**: Showing an increase from baseline\n• **Context**: For a renewable energy company, this is relatively low but improvable\n• **Action**: Focus on renewable energy procurement and process optimization'),
        
        ('energy_consumption', 'analysis', 'What about energy efficiency?',
         'Energy consumption at 41,276.3 kWh shows significant opportunity:\n\n• **Current Status**: 0% renewable energy - major improvement area\n• **Efficiency Ratio**: ~1.71 kWh per kg CO2e produced\n• **Benchmark**: Renewable energy companies typically target 80%+ renewable sources\n• **Recommendations**: Install on-site solar, purchase renewable energy credits, implement energy management systems'),
        
        ('waste_management', 'insight', 'How is our waste management?',
         'Waste generation at 0.0 kg indicates either:\n• Excellent waste reduction programs in place\n• New tracking system with no data yet\n• Need to implement comprehensive waste monitoring\n\nRecommendation: Establish waste tracking systems and set targets for recycling rates (aim for 80%+ diversion from landfills).'),
        
        ('air_quality', 'analysis', 'What does AQI 49.4 mean?',
         'Air Quality Index of 49.4 falls in the "Good" to "Moderate" range:\n\n• **Health Impact**: Acceptable for most people\n• **Status**: Slightly elevated from "Good" (0-50)\n• **Context**: Shows environmental consciousness in operations\n• **Monitoring**: Continue tracking to ensure industrial activities don\'t degrade air quality\n• **Goal**: Maintain below 50 for optimal environmental performance'),
        
        # Time period specific
        ('general', 'trend_1year', 'How were emissions over the year?',
         'Over the past year, emissions data shows:\n\n• **Production Emissions**: Increasing trend from baseline to 7,050.7 kg CO2e\n• **Travel Emissions**: Maintained at zero through remote work\n• **Energy Use**: Steady at 41,276 kWh with room for efficiency gains\n• **Overall**: Emissions intensity is manageable but requires renewable energy transition to meet sustainability targets'),
        
        ('general', 'comparison', 'How do we compare to benchmarks?',
         'Aurora Renewables performance vs. renewable energy sector benchmarks:\n\n✅ **Travel Emissions**: Excellent (0.0 vs. industry avg ~500 kg CO2e/employee)\n⚠️ **Renewable Energy**: Needs improvement (0% vs. sector target 80%+)\n✅ **Waste Management**: Strong (0.0 kg vs. industry avg ~50 kg/employee)\n⚠️ **Energy Intensity**: Moderate - 0.17 kg CO2e/kWh is improvable\n\nOverall: Good foundation, focus on renewable energy procurement.'),
    ]
    
    cursor.executemany('''
        INSERT INTO insights (metric_key, insight_type, question, answer)
        VALUES (?, ?, ?, ?)
    ''', emissions_insights)
    
    # Insert quick stats
    quick_stats = [
        ('production_emissions', 'Total CO2', '7,050.7 kg CO2e'),
        ('production_emissions', 'Change', '+Infinity% (new tracking)'),
        ('energy_consumption', 'Total Energy', '41,276.3 kWh'),
        ('energy_mix', 'Renewable %', '0.0%'),
        ('air_quality', 'Current AQI', '49.4 (Moderate)'),
        ('waste_management', 'Waste Generated', '0.0 kg'),
        ('general', 'Carbon Intensity', '0.17 kg CO2e/kWh'),
        ('general', 'Key Opportunity', 'Increase renewable energy to 80%+'),
    ]
    
    cursor.executemany('''
        INSERT INTO quick_stats (metric_key, stat_name, stat_value)
        VALUES (?, ?, ?)
    ''', quick_stats)
    
    conn.commit()
    conn.close()
    print("✅ Created emissions_ai_insights.db")

def create_social_insights_db():
    """Create social AI insights database"""
    conn = sqlite3.connect('social_ai_insights.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_key TEXT NOT NULL,
            insight_type TEXT NOT NULL,
            question TEXT,
            answer TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quick_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_key TEXT NOT NULL,
            stat_name TEXT NOT NULL,
            stat_value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert social insights
    social_insights = [
        ('general', 'overview', 'Employee wellbeing insights?',
         'Aurora Renewables shows strong commitment to employee wellbeing:\n\n• **Satisfaction Score**: Trending positively at 7.8/10 (target: 8.0+)\n• **Work-Life Balance**: Improving at 7.5/10\n• **Benefits Rating**: Strong at 8.2/10\n• **Trend**: Consistent improvement over 12 months\n• **Key**: High benefits satisfaction drives overall wellbeing'),
        
        ('employee_wellbeing', 'analysis', 'How is employee satisfaction?',
         'Employee satisfaction metrics reveal positive workplace culture:\n\n**Current State**:\n• Overall satisfaction: 7.8/10 (above industry avg of 7.2)\n• Work-life balance: 7.5/10 (good, target 8.0)\n• Benefits package: 8.2/10 (excellent)\n\n**Insights**:\n• Benefits are a key differentiator\n• Work-life balance improving but needs focus\n• High satisfaction correlates with low turnover\n\n**Recommendation**: Focus on flexible work arrangements to boost work-life balance to 8.0+'),
        
        ('diversity_inclusion', 'analysis', 'Diversity improvements?',
         'Diversity & Inclusion showing steady progress:\n\n**Gender Diversity**: ~45% representation (industry avg: 35%)\n• Leading the renewable energy sector\n• Target: Maintain 45-50% balance\n\n**Minority Representation**: ~30% (growing)\n• Above industry benchmark of 25%\n• Trend: +2% quarterly growth\n\n**Pay Equity Index**: 95% (excellent)\n• Nearly achieved pay parity\n• Goal: Reach 98%+ within next quarter\n\n**Overall**: Aurora is a D&I leader in the sector. Continue mentorship programs and equitable hiring.'),
        
        ('community_impact', 'insight', 'Community impact summary?',
         'Community engagement demonstrates strong corporate citizenship:\n\n**Investment**: $125,000 annually in community programs\n• 25% above sector average\n• Focus areas: Education, environment, local infrastructure\n\n**Volunteer Hours**: 450 hours per quarter\n• ~4 hours per employee (industry avg: 2-3 hours)\n• Highest during environmental campaigns\n\n**Beneficiaries**: 1,000+ people reached\n• Direct: 300 through programs\n• Indirect: 700+ through partnerships\n\n**Impact**: Significant positive community perception, strengthening social license to operate.'),
        
        ('health_safety', 'analysis', 'Safety record analysis?',
         'Health & Safety performance is exemplary:\n\n**Incident Rate**: 0.5 per 100 employees (excellent)\n• Industry average: 2.5 incidents\n• 80% better than sector benchmark\n• Trend: Declining over past year\n\n**Training Hours**: 24 hours per employee annually\n• Exceeds regulatory minimum (8 hours)\n• Topics: Safety protocols, emergency response, ergonomics\n\n**Compliance Score**: 98% (outstanding)\n• Only minor administrative gaps\n• Zero major violations\n\n**Culture**: Strong safety-first mindset. Continue training investments and near-miss reporting.'),
        
        ('general', 'recommendation', 'How to improve social impact?',
         'Strategic recommendations for enhanced social impact:\n\n1. **Employee Wellbeing**: Push work-life balance from 7.5 to 8.0+ through flexible schedules\n2. **Diversity**: Set 50% gender diversity target, expand minority recruitment pipeline\n3. **Community**: Increase investment to $150K, focus on sustainability education programs\n4. **Safety**: Maintain low incident rate through predictive analytics and proactive interventions\n5. **Engagement**: Launch employee resource groups (ERGs) for underrepresented groups'),
        
        ('general', 'trends', 'What are the social metric trends?',
         'Social metrics show positive momentum across all areas:\n\n📈 **Improving**:\n• Employee satisfaction: +0.3 points over 12 months\n• Diversity: +2% quarterly growth\n• Community investment: +15% year-over-year\n• Safety compliance: Maintained 98%+\n\n⚠️ **Watch Areas**:\n• Work-life balance: Good but below 8.0 target\n• Minority representation: Growing but can accelerate\n\n🎯 **Priorities**: Work-life balance initiatives and accelerated D&I programs will maximize social performance.'),
    ]
    
    cursor.executemany('''
        INSERT INTO insights (metric_key, insight_type, question, answer)
        VALUES (?, ?, ?, ?)
    ''', social_insights)
    
    # Quick stats
    quick_stats = [
        ('employee_wellbeing', 'Satisfaction Score', '7.8/10'),
        ('employee_wellbeing', 'Work-Life Balance', '7.5/10'),
        ('employee_wellbeing', 'Benefits Rating', '8.2/10'),
        ('diversity_inclusion', 'Gender Diversity', '~45%'),
        ('diversity_inclusion', 'Minority Representation', '~30%'),
        ('diversity_inclusion', 'Pay Equity', '95%'),
        ('community_impact', 'Annual Investment', '$125,000'),
        ('community_impact', 'Volunteer Hours', '450 hrs/quarter'),
        ('community_impact', 'People Reached', '1,000+'),
        ('health_safety', 'Incident Rate', '0.5 per 100 employees'),
        ('health_safety', 'Training Hours', '24 hrs/employee'),
        ('health_safety', 'Compliance Score', '98%'),
    ]
    
    cursor.executemany('''
        INSERT INTO quick_stats (metric_key, stat_name, stat_value)
        VALUES (?, ?, ?)
    ''', quick_stats)
    
    conn.commit()
    conn.close()
    print("✅ Created social_ai_insights.db")

def create_governance_insights_db():
    """Create governance AI insights database"""
    conn = sqlite3.connect('governance_ai_insights.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_key TEXT NOT NULL,
            insight_type TEXT NOT NULL,
            question TEXT,
            answer TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quick_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_key TEXT NOT NULL,
            stat_name TEXT NOT NULL,
            stat_value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert governance insights
    governance_insights = [
        ('general', 'overview', 'Board diversity status?',
         'Board composition demonstrates strong governance practices:\n\n• **Independence**: 65% independent directors (target: 60%+) ✅\n• **Diversity**: 35% diverse representation (industry avg: 25%)\n• **Expertise**: 85% have relevant sector experience\n• **Trend**: Improving diversity by 3% quarterly\n\n**Assessment**: Above-average board governance with excellent independence. Continue focusing on diverse candidate pipeline for board refreshes.'),
        
        ('board_composition', 'analysis', 'How effective is our board?',
         'Board effectiveness analysis:\n\n**Structure**:\n• 65% independent directors ensures objective oversight\n• 35% diversity brings varied perspectives (target: 40%)\n• 85% with renewable energy/sustainability expertise\n\n**Performance**:\n• Quarterly board evaluations: 4.2/5.0 average\n• Committee structure: Audit, Compensation, Sustainability\n• Meeting attendance: 97% (excellent)\n\n**Best Practices**:\n• Regular director education on ESG trends\n• Annual board refreshment policy\n• Clear separation of CEO and Board Chair roles\n\n**Recommendation**: Increase diversity to 40%+ in next board cycle.'),
        
        ('compliance_metrics', 'insight', 'Compliance summary?',
         'Compliance performance is exceptional:\n\n**Audit Score**: 92% (industry avg: 85%)\n• Only minor procedural gaps identified\n• Zero material weaknesses\n• Quick remediation of findings\n\n**Policy Adherence**: 88%\n• Strong but room for improvement\n• Focus areas: Documentation completeness, training completion\n\n**Certifications**: 15 active (ISO 14001, 45001, 50001, etc.)\n• Ahead of regulatory requirements\n• Demonstrates proactive risk management\n\n**Risk Assessment**: Mature compliance culture with strong internal controls. Target 90%+ policy adherence.'),
        
        ('esg_ratings', 'analysis', 'ESG rating trends?',
         'ESG ratings show sector-leading performance:\n\n**MSCI Rating**: A (top 25% of industry)\n• Strengths: Environmental management, board independence\n• Watch areas: Supply chain transparency\n\n**Sustainalytics Score**: 72/100 (Low Risk)\n• Above sector median of 65\n• Improving +3 points quarterly\n\n**CDP Score**: B (Management level)\n• Target: Reach A- (Leadership) next year\n• Gap: Scope 3 emissions disclosure\n\n**Overall**: Strong ESG momentum. Focus on supply chain and Scope 3 to reach A-level ratings across agencies.'),
        
        ('transparency_disclosure', 'insight', 'Transparency improvements?',
         'Transparency & disclosure practices are maturing:\n\n**Reporting Score**: 78/100\n• Publish annual sustainability report (GRI-aligned)\n• Quarterly ESG metrics updates\n• Gap: Real-time data dashboards (in progress)\n\n**Stakeholder Engagement**: 450 touchpoints/year\n• Investors: 200 meetings\n• Community: 150 sessions\n• Employees: 100 town halls\n\n**Data Quality**: 85% verified by third-party\n• Target: 95% third-party assured\n\n**Innovation**: This dashboard project exemplifies commitment to transparency. Continue with open data initiatives.'),
        
        ('general', 'recommendation', 'How to improve governance?',
         'Strategic governance enhancement roadmap:\n\n1. **Board Diversity**: Target 40% diverse representation in next cycle\n2. **Compliance**: Boost policy adherence from 88% to 92%+ through automated tracking\n3. **ESG Ratings**: Focus on Scope 3 emissions and supply chain transparency to reach A-level\n4. **Transparency**: Publish real-time ESG dashboard publicly (leverage this platform!)\n5. **Stakeholder Engagement**: Increase community touchpoints by 20%\n6. **Risk Management**: Implement ESG risk committee at board level\n\n**Priority**: Publicly launch this ESG dashboard to demonstrate transparency leadership.'),
        
        ('general', 'benchmark', 'How do we compare?',
         'Aurora Renewables vs. renewable energy sector benchmarks:\n\n**Board Governance**: ⭐ Excellent\n• Independence: 65% vs. 60% sector avg (+5%)\n• Diversity: 35% vs. 25% sector avg (+10%)\n\n**Compliance**: ⭐ Excellent\n• Audit Score: 92% vs. 85% sector avg (+7%)\n• Certifications: 15 vs. 10 sector avg (+5)\n\n**ESG Ratings**: ⭐ Above Average\n• MSCI: A vs. sector median BBB\n• Sustainalytics: 72 vs. 65 sector median\n\n**Transparency**: ⭐ Good (Improving)\n• Reporting: 78% vs. 75% sector avg\n• Target: Reach 85%+ with dashboard publication\n\n**Position**: Top quartile governance in renewable energy sector.'),
    ]
    
    cursor.executemany('''
        INSERT INTO insights (metric_key, insight_type, question, answer)
        VALUES (?, ?, ?, ?)
    ''', governance_insights)
    
    # Quick stats
    quick_stats = [
        ('board_composition', 'Independence', '65%'),
        ('board_composition', 'Diversity', '35%'),
        ('board_composition', 'Expertise', '85%'),
        ('compliance_metrics', 'Audit Score', '92%'),
        ('compliance_metrics', 'Policy Adherence', '88%'),
        ('compliance_metrics', 'Certifications', '15 active'),
        ('esg_ratings', 'MSCI Rating', 'A (Top 25%)'),
        ('esg_ratings', 'Sustainalytics', '72/100 (Low Risk)'),
        ('esg_ratings', 'CDP Score', 'B (Management)'),
        ('transparency_disclosure', 'Reporting Score', '78/100'),
        ('transparency_disclosure', 'Stakeholder Meetings', '450/year'),
        ('transparency_disclosure', 'Data Verification', '85%'),
    ]
    
    cursor.executemany('''
        INSERT INTO quick_stats (metric_key, stat_name, stat_value)
        VALUES (?, ?, ?)
    ''', quick_stats)
    
    conn.commit()
    conn.close()
    print("✅ Created governance_ai_insights.db")

if __name__ == "__main__":
    print("🤖 Creating AI Insights Databases...\n")
    create_emissions_insights_db()
    create_social_insights_db()
    create_governance_insights_db()
    print("\n✅ All AI insights databases created successfully!")
