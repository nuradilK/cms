#include <algorithm>
#include <iostream>
#include <iomanip>
#include <cstring>
#include <cstdlib>
#include <fstream>
#include <string>
#include <cstdio>
#include <vector>
#include <cmath>
#include <ctime>
#include <queue>
#include <deque>
#include <stack>
#include <map>
#include <set>

using namespace std;

#define pb push_back
#define f first
#define s second

typedef long long ll;
typedef unsigned long long ull;

ll n;

int main() {
  cin >> n;
  ll y = n * (n + 1) / 2;
  ll l = 0;
  ll r = n - 1;
  while (r - l > 1) {
    ll mid = (l + r) / 2;
    ll x = mid * (mid + 1) / 2;
    if (x + x > y) r = mid;
    else l = mid;
  }
  ll x = l * (l + 1) / 2;
  ll z = r * (r + 1) / 2;
  if (abs(y - (x + x)) < abs(y - (z + z))) {
    cout << l;
  } else {
    cout << r;
  }
  return 0;
}
