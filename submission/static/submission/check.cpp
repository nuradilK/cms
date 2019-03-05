//#include "testlib.h"
//
//using namespace std;
//
//int main(int argc, char * argv[])
//{
//    setName("compare sequences of tokens");
//    registerTestlibCmd(argc, argv);
//
//    int n = 0;
//    string j, p;
//
//    while (!ans.seekEof() && !ouf.seekEof())
//    {
//        n++;
//
//        ans.readWordTo(j);
//        ouf.readWordTo(p);
//
//        if (j != p)
//            quitf(_wa, "%d%s words differ - expected: '%s', found: '%s'", n, englishEnding(n).c_str(), compress(j).c_str(), compress(p).c_str());
//    }
//
//    if (ans.seekEof() && ouf.seekEof())
//    {
//        if (n == 1)
//            quitf(_ok, "\"%s\"", compress(j).c_str());
//        else
//            quitf(_ok, "%d tokens", n);
//    }
//    else
//    {
//        if (ans.seekEof())
//            quitf(_wa, "Participant output contains extra tokens");
//        else
//            quitf(_wa, "Unexpected EOF in the participants output");
//    }
//}
#include <iostream>
#include <cstdio>
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <vector>
#include <set>
#include <map>
#include <cassert>
#include <queue>
#include <ctime>
#include <string>
#include <cstring>
#include "testlib.h"
#define mp make_pair
#define pb push_back
#define NAME ""
#define y1 y1_423
#define list lista

using namespace std;

typedef long long ll;
typedef long double ld;

const int nmax = 1000 * 1000;
const int maxn = 1000 * 100;
const int maxm = 1000 * 100;
const int maxc = 1000 * 100;

int n, m, c;
pair<int, int> a[nmax];
bool used[nmax];
int col[nmax], color[nmax];

inline int incr(int x) {
    return (x + 1) % c;
}

int readAns(InStream& in) {
    int answ = in.readInt(1, n, "ans");
    for (int i = 0; i < n; i++) {
        used[i] = false;
        col[i] = color[i];
    }
    for (int i = 0; i < answ; i++) {
        int x = in.readInt(1, n, format("ans[%d]", i)) - 1;
        if (used[x]) {
            in.quitf(_wa, "Vertex has been written multiple times, x = %d", x);
        }
        used[x] = true;
        col[x] = incr(col[x]);
    }
    for (int i = 0; i < m; i++) {
        if (col[a[i].first] == col[a[i].second]) {
            in.quitf(_wa, "The coloring is wrong, u = %d, v = %d", a[i].first, a[i].second);
        }
    }
    return answ;
}

int main(int argc, char *argv[]) {
	registerTestlibCmd(argc, argv);
	n = inf.readInt(1, maxn, "n");
    m = inf.readInt(1, maxm, "m");
	c = inf.readInt(1, maxc, "c");
	for (int i = 0; i < n; i++) {
        color[i] = inf.readInt();
	}
    for (int i = 0; i < m; i++) {
        int x = inf.readInt(1, n, format("x[%d]", i)) - 1;
        int y = inf.readInt(1, n, format("y[%d]", i)) - 1;
        a[i] = mp(x, y);
    }
	int pans = readAns(ouf);
	int jans = readAns(ans);
	if (pans == jans) {
		quitf(_ok, "Ok");
	} else if (pans < jans) {
		quitf(_fail, "Contestant found better answer than jury");
	} else if (pans > jans) {
		quitf(_wa, "Jury found better answer than contestant");
	}
	return -1;
}