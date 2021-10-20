# Part of the Python Standard Library
import math
import time

# Created by me
from database import Database
from tools import dictMergeSort, findUpperLower

class Predictor():
    def __init__(self, timestamp, temp, menu):
        """Constructor method for the Predictor class"""
        self.todayTS = timestamp    # Timestamp for the date to predict
        self.predictionTemp = temp    # Temperature for the date to predict
        self.predictionMenu = menu      # Menu for the date to predict
        self.students = []
        self.menus = []

    def connectDB(self, host, user, pw, dbname):
        """Creates a database object"""
        self.db = Database(host, user, pw, dbname)

    def getStudents(self):
        """Gets a list containing the IDs of all students in the database"""
        query = """
            SELECT studentID
            FROM students
        """
        data = self.db.executeQuery(query)  # Executes the database query
        return data

    def getOptions(self):
        """Gets a list containing all options that are available"""
        query = """
            SELECT optionID
            FROM options
        """
        data = self.db.executeQuery(query)  # Executes the database query
        return data

    def getOrders(self):
        """Gets a list containing all historic order records from the database"""
        query = """
            SELECT * 
            FROM orders, days
            WHERE orders.dayID = days.dayID
            AND days.timestamp < %s
        """
        params = (self.todayTS)
        data = self.db.executeQuery(query, params)  # Executes the database query
        return data

    def getDays(self):
        """Gets a list containing all historic menu records from the database"""
        query = """
            SELECT * 
            FROM days
            WHERE timestamp < %s
        """
        params = (self.todayTS)
        data = self.db.executeQuery(query, params)  # Executes the database query
        return data

    def getMenuOptions(self):
        """Gets a list containing each order in a menu for each day"""
        query = """
            SELECT *
            FROM menu_options
        """
        data = self.db.executeQuery(query)  # Executes the database query
        return data

    def createStudentObjects(self, students, orders):
        """Creates a student object for each student given"""
        ordersSorted = dictMergeSort(orders, "studentID")
        orderIndices = findUpperLower(ordersSorted, "studentID")
        for student in students:    # For each student record
            studentID = student['studentID']
            studentIndices = orderIndices[studentID]
            studentOrders = ordersSorted[studentIndices[0] : studentIndices[1]]
            studentObj = Student(studentID, studentOrders)  # Create a student object
            self.students.append(studentObj)    # Add the student object to our list of students


    def createMenuObjects(self, days, menuOptions):
        """Creates an object for each menu that exists"""
        for day in days:  # For each menu record
            dayID = day['dayID']
            dateFor = day['timestamp']
            options = []    # Create an empty list of options
            for option in menuOptions:  # For each menu option record
                if option['dayID'] == dayID:  # If the menu ID of the menu and menu option records match
                    options.append(option['optionID'])  # Then add it to our list of options
            menuObj = Menu(dayID, dateFor, options)    # Create a menu object
            self.menus.append(menuObj)  # Add the menu object to our list of menus

    def setStudentOptions(self, options):
        """Creates the option objects for each student"""
        for student in self.students:   # For each student in our list of students
            student.createOptionObjects(options)    # Create an option object for out student.

    def calcOptionPriorities(self, menu):
        """Calculates the option priorities of each student in our students list"""
        for student in self.students:   # For each student in our list of students
            student.calcOptionPriority(menu)    # Calculate that student's option priorities

    def calcOrderLikelihoods(self, menu):
        """Calculates the likelihood of each student in our students list ordering a meal"""
        for student in self.students:   # For each studentin our list of students
            student.calcOrderLikelihood(menu)   # Calculate the probability of that student placing an order

    def setWeather(self, days):
        """Sets the temperature value for each menu and order"""
        daysSorted = dictMergeSort(days, "timestamp")
        dayIndices = findUpperLower(daysSorted, "timestamp")
        daysDict = {}

        for key, value in dayIndices.iteritems():
            daysDict[key] = daysSorted[value[0]]['temperature']

        for menu in self.menus:     # For each menu in our list of menus
            menu.setTemp(daysDict[menu.getDateFor()])   # Set the temperature of that menu to the temperature of that day

        for student in self.students:   # For each student in our list of students
            for order in student.getOrders():    # For each order in the list of that student's orders
                order.setTemp(daysDict[order.getDateFor()])  # Set the temperature of that order to the temperature of that day

    def setImportances(self):
        """Sets the importances of each menu and each order that a student has placed based on the weather"""
        for student in self.students:   # for each student in our list of students
            for order in student.getOrders():    # For each order in that student's list of orders
                order.setImportance(self.predictionTemp)    # Calculate the importance of that order
        for menu in self.menus:     # For each menu in our list of menus
            menu.setImportance(self.predictionTemp)     # Calculate the importance of the options in that menu

    def calcExpectedQuantities(self):
        """Calculates the expected quantities of each option in the datatabse"""
        studentExpectedOrders = []  # Create an empty expected orders list
        for student in self.students:   # For each student in our students list
            studentExpectedOrders.append(student.calcExpectedOrders(self.predictionMenu))
            
        quantities = {}     # Create an empty quantities dictionary
        for optionID in self.predictionMenu:
            quantities[optionID] = 0    # Initialises our quantities dictionaru
        for student in studentExpectedOrders:   # For each student in our expected orders
            for option in student:  # For each option in that student
                quantities[option.getID()] += option.getPriorityScaled()      # Increment the total quantity of that option by the student's priority of that option

        return quantities   # Return the final quantities of each ingredient

    def predict(self):
        """Begins execution of the prediction algorithm"""

        # We start by getting all of the data we need from the database
        studentsRaw = self.getStudents()
        ordersRaw = self.getOrders()
        optionsRaw = self.getOptions()
        daysRaw = self.getDays()
        menuOptionsRaw = self.getMenuOptions()

        # We create the student objects and menu objects
        self.createStudentObjects(studentsRaw, ordersRaw)
        self.setStudentOptions(optionsRaw)
        self.createMenuObjects(daysRaw, menuOptionsRaw)

        self.setWeather(daysRaw)     # We set the weather for each order and menu to the weather on the date it was for
        self.setImportances()   # We set all of the importance values for each order and menu
        self.calcOptionPriorities(self.menus)   # We calculate the option priorities for each student
        self.calcOrderLikelihoods(self.menus)   # We calculate the likelihood of each student placing an order
        return self.calcExpectedQuantities()    # Finally, we calculate the expected quantities of each option on the menu
        



