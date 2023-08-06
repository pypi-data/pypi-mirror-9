import numpy as np
import os
import sys
import traceback
import pyneb as pn

def execution_path(filename):
    return os.path.join(os.path.dirname(sys._getframe(1).f_code.co_filename), filename)

def _returnNone(*argv, **kwargs):
    return None

def int_to_roman(input_):
    """
    Convert an integer to Roman numerals.
    
    Examples:
    >>> int_to_roman(0)
    Traceback (most recent call last):
    ValueError: Argument must be between 1 and 3999
    
    >>> int_to_roman(-1)
    Traceback (most recent call last):
    ValueError: Argument must be between 1 and 3999
    
    >>> int_to_roman(1.5)
    Traceback (most recent call last):
    TypeError: expected integer, got <type 'float'>
    
    >>> print int_to_roman(2000)
    MM

    >>> print int_to_roman(1999)
    MCMXCIX

    """
    if type(input_) != type(1):
        #raise TypeError, "expected integer, got %s" % type(input_)
        return None
    if not 0 < input_ < 4000:
        #raise ValueError, "Argument must be between 1 and 3999"
        return None
    ints = (1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1)
    nums = ('M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I')
    result = ""
    for i in range(len(ints)):
        count = int(input_ / ints[i])
        result += nums[i] * count
        input_ -= ints[i] * count
    return result


def roman_to_int(input_):
    """
    Convert a roman numeral to an integer.
    
    >>> r = range(1, 4000)
    >>> nums = [int_to_roman(i) for i in r]
    >>> ints = [roman_to_int(n) for n in nums]
    >>> print r == ints
    1
    
    >>> roman_to_int('VVVIV')
    Traceback (most recent call last):
     ...
    ValueError: input is not a valid roman numeral: VVVIV

    >>> roman_to_int(1)
    Traceback (most recent call last):
     ...
    TypeError: expected string, got <type 'int'>

    >>> roman_to_int('a')
    Traceback (most recent call last):
     ...
    ValueError: input is not a valid roman numeral: A

    >>> roman_to_int('IL')
    Traceback (most recent call last):
     ...
    ValueError: input is not a valid roman numeral: IL

    """   
    if type(input_) != type(""):
        #raise TypeError, "expected string, got %s" % type(input_)
        return None
    input_ = input_.upper()
    nums = ['M', 'D', 'C', 'L', 'X', 'V', 'I']
    ints = [1000, 500, 100, 50, 10, 5, 1]
    places = []
    for c in input_:
        if not c in nums:
            #raise ValueError, "input is not a valid roman numeral: %s" % input_
            return None
    for i in range(len(input_)):
        c = input_[i]
        value = ints[nums.index(c)]
        # If the next place holds a larger number, this value is negative.
        try:
            nextvalue = ints[nums.index(input_[i + 1])]
            if nextvalue > value:
                value *= -1
        except IndexError:
            # there is no next place.
            pass
        places.append(value)
    sum_ = 0
    for n in places: sum_ += n
    # Easiest test for validity...
    if int_to_roman(sum_) == input_:
        return sum_
    else:
        #raise ValueError, 'input is not a valid roman numeral: %s' % input_
        return None
      
      
def parseAtom(atom):
    '''Parses an atom label into the element and spectrum parts'''

    elem = ''
    spec = ''
    cont = True
    for l in atom:
        if l.isalpha() and cont:
            elem = elem + l
        elif l.isdigit():
            spec = spec + l
            cont = False
    return str.capitalize(elem), spec


def strExtract(text, par1=None, par2=None): 
    """
    Extract a substring from text (first parameter)
     
    If par1 is a string, the extraction starts after par1,
    else if it is an integer, it starts at position par1.
    If par 2 is a string, extraction stops at par2, 
    else if par2 is an integer, extraction stops after par2 characters.
    
    Examples: 
    
    strExtract('test123','e','1')
    strExtract('test123','st',4)
    
    """
    if np.size(text) == 1:
        if type(par1) is int:
            str1 = text[par1::]
        elif type(par1) is str:
            str1 = text.split(par1)[-1]
        else:
            str1 = text
    
        if type(par2) is int:
            str2 = str1[0:par2]
        elif type(par2) is str:
            str2 = str1.split(par2)[0]
        else:
            str2 = str1
        return str2
    else:
        res = []
        for subtext in text:
            res1 = strExtract(subtext, par1=par1, par2=par2)
            if res1 != '':
                res.append(res1)
        return res


def formatExceptionInfo(maxTBlevel=5):
    cla, exc, trbk = sys.exc_info()
    excName = cla.__name__
    try:
        excArgs = exc.__dict__["args"]
    except KeyError:
        excArgs = "<no args>"
    excTb = traceback.format_tb(trbk, maxTBlevel)
    return (excName, excArgs, excTb)

def multi_split(s, seps):
    res = [s]
    for sep in seps:
        s, res = res, []
        for seq in s:
            res += seq.split(sep)
    return res


