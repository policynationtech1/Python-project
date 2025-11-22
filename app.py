# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from calculations import calculate_insurance

# app = Flask(__name__)
# CORS(app)  # allow frontend requests

# @app.route('/calculate', methods=['POST'])
# def calculate():
#     data = request.json
#     result = calculate_insurance(data)
#     return jsonify(result)

# if __name__ == '__main__':
#     app.run(debug=True)


from flask import send_file, request
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import io
from flask import request, send_file
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from flask import Flask, request, jsonify
from flask_cors import CORS

import mysql.connector

connection = mysql.connector.connect(
    host="101.53.143.92",        # Database host
    user="policynation_codeship",     # Database username
    password="QvB^yxW96hx*", # Database password
    database="policyna_tion_uat"  # Database name
)

app = Flask(__name__)
CORS(app)


# ---------------------------------------------
#  TERM LIFE CALCULATION LOGIC
# ---------------------------------------------
def calculate_term_life(data):
    import math

    age = int(data["age"])
    retirement_age = int(data["retirement_age"])
    income = float(data["monthly_income"])
    expenses = float(data["household_expenses"])
    loans = float(data["loans_outstanding"])
    existing_term = float(data["existing_term_cover"])
    employer_term = float(data["employer_life_cover"])
    smoker = data["smoker_type"]
    inflation = float(data["inflation_rate"]) / 100


    # Inflation only for goals

    # inflation = 0.06
    # avg_goal_years = 8

    # 1. Household Expense Cover
    working_years_left = max(retirement_age - age, 0)

    
    annual_expenses = expenses * 12
   
    HEC = annual_expenses * working_years_left
   

    # 2. Income Replacement Cover
    annual_income = income * 12
    
   
    if age < 30:
        multiplier = 20
    elif age <= 35:
        multiplier = 18
    elif age <= 40:
        multiplier = 16
    elif age <= 45:
        multiplier = 12
    elif age <= 50:
        multiplier = 10
    elif age <= 55:
        multiplier = 8
    else:
        multiplier = 5

    IRC = annual_income * multiplier
    

    # 3. Loan Cover
    LoanCover = loans
    
   # -------------------------
    # 4. Goal Cover (per-goal inflation)
    # -------------------------
    GoalCover = 0
    goals_list = data.get("goals", [])

    for g in goals_list:
        today_cost = float(g.get("today_cost", 0))
        years_left = int(g.get("years_left", 0))   # 0 → no inflation applied

        inflated_cost = today_cost * ((1 + inflation) ** years_left)
       

        GoalCover += inflated_cost
       

    # 5. Existing coverage
    ExistingProtection = existing_term + employer_term
   
    # 6. Total need
    TotalNeeds = HEC + IRC + LoanCover + GoalCover
   
    # 7. Minimum SA
    RecommendedSA = TotalNeeds - ExistingProtection

    RecommendedSA = max(RecommendedSA, 25_00_000)
 

    if smoker.lower() == "smoker":
        RecommendedSA *= 1.30
   
    # 8. Round to nearest 5 lakh
    RecommendedSA = round(RecommendedSA / 500000) * 500000

    # 9. Insurer max limit
    if age < 35:
        MaxAllowed = annual_income * 25
    elif age <= 45:
        MaxAllowed = annual_income * 20
    elif age <= 55:
        MaxAllowed = annual_income * 15
    else:
        MaxAllowed = annual_income * 10

    

    FinalSA = min(RecommendedSA, MaxAllowed)

    return FinalSA



