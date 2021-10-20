# Part of the Python Standard Library
import time
import datetime

# Created by third-parties
from flask import render_template, request, redirect, url_for, session

# Created by me
from database import Database
from predictor import Predictor
from pages.webpage import Webpage
from tools import redirectNonManager



class ManagerHome(Webpage):
    
    @redirectNonManager   # Redirects the user if they are not logged in as a manager
    def run(self):

        timestamp = self.TODAY      # For development purposes, we are using an artificial timestamp that does not change
        dateToday = datetime.date.fromtimestamp(timestamp)

        return render_template("manager/managerHome.html", date=dateToday)



class ManageMenus(Webpage):

    @redirectNonManager   # Redirects the user if they are not logged in as a manager
    def run(self):

        db = Database(self.HOSTNAME, self.USER, self.PASSWORD, self.DBNAME)

        timestamp = self.TODAY      # For development purposes, we are using an artificial timestamp that does not change
        dateToday = datetime.date.fromtimestamp(timestamp)

        menusQuery = """
            SELECT options.name, days.timestamp
            FROM days, menu_options, options
            WHERE options.optionID = menu_options.optionID
            AND days.dayID = menu_options.dayID
            AND days.timestamp >= %s
            ORDER BY name
        """
        menusQueryParams = (timestamp)
        data = db.executeQuery(menusQuery, menusQueryParams)    # We get all options that are available in all menus

        startDate = timestamp   # The first date that we display the menu for
        endDate = startDate + self.SECONDS_IN_DAY*28   # Menus can be set up to four weeks in advance

        return render_template("manager/manageMenus.html", date=dateToday, dateclass=datetime.date, startDate=startDate, endDate=endDate, data=data)



class ManageMenusEdit(Webpage):
    
    @redirectNonManager   # Redirects the user if they are not logged in as a manager
    def run(self):

        db = Database(self.HOSTNAME, self.USER, self.PASSWORD, self.DBNAME)
        
        timestamp = self.TODAY      # For development purposes, we are using an artificial timestamp that does not change
        dateToday = datetime.date.fromtimestamp(timestamp)

        if "deleteConfirm" in request.form:     # If the user has confirmed that they want to delete an option from the menu

            dateFor = int(request.form['dateFor'])
            optionID = request.form['optionID']

            # We first need to add back the balance to the students whose orders have been removed due to deleting the menu

            queryParams = (optionID)
            getStudentIDsQuery = """
                SELECT students.studentID, students.balance
                FROM students, orders
                WHERE students.studentID = orders.studentID
                AND orders.optionID = %s
            """
            getPriceQuery = """
                SELECT price
                FROM options
                WHERE optionID = %s
            """
            studentData = db.executeQuery(getStudentIDsQuery, queryParams)  # Gets the data about each student who ordered this option
            optionPrice = db.executeQuery(getPriceQuery, queryParams)[0]['price']   # Gets the price of the option

            for student in studentData:     # For each student
                newBalance = student['balance'] + optionPrice   # We calculate the new balance for the student
                studentID = student['studentID']    # Get the student ID of the current student
                updateQuery = """
                    UPDATE students
                    SET balance = %s
                    WHERE studentID = %s
                """
                updateQueryParams = (newBalance, studentID)
                db.executeQuery(updateQuery, updateQueryParams)     # We update each student record to have the correct balance

            dayQuery = """
                SELECT dayID
                FROM days
                WHERE timestamp = %s
            """
            dayQueryParams = (dateFor)
            dayID = db.executeQuery(dayQuery, dayQueryParams)[0]["dayID"]

            # Now we can delete the menu and any links it has to the options table

            deleteQuery1 = """
                DELETE FROM menu_options
                WHERE optionID = %s
                AND dayID = %s
            """
            deleteQuery2 = """
                DELETE FROM orders
                WHERE optionID = %s
            """
            deleteQueryParams1 = (optionID, dayID)
            deleteQueryParams2 = (optionID)

            db.executeQuery(deleteQuery1, deleteQueryParams1) # Delete the option from the menu options table
            db.executeQuery(deleteQuery2, deleteQueryParams2) # Delete any orders containing the option

            return redirect(url_for("manageMenus")) # Redirect the user back to the manage menus page

        if "addConfirm" in request.form:    # If the user has confirmed that they want to add an option to the menu
            dateFor = request.form['dateFor']   # Get the date that the menu is for
            optionID = request.form['optionID'] # Get the option ID of the option

            getDayQuery = """
                SELECT dayID
                FROM days
                WHERE timestamp = %s
            """
            getDayQueryParams = (dateFor)
            dayID = db.executeQuery(getDayQuery, getDayQueryParams)  # Get the day ID of the day that we want to add for

            if len(dayID) == 0:    # We need to create the day if it doesn't exist yet
                createDayQuery = """
                    INSERT INTO days
                    VALUES (default, %s, default)
                """
                createDayQueryParams = (dateFor)
                db.executeQuery(createDayQuery, createDayQueryParams)     # Create the day
                dayID = db.executeQuery(getDayQuery, getDayQueryParams)  # Get the ID of the day

            dayID = dayID[0]['dayID']    # Get the actual ID from the list of records

            addOptionQuery = """
                INSERT INTO menu_options
                VALUES (%s, %s)
            """
            addOptionQueryParams = (dayID, optionID)
            db.executeQuery(addOptionQuery, addOptionQueryParams)   # Adds the option to the menu for this day

            return redirect(url_for("manageMenus"))     # Redirect the user back to the manage menus page

        if "add" in request.form:   # If the user has chosen that they want add an option, but has not chosen a particular option yet
            dateFor = int(request.form['dateFor'])  # Get the date that the option will be on the menu for

            optionsQuery = """
                SELECT name, price, optionID
                FROM options
                WHERE optionID NOT IN (
                    SELECT menu_options.optionID
                    FROM menu_options, days
                    WHERE days.dayID = menu_options.dayID
                    AND days.timestamp = %s)
                ORDER BY name
            """
            optionsQueryParams = (dateFor)
            data = db.executeQuery(optionsQuery, optionsQueryParams)    # Gets the list of options that are not already in the menu
            
            return render_template("manager/manageMenusEditAdd.html", date=dateToday, dateclass=datetime.date, dateFor=dateFor, data=data)

        if "optionID" in request.form:  # If the user has chosen to delete an option from the database

            dateFor = int(request.form['dateFor'])  # Get the date that the option is in the menu for
            optionID = request.form['optionID']     # Get the option ID of the option
            name = request.form['name']     # Get the name of the option

            checkOrdersQuery = """
                SELECT COUNT(*) as count
                FROM orders, days
                WHERE days.dayID = orders.dayID
                AND orders.optionID = %s
                AND days.timestamp = %s
            """
            checkOrdersQueryParams = (optionID, dateFor)
            orders = db.executeQuery(checkOrdersQuery, checkOrdersQueryParams)[0]['count']  # Get the number of orders that have been placed for the option

            return render_template("manager/manageMenusEditDelete.html", dateclass=datetime.date, date=dateToday, dateFor=dateFor, name=name, orders=orders, optionID=optionID)

        if "dateFor" in request.form:   # If the user has not chosen to add or delete anything yet
            dateFor = int(request.form['dateFor'])  # Gets the date that the menu is for

            optionsQuery = """
                SELECT options.name, options.optionID, options.price
                FROM options, menu_options, days
                WHERE options.optionID = menu_options.optionID
                AND days.dayID = menu_options.dayID
                AND days.timestamp = %s
                ORDER BY name
            """
            optionsQueryParams = (dateFor)
            data = db.executeQuery(optionsQuery, optionsQueryParams)    # Get the options that are in the menu for this day

            return render_template("manager/manageMenusEdit.html", date=dateToday, dateclass=datetime.date, data=data, dateFor=dateFor)

        return redirect(url_for("managerHome"))



