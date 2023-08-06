from reactipy.component import ReactComponent
import os

# Define your component
class MyComponent(ReactComponent):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        'components/helloworld.js')
    props_reference = 'test123'
    container = 'content'


component = MyComponent(items=['Home', 'Services', 'About', 'Contact us'])

print component.render(items=['Home', 'Services', 'About', 'Contact us'])




