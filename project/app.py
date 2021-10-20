# Created by third-parties
from flask import Flask

# Created by me
from tools import clearSession
import pages.general as general
import pages.customer as customer
import pages.manager as manager


app = Flask(__name__)      # Creates the Flask object
app.config["SECRET_KEY"] = "dfb8c0a70337b414" # This random string allows us to store session variables securely


# Configure endpoints for all webpages in the application
@app.route("/")
def index():
    page = general.Index()
    return page.run()


@app.route("/login", methods=["GET", "POST"])
def login():
    page = general.Login()
    return page.run()


@app.route("/login-hidden", methods=["GET", "POST"])
def loginHidden():
    page = general.LoginHidden()
    return page.run()


@app.route("/home", methods=["GET", "POST"])
def customerHome():
    page = customer.CustomerHome()
    return page.run()


@app.route("/delete-order", methods=["POST"])
def deleteOrder():
    page = customer.DeleteOrder()
    return page.run()


@app.route("/add-order", methods=["POST"])
def addOrder():
    page = customer.AddOrder()
    return page.run()


@app.route("/change-order", methods=["POST"])
def changeOrder():
    page = customer.ChangeOrder()
    return page.run()


@app.route("/manager")
def managerHome():
    page = manager.ManagerHome()
    return page.run()


@app.route("/manage-menus")
def manageMenus():
    page = manager.ManageMenus()
    return page.run()


@app.route("/manage-menus/edit", methods=["POST"])
def manageMenusEdit():
    page = manager.ManageMenusEdit()
    return page.run()


@app.route("/manage-options")
def manageOptions():
    page = manager.ManageOptions()
    return page.run()


@app.route("/manage-options/add", methods=["GET", "POST"])
def manageOptionsAdd():
    page = manager.ManageOptionsAdd()
    return page.run()


@app.route("/manage-options/edit", methods=["POST"])
def manageOptionsEdit():
    page = manager.ManageOptionsEdit()
    return page.run()


@app.route("/manage-options/edit/edit-name", methods=["POST"])
def manageOptionsEditName():
    page = manager.ManageOptionsEditName()
    return page.run()


@app.route("/manage-options/edit/edit-price", methods=["POST"])
def manageOptionsEditPrice():
    page = manager.ManageOptionsEditPrice()
    return page.run()


@app.route("/manage-options/edit/add-ingredient", methods=["POST"])
def manageOptionsAddIngredient():
    page = manager.ManageOptionsAddIngredient()
    return page.run()


@app.route("/manage-options/edit/edit-ingredient", methods=["POST"])
def manageOptionsEditIngredient():
    page = manager.ManageOptionsEditIngredient()
    return page.run()


@app.route("/manage-options/edit/delete-ingredient", methods=["POST"])
def manageOptionsDeleteIngredient():
    page = manager.ManageOptionsDeleteIngredient()
    return page.run()


@app.route("/manage-options/delete", methods=["POST"])
def manageOptionsDelete():
    page = manager.ManageOptionsDelete()
    return page.run()


@app.route("/manage-ingredients")
def manageIngredients():
    page = manager.ManageIngredients()
    return page.run()


@app.route("/manage-ingredients/edit", methods=["POST"])
def manageIngredientsEdit():
    page = manager.ManageIngredientsEdit()
    return page.run()


@app.route("/manage-ingredients/edit/edit-name", methods=["POST"])
def manageIngredientsEditName():
    page = manager.ManageIngredientsEditName()
    return page.run()


@app.route("/manage-ingredients/edit/edit-priceperkg", methods=["POST"])
def manageIngredientsEditPPKG():
    page = manager.ManageIngredientsEditPPKG()
    return page.run()



@app.route("/manage-ingredients/edit/add-allergen", methods=["POST"])
def manageIngredientsAddAllergen():
    page = manager.ManageIngredientsAddAllergen()
    return page.run()


@app.route("/manage-ingredients/edit/delete-allergen", methods=["POST"])
def manageIngredientsDeleteAllergen():
    page = manager.ManageIngredientsDeleteAllergen()
    return page.run()


@app.route("/manage-ingredients/add", methods=["GET", "POST"])
def manageIngredientsAdd():
    page = manager.ManageIngredientsAdd()
    return page.run()


@app.route("/manage-ingredients/delete", methods=["POST"])
def manageIngredientsDelete():
    page = manager.ManageIngredientsDelete()
    return page.run()


@app.route("/view-reports", methods=["GET", "POST"])
def viewReports():
    page = manager.ViewReports()
    return page.run()


@app.route("/view-reports/details", methods=["POST"])
def viewReportsOptions():
    page = manager.ViewReportsOptions()
    return page.run()


@app.route("/option-creator", methods=["GET", "POST"])
def optionCreator():
    page = manager.OptionCreator()
    return page.run()


@app.route("/add-weather-data", methods=["GET", "POST"])
def addWeatherData():
    page = manager.AddWeatherData()
    return page.run()


@app.route("/predict-orders", methods=["GET", "POST"])
def predictOrders():
    page = manager.PredictOrders()
    return page.run()


@app.route("/logout")
def logout():
    return clearSession()



# Run the WSGI server
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