class ManageOptions(Webpage):
    
    @redirectNonManager   # Redirects the user if they are not logged in as a manager
    def run(self):

        timestamp = self.TODAY      # For development purposes, we are using an artificial timestamp that does not change
        dateToday = datetime.date.fromtimestamp(timestamp)

        db = Database(self.HOSTNAME, self.USER, self.PASSWORD, self.DBNAME)

        optionsQuery = """
            SELECT *
            FROM options
            ORDER BY name
        """
        ingredientsQuery = """
            SELECT ingredients.name, ingredients.pricePerKG, option_ingredients.optionID, option_ingredients.quantity
            FROM ingredients, option_ingredients
            WHERE ingredients.ingredientID = option_ingredients.ingredientID
            ORDER BY name
        """
        optionsData = db.executeQuery(optionsQuery)     # Gets a list of all options
        ingredientsData = db.executeQuery(ingredientsQuery)     # Gets a list of all ingredients that are used in an option


        optionCosts = {}    # Create an empty dictionary to store the cost of each option
        for option in optionsData:  # For each option
            optionCosts[option['optionID']] = 0     # Initialise the option cost for that option
            for ingredient in ingredientsData:      # For each ingredient record
                if ingredient['optionID'] == option['optionID']:    # If the ingredient is for the option we are looking at
                    optionCosts[option['optionID']] += ingredient['pricePerKG'] * ingredient['quantity'] / 1000     # Add the cost of that ingredient to that option's option costs

        return render_template("manager/manageOptions.html", date=dateToday, optionsData=optionsData, ingredientsData=ingredientsData, optionCosts=optionCosts)



class ManageOptionsEdit(Webpage):
    
    @redirectNonManager   # Redirects the user if they are not logged in as a manager
    def run(self):

        if "optionID" in request.form:  # If the user has chosen an option

            db = Database(self.HOSTNAME, self.USER, self.PASSWORD, self.DBNAME)

            timestamp = self.TODAY      # For development purposes, we are using an artificial timestamp that does not change
            dateToday = datetime.date.fromtimestamp(timestamp)

            optionID = request.form['optionID']  # Get the option ID of the option

            optionQuery = """
                SELECT name, price, optionID
                FROM options
                WHERE optionID = %s
            """
            optionQueryParams = (optionID)
            optionData = db.executeQuery(optionQuery, optionQueryParams)[0]     # Get the details of the chosen option

            ingredientsQuery = """
                SELECT ingredients.ingredientID, ingredients.name, ingredients.pricePerKG, option_ingredients.quantity
                FROM ingredients, option_ingredients
                WHERE ingredients.ingredientID = option_ingredients.ingredientID
                AND option_ingredients.optionID = %s
            """
            ingredientsQueryParams = (optionID)
            ingredientsData = db.executeQuery(ingredientsQuery, ingredientsQueryParams) # Gets the list of ingredients that are in the chosen option

            return render_template("manager/manageOptionsEdit.html", date=dateToday, optionData=optionData, ingredientsData=ingredientsData)

        return redirect(url_for('managerHome'))



class ManageOptionsEditName(Webpage):

    @redirectNonManager   # Redirects the user if they are not logged in as a manager
    def run(self):

        db = Database(self.HOSTNAME, self.USER, self.PASSWORD, self.DBNAME)

        timestamp = self.TODAY      # For development purposes, we are using an artificial timestamp that does not change
        dateToday = datetime.date.fromtimestamp(timestamp)

        optionID = request.form['optionID']     # Get the option ID of the selected option

        alert = None    # We may need to set an alert later

        if "newName" in request.form:   # If the user has chosen a new name for the option

            newName = request.form["newName"]   # Get the new name

            if newName:

                updateQuery = """
                    UPDATE options
                    SET name = %s
                    WHERE optionID = %s
                """
                updateQueryParams = (newName, optionID)
                db.executeQuery(updateQuery, updateQueryParams)     # Set the name of the option to the new name
    
                return redirect(url_for("manageOptions"))   # Redirect the user back to the manage options page

            alert = "The field is required"

        # If the user has not selected a new name yet
        optionName = request.form['optionName']     # Get the name of the option

        return render_template("manager/manageOptionsEditName.html", date=dateToday, optionID=optionID, optionName=optionName, alert=alert)



