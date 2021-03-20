# name: Xuechi Zhao, Yueqi Wang
# CIS 41B final project : Udemy Courses Query System

import os
import requests
import base64
import json
import urllib.parse
import concurrent.futures
import time
import pandas as pd
import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

client_id = 'q4SKCJnxxpQ2qA0vGHL1CVRTCUrTLvqpUpj0Vvpl'
client_secret = 'G9hr2Dl5iWw7R5H0DXyic1fTxe4mwZZvDIuSSfICNudCQoyOOMxY6otlxW8KXUvhEDsQEiCycvoUAkjpW3o03fMABafFxayhc8zG0mwv9zauGcUBmjNAs9c8bVW3v70A'
auth_token = 'Basic ' + base64.b64encode("{}:{}".format(client_id, client_secret).encode()).decode('ascii')
headers = {'Authorization': auth_token}

UdemyColorDict = {"red": "#ec5252", "yellow": "#f5c252",
                  "blue": "#69c1d0", "dark purple":"#430d31", "purple": "#6e1952",
                  "orange": "#f68f30", "dark blue": "#19263a", "mombasa": "#645a52"}
"""
choice 1: courses summary chart : paid/free, levels, duration, features
"""


def plotSummaryChart():
    """get 4 charts to show course summary: price, level, features and duration"""
    getCourseList = requests.get(
        "https://www.udemy.com/api-2.0/courses/?category=Development&language=en&ordering=newest&ratings=4.5",
        headers=headers)
    # courselist is a json file with aggregation information
    courseList = getCourseList.json()
    aggregationsLabels = [item["id"] for item in courseList["aggregations"]]
    optionDictList = [optionDict for optionDict in courseList["aggregations"]]
    subplot_labels = ["price", "instructional_level", "features", "duration"]  # id
    i = 1
    figure = plt.figure(figsize=(12, 3))
    for label in subplot_labels:
        ind = aggregationsLabels.index(label)
        optionDict = optionDictList[ind]
        optionValueList = optionDict["options"]
        # print(optionValueList)
        df = pd.DataFrame(optionValueList)
        # print(df)
        plt.subplot(1, 4, i)
        plt.title(label.capitalize(), fontweight='bold')
        plt.pie(df["count"], labels=df["title"], autopct='%1.1f%%', startangle=90, colors=UdemyColorDict.values())
        plt.tight_layout()
        plt.legend(loc='lower center', fontsize='xx-small')
        i += 1
    # plt.show()
    return figure


"""
choice 2.1: chart by subcategories under Development
"""
subcategories = ['Programming Languages', 'Game Development', 'Web Development', 'Development Tools',
                 'Software Engineering', 'Database Design & Development', 'Data Science', 'Mobile Development',
                 'No-Code Development', 'Software Testing']


def countByCategory(category):
    """get total count of courses per ONE subcategory"""
    url_c = urllib.parse.quote_plus(category)
    getCategoryInfo = requests.get(
        f"https://www.udemy.com/api-2.0/courses/?language=en&ordering=newest&page=2&page_size=12&ratings=4.5&subcategory={url_c}",
        headers=headers)
    categoryInfo = getCategoryInfo.json()
    return categoryInfo["count"]


def getCountDict():
    """get a count dictionary with multiThreading"""
    countD = dict()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_count = {executor.submit(countByCategory, category): category for category in subcategories}
        for future in concurrent.futures.as_completed(future_to_count):
            category = future_to_count[future]
            try:
                count = future.result()
            except Exception as exc:
                print(f"{category} generated an exception: {exc}")
            else:
                countD[category] = count
    return countD


def plotCategoryChart():
    countDict = getCountDict()
    sortedCountD = dict((sorted(countDict.items(), key=lambda t: t[1])))
    figure = plt.figure()
    plt.barh(list(sortedCountD.keys()), list(sortedCountD.values()), color=UdemyColorDict.values())
    plt.title("Course Summary by Subcategory", fontweight='bold')
    plt.tight_layout()
    # plt.show()
    return figure


"""
choice 2.2: coding language and levels chart 
"""
codingLanguages = ["Python", "Java", "C#", "C++", "JavaScript", "C", "PHP", "Kotlin", "Swift"]


def countByLanguage(language):
    """get total count of courses per ONE coding language"""
    url_l = urllib.parse.quote_plus(language)
    getCategoryInfo = requests.get(
        f"https://www.udemy.com/api-2.0/courses/?category=Development&language=en&ordering=newest&page=2&page_size=12&ratings=4.5&search={url_l}",
        headers=headers)
    languageInfo = getCategoryInfo.json()
    language_df = pd.DataFrame()
    for item in languageInfo["aggregations"]:
        if item["id"] == "instructional_level":
            language_df = pd.DataFrame(columns=[d["title"] for d in item["options"]],
                                       data=[[d["count"] for d in item["options"]]])
            language_df['language'] = language
    return language_df


def getLevelData():
    """get dataset for all languages into a DataFrame, with multiThreading"""
    # start = time.time()
    result_df = pd.DataFrame()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_df = {executor.submit(countByLanguage, language): language for language in codingLanguages}
        for future in concurrent.futures.as_completed(future_to_df):
            language = future_to_df[future]
            try:
                df = future.result()
            except Exception as exc:
                print(f"{language} generate exception: {exc}")
            else:
                result_df = pd.concat([result_df, df])
    # print("total time to generate level data: ", time.time() - start)
    return result_df.sort_values('All Levels', ascending=False)


def plotLevelChart():
    result_df = getLevelData()
    print(result_df)
    plot = result_df.plot(kind="bar", x="language", color=list(UdemyColorDict.values()))
    # fig = plot.get_figure()
    plt.title("Language and Levels", fontweight='bold')
    plt.xlabel("Coding Languages")
    plt.ylabel("Total Courses Offered at Udemy")
    plt.tight_layout()
    # plt.show()
    return plot.get_figure()

# plot1
# plotSummaryChart()
# plot2
# plotCategoryChart()
# plot3
#plotLevelChart()