class Student():
    def __init__(self, studentID, orders):
        """Constructor method for the Student class"""
        self.id = studentID
        self.createOrderObjects(orders)     # Creates an order object for each order that the student has placed

    def createOrderObjects(self, orders):
        """Gives each student an order object for each order they have placed"""
        self.orders = []    # An empty list of orders
        for orderDict in orders:    # For each order that the student has placed
            orderObj = Order(orderDict['orderID'], orderDict['optionID'], orderDict['timestamp'])     # Create an order object
            self.orders.append(orderObj)    # Add that order object to our list of orders

    def createOptionObjects(self, options):
        """Gives each student an option object for each option"""
        self.options = []   # An empty list of options
        for optionDict in options:  # For each option in the database
            optionObj = Option(optionDict['optionID'])      # Create an option object
            self.options.append(optionObj)  # Add that option object to our list of options
        
    def calcOrderLikelihood(self, menus):
        """Calculates the likelihood of this student ordering something on any given day"""
        numOrders = len(self.orders) # The total number of orders placed by the student
        numMenus = len(menus)   # The total number of menus that the student could have ordered from
        if numMenus > 0:    # If we have more than zero menus, then a divide by zero error will not occur
            self.orderLikelihood = float(numOrders)/float(numMenus)     # The order likelihood is the probability of the student ordering on any given day
        else:   # If no historic order records or menu records are available, assume the student orders 50% of the time
            self.orderLikelihood = 0.5

    def calcOptionPriority(self, menus):
        """Calculates how the student prioritises each option"""
        for option in self.options:     # For each option

            optionID = option.getID()    # Initialise some variables
            orderCount = 0
            availableCount = 0
            
            for order in self.orders:   # For each option that the student has placed
                if order.getOption() == optionID:    # If it is an order for the option we are currently looking at
                    orderCount += order.getImportance()  # Add the importance of that order to the order count (0 < importance <= 1)

            for menu in menus:  # For each menu that the student could have ordered from
                if optionID in menu.getOptions():    # If the option we are looking at is in the menu
                    availableCount += menu.getImportance()

            if availableCount > 0:  # If the option was available more than zero times, then a divide by zero error will not occur
                priority = float(orderCount)/float(availableCount)  # The option priority is the probability of the option being ordered given that it was on the menu
            else:
                priority = 0.0  # If the option was never available in any menu, then assume that it has the lowest priority

            option.setPriority(priority)

    def calcExpectedOrders(self, menu):
        """Calculates the likelihood of the student ordering each item from the menu"""
        menuOptions = []    # Create an empty list of menu options
        totalPriorityShortlisted = 0    # Initialise our total priority shortlisted

        for option in self.options: # For each option that is available
            if option.getID() in menu:   # If the option is in the menu
                menuOptions.append(option)  # Add it to our list of menu options
                totalPriorityShortlisted += option.getPriority()     # Add the priority of our option to our total priority shortlisted

        if totalPriorityShortlisted == 0:    # If the user has not ordered anything on the menu before, then assume that they like everything equally.
            if len(menuOptions) > 0:    # If there are options in the menu
                priorityOverride = float(self.orderLikelihood)/len(menuOptions)
            else:
                priorityOverride = float(self.orderLikelihood)/0.5
            for option in menuOptions:
                option.setPriorityScaled(priorityOverride)

        else:   # The priorities for each option should add to give the student's order likelihood since they are probabilities
            priorityScalar = float(self.orderLikelihood)/totalPriorityShortlisted   # Find the scalar that we need to multiply all of our priorities by
            for option in menuOptions:  # For each option
                option.setPriorityScaled(priorityScalar * option.priority)  # Multiply the priority by the scalar so that all scaled priorities add to give the student's order likelihood

        return menuOptions

    def getOrders(self):
        """Gets the list of orders that the student has placed"""
        return self.orders