class ManageOptionsEditPrice(Webpage):

    @redirectNonManager   # Redirects the user if they are not logged in as a manager
    def run(self):

        db = Database(self.HOSTNAME, self.USER, self.PASSWORD, self.DBNAME)

        timestamp = self.TODAY      # For development purposes, we are using an artificial timestamp that does not change
        dateToday = datetime.date.fromtimestamp(timestamp)

        optionID = request.form['optionID']     # Get the option ID of the selected option
        alert = None

        if "newPrice" in request.form:      # If the user has selected a new price for the option

            newPrice = request.form["newPrice"]     # Get the new price
            if newPrice:

                updateQuery = """
                    UPDATE options
                    SET price = %s
                    WHERE optionID = %s
                """
                updateQueryParams = (newPrice, optionID)
                db.executeQuery(updateQuery, updateQueryParams)     # Change the price to the new price
    
                return redirect(url_for("manageOptions"))   # Redirect the user back to the manage options page

            alert = "The field is required"

        # If the user has not chosen a new price yet
        optionName = request.form['optionName']     # Get the name of the option
        optionPrice = request.form['optionPrice']   # Get the current price of the option

        return render_template("manager/manageOptionsEditPrice.html", date=dateToday, optionID=optionID, optionName=optionName, optionPrice=optionPrice, alert=alert)



class ManageOptionsAddIngredient(Webpage):

    @redirectNonManager   # Redirects the user if they are not logged in as a manager
    def run(self):

        db = Database(self.HOSTNAME, self.USER, self.PASSWORD, self.DBNAME)
        
        timestamp = self.TODAY      # For development purposes, we are using an artificial timestamp that does not change
        dateToday = datetime.date.fromtimestamp(timestamp)

        alert = None

        if "quantity" in request.form:   # If the user has chosen an ingredient to add and a quantity
            
            # Get the data from the POST request
            quantity = request.form['quantity']
            optionID = request.form['optionID']

            if quantity and "ingredientID" in request.form:

                ingredientID = request.form['ingredientID']

                query = """
                    INSERT INTO option_ingredients
                    VALUES (%s, %s, %s)
                """
                queryParams = (optionID, ingredientID, quantity)
                db.executeQuery(query, queryParams)     # Add the ingredient to the option

                return redirect(url_for("manageOptions"))

            alert = "All fields are required"

        if "optionID" in request.form:  # If the user has not chosen an ingredient or option ID yet

            optionID = request.form['optionID']     # Get the option ID of the selected option

            optionQuery = """
                SELECT name
                FROM options
                WHERE optionID = %s
            """
            optionQueryParams = (optionID)
            optionName = db.executeQuery(optionQuery, optionQueryParams)    # Gets the name of the chosen option

            ingredientQuery = """
                SELECT name, ingredientID, pricePerKG
                FROM ingredients
                ORDER BY name
            """
            ingredientData = db.executeQuery(ingredientQuery)   # Gets the list of all ingredients

            return render_template("manager/manageOptionsAddIngredient.html", date=dateToday, optionID=optionID, optionName=optionName, data=ingredientData, alert=alert)

        return redirect(url_for("managerHome"))



class ManageOptionsEditIngredient(Webpage):

    @redirectNonManager   # Redirects the user if they are not logged in as a manager
    def run(self):

        db = Database(self.HOSTNAME, self.USER, self.PASSWORD, self.DBNAME)
        alert = None

        if "newQuantity" in request.form:   # If the user has selected a new quantity for the ingredient

            # Get the data from the POST request
            newQuantity = request.form['newQuantity']
            optionID = request.form['optionID']
            ingredientID = request.form['ingredientID']

            if newQuantity:

                updateQuery = """
                    UPDATE option_ingredients
                    SET quantity = %s
                    WHERE optionID = %s
                    AND ingredientID = %s
                """
                updateQueryParams = (newQuantity, optionID, ingredientID)
                db.executeQuery(updateQuery, updateQueryParams)     # Change the quantity to the new quuantity

                return redirect(url_for("manageOptions"))

            alert = "The field is required"

        if "optionID" in request.form:  # If the user has not selected a new quantity yet

            # Gets the data from the POST request
            optionID = request.form['optionID']
            ingredientID = request.form['ingredientID']

            timestamp = self.TODAY      # For development purposes, we are using an artificial timestamp that does not change
            dateToday = datetime.date.fromtimestamp(timestamp)

            ingredientQuery = """
                SELECT name, ingredientID
                FROM ingredients
                WHERE ingredientID = %s
            """
            ingredientQueryParams = (ingredientID)
            ingredientData = db.executeQuery(ingredientQuery, ingredientQueryParams)[0]     # Gets the data about the selected ingredient

            return render_template("manager/manageOptionsEditIngredient.html", date=dateToday, optionID=optionID, ingredientData=ingredientData, alert=alert)

        return redirect(url_for("managerHome"))



