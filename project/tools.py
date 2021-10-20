# Part of the Python Standard Library
from functools import wraps

# Created by Third Parties
from flask import redirect, url_for, session

def redirectNonCustomer(webpageCode):   # Decorator function for any pages that require the user to be logged in as a customer
    @wraps(webpageCode) # Necessary because Flask cares what the decorated functions are called
    def wrapper(*args):  # Wrapper function for the decorator
        if "userID" not in session:     # If a user isn't logged in

            if "authCode" not in session:   # If a member of the kitchen staff isn't logged in
                return redirect(url_for("index"))   # Redirect them to index

            return redirect(url_for("managerHome"))  # Otherwise. redirect them to managerHome

        return webpageCode(*args) # Runs the code for the webpage if the user wasn't redirected
    return wrapper      # Returns the identifier for wrapper



def redirectNonManager(webpageCode):    # Decorator function for any pages that require the user to be logged in as a manager
    @wraps(webpageCode) # Necessary because Flask cares what the decorated functions are called
    def wrapper(*args):  # Wrapper function for the decorator
        if "authCode" not in session:   # If the user isn't logged in as a manager

            if "userID" not in session:     # If the user isn't logged in as a customer
                return redirect(url_for("index"))   # Redirect them to index

            return redirect(url_for("customerHome")) # Otherwise, redirect them to customerHome

        return webpageCode(*args)    # Runs the rest of the webpage code if the user wasn't redirected
    return wrapper      # Returns the function identifier for wrapper



def redirectLoggedIn(webpageCode):  # Decorator function for any pages that require the user to not be logged in
    @wraps(webpageCode) # Necessary because Flask cares what the decorated functions are called
    def wrapper(*args):  # Wrapper function for the decorator

        if "userID" in session:     # If a user is already logged in
            return redirect(url_for("customerHome"))   # Then we redirect them to customerHome

        if "authCode" in session:   # If a member of the kitchen staff is logged in
            return redirect(url_for("managerHome"))     # Then we redirect them to managerHome

        return webpageCode(*args)    # Runs the rest of the webpage code if the user wasn't redirected
    return wrapper      # Returns the function identifier for the wrapper



def clearSession():   # Clears all relevant session variables from the user's device, effectively logging them out

    if "userID" in session:     # Removes the userID session variable if it exists
        session.pop("userID", None)

    if "authCode" in session:   # Removes the authCode session variable if it exists
        session.pop("authCode", None)

    if "secondWeek" in session:     # Removes the secondWeek session variable if it exists
        session.pop("secondWeek", None)

    if "reportType" in session:     # Removes the reportType session variable if it exists
        session.pop("reportType", None)

    return redirect(url_for("index"))   # Redirects the user to index



def dictMergeSort(listToSort, key):     # Sorts a list of dictionaries by the value for a given key.
    if len(listToSort) == 0 or len(listToSort) == 1:
        listSorted = listToSort
    else:
        midpoint = len(listToSort)//2
        list1 = dictMergeSort(listToSort[:midpoint], key)    # Sorts the first half of the list
        list2 = dictMergeSort(listToSort[midpoint:], key)    # Sorts the second half of the list
        listSorted = mergeDictLists(list1, list2, key)    # Merges the two sorted halves of the list

    return listSorted



def mergeDictLists(list1, list2, key):  # Merges two sorted lists of dictionaries by the value for a given key
    listMerged = []
    while len(list1) > 0 and len(list2) > 0:
        if list1[0][key] < list2[0][key]:
            element = list1.pop(0)  # Gets the first element of the list while also removing it from the list
            listMerged.append(element)
        else:
            element = list2.pop(0)  # Gets the first element of the list while also removing it from the list
            listMerged.append(element)

    listMerged += list1 + list2     # It doesn't matter if we add an empty list to the list, so we don't need to check which list is not empty

    return listMerged



def findUpperLower(listToSearch, key):
    indices = {}
    if len(listToSearch) > 0:   # If the list contains at least 1 element
        previousValue = listToSearch[0][key]
        startIndex = 0
        for i in range(len(listToSearch)):
            if listToSearch[i][key] != previousValue:   # If we have reached the next value in the list
                indices[previousValue] = (startIndex, i)
                startIndex = i
                previousValue = listToSearch[i][key]
        indices[previousValue] = (startIndex, len(listToSearch))
    return indices