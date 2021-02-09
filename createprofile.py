import extractassets
import pack
import tempfile

with tempfile.TemporaryDirectory(None, None, '.') as tmpdirname:
    # Extract all the required assets for the profile or studio we're creating the profile for
    extractassets.PullAssets(tmpdirname)
    # Build a project file using these assets and any other relevant information
    pack.BuildSB3(tmpdirname, extractassets.GetProfileData())
