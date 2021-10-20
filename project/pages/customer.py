# Part of the Python Standard Library
import time
import datetime

# Created by third-parties
from flask import render_template, request, redirect, url_for, session

# Created by me
from database import Database
from pages.webpage import Webpage
from tools import redirectNonCustomer



class CustomerHome(Webpage):
    
    @redirectNonCustomer   # Redirects the user if they are not logged in as a customer
    def run(self):

        if "secondWeek" not in session: # Sets secondWeek to its original value if it isn't set
            session["secondWeek"] = False   # We need secondWeek to be a session variable so that it is kept when the user navigates to different pages

        timestamp = self.TODAY      # For development purposes, we are using an artificial timestamp that does not change
        tsToday = timestamp - (timestamp%self.SECONDS_IN_DAY)  # We don't want to include the time, we only want the day

        if request.method == "POST" and "changeWeek" in request.form: # If the user wants to change which week they are viewing
            session["secondWeek"] = not session["secondWeek"]

        if session["secondWeek"]:   # If the user is currently viewing the second week
            tsCurrent = tsToday + self.SECONDS_IN_DAY*7
        else:
            tsCurrent = tsToday

        dateToday = datetime.date.fromtimestamp(tsToday)
        dateCurrent = datetime.date.fromtimestamp(tsCurrent)

        # Once we reach Saturday, the next week is displayed
        tableDatesDict = {
            'Sat':self.SECONDS_IN_DAY*2,
            'Sun':self.SECONDS_IN_DAY,
            'Mon':0,
            'Tue':-self.SECONDS_IN_DAY,
            'Wed':-self.SECONDS_IN_DAY*2,
            'Thu':-self.SECONDS_IN_DAY*3,
            'Fri':-self.SECONDS_IN_DAY*4,
        } 

        startOfWeek = tsCurrent + tableDatesDict[dateCurrent.strftime("%a")]
        endOfWeek = startOfWeek + 5*self.SECONDS_IN_DAY    # Includes the 1st second of Saturday, so we use < when comparing

        db = Database(self.HOSTNAME, self.USER, self.PASSWORD, self.DBNAME)

        tableQuery = """
            SELECT options.name, days.timestamp, orders.orderID
            FROM orders, options, days
            WHERE orders.optionID = options.optionID
            AND orders.dayID = days.dayID
            AND orders.studentID = %s
            AND days.timestamp >= %s
            AND days.timestamp < %s
        """
        tableQueryParams = (session["userID"], startOfWeek, endOfWeek)
        tabledata = db.executeQuery(tableQuery, tableQueryParams)     # Executes the first SQL query
        studentQuery = """
            SELECT firstname, lastname, balance
            FROM students
            WHERE studentID = %s
        """
        studentQueryParams = (session["userID"])
        studentdata = db.executeQuery(studentQuery, studentQueryParams)[0]  # Executes the second SQL query, and takes the only record
        # We also need to pass in the date class to have access to it in our template
        return render_template("customer/customerHome.html", tabledata=tabledata, studentdata=studentdata, date=dateToday, tsToday=tsToday, start=startOfWeek,
            dateclass=datetime.date, secondWeek=session["secondWeek"])