def cleanPypicFiles(files=None, all_=False, dir_=None):
    """
    Method to clean the directory containing the pypics files.

    Parameters:
        - files    list of files to be removed
        - all_      Boolean, is set to True, all the files are deleted from the directory
        - dir_      directory from where the files are removed. 
                If None (default), pn.config.pypic_path is used.

    """
    if dir_ is None:
        dir_ = pn.config.pypic_path
    if all_:
        files = os.listdir(dir_)
        if np.ndim(files) == 0:
            files = [files]
    if files is None:
        return
    if type(files) == type(''):
        files = [files]
    for file_ in files:
        file_path = os.path.join(dir_, file_)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                pn.log_.message('Deleting {0}'.format(file_path), calling='cleanPypicFiles')
        except:
            pn.log_.warn('Unable to remove {0}'.format(file_path), calling='cleanPypicFiles')


def getPypicFiles(dir_=None):
    """
    Return the list of files in the directory.

    Parameters:
        - dir_     directory from where the files are removed. 
                   If None (default), pn.pypic_path is used.

    """
    if dir_ is None:
        dir_ = pn.config.pypic_path
    files = os.listdir(dir_)
    return files


def revert_seterr(oldsettings):
    """
    This function revert the options of seterr to a value saved in oldsettings.
    
    Usage:
        oldsettings = np.seterr(all='ignore')
        to_return = (result - int_ratio) / int_ratio # this will not issue Warning messages
        revert_seterr(oldsettings)

    Parameters:
        oldsettings  result of np.seterr(all='ignore')

    """
    np.seterr(over=oldsettings['over'])
    np.seterr(divide=oldsettings['divide'])
    np.seterr(invalid=oldsettings['invalid'])
    np.seterr(under=oldsettings['under'])

def quiet_divide(a, b):
    """
    This function returns the division of a by b, without any waring in case of b beeing 0.
    """
    oldsettings = np.seterr(all='ignore')
    to_return = a / b # this will not issue Warning messages
    revert_seterr(oldsettings)
    return to_return

def quiet_log10(a):
    """
    This function returns the log10 of a, without any waring in case of b beeing 0.
    """
    oldsettings = np.seterr(all='ignore')
    to_return = np.log10(a) # this will not issue Warning messages
    revert_seterr(oldsettings)
    return to_return
     
def get_reduced(N_rand, a, value_method = 'original', error_method='std'):
    """
    This function returns a tuple of value and error corresponding to an array of values 
        obtained from a MonteCarlo computation
    It takes as argument an array that contains the original value, 
        followed by N_rand MonteCarlo values.
    The relevant value is computed by returning the original value (default), the mean or the median, 
        depending on "value_method"
    The errors are computed by 68% quantiles or standart deviation (Default), 
        depending on "error_method"
    
    """

    if error_method == 'quants' and not pn.config.INSTALLED['scipy']:
        pn.log_.error('Scipy not installed, use_quants not available', calling = 'get_reduced')
    else:
        from scipy.stats.mstats import mquantiles
    
    
    if value_method == 'original':
        value = a[0]
    elif value_method == 'mean':
        value = a.mean()
    elif value_method == 'median':
        value = np.median(a)
    
    if error_method == 'quants':
        quants = mquantiles(a, [0.16, 0.84])
        error = np.abs(quants - value).mean()
    elif error_method == 'uquants':
        quants = mquantiles(a, [0.16, 0.84])
        error = quants[1] - value
    elif error_method == 'lquants':
        quants = mquantiles(a, [0.16, 0.84])
        error = quants[0] - value
        # error = (quants[1]-quants[0])/2)
    elif error_method == 'upper':
        mask = (a - value) >= 0
        error =  ((((a[mask] - value)**2).sum())/np.float(mask.sum()))**0.5
    elif error_method == 'lower':
        mask = (a - value) <= 0
        error = -((((a[mask] - value)**2).sum())/np.float(mask.sum()))**0.5
    elif error_method == 'std':
        error = a.std()
    else:
        pn.log_.error('Unknown error method {}'.format(error_method))
        
    return (value, error)
    
def get_reduced_dic(N_rand, n_obs_ori, dic, value_method = 'original', 
                    error_method='std', abund12 = False):
    """
    This function returns a dictionary of values (ionic or atomic abundances, temp...) and errors.
    It takes as argument a dictionary that is supposed to contains n_obs_ori values from
        the original observations, followed (optionaly) by N_rand*n_obs_ori MonteCarlo values.
    The new values are computed by returning the original value (default), the mean or the median, 
        depending on "value_method"
    The errors are computed by 68% quantiles or standart deviation (Default), depending on on "error_method"
    
    It also transforms the abundances by number into 12+log10(abundances by number)
    """
    res = {}
    for key in dic:
        value = []
        error = []
        for i in np.arange(n_obs_ori):
            if abund12:
                values = 12 + np.log10(dic[key][n_obs_ori+i*N_rand:n_obs_ori+(i+1)*N_rand])
                values = np.insert(values, 0, 12 + np.log10(dic[key][i]))
            else:
                values = dic[key][n_obs_ori+i*N_rand:n_obs_ori+(i+1)*N_rand]
                values = np.insert(values, 0, dic[key][i])
            tt = np.isfinite(values)
            if tt.sum() == 0:
                value.append(np.NAN)
                error.append(0.0)
            else:
                v, e = get_reduced(N_rand, values[tt], value_method = value_method, 
                                   error_method=error_method)
                value.append(v)
                error.append(e)
        res[key] = np.array(value)
        res['{0}_e'.format(key)] = np.array(error)
    return res

    
    
    
    