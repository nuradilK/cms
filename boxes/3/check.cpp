#include <bits/stdc++.h>
#include "testlib.h"

#define ll long long

using namespace std;

int n;

int main(int argc, char* argv[]) {
    registerTestlibCmd(argc, argv);

    n = inf.readInt();

    int x = ouf.readInt(1, n - 1);
    int y = ans.readInt(1, n - 1);
    
    ll ff = x * 1LL * (x + 1) / 2;
    ll fff = y * 1LL * (y + 1) / 2;
    ll ss = (n * 1LL * (n + 1)) / 2 - ff;
    ll sss = (n * 1LL * (n + 1)) / 2 - fff; 
    
    if (abs(ff - ss) > abs(fff - sss)) quitf(_wa, "sorry :(");
    
    quitf(_ok, "OK");
}
