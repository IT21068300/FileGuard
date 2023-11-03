import re
from lib.Config import policyPath

path = policyPath
config = {}
Rules = []

def loadPolTxt(path):
    """
    Load the content of a policy text file.
    :param path: The path to the policy file.
    :return: The content of the policy file as a string.
    """
    txt = ''
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if (line.strip().startswith('#')):
                pass
            else:
                txt = txt + line
        f.close()
    return txt

def loadPolVar(txt):
    """
    Load global variables from the policy text.
    :param txt: The content of the policy text.
    :return: A dictionary containing the global variables.
    """
    global config
    txt = re.sub('#.*\n', '\n', txt)
    globalvartxt = re.compile(r'@@section GLOBAL(.*?)@@section FS')
    try:
        globalvar = globalvartxt.search(txt.replace('\n', '')).group(1)
        globalvar = re.sub('\s', '', globalvar)
        varname = re.findall(r'(\w*?)=', globalvar)
        varvalue = re.findall(r'=(.*?);', globalvar)
        for i in range(len(varname)):
            config[varname[i]] = varvalue[i].replace('\"', '')
    except:
        pass
    return config

def loadPolRules(txt):
    """
    Load rules from the policy text.
    :param txt: The content of the policy text.
    :return: A list of rules as dictionaries.
    """
    global Rules
    txt = re.sub('#.*\n', '\n', txt)
    
    # Replace variables in the policy file
    for globalvar in config:
        txt = txt.replace('$(' + globalvar + ')', config[globalvar])
    
    results = re.findall('\((.*?)\).*?{(.*?)}', txt, re.S | re.M)
    print(len(results))
    
    for rule in results:
        txt = rule[0].replace('=', ':')
        Rulekey = re.sub('(\w*?):', '"\\1":', txt.replace(' ', ''), re.M).replace('false', '0').replace('true', '1')
        Rule = eval('{' + Rulekey + '}')
        txt = rule[1].replace('->', ':')
        txt = re.sub('[ \t\f\r\v]', '', txt)
        txt = re.sub('!(.*?);', '\\1:"",', txt, flags=re.S | re.M)
        Rulecontent = re.sub('(.*?):', '"\\1":', txt)
        Rulecontent = re.sub(':(.*?);', ':"\\1",', Rulecontent)
        Rule['content'] = eval('{' + Rulecontent + '}')
        for path in Rule['content']:
            Rule['content'][path] = checkRules(Rule['content'][path])
        Rules.append(Rule)
    return Rules

def checkRules(rulestr: str):
    """
    Check and parse rules.
    :param rulestr: A string containing rules.
    :return: A string containing parsed and checked rules.
    """
    check = ''
    ignore = ''
    c = re.findall('\+([abcdgilmnprstuCHMS]+)', rulestr)
    ig = re.findall('-([abcdgilmnprstuCHMS]+)', rulestr)
    for i in c:
        check = check + i
    for i in ig:
        ignore = ignore + i
    for i in ignore:
        if i in check:
            check = check.replace(i, '')
    return check

def setRule(path: str):
    dir = path.split('/')
    pathnew = []
    for Rule in Rules:
        RuleContent = Rule['content']
        for RulePath in RuleContent:
            if RulePath.startswith('r'):
                reRule = re.search("r'(.*?)'", RulePath)
                try:
                    reRule = reRule.group(1)
                except:
                    print('Incorrect regular expression in the policy file ->', RulePath)
                    print('Correct format ->', "r'/home.*'")
                if re.search(reRule, path) is not None:
                    return Rule['rulename'], RuleContent[RulePath]
    
    for i in range(len(dir)):
        a = '/'
        a = a.join(dir[:i + 1])
        if a == '':
            a = '/'
        pathnew.append(a)
    pathnew.reverse()
    for i in pathnew:
        for Rule in Rules:
            if i in Rule['content']:
                return Rule['rulename'], Rule['content'][i]

def loadPol():
    global Rules
    try:
        txt = loadPolTxt(path=path)
        try:
            loadPolVar(txt)
            Rules = loadPolRules(txt)
    
            return {'code': 200, 'msg': 'File opened successfully', 'rules': Rules}
        except:
            return {'code': 1002, 'msg': 'Failed to load the file format'}
    except:
        return {'code': 1001, 'msg': 'Failed to open the file'}

loadPol()
print(Rules)
