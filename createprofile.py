import extractassets
import pack

# Extract all the required assets for the profile or studio we're creating the profile for
extractassets.PullAssets()

# Build a project file using these assets and any other relevant information
pack.BuildSB3(extractassets.GetProfileData())
