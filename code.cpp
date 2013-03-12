#include<iostream>
#include<string>

using namespace std;

int main(){
  float a = 2.4;
  string b = "SDSD"; 
  string* ptr = &b;
  string** ptr2 = &ptr;
  int k = 0;
  return 0;
}