class DeleteOrder(Webpage):
    
    @redirectNonCustomer   # Redirects the user if they are not logged in as a customer
    def run(self):

        if "orderConfirm" in request.form:     # If the user confirmed their choice in the POST request
            orderID = request.form["orderID"]
            oldBalance = request.form["studentBalance"]
            price = request.form["optionPrice"]

            newBalance = float(oldBalance) + float(price)

            db = Database(self.HOSTNAME, self.USER, self.PASSWORD, self.DBNAME)

            studentQuery = """
                UPDATE students
                SET balance = %s
                WHERE studentID = %s
            """
            studentQueryParams = (newBalance, session["userID"])
            db.executeQuery(studentQuery, studentQueryParams)

            deleteQuery = """
                DELETE FROM orders
                WHERE orderID = %s
            """
            deleteQueryParams = (orderID)
            db.executeQuery(deleteQuery, deleteQueryParams)

            return redirect(url_for("customerHome"))

        if "orderID" in request.form:   # If the orderID was sent in the POST request
            orderID = request.form["orderID"]

            db = Database(self.HOSTNAME, self.USER, self.PASSWORD, self.DBNAME)

            getInfoQuery = """
                SELECT students.balance, options.price, options.name, days.timestamp
                FROM students, options, orders, days
                WHERE students.studentID = orders.studentID
                AND options.optionID = orders.optionID 
                AND days.dayID = orders.dayID
                AND orders.orderID = %s
            """
            getInfoQueryParams = (orderID)
            data = db.executeQuery(getInfoQuery, getInfoQueryParams)[0]    # There will only be one record returned

            return render_template("customer/deleteOrder.html", orderID=orderID, data=data, dateclass=datetime.date)
        # If the user somehow reached this page through a POST request without submitting the correct data
        return redirect(url_for("customerHome")) 



class AddOrder(Webpage):
    
    @redirectNonCustomer   # Redirects the user if they are not logged in as a customer
    def run(self):

        alert = None    # We may need to set an alert later

        if "addConfirm" in request.form:  # If true, then the user has already selected the meal that they want to order
            optionID = request.form["optionID"]
            oldBalance = request.form["studentBalance"]
            dateTS = request.form["dateFor"]

            db = Database(self.HOSTNAME, self.USER, self.PASSWORD, self.DBNAME)

            checkExistsQuery = """
                SELECT 1
                FROM days, menu_options
                WHERE days.dayID = menu_options.dayID
                AND menu_options.optionID = %s
                AND days.timestamp = %s
            """
            checkExistsQueryParams = (optionID, dateTS)
            if db.executeQuery(checkExistsQuery, checkExistsQueryParams):   # If the option still exists in the menu for the relevant date

                priceQuery = """
                    SELECT price
                    FROM options
                    WHERE optionID = %s
                """
                priceQueryParams = (optionID)
                price = db.executeQuery(priceQuery, priceQueryParams)[0]["price"]   # The 'price' field of the first and only record

                newBalance = float(oldBalance) - float(price)

                studentQuery = """
                    UPDATE students
                    SET balance = %s
                    WHERE studentID = %s
                """
                studentQueryParams = (newBalance, session["userID"])
                db.executeQuery(studentQuery, studentQueryParams)

                dayQuery = """
                    SELECT dayID
                    FROM days
                    WHERE timestamp = %s
                """
                dayQueryParams = (dateTS)
                dayID = db.executeQuery(dayQuery, dayQueryParams)[0]["dayID"]

                orderQuery = """
                    INSERT INTO orders
                    VALUES (default, %s, %s, %s)    
                """
                orderQueryParams = (session['userID'], optionID, dayID)
                db.executeQuery(orderQuery, orderQueryParams)      # Adds the user's order to the database

                return redirect(url_for("customerHome"))
            
            else:

                alert = "The menu was changed before your order could be processed"


        if "optionID" in request.form:  # If true, then the user has already selected the meal that they want to order
            optionID = request.form["optionID"]
            balance = request.form["studentBalance"]
            dateTS = int(request.form["dateFor"])

            db = Database(self.HOSTNAME, self.USER, self.PASSWORD, self.DBNAME)

            optionQuery = """
                SELECT name, price, optionID
                FROM options
                WHERE optionID = %s
            """
            optionQueryParams = (optionID)
            optionData = db.executeQuery(optionQuery, optionQueryParams)[0]

            if float(optionData["price"]) < float(balance): # If the user can afford the option

                return render_template("customer/addConfirm.html", optionData=optionData, balance=balance, dateclass=datetime.date, date=dateTS)

            alert = "Your balance is too low to order this."

        if "submitted" in request.form and "optionID" not in request.form:  # If the user has clicked the submit button, but has not selected an option
            alert = "Please select an option"

        if "dateFor" in request.form:    # If the user hasn't chosen a meal option, or their meal option was not valid
            dateTS = int(request.form["dateFor"])

            db = Database(self.HOSTNAME, self.USER, self.PASSWORD, self.DBNAME)

            optionsQuery = """
                SELECT options.name, options.price, options.optionID
                FROM days, menu_options, options
                WHERE days.dayID = menu_options.dayID
                AND options.optionID = menu_options.optionID
                AND days.timestamp = %s
                ORDER BY name
            """
            optionsQueryParams = (dateTS)
            data = db.executeQuery(optionsQuery, optionsQueryParams)

            balanceQuery = """
                SELECT balance
                FROM students
                WHERE studentID = %s
            """
            balanceQueryParams = (session["userID"])
            balance = db.executeQuery(balanceQuery, balanceQueryParams)[0]["balance"]

            studentAllergensQuery = """
                SELECT allergens.allergenID
                FROM allergens, student_allergens
                WHERE allergens.allergenID = student_allergens.allergenID
                AND student_allergens.studentID = %s
            """
            studentAllergensQueryParams = (session["userID"])
            studentAllergens = db.executeQuery(studentAllergensQuery, studentAllergensQueryParams)

            optionAllergensQuery = """
                SELECT allergens.allergenID, allergens.name, option_ingredients.optionID
                FROM allergens, ingredient_allergens, option_ingredients, menu_options, days
                WHERE allergens.allergenID = ingredient_allergens.allergenID
                AND ingredient_allergens.ingredientID = option_ingredients.ingredientID
                AND option_ingredients.optionID = menu_options.optionID
                AND days.dayID = menu_options.dayID
                AND days.timestamp = %s
            """
            optionAllergensQueryParams = (dateTS)
            optionAllergens = db.executeQuery(optionAllergensQuery, optionAllergensQueryParams)

            return render_template("customer/addOrder.html", dateFor=dateTS, balance=balance, data=data, dateclass=datetime.date, alert=alert, studentAllergens=studentAllergens, optionAllergens=optionAllergens)

        # If the user somehow reached this page through a POST request without submitting the correct data
        return redirect(url_for("customerHome"))    



