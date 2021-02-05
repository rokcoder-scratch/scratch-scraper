import json
import requests
import re
import textwrap
from pathlib import Path
from sys import stdout

def ProgressBar(name, percent):
    n = 100
    j = percent / n
    stdout.write('\r')
    stdout.write(name + "[%-20s] %d%%" % ('='*int(20*j), 100*j))
    stdout.flush()

def ProcessTags(tags, string):
    for tag in re.findall("\\s\\#(\\w+)", string):
        if not tag.lower() in tags:
            tags.append(tag.lower())

def ExtractDescription(string):
    description = re.search("\\s\\#description\(([^\)]+)", string, flags=re.IGNORECASE)
    if description:
        return description.group(1)
    # Create a description from any tags
    tags = []
    ProcessTags(tags, string)
    if tags:
        description = ""
        for item in tags:
            if item != "description":
                if description != "":
                    description += " "
                description += item
        if description != "":
            return description

    return "Description to be added..."

def ParseEndpoint(endpoint, target, isUsername):
    validtags = [ "3d", "adventures", "arcade", "music", "retro", "techdemo", "toolkit", "tutorials", "watchable", "games", "art", "animations", "stories" ]

    if isUsername:
        pathname = requests.get(endpoint).json()["username"]
        targetName = 'Username: "' + pathname + '" - '
    else:
        pathname = requests.get(endpoint).json()["title"]
        targetName = 'Studio: "' + pathname + '" - '

    endpoint += "/projects"

    projects = []
    offset = 0
    progress = 0

    Path(pathname).mkdir(exist_ok=True)
    path = Path(pathname)

    # Pull the data for all of the user's projects

    ProgressBar(targetName, progress)

    while True:
        response = requests.get(endpoint + "?offset=" + str(offset) + "&limit=40")
        if not response.json():
            break
        projects += response.json()
        offset += 40

    # Strip out any projects that include the #noindex tag

    with (path / "../log.txt").open("w") as log:
        log.write("Ignoring following files due to #noindex\n")
        for i in range(len(projects) - 1, -1, -1):
            project = projects[i]
            tags = []
            ProcessTags(tags, project["description"])
            ProcessTags(tags, project["instructions"])
            if "noindex" in tags:
                del projects[i]
                log.write("\t" + str(project["title"].encode('ascii', "ignore"), "ascii") + "\n")
        log.write("----------------------------------------\n\n")

    # Create SVG files for all the titles

    projectNum = 1
    for project in projects:
        with (path / ("title" + str(projectNum) + ".svg")).open("w") as output:
            output.write('<svg version="1.1" viewBox="0 0 480 360" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">')
            output.write('<g data-paper-data="{&quot;isPaintingLayer&quot;:true}" fill="#ff0000" fill-rule="nonzero" stroke="none" stroke-width="1" stroke-linecap="butt" stroke-linejoin="miter" stroke-miterlimit="10" stroke-dasharray="" stroke-dashoffset="0" font-family="Serif" font-weight="normal" font-size="40" text-anchor="start" style="mix-blend-mode: normal">')
            output.write('<text transform="translate(240,188) scale(0.5,0.5)" font-size="40" xml:space="preserve" data-paper-data="{&quot;origPos&quot;:null}" fill="#ff0000" fill-rule="nonzero" stroke="none" stroke-width="1" stroke-linecap="butt" stroke-linejoin="miter" stroke-miterlimit="10" stroke-dasharray="" stroke-dashoffset="0" font-family="Serif" font-weight="normal" text-anchor="start" style="mix-blend-mode: normal">')
            output.write('<tspan x="0" dy="0">')
            output.write(str(project["title"].encode('ascii', "ignore"), "ascii"))
            output.write('</tspan>')
            output.write('</text>')
            output.write('</g>')
            output.write('</svg>')
            projectNum += 1

    # Create SVG files for all the descriptions

    projectNum = 1
    for project in projects:
        description = ExtractDescription(project["description"] + " " + project["instructions"])
        with (path / ("description" + str(projectNum) + ".svg")).open("w") as output:
            output.write('<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0,0,480,360">')
            output.write('<g data-paper-data="{&quot;isPaintingLayer&quot;:true}" fill="#ff0000" fill-rule="nonzero" stroke="none" stroke-width="1" stroke-linecap="butt" stroke-linejoin="miter" stroke-miterlimit="10" stroke-dasharray="" stroke-dashoffset="0" font-family="Serif" font-weight="normal" font-size="40" text-anchor="start" style="mix-blend-mode: normal">')
            output.write('<text transform="translate(90,158) scale(0.32812,0.32812)" font-size="40" xml:space="preserve" data-paper-data="{&quot;origPos&quot;:null}" fill="#ff0000" fill-rule="nonzero" stroke="none" stroke-width="1" stroke-linecap="butt" stroke-linejoin="miter" stroke-miterlimit="10" stroke-dasharray="" stroke-dashoffset="0" font-family="Serif" font-weight="normal" text-anchor="start" style="mix-blend-mode: normal">')
            lines = textwrap.wrap(description, 70, break_long_words=False)
            for i in range(0, min(4, len(lines))):
                output.write('<tspan x="0" dy="48">' + str(lines[i].encode('ascii', "ignore"), "ascii") + '</tspan>')
            output.write('</text>')
            output.write('</g>')
            output.write('</svg>')
            projectNum += 1

    # Pull all the thumbnails and store locally

    progressStep = 100 / len(projects)

    projectNum = 1
    for project in projects:
        while True:
            response = requests.get("https://cdn2.scratch.mit.edu/get_image/project/" + str(project["id"]) + "_160x120.png")
            if response.status_code == 200:
                break
            else:
                stdout.write("\r Retrying thumbnail " + projectNum + " (error code " + (response.status_code) + ")                         ")
        with (path / ("thumb" + str(projectNum) + ".png")).open("wb") as imageOutput:
            imageOutput.write(response.content)
            projectNum += 1
            progress += progressStep
            ProgressBar(targetName, progress)

    # Pull useful data into text file

    taglessfiles = []
    unknowntags = []
    with (path / "../log.txt").open("a") as log:
        log.write("Tags on files\n")
        with (path / "profile-data.txt").open("w") as output:
        
            # output.write(str(version) + "\n")
            output.write(str(len(projects)) + "\n")

            for project in projects:
                output.write(str(project["title"].encode('ascii', "ignore"), "ascii") + "\n")
                output.write(str(project["id"]) + "\n")
                output.write(project["history"]["shared"] + "\n")
                output.write(str(project["stats"]["views"]) + "\n")
                output.write(str(project["stats"]["loves"]) + "\n")
                tags = []
                ProcessTags(tags, project["description"])
                ProcessTags(tags, project["instructions"])
                tagcount = 0
                for tag in tags:
                    if tag != "description":
                        if tag in validtags:
                            tagcount += 1
                        else:
                            unknowntags.append("\t" + str(project["title"].encode('ascii', "ignore"), "ascii") + ": " + tag + "\n")
                output.write(str(tagcount) + "\n")
                if tagcount > 0:
                    log.write("\t" + str(project["title"].encode('ascii', "ignore"), "ascii") + ": ")
                else:
                    taglessfiles.append("\t" + str(project["title"].encode('ascii', "ignore"), "ascii") + "\n")
                c = 0
                for tag in tags:
                    if tag != "description" and tag in validtags:
                        c += 1
                        output.write(tag + "\n")
                        if c > 1:
                            log.write(", ")
                        log.write(tag)
                if tagcount > 0:
                    log.write("\n")
            log.write("-------------\n\n")

        log.write("Tagless files\n")
        for names in taglessfiles:
            log.write(names)
        log.write("-------------\n\n")

        log.write("Unknown tags in following files\n")
        for names in unknowntags:
            log.write(names)
        log.write("--------------------------------\n\n")

    ProgressBar(targetName, 100)

    print("\nView log.txt for parsing information")

target = input("Enter username or studio number:")
userEndpoint = "https://api.scratch.mit.edu/users/" + target
studioEndpoint = "https://api.scratch.mit.edu/studios/" + target

response = requests.get(userEndpoint)
validUser = response.status_code == 200
validStudio = False
if target.isnumeric():
    response = requests.get(studioEndpoint)
    validStudio = response.status_code == 200

if validStudio and not validUser:
    ParseEndpoint(studioEndpoint, target, False)
elif not validStudio and validUser:
    ParseEndpoint(userEndpoint, target, True)
elif not (validStudio or validUser):
    print('"' + target + '" is not a valid username or studio id')
else:
    while True:
        targetType = input("Is this (1) a username or (2) a studio?")
        if targetType == "1":
            ParseEndPoint(userEndpoint, target, True)
            break
        elif targetType =="2":
            ParseEndpoint(studioEndpoint, target, False)
            break
