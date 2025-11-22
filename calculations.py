def calculate_insurance(data):
    try:
        # Convert inputs to proper numeric types
        monthly_income = float(data['monthly_income'])
        retirement_age = int(data['retirement_age'])
        age = int(data['age'])
        expenses = float(data['household_expenses'])
        existing_term = float(data['existing_term_cover'])
        employer_cover = float(data['employer_life_cover'])

        print(data)
        print(type(monthly_income), type(retirement_age), type(age), type(expenses), type(existing_term), type(employer_cover))

        # Perform the calculation
        term_cover_needed = (monthly_income * 12 * (retirement_age - age)) + (expenses * 12 * 5) - existing_term - employer_cover
        
        # Return the result
        result = {'term_cover_needed': term_cover_needed}
        return result

    except KeyError as e:
        return {'error': f'Missing data: {str(e)}'}
    except ValueError as e:
        return {'error': f'Invalid input value: {str(e)}'}
