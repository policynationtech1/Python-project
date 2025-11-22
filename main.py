from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# CORS(app, origins=["http://localhost:3001/"])  # allow your React frontend
CORS(app,resources={r"/*":{"origins":"*"}})

@app.route('/send-name', methods=['POST'])
def send_name():
    # data = request.json
    # name = data.get('name')
    # if name:
    #     return jsonify({"message": f"Hello {name}, your name was received successfully!"})
    # else:
    #     return jsonify({"message": "No name received"}), 400
    



    # def send_name():
    data = request.get_json()

    # Extract data from form
    age = data.get('age')
    gender = data.get('gender')
    city_type = data.get('cityType')
    retirement_age = data.get('retirementAge')
    spouse_present = data.get('spousePresent')
    spouse_age = data.get('spouseAge')
    spouse_income = data.get('spouseIncome')
    children_count = data.get('childrenCount')
    child_ages = data.get('childAges')
    parent_count = data.get('parentCount')
    parent_details = data.get('parentDetails')

    # Validate if the necessary fields are provided
    if age is None or gender is None or city_type is None:
        return jsonify({'error': 'Missing required fields'}), 400

    # Placeholder for calculation logic (replace with actual business logic)
    term_cover = int(age) * 10000  # Example formula for Term Cover calculation
    health_cover = int(age) * 5000  # Example formula for Health Cover calculation

    # If there is a spouse and they are present, modify term cover slightly
    if spouse_present:
        term_cover += int(spouse_age) * 5000  # Adding a bonus multiplier based on spouse age
    
    # Health cover calculation might adjust depending on city type
    if city_type == "Tier 1":
        health_cover += 10000  # Higher health cover for Tier 1 cities

    # Return the response with calculated values
    result = {
        'term_cover': term_cover,
        'health_cover': health_cover,
        'message': 'Insurance calculation successful'
    }

    return jsonify(result)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)  # accessible on your local network


# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from typing import List, Dict, Optional

# app = FastAPI()
# # Enable CORS for React frontend
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Replace with your frontend URL in production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ------------------- Models -------------------

# class SelfTab(BaseModel):
#     age: int
#     gender: str
#     city_type: str
#     retirement_age: int

# class FamilyTab(BaseModel):
#     has_spouse: bool
#     spouse_age: Optional[int] = 0
#     spouse_income: Optional[int] = 0
#     num_children: int
#     children_age: List[int]
#     num_dependent_parents: int
#     parents_age_health: List[Dict]

# class FinancialTab(BaseModel):
#     monthly_income: float
#     spouse_monthly_income: float
#     monthly_expenses: float
#     loan_details: List[Dict]
#     liquid_savings: float
#     market_investments: float
#     future_goals: List[Dict]

# class ExistingInsuranceTab(BaseModel):
#     existing_term_life_cover: float
#     employer_life_cover: float
#     existing_health_cover_family: float
#     existing_health_cover_parents: float
#     financial_personality: str
#     inflation_assumption: float
#     health_premium_comfort_level: float

# class InputModel(BaseModel):
#     self_tab: SelfTab
#     family_tab: FamilyTab
#     financial_tab: FinancialTab
#     existing_insurance_tab: ExistingInsuranceTab

# # ------------------- Logic -------------------

# def calculate_insurance(self_tab, family_tab, financial_tab, existing):
#     # Life insurance calculation
#     annual_income = financial_tab.monthly_income * 12
#     years_left = max(1, self_tab.retirement_age - self_tab.age)
#     hlv = annual_income * years_left
#     expense_projection = financial_tab.monthly_expenses * 12 * 20
#     liabilities = sum([loan.get("amount", 0) for loan in financial_tab.loan_details])
#     required_life_cover = hlv + expense_projection + liabilities - existing.existing_term_life_cover - existing.employer_life_cover
#     required_life_cover = max(0, required_life_cover)

#     # Health insurance calculation
#     base_health_si = 2000000 if self_tab.city_type == "Tier 1" else 1000000
#     if self_tab.age > 45:
#         base_health_si *= 1.5
#     required_health_cover = max(0, base_health_si - existing.existing_health_cover_family)

#     # Parents health cover
#     parents_base = 500000 * family_tab.num_dependent_parents
#     required_parents_health = max(0, parents_base - existing.existing_health_cover_parents)

#     return {
#         "recommended_life_cover": int(required_life_cover),
#         "recommended_health_cover": int(required_health_cover),
#         "recommended_parents_health_cover": int(required_parents_health)
#     }

# # ------------------- API -------------------

# @app.post("/calculate")
# def calculate(data: InputModel):
#     result = calculate_insurance(
#         data.self_tab,
#         data.family_tab,
#         data.financial_tab,
#         data.existing_insurance_tab
#     )
#     return {"status": "success", "results": result}

# # ------------------- Run -------------------
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000)











