===========
TBGXMLUtils
===========

This package makes it easy to construct xml files.


Examples
--------

e = add('TBGRoot')

i = add('LevelOne', e, attrs={'type':'default', 'class':'toplevel'})
add('ID', i, txt='1234')
add('FirstName', i, text='Jack')
add('LastName', i, text='Smith')

i = add('LevelTwo', e, attrs={'type':'default', 'class':'secondlevel'})
add('ID', i, txt='12345')
add('Address', i, text='1 Main Street')
add('City', i, text='New York')

print pretty(xml=etree2xml(e))

