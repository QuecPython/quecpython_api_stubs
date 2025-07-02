"""
Function: Regular Expression
The ure module provides regular expression matching operations.

Supported operators:
  '.'    - Match any character
  '[]'   - Match set of characters (individual characters and ranges)
  '^'    - Match the start of the string
  '$'    - Match the end of the string
  '?'    - Match zero or one of the previous sub-pattern
  '*'    - Match zero or more of the previous sub-pattern
  '+'    - Match one or more of the previous sub-pattern
  '??'   - Non-greedy version of ? (match zero or one)
  '*?'   - Non-greedy version of * (match zero or more)
  '+?'   - Non-greedy version of + (match one or more)
  '|'    - Match either the left-hand side or the right-hand side
  '\d'   - Match digit
  '\D'   - Match non-digit
  '\s'   - Match whitespace
  '\S'   - Match non-whitespace
  '\w'   - Match "word characters" (ASCII only)
  '\W'   - Match non-"word characters" (ASCII only)

Not supported operators:
  '{m,n}'        - Counted repetitions
  '(?P<name>...)' - Named groups
  '(?:...)'      - Non-capturing groups
  '\b'           - Word boundary assertions
  '\B'           - Non-word boundary assertions
  '\r'           - Carriage return (use Python's escaping instead)
  '\n'           - Newline (use Python's escaping instead)

Descriptions taken from:
https://developer.quectel.com/doc/quecpython/API_reference/en/stdlib/ure.html
"""

class error(Exception):
    """Exception raised for invalid regular expressions."""
    pass

def compile(regex):
    """
    Compiles a regular expression and generates a regular-expression object
    
    :param regex: Regular expression string
    :return: Compiled regex object
    """


def match(regex, string):
    """
    Matches the compiled regular expression against string from the start
    
    :param regex: Regular expression string or compiled object
    :param string: The string to be matched
    :return: Match object if successful, otherwise None
    """


def search(regex, string):
    """
    Searches for the compiled regular expression in string
    
    :param regex: Regular expression string or compiled object
    :param string: The string to search in
    :return: Match object if found, otherwise None
    """


class Match:
    """Match object returned by successful match/search"""
    
    def group(self, index=0):
        """
        Returns the string captured by the group
        
        :param index: Group index (0 = entire match)
        :return: Captured substring
        :raises: Error when group does not exist
        """