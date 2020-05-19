#! python3
"""
Author: Joe DeFilippo
1.  Captures the current main page deals from slickdeals.net using BeautifulSoup
2.  Allows the user to maintain a persistent 'wishlist' of items/keywords to compare against the current deals
3.  The user can also perform custom queries against the current deals.
"""

import logging, bs4, requests, webbrowser, shelve
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - - %(levelname)s - %(message)s')


def setupWishlist():
    """
    Checks to see if the user already has a wishlist set up/saved on their filesystem.
    If yes, that wishlist is loaded, otherwise a new, blank wishlist is created as a set
    """
    try:
        shelfFile = shelve.open('wishlist')
        wishlist = set(shelfFile['wishlist'])
        shelfFile.close()
        logging.info('Shelf file opened.  Wishlist loaded.')
    except:
        wishlist = set()
        logging.info('Shelf file does not exist.  Wishlist is blank.')
    return wishlist

def getDeals():
    """
    Uses BeautifulSoup to get all anchor tags from slickdeals.net
    Any anchor that has a title is a deal
    The function returns a dictionary of deals with the title of the deals as the key, and the URL as the value
    """
    deals = {}
    res = requests.get('http://slickdeals.net')
    res.raise_for_status()
    slickSoup = bs4.BeautifulSoup(res.text, features='lxml')
    elems = slickSoup.find_all('a')

    for i in range(0, len(elems)):
        if elems[i].get('title') != None:
            if elems[i].get('title') not in deals.keys():
                slickDeal = elems[i].get('title')
                deals[slickDeal] = 'http://www.slickdeals.net' + elems[i].get('href')
    return deals

def outputDealsToHTML(deals, outFile):
    """
    Takes the dictionary containing deals and a file name and generates an HTML file which contains a numbered list
    of deals
    """
    sdealshtml = open(outFile, 'w')
    sdealshtml.write('<HTML>\n<HEAD>\n<TITLE>SlickDealer</TITLE>\n</HEAD>\n')
    sdealshtml.write('<BODY>\n<ol>\n')
    for k in deals.keys():
        if k is not '':
            sdealshtml.write('\t<li><a href = "' + deals[k] + '" target="_blank">' + k + '</a></li>\n\t<br>\n')

    sdealshtml.write('</ol>\n</BODY>\n</HTML>')
    sdealshtml.close()
    logging.info('HTML file ' + outFile + ' written and closed')

def displayMenu(menu, menuPath):
    """
    Prints a menu to the console (Ex main menu, wishlist maintenance menu, etc.)
    """
    print(menuPath)
    print('---------')
    for k in menu.keys():
        print(k + ' ' + menu[k])

def saveWishlistToShelf(shelf_file, wishlist):
    """
    Uses the shelve module to save the current wishlist to the user's local drive
    """
    shelfFile = shelve.open(shelf_file)
    shelfFile[shelf_file] = set(wishlist)
    shelfFile.close()
    logging.info('Wishlist saved to shelf.')

def scrubHTMLfromString(string_to_clean):
    """
    Removes HTML special character formatting from a string and returns the clean string
    """
    string_to_clean = string_to_clean.replace('&lpar;', '(')
    string_to_clean = string_to_clean.replace('&rpar;', ')')
    string_to_clean = string_to_clean.replace('&quot;', '\"')
    string_to_clean = string_to_clean.replace('&apos;', '\'')
    string_to_clean = string_to_clean.replace('&quest;', '?')
    string_to_clean = string_to_clean.replace('&num;', '#')
    string_to_clean = string_to_clean.replace('&excl;', '!')
    string_to_clean = string_to_clean.replace('&dollar;', '$')
    string_to_clean = string_to_clean.replace('&percnt;', '%')
    string_to_clean = string_to_clean.replace('&amp;', '&')
    string_to_clean = string_to_clean.replace('&colon;', ':')
    string_to_clean = string_to_clean.replace('&period;', '.')
    string_to_clean = string_to_clean.replace('&comma;', ',')
    string_to_clean = string_to_clean.replace('&commat;', '@')
    string_to_clean = string_to_clean.replace('&sol;', '/')

    return string_to_clean

def displayWishlist(wlist):
    """
    Prints the wishlist to the console
    """
    if len(wlist) > 0:
        print(wlist)
    else:
        print('Wishlist is empty')

deals = getDeals()
wishlist = setupWishlist()

main_menu = {'1.': 'View current deals in browser',
            '2.': 'Search Deals for Wishlist Items',
            '3.': 'Display My Wishlist',
            '4.': 'Wishlist Maintenance',
            '5.': 'Search Deals by Keyword',
            'Q.': 'Quit'}

wl_maintenance_menu = {'1.': 'Add item to Wishlist',
            '2.': 'Remove Item from Wishlist',
            '3.': 'Display My Wishlist',
            '4.': 'Back to Main Menu'}

outFile = 'slickdealer.html'
outputDealsToHTML(deals, outFile)

while True:
    displayMenu(main_menu, 'Slick Dealer - Main Menu')
    menuSelection = input('Enter your selection---> ').lower()
    if menuSelection == 'q': # quit the program
        print('Thanks for using Slick Dealer.  Goodbye!')
        quit()
    if menuSelection == '1': #show all current deals in browser
        print('Opening in default browser...')
        webbrowser.open(outFile)
    if menuSelection == '2': #search deals for wishlist items
        print('\n')
        for item in wishlist:
            for k in deals:
                if item in k.lower():
                    print('Wishlist item ' + item + ' found! --->' + scrubHTMLfromString(k) + ': ' + deals[k])
        print('\n')

    if menuSelection == '3':
        displayWishlist(wishlist)
    if menuSelection == '4':
        while True:
            displayMenu(wl_maintenance_menu, 'Wishlist Maintenance')
            wl_maint_sel = input('Enter your selection---> ').lower()
            if wl_maint_sel == '1':
                addMore = 'y'
                while addMore == 'y':
                    newItem = input('What keyword would you like to add to your wishlist?')
                    wishlist.add(newItem.lower())

                    displayWishlist(wishlist)
                    addMore = input('Add another item? (y/n)').lower()
                saveWishlistToShelf('wishlist', wishlist)
            if wl_maint_sel == '2':
                removeMore = 'y'
                while removeMore == 'y' and len(wishlist) > 0:
                    item_to_remove = input('What keyword would you like to remove from your wishlist?')
                    try:
                        wishlist.remove(item_to_remove)
                        displayWishlist(wishlist)
                        saveWishlistToShelf('wishlist', wishlist)
                    except:
                        print('Item not in wishlist')
                    removeMore = input('Remove another item? (y/n)').lower()
            if wl_maint_sel == '3':
                displayWishlist(wishlist)
            if wl_maint_sel == '4':
                break

    if menuSelection == '5':  # search keyword
        keep_searching = 'y'
        while keep_searching == 'y':
            keyword = input('Enter your keyword---> ').lower()
            if keyword in str(deals.keys()).lower():
                print('\n')
                for k in deals:
                    if keyword in k.lower():
                        print(scrubHTMLfromString(k) + ': ' + deals[k])
            else:
                print('No deals for the given keyword.')
            print('\n')
            keep_searching = input('Do you want to keep searching? (y/n)').lower()