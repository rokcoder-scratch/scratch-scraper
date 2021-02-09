import extractassets
import pack

# with open('temp/project.json', 'r') as file:
#     project = file.readline()
# reg = re.compile('^"name:["\:"profileData"')
# m1 = reg.search(project)
# print(m1)

# Extract all the required assets for the profile or studio we're creating the profile for
extractassets.PullAssets()

# Build a project file using these assets and any other relevant information
pack.BuildSB3()