# ---------------------------------------------
#  HEALTH INSURANCE CALCULATION LOGIC
# ---------------------------------------------
def calculate_health(data):

    age = int(data["age"])
    family_size = int(data["family_size"])
    has_parents = data["has_parents"]
    parent_age = int(data["parent_age"]) if has_parents else None
    city = data["city_type"]
    comorbidity = data["existing_diseases"]
    smoker = data["smoker_type"]

    existing_family_si = float(data["existing_health_cover_family"])
    existing_parent_si = float(data["existing_health_cover_parents"])

    # ----------------------------------------------
    # BASE FAMILY SI (AGE-based)
    # ----------------------------------------------
    if age <= 30:
        base_si = 500000
    elif 31 <= age <= 40:
        base_si = 1000000
    elif 41 <= age <= 50:
        base_si = 1500000
    else:
        base_si = 2000000

    # ----------------------------------------------
    # CITY COST MULTIPLIER
    # ----------------------------------------------
    city_multiplier = {
        "Metro": 1.4,
        "Tier-1": 1.25,
        "Tier-2": 1.1,
        "Tier-3": 1.0
    }
    base_si *= city_multiplier.get(city, 1)

    # ----------------------------------------------
    # COMORBIDITY MULTIPLIER
    # ----------------------------------------------
    disease_multipliers = {
        "none": 1.0,
        "thyroid": 1.10,
        "diabetes": 1.25,
        "hypertension": 1.25,
        "obesity": 1.30,
        "pcos": 1.30,
        "heart": 1.50,
        "cardiac": 1.50,
        "cancer": 1.75,
        "kidney_failure": 1.75,
        "liver_cirrhosis": 1.75
    }

    if isinstance(comorbidity, str):
        diseases = [d.strip().lower() for d in comorbidity.split(",") if d.strip()]
    else:
        diseases = [d.lower() for d in comorbidity]

    total_multiplier = 1.0
    for d in diseases:
        total_multiplier *= disease_multipliers.get(d, 1.0)

    total_multiplier = min(total_multiplier, 2.25)
    base_si *= total_multiplier

    # ----------------------------------------------
    # FAMILY SIZE MULTIPLIER
    # ----------------------------------------------
    if family_size == 3:
        base_si *= 1.2
    elif family_size >= 4:
        base_si *= 1.4

    # ----------------------------------------------
    # SMOKER IMPACT
    # ----------------------------------------------
    if smoker.lower() == "smoker":
        base_si *= 1.25

    # ----------------------------------------------
    # PARENT SI
    # ----------------------------------------------
    parent_si = 0

    if has_parents:
        if parent_age < 45:
            parent_multiplier = 1.2
        elif parent_age <= 60:
            parent_multiplier = 1.5
        else:
            parent_multiplier = 2.0

        parent_si = base_si * parent_multiplier
        parent_si *= city_multiplier.get(city, 1)  # add back this missing line

    # ----------------------------------------------
    # ROUNDING
    # ----------------------------------------------
    rounded_family_si = round(base_si / 100000) * 100000
    rounded_parent_si = round(parent_si / 100000) * 100000

    # ----------------------------------------------
    # GAPS
    # ----------------------------------------------
    family_gap = max(rounded_family_si - existing_family_si, 0)
    parent_gap = max(rounded_parent_si - existing_parent_si, 0)

    return {
        "recommended_family_si": int(rounded_family_si),
        "recommended_parent_si": int(rounded_parent_si),
        "family_gap": int(family_gap),
        "parent_gap": int(parent_gap)
    }


# ---------------------------------------------
#  MASTER ENGINE (TERM + HEALTH)
# ---------------------------------------------
def calculate_insurance(data):
    print(data)
    return {
        "term_life_needed": calculate_term_life(data),
        "health_insurance": calculate_health(data)
    }


# ---------------------------------------------
#  API ENDPOINT
# ---------------------------------------------
@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    result = calculate_insurance(data)
    return jsonify(result) 


@app.route('/validate-pincode', methods=['POST'])
def validatepincode():
    import math
    data = request.json
   
    pincode = int(data["pincode"])

    mysql = connection.cursor()
    query = "SELECT * FROM master_pincode WHERE pincode = %s"
    mysql.execute(query, (pincode,))
    pincode_details = mysql.fetchall()
    city_id= pincode_details[0][2]
   
    query1 = "SELECT * FROM master_city WHERE city_id = %s"
    mysql.execute(query1, (city_id,))
    city_details = mysql.fetchall()
    city_name= city_details[0][2]
   
    query2 = "SELECT * FROM City_zones WHERE city_name = %s"
    mysql.execute(query2, (city_name,))
    zone_details = mysql.fetchall()
    zone_type= zone_details[0][2]
    
    return {
        "city_name": city_name,
        "zone_type":zone_type
    }


