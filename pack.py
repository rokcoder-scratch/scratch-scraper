import hashlib
import pathlib
import zipfile
import re
import glob
import os

# We've already created all the assets and data required (in a temporary folder) so now we need to process them into an sb3 file
#
# The following steps will then be needed -
#    1) Decompress the sb3 file to the temporary folder
#    2) Scan the json file and remove all thumb, title and description costumes from both the (thumbs sprite in the) json and the temporary folder
#    3) Calculcate the MD5 hashes for all the new thumb, title and description files and rename the files appropriately
#    4) Create the asset data to be added to the json file for each image
#    5) Insert the asset data for the thumb, title and description costumes
#    6) Replace the "project data" list with the new "project data" in the (manager sprite in the) json
#    7) Remove the "project data.txt" file from the temporary folder as we don't want this including in the SB3
#    8) Compress the contents of the folder and rename the extension the sb3
#
# The above brings it to where we were before (but automated). The following extension work is planned -
#    9) Allow control over the tags being used in the project - this will also need to add svg sprites for the descriptions of the tags
#   10) Allow control over the music being used in the project (as an mp3 file)
#   11) Allow control over the animated RokCoder tile being used in the project (as either a png or gif file of specified dimensions)
#   12) Add a new tag that can be used to dictate which thumbnails will be used to automatically build a GIF file


def BuildSB3():

    # Extract the full project file to a temporary folder
    with zipfile.ZipFile("Profile Page.sb3") as myzip:
        myzip.extractall("temp")

    # Load the JSON file into memory
    with open('temp/project.json', 'r') as file:
        project = file.readline()

    # Remove all costumes in thumbs sprite other than the initial "Don't delete!" costume
    reg = re.compile('"name":"Don\'t delete!"[^\}]+\}')
    m1 = reg.search(project)
    reg = re.compile('\]')
    m2 = reg.search(project, m1.end())
    newProject = project[:m1.end()] + project[m2.start():]

    input()

    # Remove the associated files from the temp folder
    pos = 0
    removalSection = project[m1.end():m2.start()]
    reg = re.compile('\"md5ext\":\"([^\"]*)\"')
    while(True):
        thisFile = reg.search(removalSection, pos)
        if thisFile == None:
            break
        os.remove("temp/" + thisFile.group(1))
        pos = thisFile.end()

    input()

    # Scan through thumb*, description* and title* files, calculate their MD5s, build a table and rename the files
    allFiles = {}
    imageFiles = glob.glob('temp/thumb*.*')
    imageFiles += glob.glob('temp/description*.*')
    imageFiles += glob.glob('temp/title*.*')
    for file in imageFiles:
        md5_hash = hashlib.md5()
        tempFile = open(file, "rb")
        tempContent = tempFile.read()
        md5_hash.update(tempContent)
        digest = md5_hash.hexdigest()
        allFiles[digest] = file
        os.rename(file, "temp/" + digest + pathlib.Path(file).suffix)

    # with open('test.txt', 'w') as file:
    #    file.write(newProject)
