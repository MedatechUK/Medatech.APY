copy "C:\Program Files\Python39\Lib\site-packages\MedatechUK\*.py" m:\python\MedatechUK.APY\package\src\MedatechUK
move M:\python\MedatechUK.APY\package\dist\*.* M:\python\MedatechUK.APY\package\old
m:
CD m:\python\MedatechUK.APY\package
py -m build
twine upload dist/*