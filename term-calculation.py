# backend/main.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class TermLifeInput(BaseModel):
    age: int
    annual_income: float
    monthly_expenses: float
    outstanding_loans: float
    existing_term_cover: float
    family_members: int

def calculate_term_life_cover(data: TermLifeInput):
    # Step 1: Income replacement (10x annual income)
    income_cover = data.annual_income * 10

    # Step 2: Expenses for family (12 months * monthly expenses * family size)
    expenses_cover = data.monthly_expenses * 12 * data.family_members

    # Step 3: Add outstanding loans
    loans_cover = data.outstanding_loans

    # Step 4: Total required cover
    total_required_cover = income_cover + expenses_cover + loans_cover

    # Step 5: Deduct existing term cover
    recommended_cover = max(total_required_cover - data.existing_term_cover, 0)

    return {
        "income_cover": income_cover,
        "expenses_cover": expenses_cover,
        "loans_cover": loans_cover,
        "total_required_cover": total_required_cover,
        "recommended_cover": recommended_cover
    }

@app.post("/calculate")
async def calculate_term_life(input_data: TermLifeInput):
    result = calculate_term_life_cover(input_data)
    return result
