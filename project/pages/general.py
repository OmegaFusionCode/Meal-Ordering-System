# Created by third-parties
from flask import render_template, request, redirect, url_for, session

# Created by me
from database import Database
from pages.webpage import Webpage
from tools import redirectLoggedIn



class Index(Webpage):

    @redirectLoggedIn   # Redirects the user if they are already logged in
    def run(self):
        return render_template("general/main.html")



class Login(Webpage):
    
    @redirectLoggedIn   # Redirects the user if they are already logged in
    def run(self):
        
        alert = None    # We don't know if we will need an alert yet, but the variable needs to exist

        if request.method == "POST":    # If the user reached this page by submitting the form

            userID = request.form["userID"]
            password = request.form["password"]

            if userID and password:     # If the user completed both fields of the form

                db = Database(self.HOSTNAME, self.USER, self.PASSWORD, self.DBNAME)     # Create the database object

                query = """
                    SELECT 1
                    FROM students
                    WHERE studentID = %s
                    AND password = %s
                """
                params = (userID, password)

                if db.executeQuery(query, params):  # If the given user ID and password matched a student in the database
                    session["userID"] = userID      # Create a session variable so we know who has logged in
                    return redirect(url_for("customerHome"))    # Redirects the user to the customerHome page
                else:
                    alert = "Invalid network ID or password"    # We now need to set an alert
            else:
                alert = "All fields are required."

        return render_template("general/login.html", alert=alert)   # This is why the alert variable needs to exist



class LoginHidden(Webpage):

    @redirectLoggedIn   # Redirects the user if they are already logged in
    def run(self):

        alert = None    # We don't know if we will need an alert yet, but the variable needs to exist

        if request.method == "POST" and "authCode" in request.form:     # If the user entered the authorisation code
            authCode = request.form["authCode"]

            if authCode == "test":  # If the auth code matches the correct auth code
                session["authCode"] = authCode      # Create a session variable so we know we have logged in
                return redirect(url_for("managerHome"))    # Redirects the user to the customerHome page
            else:
                alert = "Invalid authorisation code"    # We now need to set an alert

        return render_template("general/loginHidden.html", alert=alert)   # This is why the alert variable needs to exist



