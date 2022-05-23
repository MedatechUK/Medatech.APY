move M:\python\MedatechUK.APY\package\dist\*.* M:\python\MedatechUK.APY\package\dist\old
m:
CD m:\python\MedatechUK.APY\package
py -m build
twine upload dist/*