class ManageOptionsDeleteIngredient(Webpage):

    @redirectNonManager   # Redirects the user if they are not logged in as a manager
    def run(self):

        db = Database(self.HOSTNAME, self.USER, self.PASSWORD, self.DBNAME)

        if "deleteConfirm" in request.form:     # If the user has confirmed their choice to delete an ingredient

            optionID = request.form['optionID']
            ingredientID = request.form['ingredientID']

            deleteQuery = """
                DELETE FROM option_ingredients
                WHERE optionID = %s
                AND ingredientID = %s
            """
            deleteQueryParams = (optionID, ingredientID)
            db.executeQuery(deleteQuery, deleteQueryParams)     # Delete the option from the database

            return redirect(url_for("manageOptions"))

        if "optionID" in request.form:  # If the user has not confirmed their choice yet

            optionID = request.form['optionID']
            ingredientID = request.form['ingredientID']

            timestamp = self.TODAY      # For development purposes, we are using an artificial timestamp that does not change
            dateToday = datetime.date.fromtimestamp(timestamp)

            ingredientQuery = """
                SELECT name, ingredientID
                FROM ingredients
                WHERE ingredientID = %s
            """
            ingredientQueryParams = (ingredientID)
            ingredientData = db.executeQuery(ingredientQuery, ingredientQueryParams)[0] # Get the data about the selected ingredient

            optionQuery = """
                SELECT name
                FROM options
                WHERE optionID = %s
            """
            optionQueryParams = (optionID)
            optionName = db.executeQuery(optionQuery, optionQueryParams)[0]['name'] # Get the name of the option that the ingredient is in

            return render_template("manager/manageOptionsDeleteIngredient.html", date=dateToday, optionID=optionID, optionName=optionName, ingredientData=ingredientData)

        return redirect(url_for("managerHome"))



class ManageOptionsAdd(Webpage):
    
    @redirectNonManager   # Redirects the user if they are not logged in as a manager
    def run(self):

        timestamp = self.TODAY      # For development purposes, we are using an artificial timestamp that does not change
        dateToday = datetime.date.fromtimestamp(timestamp)

        alert = None  # We may need to set an alert later

        if request.method == "POST":    # If the user submitted data through a POST request

            name = request.form["optionName"]
            price = request.form["optionPrice"]

            if name and price:

                db = Database(self.HOSTNAME, self.USER, self.PASSWORD, self.DBNAME)

                newOptionQuery = """
                    INSERT INTO options
                    VALUES (default, %s, %s)
                """
                newOptionQueryParams = (name, price)
                db.executeQuery(newOptionQuery, newOptionQueryParams)   # Create the new option
                return redirect(url_for("manageOptions"))

            else:
                alert = "All fields are required"

        return render_template("manager/manageOptionsAdd.html", date=dateToday, alert=alert)



class ManageOptionsDelete(Webpage):
    
    @redirectNonManager   # Redirects the user if they are not logged in as a manager
    def run(self):

        timestamp = self.TODAY      # For development purposes, we are using an artificial timestamp that does not change
        dateToday = datetime.date.fromtimestamp(timestamp)

        db = Database(self.HOSTNAME, self.USER, self.PASSWORD, self.DBNAME)

        if "deleteConfirm" in request.form:

            optionID = request.form['optionID']

            # We need to ensure that each student record has the correct balance

            getStudentIDsQuery = """
                SELECT students.studentID, students.balance
                FROM students, orders, days
                WHERE students.studentID = orders.studentID
                AND days.dayID = orders.dayID
                AND orders.optionID = %s
                AND days.timestamp >= %s
            """
            getStudentIDsQueryParams = (optionID, timestamp)

            getPriceQuery = """
                SELECT price
                FROM options
                WHERE optionID = %s
            """
            getPriceQueryParams = (optionID)

            studentData = db.executeQuery(getStudentIDsQuery, getStudentIDsQueryParams)  # Gets the data about the student who has ordered this option
            optionPrice = db.executeQuery(getPriceQuery, getPriceQueryParams)[0]['price']   # Gets the price of the option

            for student in studentData:
                newBalance = student['balance'] + optionPrice   # We calculate the new balance for the student
                studentID = student['studentID']    # Get the student ID
                updateQuery = """
                    UPDATE students
                    SET balance = %s
                    WHERE studentID = %s
                """
                updateQueryParams = (newBalance, studentID)
                db.executeQuery(updateQuery, updateQueryParams)     # We update each student record to have the correct balance

            deleteQuery1 = """
                DELETE FROM options
                WHERE optionID = %s
            """
            deleteQuery2 = """
                DELETE FROM menu_options
                WHERE optionID = %s
            """
            deleteQuery3 = """
                DELETE FROM orders
                WHERE optionID = %s
            """
            deleteQuery4 = """
                DELETE FROM option_ingredients
                WHERE optionID = %s
            """
            deleteQueryParams = (optionID)

            # We need to delete the one with the primary key last
            db.executeQuery(deleteQuery4, deleteQueryParams)    # Delete the option from the option ingredients table
            db.executeQuery(deleteQuery3, deleteQueryParams)    # Delete the option from the orders table
            db.executeQuery(deleteQuery2, deleteQueryParams)    # Delete the option from the menu options table
            db.executeQuery(deleteQuery1, deleteQueryParams)    # Finally, delete the option from the options table
            
            return redirect(url_for("manageOptions"))   # Redirect the user to the manageOptions page


        if "optionID" in request.form:      # If the user has chosen an option to delete

            optionID = request.form['optionID']

            # If the chosen option in the database is in a menu for a future day and has not been overridden by the user

            checkMenusQuery = """
                SELECT COUNT(*) as count
                FROM days, menu_options
                WHERE days.dayID = menu_options.dayID
                AND days.timestamp >= %s
                AND menu_options.optionID = %s
            """
            checkMenusQueryParams = (timestamp, optionID)
            present = db.executeQuery(checkMenusQuery, checkMenusQueryParams)[0]['count']

            checkOrdersQuery = """
                SELECT COUNT(*) as count
                FROM orders, options, days
                WHERE options.optionID = orders.optionID
                AND days.dayID = orders.dayID
                AND days.timestamp >= %s
                AND options.optionID = %s
            """
            checkOrdersQueryParams = (timestamp, optionID)
            data = db.executeQuery(checkOrdersQuery, checkOrdersQueryParams)[0]['count']

            return render_template("manager/manageOptionsDeleteConfirm.html", optionID=optionID, orders=data, present=present)

        return redirect(url_for("cafeteriaHome"))



