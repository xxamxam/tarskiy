#!/bin/env python3


import sys
import copy
from queue import Queue
import sympy as sy
from sympy.abc import x, a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, y, z, Z
from sympy.polys.numberfields import is_isomorphism_possible

sy.init_printing()
perems = sy.symbols('x a')
# добавить если недостаточно букв, x должна быть первой
# x, a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, y, z 



def sorter(e):
    if isinstance(sy.degree(e,perems[0]),sy.core.numbers.NegativeInfinity) or (sum(sy.degree_list(e)) == 0):
        return -1
    return sy.degree(e,perems[0])

def sorter_1(e):
    if isinstance(sy.degree(e,perems[0]),sy.core.numbers.NegativeInfinity):
        return 0
    return sy.degree(e,perems[0])

def next(sign_list, numb, leng, consts):
    for ii in range(consts, leng):
        sign_list[ii] = (numb % 3) - 1
        numb = numb // 3

def signum(x):
    if x == 0:
        return 0
    elif x > 0:
        return 1
    return -1

def init_consts(zero_degree_sign, polynoms, consts):
    for ii in range(consts):
        zero_degree_sign[ii] = signum(float(polynoms[ii].coeffs()[0]))

def add_columns(rez, intervals, lenn, vyr_num, pos):
    to_add = [[0]*lenn]*2
    if(pos == len(rez) - 1):
        rez = rez + to_add
        intervals = intervals + [0]*2
    else:
        rez = rez[:pos + 1] + to_add + rez[pos+1:]
        intervals = intervals[:pos + 1] + [0]*2 + intervals[pos+1:] 
 
    rez[pos + 2] = copy.deepcopy(rez[pos])
    rez[pos + 1] = copy.deepcopy(rez[pos])
    return rez, intervals

        

def string_form(_poll_):
    return str(_poll_.as_expr())

# получает список полиномов и строит по ним таблицу
#  значения в rez 1 = greater than 0
#                 0 = equiv to 0
              #   -1 = lower than 0



