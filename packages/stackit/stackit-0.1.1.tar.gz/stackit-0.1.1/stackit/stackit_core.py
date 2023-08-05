#!/usr/bin/env python
from __future__ import print_function
import sys
import stackexchange
from stackexchange import Sort
# A good testing URL: http://stackoverflow.com/questions/16800049/changepassword-test
# The approved answer ID: 16800090

import requests
import webbrowser
import subprocess
import argparse
import math
import bs4
import re

NUM_RESULTS = 5
API_KEY = "3GBT2vbKxgh*ati7EBzxGA(("
VERSION_NUM = "0.1.1"

# HTML to markdown parsing
# https://github.com/aaronsw/html2text
import html2text
h = html2text.HTML2Text()

user_api_key = API_KEY

so = stackexchange.Site(stackexchange.StackOverflow, app_key=user_api_key, impose_throttling=True)
so.be_inclusive()

def promptUser(prompt):
    response = raw_input(prompt)
    return response

def focusQuestion(questions, count):
    userInput = '0'
    #Looping while the user wants to see more input
    while(userInput != 'm'):
        userInput = promptUser("Press m for more, or a number to select: ")
        if(userInput == 'm'):
            break
        if(0 < int(userInput) and int(userInput) <= count):
            print("\n\n\n\n\n\n")
            printFullQuestion(questions[int(userInput)- 1])
            branchInput = '0'   #user deciding whether to branch to open browser, or to return to search
            while(branchInput != 'x'):
                branchInput = promptUser("Press b to launch browser, or x to return to search: ")
                if(branchInput == 'b'):
                    webbrowser.open(questions[int(userInput)-1].json['link'], new=0, autoraise=True)
            #User selects x to return to search
            if(branchInput == 'x'):
                print("\n\n\n\n\n\n\n\n\n\n\n\n")
                #Ranging over the 5 questions including the user's choice
                for j in range(5*int((int(userInput)-1)/5), 5*int((int(userInput)-1)/5)+5):
                    printQuestion(questions[j], j+1)
                continue   #exit the inner while loop

def searchTerm(term, tags):
    print('Searching for: %s... \n' % term,)
    print('Tags: ',)
    for tag in tags:
        print(tag + " ",)
    print("\n")
    questions = so.search_advanced(q = term, tagged = tags, sort = Sort.Votes)
    j = 0
    count = 0
    questionLogs = list()
    while(j < len(questions)):
        question = questions[j]
        if 'accepted_answer_id' in question.json:
            count+=1
            printQuestion(question, count)
            questionLogs.append(question)
            if(count % NUM_RESULTS == 0):
                focusQuestion(questionLogs, count)
        j+=1

def printQuestion(question, count):
    #questionurl gives the url of the SO question
    #the answer is under id "answer-answerid", and text of answer is in class post-text
    questionurl = question.json['link']
    answerid = question.json['accepted_answer_id']
    # Pulls the html from the StackOverflow site, converts to Beautiful Soup
    response = requests.get(questionurl)
    soup = bs4.BeautifulSoup(response.text)
    # Prints the accepted answer div, concatonated "answer-" and answerid
    # Gets the p string -- do al answers follow this format, or do some have more info?
    print(pColor.BLUE + str(count) + "\n" + "Question: " + question.title + pColor.END + "\nAnswer: " + h.handle(soup.find("div", {"id": "answer-"+str(answerid)}).p.prettify()) + "\n")

def getTerm(parser):
    term = ""
    pArgs = parser.parse_args()
    if(pArgs.search):
        term += (pArgs.search + " ")
    if(pArgs.stderr):
        process = subprocess.Popen(pArgs.stderr, stderr=subprocess.PIPE)
        output = process.communicate()[1]
        term += (output.splitlines()[-1] + " ")
    return term

def getTags(parser):
    pArgs = parser.parse_args()
    tags = pArgs.tag.split()
    return tags


def printFullQuestion(question):
    questionurl = question.json['link']
    answerid = question.json['accepted_answer_id']
    response = requests.get(questionurl)
    soup = bs4.BeautifulSoup(response.text)
    # Focuses on the single div with the matching answerid--necessary b/c bs4 is quirky
    for answerdiv in soup.find_all('div', attrs={'id': 'answer-'+str(answerid)}):
        # Return printable text div--the contents of the answer
        # This isn't perfect; things like code indentation aren't pretty at all
        #print(answerdiv.find('div', attrs={'class': 'post-text'}))
        answertext = h.handle(answerdiv.find('div', attrs={'class': 'post-text'}).prettify())
    for cell in soup.find_all('td', attrs={'class': 'postcell'}):
        questiontext = h.handle(cell.find('div', attrs={'class': 'post-text'}).prettify())
    print(pColor.BLUE + "-------------------------QUESTION------------------------\n" + question.title + "\n" + questiontext 
        + pColor.END + "\n\n-------------------------------ANSWER------------------------------------\n" + answertext)

def searchVerbose(term):
    questions = so.search_advanced(q = term, sort = Sort.Votes)
    question = questions[0]
    questionurl = question.json['link']
    answerid = question.json['accepted_answer_id']
    printFullQuestion(question)
    

def getParser():
    parser = argparse.ArgumentParser(description="Parses command-line arguments for StackIt")
    parser.add_argument("-s", "--search", metavar="QUERY", help="Searches StackOverflow for your query") 
    parser.add_argument("-e", "--stderr", metavar="EXECUTE", help="Runs an executable command (i.e. python script.py) and automatically inputs error message to StackOverflow")
    parser.add_argument("-t", "--tag", metavar="TAG1 TAG2", help="Searches StackOverflow for your tags")
    parser.add_argument("--verbose", help="displays full text of most relevant question and answer", action="store_true")
    parser.add_argument("--version", help="displays the version", action = "store_true")
    return parser

class pColor:
    # Want to eliminate these that won't be used!
    END =           '\033[0m'
    # Colors
    PURPLEBLUE =    '\033[34m'
    MISTGREY =      '\033[20m'
    PURPLE =        '\033[35m'
    CYAN =          '\033[36m'
    LIGHTGREY =     '\033[37m'
    DARKGREY =      '\033[90m'
    LIGHTRED =      '\033[91m'
    LIGHTGREEN =    '\033[92m'
    LIGHTBLUE =     '\033[94m'
    PINK =          '\033[95m'
    BLUE =          '\033[94m'
    GREEN =         '\033[92m'
    YELLOW =        '\033[93m'
    RED =           '\033[91m'
    # Formatting
    BOLD =          '\033[1m'
    UNDERLINE =     '\033[4m'
    REVERSE =       '\033[07m'
    STRIKETHROUGH = '\033[09m'
    INVISIBLE =     '\033[08m'
    INVISIBLE2 =    '\033[02m'


def main():
    parser = getParser()
    args = parser.parse_args()
    if not len(sys.argv) > 1:
        parser.print_help()
        return
    if(args.version):
        print("Version "+VERSION_NUM)
        return
    term = getTerm(parser)
    if(args.tag):
        tags = getTags(parser)
    else:
        tags = []
    if(parser.parse_args().verbose):
        searchVerbose(term)
    else:
        searchTerm(term, tags)

if __name__ == '__main__':
    main()
