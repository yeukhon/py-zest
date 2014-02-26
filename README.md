# py-zest

Experimental Python implementation of Zest.

## Usage

```
import json
import zest

with open("script.zest", "r") as f:
    script = json.loads(f.read())

# This function will load a JSON/dictionary and return a ZestScript object
z = zest.load(script)

# py-zest maps zest script's attribute name (using camelCase)
print(z.about)
print(z.generatedBy)

# statements is implemented as a list of ZestStatement instances
print(z.statements)
print(z.statements[0].url
print(z.statements[0].assertions

# Calling the run() method will execute all assertions
z.run()
# After run(), results are saved into the report attribute
print z.report

# {'assertions': [{'assertions': [{'assert_type': 'ZestAssertStatusCode',
#                                 'passed': True}],
#                 'url': u'http://localhost:5000/'}],
# 'failed': 0,
# 'passed': 1}
```
