# YAML Ain’t Markup Language (YAML™)

If you are a Home Assistant user, it is likely that you are already familiar with YAML. 
However, if you are new to YAML, you can find many resources with a quick search on you favorite search engine.
Here are a couple links to get you started, in order of increasing detail:

1. [YAML cheatsheet](https://quickref.me/yaml)
2. [A Brief YAML reference](https://camel.readthedocs.io/en/latest/yamlref.html)
3. [A YAML Syntax reference](https://www.linode.com/docs/guides/yaml-reference/)
4. [The YAML specification](https://yaml.org/spec/1.2.2/#1021-tags)

This software package does not use much, if any, of the complex YAML functionality described in the YAML specification.
However, there are a couple of caveats of which you need to be aware:

In general, quotes around strings are not required in YAML, but including them is not a problem. Furthermore, 
single and double quotes are interchangeable. The only difference is that backslash escape sequences will be interpreted 
when enclosed in double quotes but not in single quotes.
Here are a couple cases where you will need to use quotes:
1. To force a numeric value to be interpreted as a string.
2. To force a boolean value to be interpreted as a string. 
YAML interprets the following as booleans if they are not enclosed in quotes: **true**, **false**, **yes**, **no**, **y**, **n**, **on**, **off** or any of those words in uppercase or title case.

There are other cases where YAML interprets values as something other than a string, but you likely won't encounter them
in the context of this package. Reference 2 above provides a list of exceptions in the section on Scalars.