def fill_table(polynoms, div_pairs, is_there, _polynoms_, _sign_):
    is_true = False
    ret_polynoms = []
    ret_signs = []
    pos_numb = {}
    pos_numb[0] = {}
    pos_numb[1] = {}
    zero_degree = 0
    consts = 0
    lenn_z = len(polynoms[0])
    for ii in range(lenn_z):
        pos_numb[0][polynoms[0][ii]] = ii
        tmp = sorter(polynoms[0][ii])
        if tmp <= 0:
            zero_degree += 1
            if tmp == -1:
                consts += 1
    lenn = len(polynoms[1])
    for ii in range(lenn):
        pos_numb[1][polynoms[1][ii]] = ii 

    zero_degree_sign = [0]*zero_degree
    init_consts(zero_degree_sign, polynoms[0],consts)
      # если первый аргумент равен 0, то это точка, в которой второй аргумент(который полином) равен 0, если равен 1 то это промежуток
    for ij in range(3**(zero_degree - consts)):
        intervals = [(1,0)]
        rez = [[0]*lenn]
        next(zero_degree_sign, ij, zero_degree, consts)
        for vyr in range(lenn):
            polyn = sy.poly(sy.LC(polynoms[1][vyr],perems[0]), *perems)
            position = pos_numb[0][polyn]
            if( zero_degree_sign[position] == 0):
                polyn = (polynoms[1][vyr] - sy.LC(polynoms[1][vyr] ,perems[0])*sy.LM(polynoms[1][vyr] ,perems[0]))
                if(is_there[polyn] == 1):
                    position = pos_numb[is_there[polyn]][polyn]
                    for t_num in range(len(rez)):
                        rez[t_num][vyr] = rez[t_num][position]
                else:
                    sign_ = zero_degree_sign[pos_numb[0][polyn]]
                    for t_num in range(len(rez)):
                        rez[t_num][vyr] = sign_

            else:

                polyn = polynoms[1][vyr]

                if(len(rez) == 1):
                    rez, intervals = add_columns(rez, intervals, lenn, vyr, 0)
                    intervals[0] = intervals[2] = (1,0)
                    intervals[1] = (0, polynoms[1][vyr])
                    
                    rez[1][vyr] = 0
                    
                    rez[0][vyr] = -zero_degree_sign[position]
                    rez[2][vyr] = zero_degree_sign[position]

                else:
                    minus_inf_sign = zero_degree_sign[position]*(((sy.degree(polyn,perems[0]) + 1)%2)*2 - 1)
                    plus_inf_sign = zero_degree_sign[position]

                    for t_num in range(len(rez)):
                        if intervals[t_num][0] == 0:
                            polyn = div_pairs[(polynoms[1][vyr], intervals[t_num][1])]
                            position = pos_numb[ is_there[polyn]][polyn]
                            rez[t_num][vyr] = rez[t_num][position] if is_there[polyn] == 1 else zero_degree_sign[pos_numb[0][polyn]]

                    cycle = 1
                    if(minus_inf_sign*rez[1][vyr] < 0):
                        cycle +=2
                        rez, intervals = add_columns(rez, intervals, lenn, vyr, 0)
                        intervals[0] = intervals[2] = (1,0)
                        intervals[1] = (0, polynoms[1][vyr])
                        rez[0][vyr] = minus_inf_sign
                        rez[1][vyr] = 0
                        rez[2][vyr] = rez[3][vyr]
                    else:
                        rez[0][vyr] = minus_inf_sign

                    while(cycle != len(rez) - 2):
                        if(rez[cycle][vyr] * rez[cycle + 2][vyr] < 0):
                            rez, intervals = add_columns(rez, intervals, lenn, vyr, cycle + 1)
                            intervals[cycle + 1] = intervals[cycle + 3] = (1,0)
                            intervals[cycle + 2] = (0, polynoms[1][vyr])
                            rez[cycle + 1][vyr] = rez[cycle][vyr]
                            rez[cycle + 2][vyr] = 0
                            rez[cycle + 3][vyr] = rez[cycle + 4][vyr]
                            cycle +=4
                        else:
                            rez[cycle + 1][vyr] = rez[cycle][vyr]
                            cycle +=2   
                        
                    cycle +=1
                    if(plus_inf_sign*rez[cycle][vyr] < 0):  
                        rez, intervals = add_columns(rez, intervals, lenn, vyr, cycle)
                        intervals[cycle] = intervals[cycle + 2] = (1,0)
                        intervals[cycle + 1] = (0, polynoms[1][vyr])
                        rez[cycle][vyr] = rez[cycle -1][vyr]
                        rez[cycle + 1][vyr] = 0
                        rez[cycle + 2][vyr] = plus_inf_sign
                    else:
                        rez[cycle][vyr] = plus_inf_sign  

        for vyr in range(len(rez)):          
            vyvod = True
            if(len(_polynoms_) == 0):
                vyvod = False
                continue
            for jj in _polynoms_:
                if( sorter(jj) > 0  and rez[vyr][pos_numb[1][jj]] not in _sign_[_polynoms_.index(jj)]):
                    vyvod = False
                    break
                elif  sorter(jj) <= 0  and zero_degree_sign[pos_numb[0][jj]] not in _sign_[_polynoms_.index(jj)]:
                    vyvod = False
                    break
            if(vyvod):
                is_true = True
                ret_polynoms.append([])
                ret_signs.append([])
               
                _len = len(ret_signs)
                for kk in range(consts, zero_degree):
                
                    ret_signs[_len -1].append([zero_degree_sign[kk]])
                    ret_polynoms[_len - 1].append(polynoms[0][kk])
                break
  
    if len(ret_polynoms) == 0 or is_true and len(ret_polynoms[0]) == 0:

        if len(ret_polynoms) == 0:
            ret_polynoms.append([])
            ret_signs.append([])
        sss = "1"
        if is_true:
            sss = "0"
        ret_polynoms[0].append(sy.poly(sy.sympify(sss), *perems))
        ret_signs[0].append([0])
    return ret_polynoms, ret_signs


   
          