class ManageIngredients(Webpage):
    
    @redirectNonManager   # Redirects the user if they are not logged in as a manager
    def run(self):

        timestamp = self.TODAY      # For development purposes, we are using an artificial timestamp that does not change
        dateToday = datetime.date.fromtimestamp(timestamp)

        db = Database(self.HOSTNAME, self.USER, self.PASSWORD, self.DBNAME)

        ingredientsQuery = """
            SELECT ingredientID, name, pricePerKG
            FROM ingredients
            ORDER BY name
        """
        ingredientsData = db.executeQuery(ingredientsQuery) # Gets the data for the ingredients

        allergensQuery = """
            SELECT *
            FROM allergens, ingredient_allergens
            WHERE allergens.allergenID = ingredient_allergens.allergenID
            ORDER BY allergens.name
        """
        allergensData = db.executeQuery(allergensQuery) # Gets the data for the allergens
        
        return render_template("manager/manageIngredients.html", date=dateToday, ingredientsData=ingredientsData, allergensData=allergensData)



class ManageIngredientsAdd(Webpage):
    
    @redirectNonManager   # Redirects the user if they are not logged in as a manager
    def run(self):

        timestamp = self.TODAY      # For development purposes, we are using an artificial timestamp that does not change
        dateToday = datetime.date.fromtimestamp(timestamp)

        db = Database(self.HOSTNAME, self.USER, self.PASSWORD, self.DBNAME)
        alert = None

        if request.method == "POST":    # If data has been sent in a POST request, then the user has sent the data about the ingredient
            ingredientName = request.form['ingredientName'].lower() # Get the name of the ingredient
            pricePerKG = request.form['pricePerKG']     # Get the price per kg of the ingredient

            if ingredientName and pricePerKG:

                insertQuery = """
                    INSERT INTO ingredients
                    VALUES (default, %s, %s)
                """
                insertQueryParams = (ingredientName, pricePerKG)
                db.executeQuery(insertQuery, insertQueryParams)     # Insert the data into the database

                return redirect(url_for('manageIngredients'))

            alert = "All fields are required"

        return render_template("manager/manageIngredientsAdd.html", date=dateToday, alert=alert)



class ManageIngredientsEdit(Webpage):

    @redirectNonManager
    def run(self):

        timestamp = self.TODAY      # For development purposes, we are using an artificial timestamp that does not change
        dateToday = datetime.date.fromtimestamp(timestamp)

        db = Database(self.HOSTNAME, self.USER, self.PASSWORD, self.DBNAME)
        
        if "newName" in request.form:   # If the user has chosen a new name for the ingredient
            newName = request.form['newName'] # Get the new name that the user has chosen

        # Get the data from the POST request
        ingredientID = request.form['ingredientID']
        ingredientName = request.form['ingredientName']
        ingredientPPKG = request.form['ingredientPPKG']

        allergensQuery = """
            SELECT *
            FROM allergens, ingredient_allergens
            WHERE allergens.allergenID = ingredient_allergens.allergenID
            AND ingredient_allergens.ingredientID = %s
        """
        allergensQueryParams = (ingredientID)
        allergensData = db.executeQuery(allergensQuery, allergensQueryParams) # Get the allergens that are in the selected ingredient

        return render_template("manager/manageIngredientsEdit.html", date=dateToday, allergensData=allergensData, ingredientName=ingredientName, ingredientID=ingredientID, ingredientPPKG=ingredientPPKG)




class ManageIngredientsEditName(Webpage):

    @redirectNonManager
    def run(self):

        timestamp = self.TODAY      # For development purposes, we are using an artificial timestamp that does not change
        dateToday = datetime.date.fromtimestamp(timestamp)

        db = Database(self.HOSTNAME, self.USER, self.PASSWORD, self.DBNAME)
        alert = None
        
        ingredientID = request.form['ingredientID']

        if "newName" in request.form:   # If the user has chosen a new name for the ingredient
            newName = request.form['newName'].lower()   # Get the new name in lowercase

            if newName:

                updateQuery = """
                    UPDATE ingredients
                    SET name = %s
                    WHERE ingredientID = %s
                """
                updateQueryParams = (newName, ingredientID)
                db.executeQuery(updateQuery, updateQueryParams)     # Change the name to the new name
    
                return redirect(url_for("manageIngredients"))   # Redirect the user to the manage ingredients page

            alert = "The field is required"

        # If the user has not chosen a new name yet
        ingredientName = request.form['ingredientName']     # Get the current name of the ingredient

        return render_template("manager/manageIngredientsEditName.html", date=dateToday, ingredientName=ingredientName, ingredientID=ingredientID, alert=alert)



class ManageIngredientsEditPPKG(Webpage):

    @redirectNonManager
    def run(self):

        timestamp = self.TODAY      # For development purposes, we are using an artificial timestamp that does not change
        dateToday = datetime.date.fromtimestamp(timestamp)

        db = Database(self.HOSTNAME, self.USER, self.PASSWORD, self.DBNAME)
        alert = None

        ingredientID = request.form['ingredientID']     # Get the ingredient ID of the selected ingredient

        if "newPPKG" in request.form:   # If the user has chosen a new price per kilogram
            newPPKG = request.form['newPPKG']   # Get the new price per kilogram

            if newPPKG != "":

                updateQuery = """
                    UPDATE ingredients
                    SET pricePerKG = %s
                    WHERE ingredientID = %s
                """
                updateQueryParams = (newPPKG, ingredientID)
                db.executeQuery(updateQuery, updateQueryParams)     # Update the price per kilogram to the new one
    
                return redirect(url_for("manageIngredients"))   # Redirect to the manage ingredients page

            alert = "The field is required"

        # If the user hasn't chosen a new price per kilogram yet
        # Get the data from the POST request
        ingredientName = request.form['ingredientName']
        ingredientPPKG = request.form['ingredientPPKG']

        return render_template("manager/manageIngredientsEditPPKG.html", date=dateToday, ingredientName=ingredientName, ingredientID=ingredientID, ingredientPPKG=ingredientPPKG, alert=alert)



