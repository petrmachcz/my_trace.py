import sys
import inspect
from os.path import basename

def getTextFromCode(code, offset, linenu):
    '''Prints a relevant part of the source code.'''
    cde = code[:offset+1]
    cde.reverse()

    shortCode = []
    opendet   = 0
    closedet  = 0
    for i, line in enumerate(cde):
        if  '{{{' in line:
            opendet = 1
        if  '}}}' in line:
            closedet = 1
        sLine = line.strip()
        if sLine.startswith('def') or sLine.startswith('class') or (sLine == '' and i > 20):
            shortCode.insert(0, line)
            if  not opendet:
                shortCode.insert(0, '{{{ CODE ')
            if  not closedet:
                shortCode.append('}}} CODE ')
            break
        shortCode.insert(0, line)

    offst = len(shortCode)-1
    TEXT = [f"{linenu-offst+i+1:5d} {line[:-1]}" for i, line in enumerate(shortCode)]
    if  '{{{ CODE' in TEXT[0]:
        TEXT[0] = TEXT[0][6:]
    if  '}}} CODE' in TEXT[-1]:
        TEXT[-1] = TEXT[-1][6:]
    return '\n'.join(TEXT)
def getTextFromDict(d, title=None):
    '''Pretty prints a dictionary.'''
    TEXT = [title] if title else []
    keys = sorted(d.keys())

    if not keys:  # Přidána kontrola prázdné sekvence
        return '\n'.join(TEXT)

    keyMaxLen = max(len(key) for key in keys) + 2
    pattern = f"{{:{keyMaxLen}}} = ({{}}) {{}}"
    for key in keys:
        try:
            text = str(d[key])[:200]
        except Exception as e:
            text = f'<<<TRACE-STR-ERROR: {e}>>>'
        TEXT.append(pattern.format(key, type(d[key]), text))
    return '\n'.join(TEXT)

def getTextFromStrerr(typerr, strerr, file, linenu, obj):
    '''Formats the stderr output.'''
    return f"\nERROR: [{file}:{linenu}] {obj}(): {strerr} {typerr}"

def makeTextFromException(size='full'):
    '''Prints information about an exception.'''
    typerr, strerr, _ = sys.exc_info()
    TEXT = [f'\nEXCEPTION: {typerr}']
    traceback = inspect.trace(100)

    last = len(traceback) - 1
    for i, (frame, file, linenu, obj, code, offset) in enumerate(traceback):
        example = code[offset].strip() if code and code[offset] else '<N/A>'
        file = basename(file)

        if i == last or size in ('full', 'max'):
            TEXT.append(f'{file}/{linenu:<4d} {obj:20s}: {example}')

        if i != last and size == 'max' and code:
            TEXT.append(getTextFromCode(code, offset, linenu))
            TEXT.append(getTextFromDict(frame.f_locals, '{{{  LOCAL VARS:'))
            TEXT.append('}}}')

        if i == last:
            if code and size in ('full', 'max'):
                TEXT.append(getTextFromCode(code, offset, linenu))
            if size in ('full', 'max'):
                TEXT.append(getTextFromDict(frame.f_locals, '{{{ LOCAL VARS:'))
                TEXT.append('}}}')
            TEXT.append(getTextFromStrerr(typerr, strerr, file, linenu, obj))

    TEXT.append('----------\n')
    return '\n'.join(TEXT)

if __name__ == "__main__":

    class MyError(Exception):
        def __init__(self, value):
            self.value = value
        def __str__(self):
            return repr(self.value)

    def aa(a, b):
        '''Test function where an exception occurs.'''
        c = ['q', 123, None]
        d = a / b

    def bb():
        '''Test function.'''
        aa(1, 0)

    def cc():
        raise MyError("my error")

    def dd():
        '''Test function.'''
        print(f'{"="*10} Test: bb() {"="*60}')
        try:
            bb()
        except Exception as e:
            print(makeTextFromException())

        print(f'{"="*10} Test: cc() {"="*60}')
        try:
            cc()
        except Exception as e:
            print(makeTextFromException())

        print(f'{"="*10} Test: cc() short {"="*60}')
        try:
            cc()
        except Exception as e:
            print(makeTextFromException('short'))

        print(f'{"="*10} Test: cc() max {"="*60}')
        try:
            cc()
        except Exception as e:
            print(makeTextFromException('max'))

    def ee():
        x = 'local var in ee()'
        bb()

    def ff(): # {{{
        ee()
    # }}}

    #dd()

    print(f'{"="*10} Test: ff() max {"="*60}')
    try:
        ff()
    except Exception as e:
        #print(makeTextFromException('max'))
        print(makeTextFromException())


