udrcmd
======

Python3 command line client to access united-domains Reselling API

This is my first Python3 project beyond the "hello world" stuff and thus it might contain some oddities.

## Files

* udrcmd.cfg contains your united-domains Reselling credentials.

## Usage

The client allows two usage modes:

1. Interactive mode
2. Command mode

### Interactive mode

```
$ ./udrcmd.py
Too few arguments. Let's try interactive mode. End with "EOF" (without quotes)
command = CheckDomain
domain = ajsdfgauwezrashfjasdf.com
EOF
{'code': '210',
 'description': 'Domain name available',
 'queuetime': '0',
 'runtime': '0.447'}
```

### Command mode

```
$ ./udrcmd.py CheckDomain domain=ajsdfgauwezrashfjasdf.com
{'code': '210',
 'description': 'Domain name available',
 'queuetime': '0',
 'runtime': '0.214'}
```

If you do not provide a "command=", the command has to be the first parameter.
Alternatively, you can provide "command=". In this case the order is not relevant.

```
$ ./udrcmd.py command=CheckDomain domain=ajsdfgauwezrashfjasdf.com
{'code': '210',
 'description': 'Domain name available',
 'queuetime': '0',
 'runtime': '0.022'}
```

or

```
$ ./udrcmd.py domain=ajsdfgauwezrashfjasdf.com command=CheckDomain
{'code': '210',
 'description': 'Domain name available',
 'queuetime': '0',
 'runtime': '0.463'}
```
