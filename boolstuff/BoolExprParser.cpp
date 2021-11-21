/*  $Id: BoolExprParser.cpp,v 1.20 2017/12/09 05:42:48 sarrazip Exp $
    BoolExprParser.cpp - Boolean expression parser and syntax tree builder

    boolstuff - Disjunctive Normal Form boolean expression library
    Copyright (C) 2002-2016 Pierre Sarrazin <http://sarrazip.com/>

    This program is free software; you can redistribute it and/or
    modify it under the terms of the GNU General Public License
    as published by the Free Software Foundation; either version 2
    of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
    02110-1301, USA.
*/

#include "BoolExprParser.h"

#include <cassert>
#include <cstring>
#include <memory>
#include <string.h>

using namespace std;
using namespace boolstuff;


// Home-made replacement for auto_ptr<>, which is deprecated
// under gcc 6.1.0.
//
template <typename T>
class AutoPtr
{
public:
    AutoPtr(T *_ptr) : ptr(_ptr) {}
    ~AutoPtr() { delete ptr; }
    T *release() { T *ret = ptr; ptr = NULL; return ret; }
private:
    AutoPtr(const AutoPtr &);
    AutoPtr &operator = (const AutoPtr &);
private:
    T *ptr;
};


BoolExprParser::BoolExprParser()
  : curInput(),
    curIndex(0)
{
}


BoolExprParser::~BoolExprParser()
{
}


BoolExpr<string> *
BoolExprParser::parse(const std::string &expr)
{
    curInput = expr;
    curIndex = 0;

    AutoPtr< BoolExpr<string> > root(parseExpr());
    if (!atEnd())
        throw Error(curIndex, Error::GARBAGE_AT_END);
    return root.release();
}


BoolExpr<string> *
BoolExprParser::parseExpr()
{
    AutoPtr< BoolExpr<string> > left(parseTerm());

    if (!tokenSeen("|"))
        return left.release();

    skipToken("|");
    BoolExpr<string> *right = parseExpr();  // may throw
    return new BoolExpr<string>(BoolExpr<string>::OR, left.release(), right);
}


BoolExpr<string> *
BoolExprParser::parseTerm()
{
    AutoPtr< BoolExpr<string> > left(parseFactor());

    if (!tokenSeen("&"))
        return left.release();

    skipToken("&");
    BoolExpr<string> *right = parseTerm();  // may throw
    return new BoolExpr<string>(BoolExpr<string>::AND, left.release(), right);
}


BoolExpr<string> *
BoolExprParser::parseFactor()
{
    bool v = true;
    while (tokenSeen("!"))
    {
        skipToken("!");
        v = !v;
    }

    BoolExpr<string> *atom = parseAtom();  // may throw
    if (v)
        return atom;

    return new BoolExpr<string>(BoolExpr<string>::NOT, NULL, atom);
}


BoolExpr<string> *
BoolExprParser::parseAtom()
{
    skipSpaces();
    size_t startIndex = curIndex;
    if (tokenSeen("("))
    {
        skipToken("(");
        AutoPtr< BoolExpr<string> > expr(parseExpr());  // may throw

        if (!tokenSeen(")"))
            throw Error(startIndex, Error::RUNAWAY_PARENTHESIS);
        skipToken(")");

        return expr.release();
    }

    return parseIdentifier();  // may throw
}


BoolExpr<string> *
BoolExprParser::parseIdentifier()
{
    skipSpaces();
    size_t inputLen = curInput.length();
    if (curIndex == inputLen)
        throw Error(curIndex, Error::IDENTIFIER_EXPECTED);
    size_t startIndex = curIndex;
    while (curIndex < inputLen && isIdentifierChar(curInput[curIndex]))
        curIndex++;
    if (curIndex == startIndex)
        throw Error(startIndex, Error::IDENTIFIER_EXPECTED);
    string s(curInput, startIndex, curIndex - startIndex);
    return new BoolExpr<string>(s);
}


bool
BoolExprParser::atEnd()
{
    skipSpaces();
    return curIndex == curInput.length();
}


bool
BoolExprParser::tokenSeen(const char *s)
{
    if (s == NULL)
        return false;

    skipSpaces();
    return strncmp(curInput.c_str() + curIndex, s, strlen(s)) == 0;
}


void
BoolExprParser::skipToken(const char *s)
{
    curIndex += strlen(s);
}


void
BoolExprParser::skipSpaces()
{
    size_t inputLen = curInput.length();
    while (curIndex < inputLen && isspace(curInput[curIndex]))
        curIndex++;
}


bool
BoolExprParser::isIdentifierChar(char c) const
{
    return isalnum(c) || c == '_';
}