class ChangeOrder(Webpage):
    
    @redirectNonCustomer   # Redirects the user if they are not logged in as a customer
    def run(self):

        alert = None    # We may need to set an alert later

        if "orderConfirm" in request.form:  # If true, then the user has confirmed that they want this choice
            currOrderID = request.form["currOrderID"]
            optionID = request.form["optionID"]
            balance = float(request.form["studentBalance"])
            priceDiff = float(request.form["priceDiff"])
            dateTS = int(request.form["dateFor"])

            db = Database(self.HOSTNAME, self.USER, self.PASSWORD, self.DBNAME)

            checkExistsQuery = """
                SELECT 1
                FROM days, menu_options
                WHERE days.dayID = menu_options.dayID
                AND menu_options.optionID = %s
                AND days.timestamp = %s
            """
            checkExistsQueryParams = (optionID, dateTS)
            if db.executeQuery(checkExistsQuery, checkExistsQueryParams):   # If the option still exists in the menu for the relevant date
                
                newBalance = balance + priceDiff

                studentQuery = """
                    UPDATE students
                    SET balance = %s
                    WHERE studentID = %s
                """
                studentQueryParams = (newBalance, session["userID"])
                db.executeQuery(studentQuery, studentQueryParams)   # Updates the student's balance

                deleteQuery = """
                    DELETE FROM orders
                    WHERE orderID = %s
                """
                deleteQueryParams = (currOrderID)
                db.executeQuery(deleteQuery, deleteQueryParams)   # Deletes the old order

                dayQuery = """
                    SELECT dayID
                    FROM days
                    WHERE timestamp = %s
                """
                dayQueryParams = (dateTS)
                dayID = db.executeQuery(dayQuery, dayQueryParams)[0]["dayID"]

                orderQuery = """
                    INSERT INTO orders
                    VALUES (default, %s, %s, %s)
                """
                orderQueryParams = (session["userID"], optionID, dayID)
                db.executeQuery(orderQuery, orderQueryParams)   # Creates the new order

                return redirect(url_for("customerHome"))


        if "optionID" in request.form:  # If true, then the user has already selected the meal that they want to order
            currOrderID = request.form["currentOrderID"]
            optionID = request.form["optionID"]
            balance = request.form["studentBalance"]
            dateTS = int(request.form["dateFor"])

            db = Database(self.HOSTNAME, self.USER, self.PASSWORD, self.DBNAME)

            optionQuery = """
                SELECT name, price, optionID
                FROM options
                WHERE optionID = %s
            """
            optionQueryParams = (optionID)
            optionData = db.executeQuery(optionQuery, optionQueryParams)[0]

            currentOrderQuery = """
                SELECT options.name, options.price, orders.orderID
                FROM options, orders
                WHERE options.optionID = orders.optionID
                AND orders.orderID = %s
            """
            currentOrderQueryParams = (currOrderID)
            currOrderData = db.executeQuery(currentOrderQuery, currentOrderQueryParams)[0]

            if float(optionData["price"]) - float(currOrderData["price"]) < float(balance): # If the user can afford the option

                return render_template("customer/changeConfirm.html", optionData=optionData, currOrderData=currOrderData, balance=balance, dateclass=datetime.date, date=dateTS)

            alert = "Your balance is too low to change your order to this."

        if "currentOrderID" in request.form and "optionID" not in request.form:  # If the user has clicked submit without selecting an option
            alert = "Please select an option"

        if "dateFor" in request.form:    # If the user hasn't chosen a meal option, or their meal option was not valid
            dateTS = int(request.form["dateFor"])
            print dateTS

            db = Database(self.HOSTNAME, self.USER, self.PASSWORD, self.DBNAME)

            currentOrderQuery = """
                SELECT options.name, options.optionID, orders.orderID
                FROM orders, options, days
                WHERE options.optionID = orders.optionID
                AND days.dayID = orders.dayID
                AND orders.studentID = %s
                AND days.timestamp = %s
            """
            currentOrderQueryParams = (session["userID"], dateTS)
            currentOrderData = db.executeQuery(currentOrderQuery, currentOrderQueryParams)[0]

            menuQuery = """
                SELECT options.name, options.price, options.optionID
                FROM days, menu_options, options
                WHERE days.dayID = menu_options.dayID
                AND options.optionID = menu_options.optionID
                AND days.timestamp = %s
                AND options.optionID <> %s
                ORDER BY name
            """
            menuQueryParams = (dateTS, currentOrderData['optionID'])
            menuData = db.executeQuery(menuQuery, menuQueryParams)

            balanceQuery = """
                SELECT balance
                FROM students
                WHERE studentID = %s
            """
            balanceQueryParams = (session["userID"])
            balance = db.executeQuery(balanceQuery, balanceQueryParams)[0]["balance"]

            studentAllergensQuery = """
                SELECT allergens.allergenID
                FROM allergens, student_allergens
                WHERE allergens.allergenID = student_allergens.allergenID
                AND student_allergens.studentID = %s
            """
            studentAllergensQueryParams = (session["userID"])
            studentAllergens = db.executeQuery(studentAllergensQuery, studentAllergensQueryParams)

            optionAllergensQuery = """
                SELECT allergens.allergenID, allergens.name, option_ingredients.optionID
                FROM allergens, ingredient_allergens, option_ingredients, menu_options, days
                WHERE allergens.allergenID = ingredient_allergens.allergenID
                AND ingredient_allergens.ingredientID = option_ingredients.ingredientID
                AND option_ingredients.optionID = menu_options.optionID
                AND days.dayID = menu_options.dayID
                AND days.timestamp = %s
            """
            optionAllergensQueryParams = (dateTS)
            optionAllergens = db.executeQuery(optionAllergensQuery, optionAllergensQueryParams)


            return render_template("customer/changeOrder.html", dateFor=dateTS, balance=balance, menuData=menuData, currentOrderData=currentOrderData, dateclass=datetime.date, alert=alert, studentAllergens=studentAllergens, optionAllergens=optionAllergens)

        # If the user somehow reached this page through a POST request without submitting the correct data
        return redirect(url_for("customerHome"))    
