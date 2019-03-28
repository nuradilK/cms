sources = {

    'std::rcmp4.cpp': '''
#include "testlib.h"
#include <cmath>
using namespace std;
#define EPS 1E-4
string ending(int x)
{
    x %= 100;
    if (x / 10 == 1)
        return "th";
    if (x % 10 == 1)
        return "st";
    if (x % 10 == 2)
        return "nd";
    if (x % 10 == 3)
        return "rd";
    return "th";
}
int main(int argc, char * argv[])
{
    setName("compare two sequences of doubles, max absolute or relative error = %.5lf", EPS);
    registerTestlibCmd(argc, argv);
    int n = 0;
    double j, p;
    while (!ans.seekEof()) 
    {
      n++;
      j = ans.readDouble();
      p = ouf.readDouble();
      if (!doubleCompare(j, p, EPS))
        quitf(_wa, "%d%s numbers differ - expected: '%.5lf', found: '%.5lf', error = '%.5lf'", n, ending(n).c_str(), j, p, doubleDelta(j, p));
    }
    if (n == 1)
        quitf(_ok, "found '%.5lf', expected '%.5lf', error '%.5lf'", p, j, doubleDelta(j, p));
    quitf(_ok, "%d numbers", n);
}
''',

    'std::wcmp.cpp': '''
#include "testlib.h"
using namespace std;
string ending(int x)
{
    x %= 100;
    if (x / 10 == 1)
        return "th";
    if (x % 10 == 1)
        return "st";
    if (x % 10 == 2)
        return "nd";
    if (x % 10 == 3)
        return "rd";
    return "th";
}
int main(int argc, char * argv[])
{
    setName("compare sequences of tokens");
    registerTestlibCmd(argc, argv);
    std::string strAnswer;
    int n = 0;
    while (!ans.seekEof()) 
    {
      n++;
      std::string j = ans.readWord();
      std::string p = ouf.readWord();
      strAnswer = p;
      if (j != p)
        quitf(_wa, "%d%s words differ - expected: '%s', found: '%s'", n, ending(n).c_str(), j.c_str(), p.c_str());
    }
    if (n == 1 && strAnswer.length() <= 128)
        quitf(_ok, "%s", strAnswer.c_str());
    quitf(_ok, "%d words", n);
}
''',

    'std::fcmp.cpp': '''
#include "testlib.h"
#include <string>
#include <vector>
#include <sstream>
using namespace std;
string ending(int x)
{
    x %= 100;
    if (x / 10 == 1)
        return "th";
    if (x % 10 == 1)
        return "st";
    if (x % 10 == 2)
        return "nd";
    if (x % 10 == 3)
        return "rd";
    return "th";
}
int main(int argc, char * argv[])
{
    setName("compare files as sequence of lines");
    registerTestlibCmd(argc, argv);
    std::string strAnswer;
    int n = 0;
    while (!ans.eof()) 
    {
      std::string j = ans.readString();
      if (j == "" && ans.eof())
        break;
      strAnswer = j;

      std::string p = ouf.readString();
      n++;
      if (j != p)
        quitf(_wa, "%d%s lines differ - expected: '%s', found: '%s'", n, ending(n).c_str(), j.c_str(), p.c_str());
    }

    if (n == 1 && strAnswer.length() <= 128)
        quitf(_ok, "%s", strAnswer.c_str());
    quitf(_ok, "%d lines", n);
}
''',

    'std::rcmp6.cpp': '''
#include "testlib.h"
#include <cmath>
using namespace std;
#define EPS 1E-6
string ending(int x)
{
    x %= 100;
    if (x / 10 == 1)
        return "th";
    if (x % 10 == 1)
        return "st";
    if (x % 10 == 2)
        return "nd";
    if (x % 10 == 3)
        return "rd";
    return "th";
}
int main(int argc, char * argv[])
{
    setName("compare two sequences of doubles, max absolute or relative  error = %.7lf", EPS);
    registerTestlibCmd(argc, argv);
    int n = 0;
    double j, p;
    while (!ans.seekEof()) 
    {
      n++;
      j = ans.readDouble();
      p = ouf.readDouble();
      if (!doubleCompare(j, p, EPS))
        quitf(_wa, "%d%s numbers differ - expected: '%.7lf', found: '%.7lf', error = '%.7lf'", n, ending(n).c_str(), j, p, doubleDelta(j, p));
    }
    if (n == 1)
        quitf(_ok, "found '%.7lf', expected '%.7lf', error '%.7lf'", p, j, doubleDelta(j, p));
    quitf(_ok, "%d numbers", n);
}
''',

    'std::ncmp.cpp': '''
#include "testlib.h"
#include <sstream>

using namespace std;

int main(int argc, char * argv[])
{
    setName("compare ordered sequences of signed int%d numbers", 8 * int(sizeof(long long)));

    registerTestlibCmd(argc, argv);

    int n = 0;
    string firstElems;

    while (!ans.seekEof() && !ouf.seekEof())
    {
        n++;
        long long j = ans.readLong();
        long long p = ouf.readLong();
        if (j != p)
            quitf(_wa, "%d%s numbers differ - expected: '%s', found: '%s'", n, englishEnding(n).c_str(), vtos(j).c_str(), vtos(p).c_str());
        else
            if (n <= 5)
            {
                if (firstElems.length() > 0)
                    firstElems += " ";
                firstElems += vtos(j);
            }
    }

    int extraInAnsCount = 0;

    while (!ans.seekEof())
    {
        ans.readLong();
        extraInAnsCount++;
    }
    
    int extraInOufCount = 0;

    while (!ouf.seekEof())
    {
        ouf.readLong();
        extraInOufCount++;
    }

    if (extraInAnsCount > 0)
        quitf(_wa, "Answer contains longer sequence [length = %d], but output contains %d elements", n + extraInAnsCount, n);
    
    if (extraInOufCount > 0)
        quitf(_wa, "Output contains longer sequence [length = %d], but answer contains %d elements", n + extraInOufCount, n);
    
    if (n <= 5)
        quitf(_ok, "%d number(s): \\"%s\\"", n, compress(firstElems).c_str());
    else
        quitf(_ok, "%d numbers", n);
}
''',

    'std::hcmp.cpp': '''
#include "testlib.h"
#include <string>
using namespace std;
string part(const string& s)
{
    if (s.length() <= 128)
        return s;
    else
        return s.substr(0, 64) + "..." + s.substr(s.length() - 64, 64);
}
bool isNumeric(string p)
{
    bool minus = false;
    if (p[0] == '-')
        minus = true,
        p = p.substr(1);
    for (int i = 0; i < p.length(); i++)
        if (p[i] < '0' || p[i] > '9')
            return false;
    if (minus)
        return (p.length() > 0 && (p.length() == 1 || p[0] != '0')) && (p.length() > 1 || p[0] != '0');
    else
        return p.length() > 0 && (p.length() == 1 || p[0] != '0');
}
int main(int argc, char * argv[])
{
    setName("compare two signed huge integers");
    registerTestlibCmd(argc, argv);

    string ja = ans.readWord();
    string pa = ouf.readWord();
    if (!isNumeric(ja))
        quitf(_fail, "%s is not valid integer", part(ja).c_str());
    if (!ans.seekEof())
        quitf(_fail, "expected exactly one token in the answer file");

    if (!isNumeric(pa))
        quitf(_pe, "%s is not valid integer", part(pa).c_str());
    if (ja != pa)
        quitf(_wa, "expected %s, found %s", part(ja).c_str(), part(pa).c_str());

    quitf(_ok, "answer is %s", part(ja).c_str());
}	
''',

    'std::yesno.cpp': '''
#include "testlib.h"
std::string upper(std::string sa)
{
    for (size_t i = 0; i < sa.length(); i++)
        if ('a' <= sa[i] && sa[i] <= 'z')
            sa[i] = sa[i] - 'a' + 'A';
    return sa;
}
int main(int argc, char * argv[])
{
    setName("YES or NO (case insensetive)");
    registerTestlibCmd(argc, argv);
    std::string ja = upper(ans.readWord());
    std::string pa = upper(ouf.readWord());
    if (pa != "YES" && pa != "NO")
        quitf(_pe, "YES or NO expected, but %s found", pa.c_str());
    if (ja != "YES" && ja != "NO")
        quitf(_fail, "YES or NO expected in answer, but %s found", ja.c_str());
    if (ja != pa)
        quitf(_wa, "expected %s, found %s", ja.c_str(), pa.c_str());
    quitf(_ok, "answer is %s", ja.c_str());
}
''',

    'std::rcmp9.cpp': '''
#include "testlib.h"
#include <cmath>
using namespace std;
#define EPS 1E-9
string ending(int x)
{
    x %= 100;
    if (x / 10 == 1)
        return "th";
    if (x % 10 == 1)
        return "st";
    if (x % 10 == 2)
        return "nd";
    if (x % 10 == 3)
        return "rd";
    return "th";
}
int main(int argc, char * argv[])
{
    setName("compare two sequences of doubles, max absolute or relative error = %.10lf", EPS);
    registerTestlibCmd(argc, argv);
    int n = 0;
    double j, p;
    while (!ans.seekEof()) 
    {
      n++;
      j = ans.readDouble();
      p = ouf.readDouble();
      if (!doubleCompare(j, p, EPS))
        quitf(_wa, "%d%s numbers differ - expected: '%.10lf', found: '%.10lf', error = '%.10lf'", n, ending(n).c_str(), j, p, doubleDelta(j, p));
    }
    if (n == 1)
        quitf(_ok, "found '%.10lf', expected '%.10lf', error '%.10lf'", p, j, doubleDelta(j, p));
    quitf(_ok, "%d numbers", n);
}
''',

    'std::lcmp.cpp': '''
#include "testlib.h"
#include <string>
#include <vector>
#include <sstream>
using namespace std;
string ending(int x)
{
    x %= 100;
    if (x / 10 == 1)
        return "th";
    if (x % 10 == 1)
        return "st";
    if (x % 10 == 2)
        return "nd";
    if (x % 10 == 3)
        return "rd";
    return "th";
}
bool compareWords(string a, string b)
{
    vector<string> va, vb;
    stringstream sa;

    sa << a;
    string cur;
    while (sa >> cur)
        va.push_back(cur);
    stringstream sb;
    sb << b;
    while (sb >> cur)
        vb.push_back(cur);
    return (va == vb);
}
int main(int argc, char * argv[])
{
    setName("compare files as sequence of tokens in lines");
    registerTestlibCmd(argc, argv);
    std::string strAnswer;
    int n = 0;
    while (!ans.eof()) 
    {
      std::string j = ans.readString();
      if (j == "" && ans.eof())
        break;

      std::string p = ouf.readString();
      strAnswer = p;
      n++;
      if (!compareWords(j, p))
        quitf(_wa, "%d%s lines differ - expected: '%s', found: '%s'", n, ending(n).c_str(), j.c_str(), p.c_str());
    }

    if (n == 1 && strAnswer.length() <= 128)
        quitf(_ok, "%s", strAnswer.c_str());

    quitf(_ok, "%d lines", n);
}
''',
}
