copy "C:\Program Files\Python39\Lib\site-packages\MedatechUK\*.py" m:\python\MedatechUK.APY\package\src\MedatechUK
copy "C:\pyedi\*.*" M:\python\MedatechUK.APY\transport\service
copy M:\python\apy\default.py M:\python\MedatechUK.APY\transport\web
copy M:\python\apy\web.config M:\python\MedatechUK.APY\transport\web
move M:\python\MedatechUK.APY\package\dist\*.* M:\python\MedatechUK.APY\package\old
m:
CD m:\python\MedatechUK.APY\package
py -m build
twine upload dist/*