# список списков выражений первый уорвенб коньюнкты, второй выражения
def print_all(polynoms, _sign_):
    aa = len(polynoms)
    rezult_string = ""
    for ii in range(aa):
        bb = len(polynoms[ii])
        rezult_string += " "
        for jj in range(bb):
            rezult_string += " ( " + string_form(polynoms[ii][jj])
            sign_ = _sign_[ii][jj]
            if len(sign_) != 1:
                print("error")
            else:
                sign_ = sign_[0]
            if sign_ == 1:
                rezult_string += (' > 0 )')
            elif sign_ == 0:
                rezult_string +=(' = 0 )')
            else:
                rezult_string +=(' < 0 )')
            if jj != bb - 1:
                rezult_string += " & "
        rezult_string = rezult_string + " |"

    rezult_string = rezult_string[:-2]
    if(rezult_string == ""):
        rezult_string = "(1 = 0)"
    if(rezult_string == " "):
        rezult_string = "(0 = 0)"
    if "0 = 0" in rezult_string:
        rezult_string = "( 0 = 0)"

    return rezult_string    
                

def add(polyn, polys, polys_0, queu, is_there):
    polyn = sy.poly_from_expr(polyn.as_expr(), *perems)[0]
   
    if(polyn not in is_there): # and (-polyn) not in is_there ):
        if sorter_1(polyn) > 0:
            is_there[polyn] = 1
            queu.put(polyn)
            polys.append(polyn)
        else:
            is_there[polyn] = 0
            polys_0.append(polyn)


def add_div(pol1, pol2, polyn,polys, polys_0, queu, is_there, div_pairs):
    polyn = sy.poly_from_expr(polyn.as_expr(), *perems)[0]
    div_pairs[(pol1,pol2)] = polyn
    # div_pairs[(pol1,pol1)] = polyn
    if(polyn not in is_there): # and (-polyn) not in is_there ):   
        if sorter_1(polyn) > 0:
            is_there[polyn] = 1
            queu.put(polyn)
            polys.append(polyn)
        else:
            is_there[polyn] = 0
            polys_0.append(polyn)
     

def closure_div(polys, polys_0, queu, is_there, div_pairs):
    for _i in range(len(polys)): 
        for _j in range(len(polys)):
            if _i != _j and (sy.degree(polys[_i], perems[0]) >= sy.degree(polys[_j], perems[0])) and (polys[_i],polys[_j]) not in div_pairs :     
                  
                _first , _second = sy.pdiv(polys[_i], polys[_j], gens = perems)
                add_div(polys[_i], polys[_j], _second, polys, polys_0, queu, is_there, div_pairs) 

def closure(polys, div_pairs, is_there):
    polys_0 = []
    queu = Queue()
    ii = 0
    while ii < len(polys):
        if sorter_1(polys[ii]) > 0:
            is_there[polys[ii]] = 1
            queu.put(polys[ii])
            ii +=1
        else:
            is_there[polys[ii]] = 0
            polys_0.append(1)
            polys_0[-1] = copy.deepcopy(polys[ii])
            del polys[ii]
    
    _ssize = len(polys)
    while(not(queu.empty())):
        while(not(queu.empty())):
            next = queu.get()
            polyn = sy.LC(next,perems[0])
            add(polyn, polys, polys_0, queu, is_there)

            polyn = (next - sy.LC(next,perems[0])*sy.LM(next,perems[0]))
            add(polyn, polys, polys_0, queu, is_there)

            polyn = (next.diff(perems[0]))
            add(polyn, polys, polys_0, queu, is_there)
        
        if(_ssize != len(polys)):
            closure_div(polys, polys_0, queu, is_there, div_pairs)
            _ssize = len(polys)

    closure_div(polys, polys_0, queu, is_there, div_pairs)
    return [sorted(polys_0, key = sorter, reverse=False), sorted(polys, key = sorter, reverse=False)]