class ManageIngredientsDeleteAllergen(Webpage):

    @redirectNonManager
    def run(self):

        timestamp = self.TODAY      # For development purposes, we are using an artificial timestamp that does not change
        dateToday = datetime.date.fromtimestamp(timestamp)

        db = Database(self.HOSTNAME, self.USER, self.PASSWORD, self.DBNAME)

        # Get the data from the POST request
        allergenID = request.form['allergenID']
        ingredientID = request.form['ingredientID']
        
        if "deleteConfirm" in request.form:     # If the user has confirmed their choice to delete the allergen
            
            deleteQuery = """
                DELETE FROM ingredient_allergens
                WHERE ingredientID = %s
                AND allergenID = %s
            """
            deleteQueryParams = (ingredientID, allergenID)
            db.executeQuery(deleteQuery, deleteQueryParams)     # Delete the allergen from the database

            return redirect(url_for("manageIngredients")) # Redirect the user to the manage ingredients page

        # If the user hasn't confirmed their choice yet
        # Get the rest of the data from the POST request
        ingredientName = request.form['ingredientName']
        allergenName = request.form['allergenName']

        return render_template("manager/manageIngredientsDeleteAllergen.html", date=dateToday, ingredientName=ingredientName, ingredientID=ingredientID, allergenName=allergenName, allergenID=allergenID)



class ManageIngredientsAddAllergen(Webpage):

    @redirectNonManager
    def run(self):

        timestamp = self.TODAY      # For development purposes, we are using an artificial timestamp that does not change
        dateToday = datetime.date.fromtimestamp(timestamp)

        db = Database(self.HOSTNAME, self.USER, self.PASSWORD, self.DBNAME)
        alert = None

        ingredientID = request.form['ingredientID']     # Get the ingredient ID for the selected ingredient   
        ingredientName = request.form['ingredientName']     # Get the ingredient name

        if "add" in request.form:   # If the user has confirmed their choice to add the allergen

            if "allergenID" in request.form:    # If the user has chosen an allergen to add

                allergenID = request.form['allergenID']     # Get the allergen ID
                
                insertQuery = """
                    INSERT INTO ingredient_allergens
                    VALUES (%s, %s)
                """
                insertQueryParams = (ingredientID, allergenID)
                db.executeQuery(insertQuery, insertQueryParams)     # Add the allergen to the database
    
                return redirect(url_for("manageIngredients"))   # Redirect the user to the manage ingredients page

            alert = "The field is required"
        
        # If the user has not chosen an allergen
        allergensQuery = """
            SELECT *
            FROM allergens
            WHERE allergenID NOT IN (
                SELECT allergenID
                FROM ingredient_allergens
                WHERE ingredientID = %s)
            ORDER BY name
        """
        allergensQueryParams = (ingredientID)
        allergensData = db.executeQuery(allergensQuery, allergensQueryParams)     # Get the data about the allergens

        return render_template("manager/manageIngredientsAddAllergen.html", date=dateToday, ingredientName=ingredientName, ingredientID=ingredientID, allergensData=allergensData, alert=alert)



class ManageIngredientsDelete(Webpage):
    
    @redirectNonManager   # Redirects the user if they are not logged in as a manager
    def run(self):

        timestamp = self.TODAY      # For development purposes, we are using an artificial timestamp that does not change
        dateToday = datetime.date.fromtimestamp(timestamp)

        db = Database(self.HOSTNAME, self.USER, self.PASSWORD, self.DBNAME)

        # Get the data from the POST request        
        ingredientID = request.form['ingredientID']
        ingredientName = request.form['ingredientName']

        if "deleteConfirm" in request.form:     # If the user has confirmed their choice to delete an ingredient

            deleteQueryParams = (ingredientID)
            deleteQuery1 = """
                DELETE FROM ingredients
                WHERE ingredientID = %s
            """
            deleteQuery2 = """
                DELETE FROM option_ingredients
                WHERE ingredientID = %s
            """
            deleteQuery3 = """
                DELETE FROM ingredient_allergens
                WHERE ingredientID = %s
            """

            db.executeQuery(deleteQuery3, deleteQueryParams)    # Delete the ingredient from the ingredient allergens table
            db.executeQuery(deleteQuery2, deleteQueryParams)    # Delete the ingredient from the option ingredients table
            db.executeQuery(deleteQuery1, deleteQueryParams)    # Finally, delete the ingredient from the ingredients table
            # The record containing the primary key must be deleted last

            return redirect(url_for('manageIngredients'))   # Redirect the user to the manage ingredients page

        # If the user has not yet confirmed their choice to delete the ingredient
        optionsQuery = """
            SELECT COUNT(*) AS count
            FROM option_ingredients
            WHERE ingredientID = %s
        """
        optionsQueryParams = (ingredientID)
        optionsCount = db.executeQuery(optionsQuery, optionsQueryParams)[0]['count'] # Get the number of options that contain the ingredient

        return render_template("manager/manageIngredientsDelete.html", date=dateToday, count=optionsCount, ingredientID=ingredientID, name=ingredientName)



