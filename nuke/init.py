import nuke, os
toolbox = os.path.join(os.path.expanduser("~"), ".nuke", "PXLtools")
nuke.pluginAddPath(os.path.join(toolbox, "scripts"))
nuke.pluginAddPath(os.path.join(toolbox, "icons"))
nuke.pluginAddPath("C:/Users/Evil Knight/.nuke/NukeSurvivalToolkit")