class Order():
    def __init__(self, orderID, optionID, dateFor):
        """Constructor method for the Order class"""
        self.id = orderID
        self.option = optionID
        self.dateFor = dateFor

    def setTemp(self, temp):
        """Sets temp to the temperature on the date that the menu is for"""
        self.temp = temp

    def setImportance(self, temp):  
        """Calculates the importance of the order by mapping the temperature to the height of a bell curve.
        The x-coordinate of the bell curve is the temperature and the y-value of the bell curve is the importance.
        The centre of the bell curve is the predicted temerature
        The importance fits in the range 0 < importance <= 1
        """
        difference = self.temp - temp
        exponent = -float(difference**2)/30     # The natural logarithm of the height of the bell curve at the given temperature value
        importance = math.exp(exponent)     # The immportance is the height of the bell curve at the given temperature value
        self.importance = importance

    def getOption(self):
        """Gets the option ID of the option that the order is for"""
        return self.option

    def getDateFor(self):
        """Gets the date that the order is for"""
        return self.dateFor

    def getImportance(self):
        """Gets the importance value for the order"""
        return self.importance



class Option():
    def __init__(self, optionID):
        """Construtor method for the Option class"""
        self.id = optionID

    def setPriority(self, priority):
        """Sets the priority of this order to the given value"""
        self.priority = priority

    def setPriorityScaled(self, priority):
        """Sets the scaled priority of this order to the given value"""
        self.priorityScaled = priority

    def getID(self):
        """Gets the option ID of the option"""
        return self.id

    def getPriority(self):
        """Gets the priority of the option"""
        return self.priority

    def getPriorityScaled(self):
        """Gets the scaled priority of the option"""
        return self.priorityScaled

    

class Menu():
    def __init__(self, menuID, dateFor, options):
        """Constructor method for the Menu class"""
        self.id = menuID
        self.dateFor = dateFor
        self.options = options

    def setTemp(self, temp):
        """Sets temp to the temperature on the date that the menu is for"""
        self.temp = temp

    def setImportance(self, temp):
        """Calculates the importance of the orders for this menu by mapping the temperature to the height of a bell curve at that x-coordinate"""
        difference = self.temp - temp
        exponent = -float(difference**2)/30     # The natural logarithm of the height of the bell curve
        importance = math.exp(exponent)     # The importance is the height of the bell curve at that point
        self.importance = importance

    def getDateFor(self):
        """Gets the date that the menu is for"""
        return self.dateFor

    def getOptions(self):
        """Gets a list of the option IDs of the options on the menu"""
        return self.options

    def getImportance(self):
        """Gets the importance of the menu"""
        return self.importance