class ViewReports(Webpage):
    
    @redirectNonManager   # Redirects the user if they are not logged in as a manager
    def run(self):

        timestamp = self.TODAY      # For development purposes, we are using an artificial timestamp that does not change
        dateToday = datetime.date.fromtimestamp(timestamp)

        db = Database(self.HOSTNAME, self.USER, self.PASSWORD, self.DBNAME)

        if "reportType" not in session:     # If no session variable exists called report type
            session["reportType"] = "option"    # Initialise it by setting it to option

        if request.method == "POST" and "reportType" in request.form:   # If the user wants to change the report type
            session["reportType"] = request.form["reportType"]  # Change the report type

        startDate = timestamp
        endDate = startDate + 14*self.SECONDS_IN_DAY    # Because students can place orders two weeks in advance, the cafeteria staff can see orders that have been placed two weeks in advance

        reportType = session["reportType"]

        if reportType == "option":   # If we are doing an option report

            quantitiesQuery = """
                SELECT options.name, days.timestamp, COUNT(*) as quantity
                FROM options, orders, days
                WHERE options.optionID = orders.optionID
                AND days.dayID = orders.dayID
                AND days.timestamp >= %s
                GROUP BY options.optionID, days.timestamp
                ORDER BY options.name
            """
            quantitiesQueryParams = (timestamp)
            quantitiesData = db.executeQuery(quantitiesQuery, quantitiesQueryParams)    # Gets the quantity of each option that has been ordered on each day
            
        else:   # If we are doing an ingredient report

            ingredientsQuery = """
                SELECT ingredients.name, days.timestamp, SUM(option_ingredients.quantity) as quantity
                FROM ingredients, option_ingredients, orders, days
                WHERE ingredients.ingredientID = option_ingredients.ingredientID
                AND option_ingredients.optionID = orders.optionID
                AND days.dayID = orders.dayID
                AND days.timestamp >= %s
                GROUP BY ingredients.ingredientID, days.timestamp
                ORDER BY ingredients.name

            """
            ingredientsQueryParams = (timestamp)
            quantitiesData = db.executeQuery(ingredientsQuery, ingredientsQueryParams)

        return render_template("manager/viewReports.html", date=dateToday, dateclass=datetime.date, startDate=timestamp, endDate=endDate, reportType=reportType, data=quantitiesData)



class ViewReportsOptions(Webpage):
    
    @redirectNonManager   # Redirects the user if they are not logged in as a manager
    def run(self):

        timestamp = self.TODAY      # For development purposes, we are using an artificial timestamp that does not change
        dateToday = datetime.date.fromtimestamp(timestamp)

        db = Database(self.HOSTNAME, self.USER, self.PASSWORD, self.DBNAME)

        if 'dateFor' in request.form:   # If we have a date to view the order reports for
            dateFor = int(request.form['dateFor'])

            queryParams = (dateFor) # Both queries use the same parameters

            optionsQuery = """
                SELECT options.name, options.optionID
                FROM options, menu_options, days
                WHERE options.optionID = menu_options.optionID
                AND days.dayID = menu_options.dayID
                AND days.timestamp = %s
                ORDER BY options.name
            """

            ordersQuery = """
                SELECT students.firstname, students.lastname, students.tutorgroup, orders.optionID
                FROM students, orders, days
                WHERE students.studentID = orders.studentID
                AND days.dayID = orders.dayID
                AND days.timestamp = %s
            """

            optionsData = db.executeQuery(optionsQuery, queryParams) # Get the options that are available on this day
            ordersData = db.executeQuery(ordersQuery, queryParams) # Get the orders that have been placed for this day

            quantities = {}     
            for option in optionsData:  # For each option
                count = 0   # Couns stores the quantity of this option needed
                for order in ordersData:    # For each order
                    if order['optionID'] == option['optionID']: # If the option IDs of the option and order match
                        count += 1      # Increment count by 1
                quantities[option['optionID']] = count  # Set the quantity of the current option to the count


            dateForObj = datetime.date.fromtimestamp(dateFor)   # Create a date object for dateFor

            return render_template("manager/viewReportsOptions.html", date=dateToday, dateclass=datetime.date, dateFor=dateForObj, optionsData=optionsData, ordersData=ordersData, quantities=quantities)

        return redirect(url_for("managerHome"))



class OptionCreator(Webpage):

    @redirectNonManager
    def run(self):

        timestamp = self.TODAY      # For development purposes, we are using an artificial timestamp that does not change
        dateToday = datetime.date.fromtimestamp(timestamp)

        db = Database(self.HOSTNAME, self.USER, self.PASSWORD, self.DBNAME)
        alert = None

        ingredientsQuery = """
            SELECT *
            FROM ingredients
            ORDER BY name
        """
        ingredientsData = db.executeQuery(ingredientsQuery)     # Gets the list of all ingredients
        
        if request.method == "POST":    # If the user has submitted their choices for the quantities of meals

            if "addConfirm" in request.form:    # If the user has confirmed their choice to add their choice to the database

                if request.form.get('usePrice'):    # If the user has chosen to use a price other than the calculated price
                    price = request.form['priceOverride']   # The overridden price
                else:
                    price = request.form['price']   # The calculated price

                name = request.form['name']

                if price and name:
    
                    addOptionQuery = """
                        INSERT INTO options
                        VALUES (default, %s, %s)
                    """
                    addOptionQueryParams = (name, price)
                    db.executeQuery(addOptionQuery, addOptionQueryParams, close=False)  # Add the option to the database
    
                    getIDQuery = "SELECT LAST_INSERT_ID() AS id"
                    optionID = db.executeQuery(getIDQuery)[0]['id']     # Get the primary key of the last record inserted
    
                    for ingredient in ingredientsData:  # For each ingredient 
                        if str(ingredient['ingredientID']) in request.form:     # If the ingredient is in the new option
                            ingredientID = ingredient['ingredientID']
                            if request.form[str(ingredientID)] != "":
                                quantity = int(request.form[str(ingredientID)])   # Get the quantity of the ingredient needed
                            else:
                                quantity = 0
    
                            addIngredientQuery = """
                                INSERT INTO option_ingredients
                                VALUES (%s, %s, %s)
                            """
                            addIngredientQueryParams = (optionID, ingredientID, quantity)
                            db.executeQuery(addIngredientQuery, addIngredientQueryParams)   # Adds the ingredient to the option
    
                    return redirect(url_for("optionCreator"))   # Redirects the user to the option creator page

                elif not name:
                    alert = "A name is required"
                elif not price:
                    alert = "An alternative price is required if one is to be used instead of the recommended price"

            # If the user has chosen ingredients, but has not confirmed their choice to add the option to the database
            ingredients = {}
            cost = 0

            for ingredient in ingredientsData:  # For each ingredient
                if str(ingredient['ingredientID']) in request.form:     # If the ingredient is in the option that we have created
                    if request.form[str(ingredient['ingredientID'])] != "":
                        quantity = int(request.form[str(ingredient['ingredientID'])])   # Get the quantity of the ingredient
                    else:
                        quantity = 0
                    if quantity > 0:    # If the quantity is greater than zero, then we include the ingredient
                        ingredientCost = quantity * float(ingredient['pricePerKG']) / 1000  # Calculate the cost of the ingredient in the meal
                        ingredientCostDisplay = "{:.2f}".format(ingredientCost)     # Turn the cost into a string to display on the webpage
                        ingredients[ingredient['ingredientID']] = {'quantity':quantity, 'name':ingredient['name'], 'cost':ingredientCostDisplay} # Adds the data for the ingredient to the ingredients dictionary for the ingredientID
                        cost += ingredientCost  # Add the cost of that ingredient to the cost of the option

            sellingPrice = cost * 1.5   # Multiplies our cost by 1.5 for a price markup of 50%

            costDisplay = "{:.2f}".format(cost)     # Format the cost for display
            priceDisplay = "{:.2f}".format(sellingPrice)    # Format the price for display

            return render_template("manager/optionCreatorPreview.html", date=dateToday, cost=costDisplay, price=priceDisplay, ingredientsData=ingredients, alert=alert)

        return render_template("manager/optionCreator.html", date=dateToday, ingredientsData=ingredientsData)