@app.post("/download-report")
def download_report():
    data = request.json

    # --- Currency Formatting ----
    def money(x):
        try:
            return f"₹{int(float(x)):,}"
        except:
            return "₹0"

    # ---- PDF BUFFER ----
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )

    styles = getSampleStyleSheet()

    # ==== BRAND COLORS ====
    BRAND_PRIMARY = "#1BAA7A"   # Your logo's green
    BRAND_DARK = "#0D6E58"

    # ==== CUSTOM STYLES ====
    styles.add(ParagraphStyle(
        name="SectionTitle",
        fontSize=16,
        textColor=BRAND_DARK,
        spaceAfter=10,
        leading=20,
        bold=True
    ))
    styles.add(ParagraphStyle(
        name="ItemLabel",
        fontSize=11,
        leading=14,
        textColor="#333",
    ))
    styles.add(ParagraphStyle(
        name="ItemValue",
        fontSize=11,
        leading=14,
        textColor="#000",
        leftIndent=4
    ))

    story = []

    # -------------------------------------------------
    # 🔰 HEADER BRAND BAR
    # -------------------------------------------------
    story.append(Paragraph(
        f"<para align='center'><b><font size=18 color='{BRAND_PRIMARY}'>PolicyNation Protection Report</font></b></para>",
        styles["BodyText"]
    ))
    story.append(Spacer(1, 12))

    # -------------------------------------------------
    # 🔁 SECTION COMPONENT
    # -------------------------------------------------
    def section(title, rows):
        story.append(Spacer(1, 18))

        # Section title
        story.append(Paragraph(title, styles["SectionTitle"]))

        # Table
        table_data = []
        for label, value in rows:
            table_data.append([
                Paragraph(f"<b>{label}</b>", styles["ItemLabel"]),
                Paragraph(str(value), styles["ItemValue"])
            ])

        table = Table(table_data, colWidths=[170, 300])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E9F7F2")),   # lighter green shade
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor(BRAND_PRIMARY)),
            ('INNERGRID', (0,0), (-1,-1), 0.4, colors.HexColor("#A9DFBF")),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))

        story.append(table)

    # -------------------------------------------------
    # 1. PERSONAL SUMMARY
    # -------------------------------------------------
    section("1. Personal Summary", [
        ("Name", data.get("name")),
        ("Age", data.get("age")),
        ("City Type", data.get("city_type")),
        ("Household", data.get('household_description')),
    ])

    # -------------------------------------------------
    # 2. FINANCIAL SUMMARY
    # -------------------------------------------------
    section("2. Financial Summary", [
        ("Monthly Income", money(data.get('monthly_income'))),
        ("Monthly Expenses", money(data.get('monthly_expenses'))),
        ("Loans", money(data.get('loans'))),
        ("Savings & Investments", money(data.get('savings'))),
    ])

    # -------------------------------------------------
    # 3. LIFE INSURANCE
    # -------------------------------------------------
    section("3. Life Insurance Recommendation", [
        ("Ideal Term Cover", money(data.get('ideal_term_cover'))),
        ("Minimum Recommended Cover", money(data.get('minimum_cover'))),
        ("Reasoning", data.get('life_explanation')),
    ])

    # -------------------------------------------------
    # 4. HEALTH INSURANCE
    # -------------------------------------------------
    section("4. Health Insurance Recommendation", [
        ("Family Floater Recommendation", money(data.get('family_floater'))),
        ("Parents Health Cover", money(data.get('parents_si'))),
        ("Explanation", data.get('health_explanation')),
    ])

    # -------------------------------------------------
    # 5. GAP ANALYSIS
    # -------------------------------------------------
    section("5. Existing Coverage Gap Analysis", [
        ("Current Life Cover", money(data.get('current_life_cover'))),
        ("Required Life Cover", money(data.get('required_life_cover'))),
        ("Life Cover Gap", money(data.get('life_gap'))),
        ("Current Health SI", money(data.get('current_health_si'))),
        ("Required Health SI", money(data.get('required_health_si'))),
        ("Health Cover Gap", money(data.get('health_gap'))),
    ])

    # -------------------------------------------------
    # 6. ADVICE NOTES
    # -------------------------------------------------
    section("6. Advisory Notes", [
        ("Notes", data.get('advice_notes')),
    ])

    # -------------------------------------------------
    # 7. NEXT STEPS
    # -------------------------------------------------
    section("7. Next Steps", [
        ("Action Items",
         "• Speak to your advisor<br/>"
         "• Request quotations<br/>"
         "• Review protection yearly"
        ),
    ])

    # -------------------------------------------------
    doc.build(story)

    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="Protection_Report.pdf",
        mimetype="application/pdf"
    )


# if __name__ == "__main__":
#     app.run(port=5000, debug=True)
# if __name__ == '__main__':
#     app.run(debug=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