_except_str_ = ""
def init(polynoms, _sign):
    string = sys.argv[3]
    disjunct_number = 0
    disjunct  = True
    pos = 0
    dict = {}
    length = len(string)
    while(pos != length):
        if(string[pos] == 'a' and disjunct):
            is_not = pos > 0 and string[pos-1] == "!" 
            pos +=2
            number = 0
            while(pos != length and str.isnumeric(string[pos])):
                number  = number *10 + int(string[pos])
                pos +=1
            pos -=1
            pol_string = sys.argv[4 + number]
            _except_str_ = pol_string
            pos1 = pol_string.find("=")
            pos2 = pol_string.find(">")
            pos3 = pol_string.find("<")

            if(pos3 != -1 and pol_string.find("<", pos3+1) == -1):
                polynom = sy.poly((sy.sympify(pol_string[0:pos3]) - sy.sympify(pol_string[pos3 + 1:])),*perems)
                sign = []
                if(is_not):
                    sign = [0,1]
                else:
                    sign = [-1]
                xx = dict.get(polynom)
                if xx == None:
                    polynoms[disjunct_number].append(polynom)
                    _sign[disjunct_number].append(sign)
                    dict[polynom] = len(_sign[disjunct_number]) - 1
                else:
                    inter = list(set(sign).intersection(set(_sign[disjunct_number][xx])))
                    if len(inter) ==0:
                        polynoms[disjunct_number] = []
                        disjunct = False
                    else:
                        _sign[disjunct_number][xx] = inter
            

            elif (pos1 != -1 and pol_string.find("=", pos1+1) == -1):
                polynom = sy.poly((sy.sympify(pol_string[0:pos1]) - sy.sympify(pol_string[pos1 + 1:])),*perems)
                sign = []
                if(is_not):
                    sign = [-1,1]
                else:
                    sign = [0]
                xx = dict.get(polynom)
                if xx == None:
                    polynoms[disjunct_number].append(polynom)
                    _sign[disjunct_number].append(sign)
                    dict[polynom] = len(_sign[disjunct_number]) - 1
                else:
                    inter = list(set(sign).intersection(set(_sign[disjunct_number][xx])))
                    if len(inter) ==0:
                        polynoms[disjunct_number] = []
                        disjunct = False
                    else:
                        _sign[disjunct_number][xx] = inter

            elif (pos2 != -1 and pol_string.find("=", pos2+1) == -1):
                polynom = sy.poly((sy.sympify(pol_string[0:pos2]) - sy.sympify(pol_string[pos2 + 1:])), *perems)
                sign = []
                if(is_not):
                    sign = [-1,0]
                else:
                    sign = [1]
                xx = dict.get(polynom)
                if xx == None:
                    polynoms[disjunct_number].append(polynom)
                    _sign[disjunct_number].append(sign)
                    dict[polynom] = len(_sign[disjunct_number]) - 1
                else:
                    inter = list(set(sign).intersection(set(_sign[disjunct_number][xx])))
                    if len(inter) ==0:
                        polynoms[disjunct_number] = []
                        disjunct = False
                    else:
                        _sign[disjunct_number][xx] = inter        

        elif(string[pos] == '|'):
            disjunct_number +=1
            polynoms.append([])
            _sign.append([])
            dict = {}
            disjunct = True
        pos +=1
        

def str_st():
    ss = ""
    string = sys.argv[2]
    for ch in string:
        ss += ch + ' '
    ss += "Z"
    return ss
try:
    if(len(sys.argv)> 2):
        # size = len(sys.argv)
        perems_string = str_st()
        remove_times = int(sys.argv[1])

        polynoms = [[]]
        sign = [[]]

        init(polynoms, sign)

        for times in range(remove_times):
            
            poly_close = []
            div_pairs = []
            is_there = []

            perems = sy.symbols(perems_string)

            for ii in range(len(polynoms)):
                div_pairs.append({})
                is_there.append({})
                poly_close.append(closure(copy.deepcopy(polynoms[ii]), div_pairs[ii], is_there[ii]))



            print("замыкания:")
            for ii in range(len(poly_close)):
                print("номер коньюнкта ", ii)
                print(*map(string_form,polynoms[ii]), sep=" ; ", end=":\n")
                for kk in range(2):
                    for jj in range(len(poly_close[ii][kk])):
                        print("    ",string_form(poly_close[ii][kk][jj]))
                print("количество в замыкании: ", len(poly_close[ii][0]) + len(poly_close[ii][1])) 
                print('\n')
             
            polynomss = []
            signss = []
            for ii in range(len(poly_close)):
                tmp1, tmp2 = fill_table(poly_close[ii], div_pairs[ii], is_there[ii], polynoms[ii], sign[ii])
                polynomss += tmp1
                signss += tmp2
            
            polynoms = copy.deepcopy(polynomss)
            sign = copy.deepcopy(signss)
            perems_string = perems_string[2:] + perems_string[:2]


    print(print_all(polynoms, sign))
except ValueError:
    print("valueError, формула мб введена неправильно: ", _except_str_ )