class AddWeatherData(Webpage):

    @redirectNonManager
    def run(self):

        timestamp = self.TODAY     # For development purposes, we are using an artificial timestamp that does not change
        dateToday = datetime.date.fromtimestamp(timestamp)

        db = Database(self.HOSTNAME, self.USER, self.PASSWORD, self.DBNAME)
        alert = None

        if request.method == "POST":    # If the user submitted the new weather data in the POST request
            # Get the data from the POST request
            dateTS = request.form['date']
            temp = request.form['temp']

            if temp != "":

                checkExistsQuery = """
                    SELECT COUNT(*) AS count
                    FROM days
                    WHERE timestamp = %s
                """
                checkExistsQueryParams = (dateTS)
                if db.executeQuery(checkExistsQuery, checkExistsQueryParams) == 0:      # If the day doesn't exist yet

                    insertQuery = """
                        INSERT INTO days
                        VALUES (default, %s, %s)
                    """
                    insertQueryParams = (dateTS, temp)
                    db.executeQuery(insertQuery, insertQueryParams)     # Add the weather data to the database

                else:   # If the day already exists

                    updateQuery = """
                        UPDATE days
                        SET temperature = %s
                        WHERE timestamp = %s
                    """
                    updateQueryParams = (temp, dateTS)
                    db.executeQuery(updateQuery, updateQueryParams)

                return redirect(url_for("managerHome"))     # redirect the user to the manager home page

            alert = "The field is required"

        datesQuery = """
            SELECT COUNT(*) AS count
            FROM days
            WHERE temperature IS NOT NULL
        """
        if db.executeQuery(datesQuery)[0]['count'] > 0:     # If there are days that don't have weather data yet

            maxDateQuery = """
                SELECT MAX(timestamp) AS max
                FROM days
                WHERE temperature IS NOT NULL
            """
            maxDate = db.executeQuery(maxDateQuery)[0]['max']   # Get the most recent date that has weather data for it

        else:   # If all of the days have weather data then we need a new day with no weather data

            maxDateQuery = """
                SELECT MAX(timestamp) AS max
                FROM days
            """
            maxDate = self.SECONDS_IN_DAY + db.executeQuery(maxDateQuery)[0]['max']

        repeat = True
        while repeat:   # Iterates until we reach a new day that is a weekday
            maxDate += self.SECONDS_IN_DAY
            if datetime.date.fromtimestamp(maxDate).strftime("%a") not in ("Sat", "Sun"):
                repeat = False

        # If the date hasn't happened yet, don't let the user set weather data because they won't know what it is yet
        if maxDate > timestamp:
            return render_template("manager/addWeatherDataBlocked.html", date=dateToday, dateclass=datetime.date, weatherTS=maxDate)

        # If it has happened, then they are free to set it as they wish
        return render_template("manager/addWeatherData.html", date=dateToday, dateclass=datetime.date, weatherTS=maxDate, alert=alert)



class PredictOrders(Webpage):
    
    @redirectNonManager   # Redirects the user if they are not logged in as a manager
    def run(self):

        timestamp = self.TODAY     # For development purposes, we are using an artificial timestamp that does not change
        dateToday = datetime.date.fromtimestamp(timestamp)

        db = Database(self.HOSTNAME, self.USER, self.PASSWORD, self.DBNAME)
        alert = None

        if request.method == "POST":    # If the user has submitted the data to predict for

            options = request.form.getlist("optionID")

            if request.form['temp'] != "" and len(options) > 0:

                temp = int(request.form['temp'])    # Get the temperature on the date to predict for

                options = request.form.getlist("optionID")
                optionsFormatted = [int(i) for i in options]    # We need to turn the contents of options into integers.

                pd = Predictor(timestamp, temp, optionsFormatted)
                pd.connectDB(self.HOSTNAME, self.USER, self.PASSWORD, self.DBNAME)  # Connect the predictor to the database
                orders = pd.predict()   # Predict the orders

                optionsQuery = """
                    SELECT name, optionID
                    FROM options
                """
                optionsData = db.executeQuery(optionsQuery)     # Get a list of all options

                menuData = []
                for option in optionsData:  # For each option that is available
                    for optionID, quantity in orders.iteritems():   # For the option ID and predicted quantity of each option in the menu
                        if optionID == option['optionID']:      # If the option IDs match
                            menuData.append({'optionID':optionID, 'name':option['name'], 'quantity':int(round(quantity))})  # Add to menu data a dictionary containing data about the option

                return render_template("manager/predictOrdersDisplay.html", date=dateToday, menuData=menuData)

            alert = "All fields are required"

        optionsQuery = """
            SELECT *
            FROM options
            ORDER BY name
        """
        optionsData = db.executeQuery(optionsQuery)     # Gets a list of all options

        return render_template("manager/predictOrders.html", date=dateToday, optionsData=optionsData, alert=alert)
